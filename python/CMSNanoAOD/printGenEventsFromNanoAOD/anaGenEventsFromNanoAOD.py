#!/usr/bin/env python

'''
Analysis code for HH->4W analysis in 3l+0tau channel.
It reads i/p post-processed NanoAOD (having JET-MET smearing, bTag SF, puWeights).
It reads i/p trees.root, electron IDs in input json file.

2020/08/30
'''

 
import os, sys
import itertools
import collections

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor


from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Event
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2       import *

import math as math
from collections import OrderedDict as OD
import json
import time
import datetime


#useLeptonSelection_Tallinnlike = True # $$$$$$$ IMPORTANT $$$$$$$



isDEBUG = True
printLevel = 10 

EtaECALBarrel = 1.479
z_mass   = 91.1876;
z_window = 10.0;
pdgId_ZBoson = 23

# Reproduced https://github.com/HEP-KBFI/tth-nanoAOD/blob/dde7a1e5640f7a66ad635cb6f618dd1119bc1244/test/datasets/txt/datasets_data_2017_31Mar18.txt#L38
# Official figures: https://hypernews.cern.ch/HyperNews/CMS/get/luminosity/761/1.html & PAS LUM-17-004 
lumi_2017 = 41.529e+3 # 1/pb (uncertainty: 2.3%)


isMC                         = True
output_dir                   = None


runOnSelectedEventsList = "" #"selectedEvents_3SelLeptons_TauVeto_Disprepancy.txt" #"selectedEvents_3SelLeptons_BJetVeto_Disprepancy.txt" #"selEventsToTest_3selLepton_Discripancy_1.txt" # file with run:lumi:event of selected events. Use empty string when want to run on all events

cutFlowList = None




# make generator-level particl decay chain: using clas Person, createTree, printFamilyTree, getFamilyTreeFinalMembers ---------
class Person:
    ID = itertools.count()
    def __init__(self, name, parent=None, level=0):
        self.id = self.__class__.ID.next() # next(self.__class__.ID) in python 2.6+
        self.parent = parent
        self.name = name  # genParticle index
        self.level = level
        self.children = []

def createTree(d, particleFamilyHead, parent=None, level=0):
    if not particleFamilyHead == '':
        #print "\nmember: ", particleFamilyHead, "level: ",level,
        member = Person(particleFamilyHead, parent, level)
        level = level + 1
        if particleFamilyHead in d:
            member.children = [createTree(d, child, member, level) for child in d[particleFamilyHead]]
        #print "\n~~member: ", particleFamilyHead, "level: ",level,", children: ",member.children
        return member
    elif not particleFamilyHead == '':
        return particleFamilyHead

def printFamilyTree(genParticles, parent, indent=0):
    #print '\t'*indent, parent.name, "(",genParticles[parent.name].pdgId,")"
    print "%s %d (%d) [%.0f, %.2f, %.3f]" % ('\t'*indent, parent.name, genParticles[parent.name].pdgId, genParticles[parent.name].pt,genParticles[parent.name].eta,genParticles[parent.name].phi )
    for child in parent.children:
        printFamilyTree(genParticles, child, indent+1)

def getFamilyTreeFinalMembers(genParticles, parent, level=0,familyTreeFinalMembers=[]):
    if level == 0:
        familyTreeFinalMembers = []
    #print "getFamilyTreeFinalMembers:: parent: ",parent.name, ", level:",level,", familyTreeFinalMembers:",familyTreeFinalMembers
    if len(parent.children) == 0:
        familyTreeFinalMembers.append(parent.name)
    for child in parent.children:
        getFamilyTreeFinalMembers(genParticles, child, level+1,familyTreeFinalMembers)
    return familyTreeFinalMembers    
# -------------------------------------------------------------------------------------------------------------------------------


def cutFlowHistogram_old(histo, histo_wtd, sCut, wt=1.0):
    if not histo.GetNbinsX() >= 1:
        print "def cutFlowHistogram():: histo not defined \t *** ERROR *** \nTerminating\n"
        exit ()
        
    if sCut == "":
        print "def cutFlowHistogram():: enpty cut string *** ERROR ***"
        return
    
    cutBin = 1
    for i in range(1,histo.GetNbinsX()+1):
        if histo.GetXaxis().GetBinLabel(i) == sCut  or  histo.GetXaxis().GetBinLabel(i) == "":
            cutBin = i
            break
        
    if histo.GetXaxis().GetBinLabel(cutBin) == "":
        histo.GetXaxis().SetBinLabel(cutBin, sCut)
        histo_wtd.GetXaxis().SetBinLabel(cutBin, sCut)
        
    x = histo.GetBinCenter(cutBin)
    histo.Fill(x)
    histo_wtd.Fill(x, wt)
    return

def cutFlowHistogram(histo, histo_wtd, sCut, wt=1.0):
    if not histo.GetNbinsX() >= 1:
        print "def cutFlowHistogram():: histo not defined \t *** ERROR *** \nTerminating\n"
        exit ()
        
    if sCut == "":
        print "def cutFlowHistogram():: enpty cut string *** ERROR ***"
        return
    
    if len(cutFlowList) < 1:
        print "def cutFlowHistogram():: cutFlowList not set \t *** ERROR *** \nTerminating\n"
        exit ()
    
    # set bin label
    if histo.GetXaxis().GetBinLabel(1) == "" or histo_wtd.GetXaxis().GetBinLabel(1) == "":
        for iCut in range(len(cutFlowList)):
            histo.GetXaxis().SetBinLabel(iCut+1,     cutFlowList[iCut])
            histo_wtd.GetXaxis().SetBinLabel(iCut+1, cutFlowList[iCut])
    
    
    cutBin = -1
    for iCut in range(len(cutFlowList)):
        if cutFlowList[iCut] == sCut:
            cutBin = iCut + 1
        
    x = histo.GetBinCenter(cutBin)
    histo.Fill(x)
    histo_wtd.Fill(x, wt)
    return


def printCutFlowTable(histo, histo_wtd):
    if ( (not histo.GetNbinsX() >= 1) or (not histo_wtd.GetNbinsX() >= 1)):
        print "def cutFlowHistogram():: histo not defined \t *** ERROR *** \nTerminating\n"
        exit ()
        
    print "Cut-flow table:: \n entries  entries_weighted \t cuts"
    for i in range(1,histo.GetNbinsX()+1):
        if histo.GetXaxis().GetBinLabel(i) == "":
            break
        
        print "%10d %10g  %s" % (histo.GetBinContent(i), histo_wtd.GetBinContent(i), histo.GetXaxis().GetBinLabel(i))
        #print "  ", histo.GetBinContent(i), "  ", histo_wtd.GetBinContent(i), "  ",histo.GetXaxis().GetBinLabel(i)
        
    return





def printLeptonsCollection(sCollection, particles, branch=""):
    print "%s::  %d" % (sCollection,len(particles))
    for i in range(0, len(particles)):
        particle = particles[i]
        if branch == "":
            print "particle %d: pt %g, eta %g, phi %g" % (i,particle.pt, particle.eta, particle.phi)
        elif branch == "Jet":
            print "particle %d: pt %g, %g eta %g, phi %g,   jetId %d, btagDeepFlavB %g" % (i,particle.pt,particle.pt_nom, particle.eta, particle.phi, particle.jetId, particle.btagDeepFlavB)
        elif branch == "Tau":
            print "particle %d: pt %g, eta %g, phi %g,  dxy %g, dz %g, idDecayMode %g, idDecayModeNewDMs %g, decayMode %g" % (i,particle.pt, particle.eta, particle.phi,  particle.dxy,particle.dz, particle.idDecayMode,particle.idDecayModeNewDMs, particle.decayMode), \
                ", idDeepTau2017v2p1VSjet ",particle.idDeepTau2017v2p1VSjet, \
                ", idDeepTau2017v2p1VSmu  ",particle.idDeepTau2017v2p1VSmu, \
                ", idDeepTau2017v2p1VSe ",particle.idDeepTau2017v2p1VSe
    return


    
class ExampleAnalysis(Module):
    def __init__(self):
        self.writeHistFile=True
  
    
    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)
        
        self.nEventsAnalyzed     = 0
        self.nEventsSelected     = 0
        self.nEventsSelected_Wtd = 0.0
        
        
        self.h_Stat = ROOT.TH1D('Stat',   'Stat',   101, -0.5, 100.5)
        self.addObject(self.h_Stat )
        self.h_Stat.SetDefaultSumw2()
        
        self.h_Stat1 = ROOT.TH1D('Stat1',   'Stat1',   101, -0.5, 100.5)
        self.addObject(self.h_Stat1 )
        self.h_Stat1.Sumw2()
        
        self.h_Stat1_wtd = ROOT.TH1D('Stat1_wtd',   'Stat1_wtd',   101, -0.5, 100.5)
        self.addObject(self.h_Stat1_wtd )
        self.h_Stat1_wtd.Sumw2()
        
        self.h_Info = ROOT.TH1D('Info',   'Info',   101, -0.5, 100.5)
        self.addObject(self.h_Info )



        '''
        cutFlowList = [
            "all",
            "all * L1PreFiringWeight",
            "trigger",
            ">= 3 presel leptons",
            "presel lepton trigger match",
            ">= 3 sel leptons",
            "<= 3 tight leptons",
            "0 e in selLeptons",
            "1 e in selLeptons",
            "2 e in selLeptons",
            "3 e in selLeptons",
            "0 mu in selLeptons",
            "1 mu in selLeptons",
            "2 mu in selLeptons",
            "3 mu in selLeptons",
            "b-jet veto",
            "tau veto",
            "sellepton pt > 25 / 15 / 10",
            "sel lepton charge",
            ">= 1 jets from W->jj",
            "m(ll) > 12 GeV",
            "Z-boson mass veto",
            "H->ZZ*->4l veto",
            "met LD",
            "MEt filters",
            "MEt filters; hh_3e",
            "MEt filters; hh_2e1mu",
            "MEt filters; hh_1e2mu",
            "MEt filters; hh_3mu",
        ]
        '''
        
        
        # event weight
        self.h_evtWeight = ROOT.TH1D('evtWeight',   'evtWeight',   600, -3.0, 3.0)
        self.addObject(self.h_evtWeight )
        
        self.h_evtWeight_genWeight = ROOT.TH1D('evtWeight_genWeight',   'evtWeight_genWeight',   600, -1000.0, 1000.0)
        self.addObject(self.h_evtWeight_genWeight )

        
        self.fRunOnselectedEvents = None
        self.listOfSelectedEvent = None
        if runOnSelectedEventsList != "":
            self.fRunOnselectedEvents = open(runOnSelectedEventsList, "r")
            self.listOfSelectedEvent = self.fRunOnselectedEvents.readlines()
            self.fRunOnselectedEvents.close()
            print "listOfSelectedEvent: ",self.listOfSelectedEvent
        
        
        
        
        
        
        
        # other histograms --------------------------------------------------------------------
        self.h_genMassZ = ROOT.TH1D('h_genMassZ',   'h_genMassZ',   200, 0, 200)
        self.addObject(self.h_genMassZ )
        
        self.h_genMassZ_ll = ROOT.TH1D('h_genMassZ_ll',   'h_genMassZ_ll',   200, 0, 200)
        self.addObject(self.h_genMassZ_ll )

        self.h_genMass_2lSFOS = ROOT.TH1D('h_genMass_2lSFOS',   'h_genMass_2lSFOS',   200, 0, 200)
        self.addObject(self.h_genMass_2lSFOS )







    def endJob(self):
        print "\nendJob()"
        if self.h_Stat1:
            print "nendJob():: printCutFlowTable::"
            printCutFlowTable(self.h_Stat1, self.h_Stat1_wtd)
        
            
        Module.endJob(self)            










    def analyze(self, event):
        runNumber = getattr(event,"run")
        lumiBlock = getattr(event,"luminosityBlock")
        eventNumber = getattr(event,"event")
        
        if printLevel >= 11: 
            print "\n\n run: %d, lumi: %d, eventNumber: %d" % (runNumber,lumiBlock,eventNumber)
        
        
        if runOnSelectedEventsList != "":
            sEvt = "%d:%d:%d\n" % (runNumber,lumiBlock,eventNumber)
            if sEvt  in  self.listOfSelectedEvent:
                print "\n\n\n%s event  found in listOfSelectedEvent. Analyze this event" % sEvt
            else:
                return True
        
        
        self.nEventsAnalyzed += 1
        self.h_Stat.Fill(0)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "all")
        #self.ofEventNumber_SelectedEvents_All.write("%d:%d:%d\n" % (runNumber,lumiBlock,eventNumber))
        
        
        # Gen-level study ----------------------------------------------------------------------------------------------------------------------
        if isMC:
            genParts = Collection(event, "GenPart")
            
            #store gen particle index into dictionary to get genParticle family tree
            genPartFamily = collections.OrderedDict()    # { idxPart: [idxDaughter0, idxDaughter1, ..], }                        
            for iGenPart in range(0,len(genParts)):
                genPart = genParts[iGenPart]
                if isDEBUG and printLevel >=10:
                    print "genPart %d: pt %5.1f, \t eta %5.3f, \t phi %5.3f, \t m %5.2f, \t pdgId %d, \t genPartIdxMother %d, \t status %d, \t statusFlags %d" % (iGenPart, genPart.pt, genPart.eta, genPart.phi, genPart.mass, genPart.pdgId, genPart.genPartIdxMother, genPart.status, genPart.statusFlags)
                
                if genPart.genPartIdxMother < 0:
                    continue
                
                if not genPart.genPartIdxMother in genPartFamily:
                    genPartFamily[genPart.genPartIdxMother] = [iGenPart]
                else:
                    genPartFamily[genPart.genPartIdxMother].append(iGenPart)
            
            if isDEBUG and printLevel >=11:
                print "\n\n genPartFamily:\n"        
                for key, value in genPartFamily.items():
                    print "key:",key, ",  value:",value
            
            
            firstFamilyMember = list(genPartFamily.keys())[0]
            familyTree =  createTree(genPartFamily, firstFamilyMember)
            if isDEBUG and printLevel >=10:
                print "\n\n printFamilyTree: \n"
                printFamilyTree(genParts, familyTree)
            

                    
                    
        # Gen-level study ----------------------------------------------------------------------------------------------------------------------
        
        





        return True;





if __name__ == "__main__":
    start_time = time.time()
    print "\nanaHHTo4W_3l_1qq.py: datetime: {} start_time {}, ".format(datetime.datetime.now(), start_time)
    
    
    print "anaHHTo4W_3l_1qq.py:  commandline arguments: ",sys.argv
    if len(sys.argv) != 2:
        print "anaHHTo4W_3l_1qq.py: 1 command line argument (anaConfir.json) is expected to run anaHHTo4W_3l_1qq.py  ***** ERROR ****"
        exit(0)
    
    analysisSettings = None
    with open(sys.argv[1]) as fAnaSetting:
        analysisSettings = json.load(fAnaSetting)
        
    #analysisSettings[""]
    # = analysisSettings[""]
    
    process_name_specific         = analysisSettings["process_name_specific"]
    sample_category               = analysisSettings["sample_category"] 
    NanoAOD_PostProc_Files        = analysisSettings["NanoAOD_PostProc"]
    
    output_dir                    = analysisSettings["output_dir"] 
    output_histFileName           = "%s/hist_stage1_%s.root" % (output_dir,process_name_specific)
    output_histDirName            = "%s" % (sample_category)
    
    runOnSelectedEventsList       = analysisSettings["runOnSelectedEventsList"]
    
    if len(NanoAOD_PostProc_Files) == 0:
        print "No input NanoAOD_PostProc_Files \t\t\t ******* ERROR ********" 
        exit(0)
    
    
    '''
    #files=[" root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAOD/TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/40000/2CE738F9-C212-E811-BD0E-EC0D9A8222CE.root"]
    #files=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv6/GluGluToRadionToHHTo4V_M-400_narrow_13TeV-madgraph_correctedcfg/NANOAODSIM/PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/70000/D6A8EF07-3425-3346-96C4-D000C58E4735.root"]
    #files=["/home/ssawant/dataFiles/GluGluToRadionToHHTo4V_M-400_narrow_13TeV-madgraph_correctedcfg/NanoAODSIM/D6A8EF07-3425-3346-96C4-D000C58E4735.root"] # gpu@indiacms
    #files=["root://se01.indiacms.res.in:1094//cms/store/user/ssawant/NanoPost/GluGluToRadionToHHTo4V_M-400_narrow_13TeV-madgraph_correctedcfg/NanoTestPost/200626_214151/0000/tree_1.root"] # nanoAOD skimmed
    #files=["/afs/cern.ch/work/s/ssawant/private/HHAnalysis/ana_nanoAOD/v1_20200519/myAna/NanoAOD_Skimmed/GluGluToRadionToHHTo4V_M-400_narrow_13TeV-madgraph_correctedcfg/tree_1.root"] # nanoAOD skimmed
    #files=["root://se01.indiacms.res.in:1094//cms/store/user/ssawant/NanoPost/GluGluToRadionToHHTo4V_M-400_narrow_13TeV-madgraph_correctedcfg/NanoTestPost/200630_163102/0000/tree_1.root"]
    files=["root://se01.indiacms.res.in:1094//cms/store/user/ssawant/NanoPost/GluGluToRadionToHHTo4V_M-400_narrow_13TeV-madgraph_correctedcfg/NanoTestPost/*/0000/tree_*.root"]
    sHistFileName="histOut_HHTo4W_400_tmp.root"
    files= [
        "root://se01.indiacms.res.in:1094//cms/store/user/ssawant/NanoAODPostProc_2017/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1/200703_155812/0000/tree_3.root",
        "root://se01.indiacms.res.in:1094//cms/store/user/ssawant/NanoAODPostProc_2017/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1/200703_155812/0000/tree_4.root",
        "root://se01.indiacms.res.in:1094//cms/store/user/ssawant/NanoAODPostProc_2017/WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8/RunIIFall17NanoAODv6-PU2017_12Apr2018_Nano25Oct2019_new_pmx_102X_mc2017_realistic_v7-v1/200703_155812/0000/tree_6.root"
    ]
    
    #
    #files=["/home/ssawant/dataFiles/GluGluToRadionToHHTo4V_M-250_narrow_13TeV-madgraph_correctedcfg/NanoAODSIM/08B63BBC-7C86-114C-8EDE-03BA4F7DF4E6.root"]
    #sHistFileName="histOut_HHTo4W_250.root"
    #
    #files=["/home/ssawant/dataFiles/GluGluToRadionToHHTo4V_M-700_narrow_13TeV-madgraph_correctedcfg/NanoAODSIM/30397A8B-8139-194A-8D98-525BEA175173.root",
    #     "/home/ssawant/dataFiles/GluGluToRadionToHHTo4V_M-700_narrow_13TeV-madgraph_correctedcfg/NanoAODSIM/EFF83B3B-A2B1-8246-9B11-1075D89429FC.root"]
    #sHistFileName="histOut_HHTo4W_700.root"
    #
    #files=["/home/ssawant/dataFiles/GluGluToRadionToHHTo4V_M-1000_narrow_13TeV-madgraph_correctedcfg/NanoAODSIM/CE4A9A12-C0BC-174E-B43B-19E2602DDFF0.root","/home/ssawant/dataFiles/GluGluToRadionToHHTo4V_M-1000_narrow_13TeV-madgraph_correctedcfg/NanoAODSIM/FC022D32-5C75-A547-9935-7A49EF099668.root"]
    #sHistFileName="histOut_HHTo4W_1000.root"
    
    #isMC = True
    '''
    
    #ElectronID_presel = "Electron_mvaFall17V2Iso_WPL"
    #ElectronID_sel    = "Electron_mvaFall17V2Iso_WP80" # Electron_mvaFall17V2Iso_WP80, Electron_mvaFall17V2Iso_WP90, Electron_mvaFall17V2Iso_WPL
    #ElectronID_presel = "Electron_mvaFall17V2noIso_WPL"
    #ElectronID_sel    = "Electron_mvaFall17V2noIso_WP80" # Electron_mvaFall17V2Iso_WP80, Electron_mvaFall17V2Iso_WP90, Electron_mvaFall17V2Iso_WPL
    
    

    print "NanoAOD_PostProc_Files: nTrees {}: {}".format(len(NanoAOD_PostProc_Files),NanoAOD_PostProc_Files)
    print "output_dir: %s, output_histFileName: %s, output_histDirName: %s" % (output_dir, output_histFileName, output_histDirName)
    print "runOnSelectedEventsList: {}".format(runOnSelectedEventsList)
    sys.stdout.flush();
    
    os.system("mkdir -p %s" % output_dir)
    
    
    cutFlowList = [
        "all",
    ]
    
    
    
    preselection=""
    
    #p=PostProcessor(".",files,cut=preselection,branchsel=None,modules=[jmeCorrections(), ExampleAnalysis()],noOut=False,histFileName=sHistFileName,histDirName="plots")
    #p=PostProcessor(".",files,cut=preselection,branchsel=None,modules=[ExampleAnalysis()],noOut=True,histFileName=sHistFileName,histDirName="plots",maxEntries=10000)
    #p=PostProcessor(".",files,cut=preselection,branchsel=None,modules=[ExampleAnalysis()],noOut=True,histFileName=sHistFileName,histDirName="plots")
    
    #p=PostProcessor(".", NanoAOD_PostProc_Files, cut="", branchsel=None, modules=[ExampleAnalysis()], noOut=True, histFileName=output_histFileName, histDirName=output_histDirName, maxEntries=10000)
    #p=PostProcessor(".", NanoAOD_PostProc_Files, cut="", branchsel=None, modules=[ExampleAnalysis()], noOut=True, histFileName=output_histFileName, histDirName=output_histDirName,maxEntries=10000)
    p=PostProcessor(".", NanoAOD_PostProc_Files, cut="", branchsel=None, modules=[ExampleAnalysis()], noOut=True, histFileName=output_histFileName, histDirName=output_histDirName)
    
    
    p.run()
    
    time_now = time.time()
    #print "anaHHTo4W_3l_1qq_gen.py:  time_now {}".format(time_now)
    exec_time = time_now - start_time
    sexec_time = str(datetime.timedelta(seconds=exec_time))
    #print "anaHHTo4W_3l_1qq_gen.py:  exec_now {}".format(exec_time)
    print "anaHHTo4W_3l_1qq_gen.py:  datetime: {}, \t execution time: {}".format(datetime.datetime.now(), sexec_time)
    
    with open("%s/tmp_file_ExecutionFinished.txt" % output_dir, 'w') as f:
        f.write("anaHHTo4W_3l_1qq.py: Execution finished %s. Execution time = %s \n" % (str(datetime.datetime.now()), sexec_time))
