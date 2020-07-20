#!/usr/bin/env python
import os, sys
import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor
##soon to be deprecated
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetUncertainties import *
##new way of using jme uncertainty
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import *

from PhysicsTools.NanoAODTools.postprocessing.modules.btv.btagSFProducer  import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer  import *   

#from  exampleModule import *

#this takes care of converting the input files from CRAB
from PhysicsTools.NanoAODTools.postprocessing.framework.crabhelper import inputFiles,runsAndLumis



##Function parameters
##(isMC=True, dataYear=2016, runPeriod="B", jesUncert="Total", redojec=False, jetType = "AK4PFchs", noGroom=False)
##All other parameters will be set in the helper module
jmeCorrections = createJMECorrector(True, "2017", "B", "Total", True, "AK4PFchs", False)

# b tag scale-factors
btagSF2017_1 = lambda : btagSFProducer(era="2017", algo="deepjet", selectedWPs=["L", "M", "shape_corr"]) 

# PU weights
puWeight_2017_1 = lambda : puWeightProducer(pufile_mc2017,pufile_data2017,"pu_mc","pileup",verbose=False, doSysVar=True)



p=PostProcessor(".",inputFiles(),"",modules=[puWeight_2017_1(), jmeCorrections(), btagSF2017_1()],provenance=True,fwkJobReport=True,jsonInput=runsAndLumis())

p.run()

print "DONE"  
