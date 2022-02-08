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
import glob

'''
Test the following command before submitting the condor jobs: Sometime xrdfs command doesn't work on ui3, which can bring problem
    (xrdfs se01.indiacms.res.in:1094 ls -R /cms/store/user/ssawant/NanoAODPostProc_2017/TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1)

'''


era = 2017
anaVersion = "_v20200707_eIDGrid"
hist_stage1_FileSizeThrsh = 3000 # Minimum file size (in bytes) of hist_stage1 root file to consider the job ran successfully


signal_sample_ToUse = ["signal_ggf_spin0_400_hh_4v", "signal_ggf_spin0_400_hh_2v2t", "signal_ggf_spin0_400_hh_4t"]
#signal_sample_ToUse = ["WZTo3LNu"]
#signal_sample_ToUse = ["TTTo2L2Nu_PSweights"]

processesToResubmit = ["TTWW_ext1", "TTTW", "TTTJ", "TTWZ", "TTZZ", "TTWH", "TTZH" ]

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

fAnaJobSubmissionLog = open("analyzeRun_HHTo4W_3l_1qq_submission_%s.log" % sDateTime, 'w')


pwd = os.getcwd()

for ElectronID_sel in ElectronID_sel_list:
    print "\n\nElectronID_sel: ",ElectronID_sel
    sys.stdout.flush()
    
    for sEle_mvaTTH, vEle_mvaTTH in ElectronID_mvaTTH_sel_list.items():
        print "\n\nElectronID_mvaTTH_sel: %s %g" % (sEle_mvaTTH, vEle_mvaTTH)
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
            
            if ("signal" in sample_info["process_name_specific"])  and (not sample_info["process_name_specific"] in signal_sample_ToUse):
                continue
            
            
            print "\n\n\n{},  {},  {}".format(ElectronID_sel, sEle_mvaTTH, sample_info["process_name_specific"])
            sys.stdout.flush()
            
            dirOutput = "%s/analyzeRun_hh_3l%s/%d/%s_%s/%s" % (pwd, anaVersion, era, ElectronID_sel, sEle_mvaTTH, sample_info["process_name_specific"])
            
            if not os.path.isdir(dirOutput):
                os.system("mkdir -p %s" % dirOutput)            
            
            print "ls -ltrh %s" % dirOutput
            os.system("ls -ltrh %s" % dirOutput) 
            
            anaSettingsJSON = '%s/anaSettingsHHTo4W_3l_%s_%s_%s_cfg.json' % (dirOutput, ElectronID_sel, sEle_mvaTTH, sample_info["process_name_specific"])
            
            # check if analysis-input JSON file exists. If exists then submit job with it
            isCfgJSONFileAlreadyExists = os.path.isfile(anaSettingsJSON)
            if not isCfgJSONFileAlreadyExists:
                with open(anaSettingsJSON, 'w') as fanaSettingsJSON:
                    
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
                        #print "cmd1 output: ",output
                    except: # try old command
                        cmd2 = "(xrd se01.indiacms.res.in dirlistrec  %s) > %s/samplelist_4.txt" % (DirToScpPath, dirOutput)
                        #print "Now try, cmd2: ",cmd2
                        os.system(cmd2)
                        getSampleList_style = 2
                    if getSampleList_style == 1:
                        os.system("cat %s/samplelist_4.txt | grep root > %s/samplelist_1.txt" % (dirOutput, dirOutput))
                    else: # getSampleList_style = 2
                        os.system("cat %s/samplelist_4.txt | grep root | awk '{ print $5 }'> %s/samplelist_1.txt" % (dirOutput, dirOutput))
                        
                    #print "DirToScpPath: ",DirToScpPath
                    with open("%s/samplelist_1.txt" % dirOutput, 'r') as f:
                        for line in f:
                            fileName = line.split("\n")[0]
                            #print fileName
                            nanoAOD_postproc_filelist.append("%s%s" % (T2Path0, fileName))
                    
                    print "nanoAOD_postproc_filelist: \n",nanoAOD_postproc_filelist
                    anaSettings["NanoAOD_PostProc"] = nanoAOD_postproc_filelist
                    
                    
                    nTreeEntriesTotal = 0
                    isTreesReadProperly = True
                    for fname in anaSettings["NanoAOD_PostProc"]:
                        try:
                            inFile = ROOT.TFile.Open(fname)
                        except:
                            #if not inFile.IsOpen():
                            print "NanoAOD_PostProc file %s couldn't open \t\t\t ******* ERROR ********" % (fname)
                            fAnaJobSubmissionLog.write("%s %s %s \t NanoAOD_PostProc file %s couldn't open \t\t **** ERROR **** \n" % (anaSettings["ElectronID_sel"],anaSettings["ElectronID_mvaTTH_sel"], anaSettings["process_name_specific"], fname))
                            isTreesReadProperly = False
                            continue
                        inTree = inFile.Get("Events")
                        nTreeEntries = inTree.GetEntries()
                        nTreeEntriesTotal += nTreeEntries
                        inFile.Close()
                        print "File %s,  nTreeEntries: %d, nTreeEntriesTotal: %d" % (fname, nTreeEntries, nTreeEntriesTotal)
                    
                    # not going ahead if any of the input tree couldn't open to calculate nTreeEntriesTotal. Otherwise it will create wrong lumiscale further in the analysis   
                    if not isTreesReadProperly: 
                        continue
                    
                    anaSettings["nof_events_NanoAOD_PostProc"] = nTreeEntriesTotal
                    anaSettings["output_dir"]                  = dirOutput
                    
                    # check input trees were read properly
                    if len(anaSettings["NanoAOD_PostProc"]) == 0:
                        print "No NanoAOD_PostProc files could read \t\t **** ERROR **** \nNanoAOD_PostProc: {}  ".format(anaSettings["NanoAOD_PostProc"])
                        fAnaJobSubmissionLog.write("%s %s %s \t No NanoAOD_PostProc files \t\t **** ERROR **** \n" % (anaSettings["ElectronID_sel"],anaSettings["ElectronID_mvaTTH_sel"], anaSettings["process_name_specific"]))
                        continue
                    if anaSettings["nof_events_NanoAOD_PostProc"] == 0:
                        print "No events in NanoAOD_PostProc ({}) could read".format(anaSettings["nof_events_NanoAOD_PostProc"])
                        fAnaJobSubmissionLog.write("%s %s %s \t No events in NanoAOD_PostProc \t\t **** ERROR **** \n" % (anaSettings["ElectronID_sel"],anaSettings["ElectronID_mvaTTH_sel"], anaSettings["process_name_specific"]))
                        continue
                    
                    
                    json.dump(anaSettings, fanaSettingsJSON, sort_keys = False, indent = 4, ensure_ascii = False)
            
           
            
            '''
            cmd1 = "time python %s/anaHHTo4W_3l_1qq.py  %s " % (pwd, anaSettingsJSON)
            print "cmd: ",cmd1
            os.system(cmd1)
            '''
            
            
            condor_exec_file = '%s/condor_exec_%s_%s_%s.sh' % (dirOutput, ElectronID_sel, sEle_mvaTTH, sample_info["process_name_specific"]) 
            if not os.path.isfile(condor_exec_file):
                with open(condor_exec_file, 'w') as f:
                    f.write("#!/bin/bash  \n\n")
                    f.write("cd %s \n" % pwd)
                    f.write("export VO_CMS_SW_DIR=/cvmfs/cms.cern.ch \n")
                    f.write("export SCRAM_ARCH=slc6_amd64_gcc700  \n")
                    f.write("source /cvmfs/cms.cern.ch/cmsset_default.sh \n\n")
                    #f.write("cd ")
                    f.write("export X509_USER_PROXY=/home/ssawant/x509up_u56558 \n")
                    f.write("eval \n")
                    f.write("time python %s/anaHHTo4W_3l_1qq.py  %s \n" % (pwd, anaSettingsJSON))
                    #f.write("time python anaHHTo4W_3l_1qq.py  %s \n" % (pwd, anaSettingsJSON))
            
            condor_submit_file = '%s/condor_submit_%s_%s_%s.sh' % (dirOutput, ElectronID_sel, sEle_mvaTTH, sample_info["process_name_specific"])
            if not os.path.isfile(condor_submit_file):
                with open(condor_submit_file, 'w') as f:
                    f.write("universe = vanilla \n")
                    f.write("executable = %s \n" % condor_exec_file)
                    f.write("getenv = TRUE \n")
                    f.write("log = %s/anaHHTo4W_3l_1qq_%s_%s_%s.log \n" % (dirOutput, ElectronID_sel, sEle_mvaTTH, sample_info["process_name_specific"]))
                    f.write("output = %s/anaHHTo4W_3l_1qq_%s_%s_%s.out \n" % (dirOutput, ElectronID_sel, sEle_mvaTTH, sample_info["process_name_specific"]))
                    f.write("error = %s/anaHHTo4W_3l_1qq_%s_%s_%s.error \n" % (dirOutput, ElectronID_sel, sEle_mvaTTH, sample_info["process_name_specific"]))
                    f.write("notification = never \n")
                    f.write("should_transfer_files = YES \n")
                    f.write("when_to_transfer_output = ON_EXIT \n")
                    f.write("queue \n")
            
            os.system("chmod a+x %s" % condor_exec_file)
            os.system("chmod a+x %s" % condor_submit_file)
            
            doSubmitJob = False
            if not isCfgJSONFileAlreadyExists: # fresh job
                doSubmitJob = True
            else: # submitted job
                isExecStarted  = os.path.isfile("%s/tmp_file_ExecutionStarted.txt" % dirOutput)
                isExecFinished = os.path.isfile("%s/tmp_file_ExecutionFinished.txt" % dirOutput)
                isHistFileZombi = False
                hist_stage1_list = glob.glob("%s/hist_stage1_*.root" % dirOutput)
                print "hist_stage1_list: ",hist_stage1_list
                for hist_file in hist_stage1_list:
                    file_size = os.stat(hist_file).st_size
                    print "hist_file: {}, size: {}  isSizeAboveThrsh: {}".format(hist_file, file_size, (file_size > hist_stage1_FileSizeThrsh))
                    if not file_size > hist_stage1_FileSizeThrsh:
                        isHistFileZombi = True
                        
                if isExecFinished and isHistFileZombi: # job finished successfully but root file is zombi. Less probable though
                    doSubmitJob = True
                
                if isExecStarted and (not isExecFinished) and isHistFileZombi: # job is either running or terminated with error
                    # check if job is terminated without suceesful execution
                    errorLog = ("%s/anaHHTo4W_3l_1qq_%s_%s_%s.error" % (dirOutput, ElectronID_sel, sEle_mvaTTH, sample_info["process_name_specific"]))
                    if not os.path.isfile(errorLog):
                        print "%s doesn't exists in submitted job.... Strange... \t\t ****** ERROR *******" % errorLog
                        exit(0)
                    else:
                        with open(errorLog, 'r') as ferrorLog:
                            isRealStringExists = False
                            isUserStringExists = False
                            isSysStringExists = False
                            # jobs are ran with 'time' presetter tag, so .error file of completed job will have, for e.g.,
                            #real    0m2.105s
                            #user    0m0.832s
                            #sys     0m0.763s
                            for line in ferrorLog:
                                if "real" in line and "m" in line and "." in line and "s" in line: # real    0m2.105s
                                    isRealStringExists = True
                                if "user" in line and "m" in line and "." in line and "s" in line: # user    0m2.105s
                                    isUserStringExists = True
                                if "sys" in line  and "m" in line and "." in line and "s" in line: # sys    0m2.105s
                                    isSysStringExists = True
                                
                            if  isRealStringExists and  isUserStringExists  and  isSysStringExists:
                                # job execution is done, but not 'tmp_file_ExecutionFinished.txt' file --> job got error. resubmit
                                doSubmitJob = True
            
            
            if sample_info["process_name_specific"] in processesToResubmit:
                doSubmitJob = True
                fAnaJobSubmissionLog.write("%s %s %s \t resubmitted as process is in processesToResubmit \n" % (ElectronID_sel, sEle_mvaTTH, sample_info["process_name_specific"]))
                
            print "doSubmitJob=",doSubmitJob            
            if not doSubmitJob:
                continue
            
            cmd1 = "condor_submit %s" % condor_submit_file
            print "Now:  %s " % cmd1            
            os.system(cmd1)
            fAnaJobSubmissionLog.write("%s %s %s \t condor_submit \n" % (ElectronID_sel, sEle_mvaTTH, sample_info["process_name_specific"]))
            sys.stdout.flush()


fAnaJobSubmissionLog.close()
