#!/usr/bin/env python

'''
Script to analyze event yield produced by 'anaHHTo4W_3l_1qq.py' and 'analyzeRun_HHTo4W_3l_1qq'.
The anaHHTo4W_3l_1qq.py is run for different combinations of ElectronID_sel, ElectronID_mvaTTH cut and for list of signal and background samples.

To run:
    time python analyzeEvtYield_HHTo4W_3l_1qq.py 2>&1 | tee cout_analyzeEvtYield_HHTo4W_3l_1qq_v20200707_eIDGrid_20200712_0.txt

2020/07/11
'''


from Samples_HH_wNanoAOD_2017_Final_20200703 import samples_2017 as samples
from collections import OrderedDict as OD
import json
import os
import subprocess
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
import time
import datetime
import sys
import glob
import math as math


era = 2017
anaVersion = "_gen_v20200706_eIDGrid" 
hist_stage1_FileSizeThrsh = 3000 # Minimum file size (in bytes) of hist_stage1 root file to consider the job ran successfully



signal_sample_ToUse = [
    "signal_ggf_spin0_400_hh_4v",
    #"signal_ggf_spin0_400_hh_2v2t", "signal_ggf_spin0_400_hh_4t"
]
#signal_sample_ToUse = ["WZTo3LNu"]
#signal_sample_ToUse = ["TTTo2L2Nu_PSweights"]

ElectronID_sel_list = [
    "Electron_mvaFall17V2noIso_WPL", "Electron_mvaFall17V2noIso_WP90", "Electron_mvaFall17V2noIso_WP80",
    "Electron_mvaFall17V2Iso_WPL",   "Electron_mvaFall17V2Iso_WP90",   "Electron_mvaFall17V2Iso_WP80",
]

ElectronID_mvaTTH_sel_list = OD([
    ("mvaTTH_m0p4", -0.4),
    ("mvaTTH_0",     0.0),
    ("mvaTTH_0p4",   0.4),
    ("mvaTTH_0p8",   0.8),    
])

sDateTime = str(datetime.datetime.now()) # for e.g. 2020-07-07 14:52:18.381356
print "sDateTime: ",sDateTime
sDateTime = sDateTime.replace("-", "_")
sDateTime = sDateTime.replace(":", "")
sDateTime = sDateTime.replace(" ", "_")
sDateTime = sDateTime.split(".")[0]
print "Datetime: {}, {}".format(datetime.datetime.now(), sDateTime)

#sDateTime = "tmp" 
fAnaEvtYieldLog = open("analyzeEvtYield_HHTo4W_3l_1qq_gen_EleEfficiency_%s.log" % sDateTime, 'w')
fAnaEvtYieldRootFile = None

pwd = os.getcwd()

sample_categories = []
selection_cuts = []

hDummy = ROOT.TH1D("hDummy","",1,-0.5,0.5)
hDummy.SetDefaultSumw2()


def analyzeEvtYield(histogramWorkingDir):    
    print "analyzeEvtYield:: \t histogramWorkingDir: %s" % histogramWorkingDir
    
    #fAnaEvtYieldRootFile = ROOT.TFile("analyzeEvtYield_HHTo4W_3l_1qq%s.root" % anaVersion, 'w')
    
    histogramWorkingDir_split = histogramWorkingDir.split("/")
    #print "histogramWorkingDir_split: {},  len: {}".format(histogramWorkingDir_split, len(histogramWorkingDir_split))
    ElectronID = histogramWorkingDir_split[len(histogramWorkingDir_split) - 1]
    print "ElectronID: ",ElectronID
    ElectronID_part1 = ElectronID.split("_mvaTTH")[0]
    print "ElectronID_part1: ",ElectronID_part1
    
    fHist_S = None
    hStat_S = None
    
    # Read input NanoAOD dataset from samples.py file
    for sample_name, sample_info in samples.items():
        #print "\n{}: {}".format(sample_name, sample_info)
        if sample_name == 'sum_events'  or  sample_info["type"] == "data":
            continue
        
        if sample_info["use_it"] == False:
            continue
        
        if not 'NANOAODSIM' in sample_info['NanoAOD']:
            continue
        
        #if ("signal" in sample_info["process_name_specific"])  and (not sample_info["process_name_specific"] in signal_sample_ToUse):
        #    continue
        if (not sample_info["process_name_specific"] in signal_sample_ToUse):
            continue
        
        sHist_S = "%s/%s/hist_stage1_%s_%s.root" % (histogramWorkingDir, sample_info["process_name_specific"], sample_info["process_name_specific"], ElectronID_part1)
        fHist_S = ROOT.TFile(sHist_S)
        if not fHist_S.IsOpen():
            print "Couldn't read %s \t\t ****** ERROR *******" % sHist_S
            exit(0)
        
        hStat_S = fHist_S.Get("%s/Stat1" % sample_info["sample_category"])
        
        nEventsGen   = 0
        nEventsReco  = 0
        enEventsGen  = 0
        enEventsReco = 0
        sLabelGen    = "genHH->4W -> 3l (1qq ?); l, j with CMS pt, eta acceptance; 3 genEle "
        sLabelReco   = ">=3 tightEle genMatch"
        kBinGen      = hStat_S.GetXaxis().FindBin(sLabelGen)
        kBinReco     = hStat_S.GetXaxis().FindBin(sLabelReco)
        nEventsGen   = hStat_S.GetBinContent(kBinGen)
        enEventsGen  = hStat_S.GetBinError(kBinGen)
        nEventsReco  = hStat_S.GetBinContent(kBinReco)
        enEventsReco = hStat_S.GetBinError(kBinReco)
        effi  = 0
        eeffi = 0
        if nEventsGen > 0:
            N  = nEventsReco
            D  = nEventsGen
            eN = enEventsReco
            eD = enEventsGen
            
            effi = N / D
            eeffi = (1./pow(D,2) * pow(eN,2)) + (pow(N,2)/pow(D,4) * pow(eD,2))
            eeffi = math.sqrt(eeffi)
            
        return (effi, eeffi)









if __name__ == "__main__":
    print "analyzeEvtYield_HHTo4W_3l_1qq:: main::"
    
    fAnaEvtYieldRootFile = ROOT.TFile("%s/analyzeRun_hh_3l%s/%d/analyzeEvtYield_HHTo4W_3l_1qq_gen_EleEfficiency.root" % (pwd, anaVersion, era), "RECREATE")
    
    SByB_dict = OD() #  represents electron efficiency in this macro
    for ElectronID_sel in ElectronID_sel_list:
        print "\n\nElectronID_sel: ",ElectronID_sel
        sys.stdout.flush()
        
        for sEle_mvaTTH, vEle_mvaTTH in ElectronID_mvaTTH_sel_list.items():
            print "\n\nElectronID_mvaTTH_sel: %s %g" % (sEle_mvaTTH, vEle_mvaTTH)
            sys.stdout.flush()
            
            histogramWorkingDir = "%s/analyzeRun_hh_3l%s/%d/%s_%s" % (pwd, anaVersion, era, ElectronID_sel, sEle_mvaTTH)
            
            SByB_FinalCut = analyzeEvtYield(histogramWorkingDir)
            
            if len(SByB_FinalCut) != 2:
                print "%s %s \t S/B: couldn't calculate \t\t ***** ERROR ******" % (ElectronID_sel, sEle_mvaTTH)
                #continue
                exit(0)
            
            sElectronID_nice = "%s mvaTTH > %s" % (ElectronID_sel, str(vEle_mvaTTH))
            sElectronID_nice = sElectronID_nice.replace("Electron_", "")
            SByB_dict[sElectronID_nice] = SByB_FinalCut
            print "%s  \t S/B: %g  +-  %g" % (sElectronID_nice, SByB_dict[sElectronID_nice][0], SByB_dict[sElectronID_nice][1])
    
    
    # S/B vs ElectronID histogram
    hSByB_vs_EleID = ROOT.TH1D("SByB_vs_EleID","#frac{S}{#sqrt{B}} vs electron ID", len(SByB_dict), 0.5, len(SByB_dict)+0.5)
    for index, sEleID in enumerate(SByB_dict):
        SByB    = SByB_dict[sEleID][0]
        errSByB = SByB_dict[sEleID][1]
        print "index {} \t sEleID {} \t s/b {} +- {}".format(index, sEleID, SByB, errSByB)
        hSByB_vs_EleID.GetXaxis().SetBinLabel(index+1, sEleID)
        hSByB_vs_EleID.SetBinContent(index+1, SByB)
        hSByB_vs_EleID.SetBinError(index+1, errSByB)
    
    fAnaEvtYieldRootFile.cd()
    hSByB_vs_EleID.Write()    
    fAnaEvtYieldRootFile.Close()
    
    fAnaEvtYieldLog.close()
    
    print "Done ***"
