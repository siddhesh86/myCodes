#!/usr/bin/env python

'''
Script to submit 'anaHHTo4W_3l_1qq.py' run jobs in condor.
The anaHHTo4W_3l_1qq.py is run for different combinations of ElectronID_sel, ElectronID_mvaTTH cut and for list of signal and background samples.

2020/07/06
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

'''
Test the following command before submitting the condor jobs: Sometime xrdfs command doesn't work on ui3, which can bring problem
    (xrdfs se01.indiacms.res.in:1094 ls -R /cms/store/user/ssawant/NanoAODPostProc_2017/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1)

'''

anaVersion = "_gen_v20200706_eIDGrid"

era = 2017

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

fAnaJobSubmissionLog = open("analyzeRun_HHTo4W_3l_1qq_gen_submission_%s.log" % sDateTime, 'w')

pwd = os.getcwd()

for ElectronID_sel in ElectronID_sel_list:
    print "ElectronID_sel: ",ElectronID_sel
    sys.stdout.flush()
    
    for sEle_mvaTTH, vEle_mvaTTH in ElectronID_mvaTTH_sel_list.items():
        print "ElectronID_mvaTTH_sel: %s %g" % (sEle_mvaTTH, vEle_mvaTTH)
        sys.stdout.flush()
        
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
            
            print "\n\n\n{},  {},  {}".format(ElectronID_sel, sEle_mvaTTH, sample_info["process_name_specific"])
            sys.stdout.flush()
            
            dirOutput = "%s/analyzeRun_hh_3l%s/%d/%s_%s/%s" % (pwd, anaVersion, era, ElectronID_sel, sEle_mvaTTH, sample_info["process_name_specific"])
            os.system("mkdir -p %s" % dirOutput)
            
            anaSettings = OD()
            
            anaSettings["era"]                     = era
            anaSettings["ElectronID_sel"]          = ElectronID_sel
            anaSettings["ElectronID_mvaTTH_sel"]   = vEle_mvaTTH
            
            anaSettings["type"]                    = sample_info["type"]
            anaSettings["process_name_specific"]   = sample_info["process_name_specific"]        
            anaSettings["sample_category"]         = sample_info["sample_category"]
            anaSettings["nof_events"]              = sample_info["nof_events"]
            #anaSettings["use_it"]                 = sample_info["use_it"]
            anaSettings["use_it"]                  = "True" if sample_info["use_it"] else "False"        
            anaSettings["xsection"]                = sample_info["xsection"]
            anaSettings["MiniAOD"]                 = sample_name
            anaSettings["NanoAOD"]                 = sample_info["NanoAOD"]
            anaSettings["NanoAOD_PostProc"]        = []
            
            nanoAOD_postproc_filelist = []
            T2Path0="root://se01.indiacms.res.in:1094/"
            DirToScpPath1="/cms/store/user/ssawant/NanoAODPostProc_2017/"
            DirToScpPath2= "%s/%s" % (sample_info["NanoAOD"].split("/")[1], sample_info["NanoAOD"].split("/")[2])
            DirToScpPath = DirToScpPath1 + DirToScpPath2
            cmd1 = "(xrdfs se01.indiacms.res.in:1094 ls -R %s) > %s/samplelist_4.txt" % (DirToScpPath, dirOutput)
            print "cmd1: ",cmd1
            getSampleList_style = 1
            try:
                #os.system(cmd1)
                output = subprocess.check_output(
                    cmd1, stderr=subprocess.STDOUT, shell=True, timeout=3,
                    universal_newlines=True)
                print "cmd1 output: ",output
            except: # try old command
                cmd2 = "(xrd se01.indiacms.res.in dirlistrec  %s) > %s/samplelist_4.txt" % (DirToScpPath, dirOutput)
                print "Now try, cmd2: ",cmd2
                os.system(cmd2)
                getSampleList_style = 2
            if getSampleList_style == 1:
                os.system("cat %s/samplelist_4.txt | grep root > %s/samplelist_1.txt" % (dirOutput, dirOutput))
            else: # getSampleList_style = 2
                os.system("cat %s/samplelist_4.txt | grep root | awk '{ print $5 }'> %s/samplelist_1.txt" % (dirOutput, dirOutput))
            
            print "DirToScpPath: ",DirToScpPath
            with open("%s/samplelist_1.txt" % dirOutput, 'r') as f:
                for line in f:
                    fileName = line.split("\n")[0]
                    print fileName
                    nanoAOD_postproc_filelist.append("%s%s" % (T2Path0, fileName))
            
            print "nanoAOD_postproc_filelist: \n",nanoAOD_postproc_filelist
            anaSettings["NanoAOD_PostProc"] = nanoAOD_postproc_filelist
            
            
            nTreeEntriesTotal = 0
            for fname in anaSettings["NanoAOD_PostProc"]:
                inFile = ROOT.TFile.Open(fname)
                if not inFile.IsOpen():
                    print "NanoAOD_PostProc file %s couldn't open \t\t\t ******* ERROR ********" % (fname)
                inTree = inFile.Get("Events")
                nTreeEntries = inTree.GetEntries()
                nTreeEntriesTotal += nTreeEntries
                inFile.Close()
                print "File %s,  nTreeEntries: %d, nTreeEntriesTotal: %d" % (fname, nTreeEntries, nTreeEntriesTotal)
            
            anaSettings["nof_events_NanoAOD_PostProc"] = nTreeEntriesTotal
            anaSettings["output_dir"]                  = dirOutput
            
            anaSettingsJSON = '%s/anaSettingsHHTo4W_3l_%s_%s_%s_cfg.json' % (dirOutput, anaSettings["ElectronID_sel"],sEle_mvaTTH, anaSettings["process_name_specific"])
            with open(anaSettingsJSON, 'w') as f:
                json.dump(anaSettings, f, sort_keys = False, indent = 4, ensure_ascii = False)
                
            if len(anaSettings["NanoAOD_PostProc"]) == 0:
                print "No NanoAOD_PostProc files could read \t\t **** ERROR **** \nNanoAOD_PostProc: {}  ".format(anaSettings["NanoAOD_PostProc"])
                fAnaJobSubmissionLog.write("%s %s %s \t No NanoAOD_PostProc files \t\t **** ERROR **** \n" % (anaSettings["ElectronID_sel"],anaSettings["ElectronID_mvaTTH_sel"], anaSettings["process_name_specific"]))
                continue
            if anaSettings["nof_events_NanoAOD_PostProc"] == 0:
                print "No events in NanoAOD_PostProc ({}) could read".format(anaSettings["nof_events_NanoAOD_PostProc"])
                fAnaJobSubmissionLog.write("%s %s %s \t No events in NanoAOD_PostProc \t\t **** ERROR **** \n" % (anaSettings["ElectronID_sel"],anaSettings["ElectronID_mvaTTH_sel"], anaSettings["process_name_specific"]))
                continue
            
            
            '''
        cmd1 = "time python %s/anaHHTo4W_3l_1qq_gen.py  %s " % (pwd, anaSettingsJSON)
            print "cmd: ",cmd1
            os.system(cmd1)
            '''
            
            
            condor_exec_file = '%s/condor_exec_%s_%s_%s.sh' % (dirOutput, anaSettings["ElectronID_sel"],sEle_mvaTTH,anaSettings["process_name_specific"])
            with open(condor_exec_file, 'w') as f:
                f.write("#!/bin/bash  \n\n")
                f.write("cd %s \n" % pwd)
                f.write("export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch \n")
                f.write("export SCRAM_ARCH=slc6_amd64_gcc630 \n")
                f.write("source /cvmfs/cms.cern.ch/cmsset_default.sh \n\n")
                #f.write("cd ")
                f.write("export X509_USER_PROXY=/home/ssawant/x509up_u56558 \n")
                f.write("eval \n")
                f.write("time python %s/anaHHTo4W_3l_1qq_gen.py  %s \n" % (pwd, anaSettingsJSON))
                #f.write("time python anaHHTo4W_3l_1qq.py  %s \n" % (pwd, anaSettingsJSON))
            
            condor_submit_file = '%s/condor_submit_%s_%s_%s.sh' % (dirOutput, anaSettings["ElectronID_sel"],sEle_mvaTTH,anaSettings["process_name_specific"])
            with open(condor_submit_file, 'w') as f:
                f.write("universe = vanilla \n")
                f.write("executable = %s \n" % condor_exec_file)
                f.write("getenv = TRUE \n")
                f.write("log = %s/anaHHTo4W_3l_1qq_%s_%s_%s.log \n" % (dirOutput, anaSettings["ElectronID_sel"],sEle_mvaTTH,anaSettings["process_name_specific"]))
                f.write("output = %s/anaHHTo4W_3l_1qq_%s_%s_%s.out \n" % (dirOutput, anaSettings["ElectronID_sel"],sEle_mvaTTH,anaSettings["process_name_specific"]))
                f.write("error = %s/anaHHTo4W_3l_1qq_%s_%s_%s.error \n" % (dirOutput, anaSettings["ElectronID_sel"],sEle_mvaTTH,anaSettings["process_name_specific"]))
                f.write("notification = never \n")
                f.write("should_transfer_files = YES \n")
                f.write("when_to_transfer_output = ON_EXIT \n")
                f.write("queue \n")
            
            os.system("chmod a+x %s" % condor_exec_file)
            os.system("chmod a+x %s" % condor_submit_file)
            
            cmd1 = "condor_submit %s" % condor_submit_file
            print "Now:  %s " % cmd1
            os.system(cmd1)
            sys.stdout.flush()


fAnaJobSubmissionLog.close()
