import os
import sys
import traceback
import uproot as up

import python.l1THistos as histos
import python.file_manager as fm
import python.collections as collections
import python.calibrations as calibs
import python.tree_reader as treereader
import python.timecounter as timecounter


# @profile
def analyze(params, batch_idx=-1):
    print(params)
    debug = int(params.debug)

    input_files = []
    range_ev = (0, params.maxEvents)

    if params.events_per_job == -1:
        print("This is interactive processing...")
        input_files = fm.get_files_for_processing(
            input_dir=os.path.join(params.input_base_dir, params.input_sample_dir),
            tree=params.tree_name,
            nev_toprocess=params.maxEvents,
            debug=debug,
        )
    else:
        print("This is batch processing...")
        input_files, range_ev = fm.get_files_and_events_for_batchprocessing(
            input_dir=os.path.join(params.input_base_dir, params.input_sample_dir),
            tree=params.tree_name,
            nev_toprocess=params.maxEvents,
            nev_perjob=params.events_per_job,
            batch_id=batch_idx,
            debug=debug,
        )

    print(f"- will read {len(input_files)} files from dir {params.input_sample_dir}:")
    for file_name in input_files:
        print(f"        - {file_name}")

    files_with_protocol = [
        fm.get_eos_protocol(file_name) + file_name for file_name in input_files
    ]

    calib_manager = calibs.CalibManager()
    calib_manager.set_calibration_version(params.calib_version)
    if params.rate_pt_wps:
        calib_manager.set_pt_wps_version(params.rate_pt_wps)

    output = up.recreate(params.output_filename)
    hm = histos.HistoManager()
    hm.file = output

    # instantiate all the plotters
    plotter_collection = []
    plotter_collection.extend(params.plotters)

    # -------------------------BOOK HISTOS------------------------------

    for plotter in plotter_collection:
        plotter.book_histos()

    collection_manager = collections.EventManager()

    if params.weight_file is not None:
        collection_manager.read_weight_file(params.weight_file)

    # -------------------------EVENT LOOP--------------------------------

    tree_reader = treereader.TreeReader(range_ev, params.maxEvents)
    print(f"events_per_job: {params.events_per_job}")
    print(f"maxEvents: {params.maxEvents}")
    print(f"range_ev: {range_ev}")

    break_file_loop = False
    for tree_file_name in files_with_protocol:
        if break_file_loop:
            break

        tree_file = up.open(tree_file_name, num_workers=1)
        print(f"opening file: {tree_file_name}")
        print(f" . tree name: {params.tree_name}")

        def getUpTree(uprobj, name):
            parts = name.split("/")
            if len(parts) > 1:
                return getUpTree(uprobj, "/".join(parts[1:]))
            return uprobj[name]

        ttree = getUpTree(tree_file, params.tree_name)

        tree_reader.setTree(ttree)

        while tree_reader.next(debug):
            try:
                collection_manager.read(tree_reader, debug)

                for plotter in plotter_collection:
                    plotter.fill_histos_event(tree_reader.file_entry, debug=debug)

                if (
                    batch_idx != -1
                    and timecounter.counter.started()
                    and tree_reader.global_entry % 100 == 0
                ):
                    # when in batch mode, if < 5min are left we stop the event loop
                    if (
                        timecounter.counter.job_flavor_time_left(params.htc_jobflavor)
                        < 5 * 60
                    ):
                        tree_reader.printEntry()
                        print(
                            "    less than 5 min left for batch slot: exit event loop!"
                        )
                        timecounter.counter.job_flavor_time_perc(params.htc_jobflavor)
                        break_file_loop = True
                        break

            except Exception as inst:
                tree_reader.printEntry()
                print(f"[EXCEPTION OCCURRED:] {str(inst)}")
                print("Unexpected error:", sys.exc_info()[0])
                traceback.print_exc()
                tree_file.close()
                sys.exit(200)

        tree_file.close()

    print(f"Writing histos to file {params.output_filename}")
    hm.writeHistos()
    output.close()

    return tree_reader.n_tot_entries
