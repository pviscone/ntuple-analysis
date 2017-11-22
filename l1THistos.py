
import ROOT
import root_numpy as rnp
import numpy as np
import pandas as pd

class BaseHistos():
    def __init__(self, name, root_file=None):
        if root_file is not None:
            root_file.cd()
            histo_names = [histo.GetName() for histo in root_file.GetListOfKeys() if name+'_' in histo.GetName()]
            #print histo_names
            for histo_name in  histo_names:
                hinst = root_file.Get(histo_name)
                attr_name = 'h_'+histo_name.split('_')[2]
                setattr(self, attr_name, hinst)
#            self.h_test = root_file.Get('h_EleReso_ptRes')
            #print 'XXXXXX'+str(self.h_test)
        else:
            for histo in [a for a in dir(self) if a.startswith('h_')]:
                getattr(self, histo).Sumw2()

    def write(self):
        for histo in [a for a in dir(self) if a.startswith('h_')]:
            getattr(self, histo).Write()


class GenPartHistos():
    def __init__(self, name):
        self.h_pt = ROOT.TH1F(name+'_pt', 'Gen Part Pt (GeV)', 100, 0, 100)
        self.h_energy = ROOT.TH1F(name+'_energy', 'Gen Part Energy (GeV)', 100, 0, 100)

        for histo in [a for a in dir(self) if a.startswith('h_')]:
            getattr(self, histo).Sumw2()

    def fill(self, gps):
        rnp.fill_hist(self.h_pt, gps.pt)
        rnp.fill_hist(self.h_energy, gps.energy)

    def write(self):
        for histo in [a for a in dir(self) if a.startswith('h_')]:
            getattr(self, histo).Write()


class DigiHistos(BaseHistos):
    def __init__(self, name, root_file=None):
        if not root_file:
            self.h_layer = ROOT.TH1F(name+'_layer', 'Digi layer #', 60, 0, 60)
            self.h_simenergy = ROOT.TH1F(name+'_energy', 'Digi sim-energy (GeV)', 100, 0, 2)
        BaseHistos.__init__(self, name, root_file)

    def fill(self, digis):
        rnp.fill_hist(self.h_layer, digis.layer)
        rnp.fill_hist(self.h_simenergy, digis.simenergy)


class TCHistos(BaseHistos):
    def __init__(self, name, root_file=None):
        if not root_file:
            self.h_energy = ROOT.TH1F(name+'_energy', 'TC energy (GeV)', 100, 0, 2)
            self.h_subdet = ROOT.TH1F(name+'_subdet', 'TC subdet #', 8, 0, 8)
            self.h_layer = ROOT.TProfile(name+'_layer', 'TC layer #', 60, 0, 60, 's')
            self.h_absz = ROOT.TH1F(name+'_absz', 'TC z(cm)', 100, 300, 500)
            self.h_wafertype = ROOT.TH1F(name+'_wafertype', 'Wafer type', 10, 0, 10)
            self.h_layerVenergy = ROOT.TH2F(name+'_layerVenergy', "Energy (GeV) vs Layer #", 60, 0, 60, 100, 0, 2)
            self.h_energyVeta = ROOT.TH2F(name+'_energyVeta', "Energy (GeV) vs Eta", 100, -3.5, 3.5, 100, 0, 2)
            self.h_energyVetaL1t5 = ROOT.TH2F(name+'_energyVetaL1t5', "Energy (GeV) vs Eta (layers 1 to 5)", 100, -3.5, 3.5, 100, 0, 2)
            self.h_energyVetaL6t10 = ROOT.TH2F(name+'_energyVetaL6t10', "Energy (GeV) vs Eta (layers 6 to 10)", 100, -3.5, 3.5, 100, 0, 2)
            self.h_energyVetaL11t20 = ROOT.TH2F(name+'_energyVetaL11t20', "Energy (GeV) vs Eta (layers 11 to 20)", 100, -3.5, 3.5, 100, 0, 2)
            self.h_energyVetaL21t60 = ROOT.TH2F(name+'_energyVetaL21t60', "Energy (GeV) vs Eta (layers 21 to 60)", 100, -3.5, 3.5, 100, 0, 2)
            self.h_energyPetaVphi = ROOT.TProfile2D(name+'_energyPetaVphi', "Energy profile (GeV) vs Eta and Phi", 100, -3.5, 3.5, 100, -3.2, 3.2)

        BaseHistos.__init__(self, name, root_file)

    def fill(self, tcs):
        rnp.fill_hist(self.h_energy, tcs.energy)
        rnp.fill_hist(self.h_subdet, tcs.subdet)
        cnt = tcs.layer.value_counts().to_frame(name='counts')
        cnt['layer'] = cnt.index.values
        rnp.fill_profile(self.h_layer, cnt[['layer', 'counts']])
        rnp.fill_hist(self.h_absz, np.fabs(tcs.z))
        rnp.fill_hist(self.h_wafertype, tcs.wafertype)
        rnp.fill_hist(self.h_wafertype, tcs.wafertype)
        # FIXME: should bin this guy in eta bins
        rnp.fill_hist(self.h_layerVenergy, tcs[['layer', 'energy']])
        rnp.fill_hist(self.h_energyVeta, tcs[['eta', 'energy']])
        rnp.fill_hist(self.h_energyVeta, tcs[['eta', 'energy']])
        rnp.fill_hist(self.h_energyVetaL1t5, tcs[(tcs.layer >= 1) & (tcs.layer <= 5)][['eta', 'energy']])
        rnp.fill_hist(self.h_energyVetaL6t10, tcs[(tcs.layer >= 6) & (tcs.layer <= 10)][['eta', 'energy']])
        rnp.fill_hist(self.h_energyVetaL11t20, tcs[(tcs.layer >= 11) & (tcs.layer <= 20)][['eta', 'energy']])
        rnp.fill_hist(self.h_energyVetaL21t60, tcs[(tcs.layer >= 21) & (tcs.layer <= 60)][['eta', 'energy']])
        rnp.fill_profile(self.h_energyPetaVphi, tcs[['eta', 'phi', 'energy']])


class ClusterHistos(BaseHistos):
    def __init__(self, name, root_file=None):
        if not root_file:
            self.h_energy = ROOT.TH1F(name+'_energy', 'Cluster energy (GeV)', 100, 0, 20)
            self.h_layer = ROOT.TH1F(name+'_layer', 'Cluster layer #', 60, 0, 60)
            self.h_ncells = ROOT.TH1F(name+'_ncells', 'Cluster # cells', 30, 0, 30)
            self.h_layerVenergy = ROOT.TH2F(name+'_layerVenergy', "Cluster Energy (GeV) vs Layer #", 50, 0, 50, 100, 0, 20)
            self.h_layerVncells = ROOT.TH2F(name+'_layerVncells', "Cluster #cells vs Layer #",  50, 0, 50, 30, 0, 30)
        BaseHistos.__init__(self, name, root_file)

    def fill(self, selfts):
        rnp.fill_hist(self.h_energy, selfts.energy)
        rnp.fill_hist(self.h_layer, selfts.layer)
        rnp.fill_hist(self.h_ncells, selfts.ncells)
        rnp.fill_hist(self.h_layerVenergy, selfts[['layer', 'energy']])
        rnp.fill_hist(self.h_layerVncells, selfts[['layer', 'ncells']])


class Cluster3DHistos(BaseHistos):
    def __init__(self, name, root_file=None):
        if not root_file:
            self.h_pt = ROOT.TH1F(name+'_pt', '3D Cluster Pt (GeV)', 100, 0, 100)
            self.h_energy = ROOT.TH1F(name+'_energy', '3D Cluster energy (GeV)', 100, 0, 100)
            self.h_nclu = ROOT.TH1F(name+'_nclu', '3D Cluster # clusters', 30, 0, 30)
            self.h_showlenght = ROOT.TH1F(name+'_showlenght', '3D Cluster showerlenght', 60, 0, 60)
            self.h_firstlayer = ROOT.TH1F(name+'_firstlayer', '3D Cluster first layer', 30, 0, 30)
            self.h_sEtaEtaTot = ROOT.TH1F(name+'_sEtaEtaTot', '3D Cluster RMS Eta', 100, 0, 0.1)
            self.h_sEtaEtaMax = ROOT.TH1F(name+'_sEtaEtaMax', '3D Cluster RMS Eta (max)', 100, 0, 0.1)
            self.h_sPhiPhiTot = ROOT.TH1F(name+'_sPhiPhiTot', '3D Cluster RMS Phi', 100, 0, 2)
            self.h_sPhiPhiMax = ROOT.TH1F(name+'_sPhiPhiMax', '3D Cluster RMS Phi (max)', 100, 0, 2)
            self.h_sZZ = ROOT.TH1F(name+'_sZZ', '3D Cluster RMS Z ???', 100, 0, 10)
            self.h_eMaxOverE = ROOT.TH1F(name+'_eMaxOverE', '3D Cluster Emax/E', 100, 0, 1)
        BaseHistos.__init__(self, name, root_file)

    def fill(self, cl3ds):
        rnp.fill_hist(self.h_pt, cl3ds.pt)
        rnp.fill_hist(self.h_energy, cl3ds.energy)
        rnp.fill_hist(self.h_nclu, cl3ds.nclu)
        rnp.fill_hist(self.h_showlenght, cl3ds.showerlength)
        rnp.fill_hist(self.h_firstlayer, cl3ds.firstlayer)
        rnp.fill_hist(self.h_sEtaEtaTot, cl3ds.seetot)
        rnp.fill_hist(self.h_sEtaEtaMax, cl3ds.seemax)
        rnp.fill_hist(self.h_sPhiPhiTot, cl3ds.spptot)
        rnp.fill_hist(self.h_sPhiPhiMax, cl3ds.sppmax)
        rnp.fill_hist(self.h_sZZ, cl3ds.szz)
        rnp.fill_hist(self.h_eMaxOverE, cl3ds.emaxe)


class ResoHistos(BaseHistos):
    def __init__(self, name, root_file=None):
        self.h_ptRes = ROOT.TH1F(name+'_ptRes', '3D Cluster Pt reso (GeV)', 100, -10, 10)
        self.h_energyRes = ROOT.TH1F(name+'_energyRes', '3D Cluster Energy reso (GeV)', 200, -100, 100)
        self.h_ptResVeta = ROOT.TH2F(name+'_ptResVeta', '3D Cluster Pt reso (GeV) vs eta', 100, -3.5, 3.5, 100, -10, 10)
        self.h_energyResVeta = ROOT.TH2F(name+'_energyResVeta', '3D Cluster Pt reso (GeV) vs eta', 100, -3.5, 3.5, 200, -100, 100)

        BaseHistos.__init__(self, name, root_file)

    def fill(self, reference, target):
        self.h_ptRes.Fill(target.pt - reference.pt)
        self.h_energyRes.Fill(target.energy - reference.energy)
        self.h_ptResVeta.Fill(reference.eta, target.pt - reference.pt)
        self.h_energyResVeta.Fill(reference.eta, target.energy - reference.energy)


class GeomHistos(BaseHistos):
    def __init__(self, name, root_file=None):
        self.h_maxNNDistVlayer = ROOT.TH2F(name+'_maxNNDistVlayer', 'Max dist between NN vs layer', 60, 0, 60, 100, 0, 10)
        self.h_nTCsPerLayer = ROOT.TH1F(name+'_nTCsPerLayer', '# of Trigger Cells per layer', 60, 0, 60)
        self.h_radiusVlayer = ROOT.TH2F(name+'_radiusVlayer', '# of cells radius vs layer', 60, 0, 60, 200, 0, 200)
        BaseHistos.__init__(self, name, root_file)

    def fill(self, tcs):
        if False:
            ee_tcs = tcs[tcs.subdet == 3]
            for index, tc_geom in ee_tcs.iterrows():
                self.h_maxNNDistVlayer.Fill(tc_geom.layer, np.max(tc_geom.neighbor_distance))

        rnp.fill_hist(self.h_nTCsPerLayer, tcs[tcs.subdet == 3].layer)
        rnp.fill_hist(self.h_radiusVlayer, tcs[['layer', 'radius']])
