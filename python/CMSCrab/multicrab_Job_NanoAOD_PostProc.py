#!/usr/bin/env python
"""
This is a small script that does the equivalent of multicrab.

To run:
  ./multicrab --crabCmd CMD [--workArea WAD --crabCmdOpts OPTS]
  where CMD is the crab command, WAD is a work area directory with many CRAB project directories inside and OPTS are options for the crab command. 

For e.g.
Command to crab submit:
  ./multicrab_Job_<current file>.py --crabCmd submit

Command to crab status:
  ./multicrab_Job_<current file>.py --crabCmd status --workArea <working area (common)>

"""

import os
from optparse import OptionParser

from CRABAPI.RawCommand import crabCommand
from CRABClient.ClientExceptions import ClientException
from httplib import HTTPException

from Samples_HH_wNanoAOD_2017_Final_20200703 import samples_2017 as samples

era = 2017

def getOptions():
    """
    Parse and return the arguments provided by the user.
    """
    usage = ("Usage: %prog --crabCmd CMD [--workArea WAD --crabCmdOpts OPTS]"
             "\nThe multicrab command executes 'crab CMD OPTS' for each project directory contained in WAD"
             "\nUse multicrab -h for help")

    parser = OptionParser(usage=usage)

    parser.add_option('-c', '--crabCmd',
                      dest = 'crabCmd',
                      default = '',
                      help = "crab command",
                      metavar = 'CMD')

    parser.add_option('-w', '--workArea',
                      dest = 'workArea',
                      default = '',
                      help = "work area directory (only if CMD != 'submit')",
                      metavar = 'WAD')

    parser.add_option('-o', '--crabCmdOpts',
                      dest = 'crabCmdOpts',
                      default = '',
                      help = "options for crab command CMD",
                      metavar = 'OPTS')

    (options, arguments) = parser.parse_args()

    if arguments:
        parser.error("Found positional argument(s): %s." % (arguments))
    if not options.crabCmd:
        parser.error("(-c CMD, --crabCmd=CMD) option not provided.")
    if options.crabCmd != 'submit':
        if not options.workArea:
            parser.error("(-w WAR, --workArea=WAR) option not provided.")
        if not os.path.isdir(options.workArea):
            parser.error("'%s' is not a valid directory." % (options.workArea))

    return options


def main():

    options = getOptions()

    # The submit command needs special treatment.
    if options.crabCmd == 'submit':

        #--------------------------------------------------------
        # This is the base config:
        #--------------------------------------------------------
        from CRABClient.UserUtilities import config
        config = config()
        
        config.General.requestName = None
        #config.General.workArea = None
        
        config.General.transferOutputs = True
        config.General.transferLogs = False
        
        config.JobType.pluginName = 'Analysis'
        config.JobType.psetName = 'PSet.py'
        config.JobType.scriptExe = 'crab_script.sh'
        config.JobType.inputFiles = ['example_postproc_2017_MC.py','../scripts/haddnano.py'] #hadd nano will not be needed once nano tools are in cmssw
        config.JobType.sendPythonFolder	 = True
        config.JobType.allowUndistributedCMSSW = True
        
        config.Data.inputDataset = None
        config.Data.inputDBS = 'global'
        config.Data.splitting = 'FileBased' # 'Automatic' #'LumiBased'
        #config.Data.splitting = 'EventAwareLumiBased'
        config.Data.unitsPerJob = 2
        config.Data.totalUnits = 10
        
        config.Data.outLFNDirBase = '/store/user/ssawant/NanoAODPostProc_%d' % era 
        config.Data.publication = False
        config.Data.outputDatasetTag = None ####
        #config.Data.useParent = True
        
        config.Site.storageSite = 'T2_IN_TIFR' # Choose your site. 
        #--------------------------------------------------------
        
        # Will submit one task for each of these input datasets.
        inputDatasets = []
        
        # Read input NanoAOD dataset from samples.py file
        for sample_name, sample_info in samples.items():
            #print "\n{}: {}".format(sample_name, sample_info)
            if sample_name == 'sum_events'  or  sample_info["type"] == "data":
                continue
            
            if sample_info["use_it"] == False:
                continue
            
            if 'NANOAODSIM' in sample_info['NanoAOD']:
                if not sample_info["process_name_specific"] in ["signal_ggf_spin0_400_hh_4t", "signal_ggf_spin0_400_hh_2v2t", "signal_ggf_spin0_400_hh_4v"]:
                    continue
                inputDatasets.append(sample_info['NanoAOD'])
        
        
        
        
        for inDS in inputDatasets: 
            config.General.requestName = inDS.split('/')[1] # sample name
            #config.General.workArea = config.General.requestName
            config.Data.inputDataset = inDS
            config.Data.outputDatasetTag = '%s' % (inDS.split('/')[2]) # Campaign GT details
            
            # Submit.
            try:
                print "Submitting for input dataset %s" % (inDS)
                crabCommand(options.crabCmd, config = config, *options.crabCmdOpts.split())
            except HTTPException as hte:
                print "Submission for input dataset %s failed: %s" % (inDS, hte.headers)
            except ClientException as cle:
                print "Submission for input dataset %s failed: %s" % (inDS, cle)
        
    # resubmit FAILED jobs
    elif options.crabCmd == 'resubmit' and options.workArea:
        
        for dir in os.listdir(options.workArea):
            projDir = os.path.join(options.workArea, dir)
            if not os.path.isdir(projDir):
                continue
            # Execute the crab status.
            msg = "Executing (the equivalent of): crab status --dir %s %s" % (projDir, options.crabCmdOpts)
            print "-"*len(msg)
            print msg
            print "-"*len(msg)
         
            result = crabCommand("status", dir = projDir, *options.crabCmdOpts.split())
            print "\n\nresult of the crab resubmit: ",result
            print "result['status']: ",result['status']
            print "result['dagStatus']: ",result['dagStatus']
            if not result['status'] in ['FAILED', 'SUBMITFAILED']:
                continue
            print "crab_resubmit: %s  *******" % projDir
            
            # resubmit
            try:
                crabCommand("resubmit", dir = projDir, *options.crabCmdOpts.split())
            except HTTPException as hte:
                print "Failed executing command %s for task %s: %s" % (options.crabCmd, projDir, hte.headers)
            except ClientException as cle:
                print "Failed executing command %s for task %s: %s" % (options.crabCmd, projDir, cle)
            
            
    # All other commands can be simply executed.
    elif options.workArea:
        
        for dir in os.listdir(options.workArea):
            projDir = os.path.join(options.workArea, dir)
            if not os.path.isdir(projDir):
                continue
            # Execute the crab command.
            msg = "Executing (the equivalent of): crab %s --dir %s %s" % (options.crabCmd, projDir, options.crabCmdOpts)
            print "-"*len(msg)
            print msg
            print "-"*len(msg)
            try:
                crabCommand(options.crabCmd, dir = projDir, *options.crabCmdOpts.split())
            except HTTPException as hte:
                print "Failed executing command %s for task %s: %s" % (options.crabCmd, projDir, hte.headers)
            except ClientException as cle:
                print "Failed executing command %s for task %s: %s" % (options.crabCmd, projDir, cle)


if __name__ == '__main__':
    main()
