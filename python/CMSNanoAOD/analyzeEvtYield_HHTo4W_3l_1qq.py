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
anaVersion = "_v20200707_eIDGrid"
hist_stage1_FileSizeThrsh = 3000 # Minimum file size (in bytes) of hist_stage1 root file to consider the job ran successfully



signal_sample_ToUse = ["signal_ggf_spin0_400_hh_4v", "signal_ggf_spin0_400_hh_2v2t", "signal_ggf_spin0_400_hh_4t"]
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
fAnaEvtYieldLog = open("analyzeEvtYield_HHTo4W_3l_1qq_%s.log" % sDateTime, 'w')
fAnaEvtYieldRootFile = None 
fAnaEvtYieldAll = None

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
    
    
    sHistosToAdd = "%s/*/hist_stage1_*.root" % (histogramWorkingDir)
    sHistoAdded  = "%s/hist_stage1_%s.root" % (histogramWorkingDir,ElectronID)
    cmd1 = "hadd -f  %s  %s  " % (sHistoAdded, sHistosToAdd)
    print "cmd: ",cmd1;  sys.stdout.flush();
    os.system(cmd1)
    
    # open hadd_stage1.root
    histoAdded = ROOT.TFile(sHistoAdded)
    if not histoAdded.IsOpen():
        print "%s coludn't open \t\t ***** ERROR *****" % (sHistoAdded)
        return
    
    
    if (len(sample_categories) == 0):
        # Read input NanoAOD dataset from samples.py file
        for sample_name, sample_info in samples.items():
            #print "\n{}: {}".format(sample_name, sample_info)
            if sample_name == 'sum_events'  or  sample_info["type"] == "data":
                continue
            
            if sample_info["use_it"] == False:
                continue
            
            if not 'NANOAODSIM' in sample_info['NanoAOD']:
                continue
            
            if ("signal" in sample_info["process_name_specific"])  and (not sample_info["process_name_specific"] in signal_sample_ToUse):
                continue
            
            if not sample_info["sample_category"] in sample_categories:
                sample_categories.append(sample_info["sample_category"])
            
            
            # Fill selection_cuts list. Use signal Stat1 histogram.
            if sample_info["process_name_specific"] == signal_sample_ToUse[0]:
                hStat_wtd = histoAdded.Get("%s/Stat1_wtd" % (sample_info["sample_category"]))
                if not hStat_wtd:
                    print "hadd:signal failed to read histo Stat1_wtd \t\t ***** ERROR *****" % (sfHist)
                    exit(0)
                    
                for iBin in range(1, hStat_wtd.GetNbinsX()+1):
                    binLabel = hStat_wtd.GetXaxis().GetBinLabel(iBin)
                    if binLabel:
                        selection_cuts.append(binLabel)
        
        
        print "sample_categories: ",sample_categories;
        print "selection_cuts: ",selection_cuts
        
    
    kBin_selection_cut_Last = len(selection_cuts)
    selection_cut_Last      = selection_cuts[-1]
    print "len(selection_cuts): ",len(selection_cuts)
    print "kBin_selection_cut_Last: ",kBin_selection_cut_Last
    print "selection_cut_Last: intended {},  used {}".format(selection_cut_Last, selection_cuts[kBin_selection_cut_Last - 1])
    sys.stdout.flush();
    
    #fAnaEvtYieldRootFile.cd()
    hStat_wtd_S = None
    hStat_wtd_B = None
    evtYield_S_dict = OD()
    evtYield_B_dict = OD()
    
    for category in sample_categories:
        hStat     = histoAdded.Get("%s/Stat1" % (category))
        hStat_wtd = histoAdded.Get("%s/Stat1_wtd" % (category))
        
        #fAnaEvtYieldRootFile.cd()
        if 'signal' in category:
            if not hStat_wtd_S:
                hStat_wtd_S = hStat_wtd.Clone("hStat_wtd_Signal_%s" % (ElectronID))
                #hStat_wtd_S.SetDirectory(0)
            else:
                hStat_wtd_S.Add(hStat_wtd)
        else:
            if not hStat_wtd_B:
                hStat_wtd_B = hStat_wtd.Clone("hStat_wtd_Bk_%s" % (ElectronID))
                #hStat_wtd_B.SetDirectory(0)
            else:
                hStat_wtd_B.Add(hStat_wtd)
        
        # validation
        if 'signal' in category:
            sUsed_selection_cut_Last = hStat_wtd.GetXaxis().GetBinLabel(kBin_selection_cut_Last)
            if sUsed_selection_cut_Last != selection_cut_Last: # Big error
                print "hStat bin read for event yield table (%s) is wrong (not %s) \t\t\t ****** ERROR ******" % (sUsed_selection_cut_Last, selection_cut_Last)
                exit(0)
        
        sBinLabel_tmp = hStat_wtd.GetXaxis().GetBinLabel(kBin_selection_cut_Last)
        nEvts         = hStat_wtd.GetBinContent(kBin_selection_cut_Last)
        errnEvts      = hStat_wtd.GetBinError(kBin_selection_cut_Last)
        nEvts_UnWtd   = hStat.GetBinContent(kBin_selection_cut_Last)
        print "Category %s: %g  +-  %g (%g) \t %s %g %s" % (category, nEvts,errnEvts,nEvts_UnWtd, selection_cut_Last,kBin_selection_cut_Last,sBinLabel_tmp)
        
        if 'signal' in category:
            evtYield_S_dict[category] = OD([ ("nEvents",nEvts), ("errNEvents",errnEvts), ("nEvents_unweighted",nEvts_UnWtd) ])
        else:
            evtYield_B_dict[category] = OD([ ("nEvents",nEvts), ("errNEvents",errnEvts), ("nEvents_unweighted",nEvts_UnWtd) ]) 
    
    print "evtYield_S_dict: ", json.dumps(evtYield_S_dict, sort_keys = False, indent = 4, ensure_ascii = False)
    print "evtYield_B_dict: ", json.dumps(evtYield_B_dict, sort_keys = False, indent = 4, ensure_ascii = False)
    
    evtYield_B_dict_sorted = OD(sorted(evtYield_B_dict.items(), key = lambda t: t[1]["nEvents"],  reverse=True)) # t[1][0]: [1]: Read (nEvts, errnEvts).  [0]: read nEvts from (nEvts, errnEvts)
    print "\nAfter sorting \nevtYield_B_dict_sorted:  ", json.dumps(evtYield_B_dict_sorted, sort_keys = False, indent = 4, ensure_ascii = False)
    sys.stdout.flush();
    
    SByB_FinalCut = None
    #fAnaEvtYieldRootFile.cd()
    hStat_wtd_SByB = hStat_wtd_S.Clone("hStat_wtd_SByB_%s" % (ElectronID))
    for iBin in range(1, hStat_wtd_SByB.GetNbinsX()+1):
        binLabel = hStat_wtd_SByB.GetXaxis().GetBinLabel(iBin)
        if not binLabel:
            continue
        
        S  = hStat_wtd_S.GetBinContent(iBin)
        B  = hStat_wtd_B.GetBinContent(iBin)
        eS = hStat_wtd_S.GetBinError(iBin)
        eB = hStat_wtd_B.GetBinError(iBin)
        SByB  = S / math.sqrt(B)
        eSByB = (1/B * pow(eS,2)) + (pow(S,2)/(4*pow(B,3)) * pow(eB,2))
        eSByB = math.sqrt(eSByB)
        print "%-50s  S: %g +- %g, \t B: %g +- %g, \t\t S/B: %g +- %g" % (binLabel, S,eS, B,eB, SByB,eSByB)
        
        hStat_wtd_SByB.SetBinContent(iBin, SByB)
        hStat_wtd_SByB.SetBinError(iBin, eSByB)
        
        if binLabel == 'MEt filters':
            SByB_FinalCut = (SByB, eSByB)
    
    
    
    #hStat_wtd_S.SetDirectory (0)
    #hStat_wtd_B.SetDirectory (0)
    #hStat_wtd_SByB.SetDirectory (0)
    sys.stdout.flush();
    
    #fAnaEvtYieldRootFile = ROOT.TFile("analyzeEvtYield_HHTo4W_3l_1qq%s.root" % anaVersion, 'w')
    #fAnaEvtYieldRootFile = ROOT.TFile("anaTest.root", "RECREATE")
    if not fAnaEvtYieldRootFile.IsOpen():
        print "o/p root files not open"
    else:
        print "o/p root files opened"
    fAnaEvtYieldRootFile.cd()
    hStat_wtd_S.Write()
    hStat_wtd_B.Write()
    hStat_wtd_SByB.Write()
    #fAnaEvtYieldRootFile.Write()
    #fAnaEvtYieldRootFile.Close()
    sys.stdout.flush();


    # Write event yield into .txt file
    fAnaEvtYield_EleID = open("%s/EventYield_%s.txt"  % (histogramWorkingDir, ElectronID), 'w')
    sline = "%-50s \t S/sqrt(B) = %g  +-  %g \n\n\n" % (ElectronID, SByB_FinalCut[0],SByB_FinalCut[1])
    fAnaEvtYield_EleID.write(sline);    fAnaEvtYieldAll.write(sline);
    sline = "%-30s \t %35s \t %35s \t %35s \n\n" % ("Sample category", "No. of selected events", "Error on no. of selected events", "No. of selected unweighted events")
    fAnaEvtYield_EleID.write(sline);    fAnaEvtYieldAll.write(sline);
    for sample_category, evtYieldDetails in evtYield_S_dict.items():
        sline = "%-30s \t %35.3f \t %35.3f \t %35d \n" % (sample_category, evtYieldDetails["nEvents"], evtYieldDetails["errNEvents"], evtYieldDetails["nEvents_unweighted"])
        fAnaEvtYield_EleID.write(sline);    fAnaEvtYieldAll.write(sline);
    sline = "\n"
    fAnaEvtYield_EleID.write(sline);    fAnaEvtYieldAll.write(sline);
    for sample_category, evtYieldDetails in evtYield_B_dict_sorted.items():
        sline = "%-30s \t %35.3f \t %35.3f \t %35d \n" % (sample_category, evtYieldDetails["nEvents"], evtYieldDetails["errNEvents"], evtYieldDetails["nEvents_unweighted"])
        fAnaEvtYield_EleID.write(sline);    fAnaEvtYieldAll.write(sline);
    sline = "\n\n\n\n\n"
    fAnaEvtYield_EleID.write(sline);    fAnaEvtYieldAll.write(sline);        
    fAnaEvtYield_EleID.close()
    
    return SByB_FinalCut








if __name__ == "__main__":
    print "analyzeEvtYield_HHTo4W_3l_1qq:: main::"
    
    fAnaEvtYieldRootFile = ROOT.TFile("%s/analyzeRun_hh_3l%s/%d/analyzeEvtYield_HHTo4W_3l_1qq.root" % (pwd, anaVersion, era), "RECREATE")
    fAnaEvtYieldAll = open("%s/analyzeRun_hh_3l%s/%d/EventYield_ElectronID_All.txt"  % (pwd, anaVersion, era), 'w')
    
    SByB_dict = OD()
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
    #fAnaEvtYieldRootFile.Write()
    fAnaEvtYieldRootFile.Close()
    
    fAnaEvtYieldLog.close()
    fAnaEvtYieldAll.close()
    
    print "Done ***"
