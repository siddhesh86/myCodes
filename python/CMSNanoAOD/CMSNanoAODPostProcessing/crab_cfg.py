from WMCore.Configuration import Configuration
#from CRABClient.UserUtilities import config, getUsernameFromSiteDB
from CRABClient.UserUtilities import config

config = Configuration()

config.section_("General")
config.General.requestName = 'NanoPost2'
config.General.transferLogs=True

config.section_("JobType")
config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'PSet.py'
config.JobType.scriptExe = 'crab_script.sh'
#config.JobType.inputFiles = ['crab_script.py','../scripts/haddnano.py'] #hadd nano will not be needed once nano tools are in cmssw
config.JobType.inputFiles = ['example_postproc_2017_MC.py','../scripts/haddnano.py'] #hadd nano will not be needed once nano tools are in cmssw
config.JobType.sendPythonFolder	 = True
config.JobType.allowUndistributedCMSSW = True

config.section_("Data")
#config.Data.inputDataset = '/DYJetsToLL_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17NanoAOD-PU2017_12Apr2018_94X_mc2017_realistic_v14-v1/NANOAODSIM'
config.Data.inputDataset = '/GluGluToRadionToHHTo4V_M-400_narrow_13TeV-madgraph_correctedcfg/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/NANOAODSIM'
#config.Data.inputDBS = 'phys03'
config.Data.inputDBS = 'global'
config.Data.splitting = 'FileBased'
#config.Data.splitting = 'EventAwareLumiBased'
config.Data.unitsPerJob = 2
config.Data.totalUnits = 10

#config.Data.outLFNDirBase = '/store/user/%s/NanoPost' % (getUsernameFromSiteDB())
config.Data.outLFNDirBase = '/store/user/ssawant/NanoPost' 
config.Data.publication = False
config.Data.outputDatasetTag = 'NanoTestPost'
config.section_("Site")
config.Site.storageSite = "T2_IN_TIFR"

#config.Site.storageSite = "T2_CH_CERN"
#config.section_("User")
#config.User.voGroup = 'dcms'

