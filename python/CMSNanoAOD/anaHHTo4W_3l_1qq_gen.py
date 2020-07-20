#!/usr/bin/env python

'''
Analysis code for HH->4W analysis in 3l+0tau channel.
It reads i/p post-processed NanoAOD (having JET-MET smearing, bTag SF, puWeights).
It reads i/p trees.root, electron IDs in input json file.

2020/07/06
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

isDEBUG = False
printLevel = 0 

EtaECALBarrel = 1.479
z_mass   = 91.1876;
z_window = 10.0;

# Reproduced https://github.com/HEP-KBFI/tth-nanoAOD/blob/dde7a1e5640f7a66ad635cb6f618dd1119bc1244/test/datasets/txt/datasets_data_2017_31Mar18.txt#L38
# Official figures: https://hypernews.cern.ch/HyperNews/CMS/get/luminosity/761/1.html & PAS LUM-17-004
lumi_2017 = 41.529e+3 # 1/pb (uncertainty: 2.3%)


ERA                          = None # 2017
era_luminosity               = None
isMC                         = None
nof_events_NanoAOD_PostProc  = None
process_xsection             = None
sample_lumiScaleToUse        = None
output_dir                   = None

ElectronID_presel      = None # Electron_mvaFall17V2Iso_WP80, Electron_mvaFall17V2Iso_WP90, Electron_mvaFall17V2Iso_WPL
ElectronID_sel         = None
ElectronID_mvaTTH_sel  = None
ElectronSFDetails      = None

MuonID_presel = None # WP: looseId, mediumId, tightId
MuonID_sel    = None # WP: looseId, mediumId, tightId
MuonID_sel_lowPt = None
MuonSFDetails = None

# DeepTau2017v2p1VSjet_WP  1 = VVVLoose, 2 = VVLoose, 4 = VLoose, 8 = Loose, 16 = Medium, 32 = Tight, 64 = VTight, 128 = VVTight
DeepTau2017v2p1VSjet_WPVVLoose = 2
DeepTau2017v2p1VSjet_WPLoose   = 8

jetBtagWPLoose  = None
jetBtagWPMedium = None

jetBtagWPLoose_2017  = 0.0521
jetBtagWPMedium_2017 = 0.3033

jetCleaningMethod = "cleanedJetsAK4_byIndex" # Methonds: cleanedJetsAK4_bydR, cleanedJetsAK4_byIndex

MEtFiltersToApply = None
'''
MEtFiltersToApply_2017_data = ["Flag_goodVertices",
                               "Flag_globalSuperTightHalo2016Filter",
                               "Flag_HBHENoiseFilter",
                               "Flag_HBHENoiseIsoFilter",
                               "Flag_EcalDeadCellTriggerPrimitiveFilter",
                               "Flag_BadPFMuonFilter",
                               "Flag_eeBadScFilter",
                               "Flag_ecalBadCalibFilterV2 ", # not on MEt-POG twiki, but used in HH-analysis
]
MEtFiltersToApply_2017_mc   = ["Flag_goodVertices",
                               "Flag_globalSuperTightHalo2016Filter",
                               "Flag_HBHENoiseFilter",
                               "Flag_HBHENoiseIsoFilter",
                               "Flag_EcalDeadCellTriggerPrimitiveFilter",
                               "Flag_BadPFMuonFilter",
                               #"Flag_eeBadScFilter", # not for mc
                               "Flag_ecalBadCalibFilterV2 ", # not on MEt-POG twiki, but used in HH-analysis
]
'''
MEtFiltersToApply_2017 = OD([
    ("Flag_goodVertices",                         {"forMC": True,   "forData": True}),    
    ("Flag_globalSuperTightHalo2016Filter",       {"forMC": True,   "forData": True}),
    ("Flag_HBHENoiseFilter",                      {"forMC": True,   "forData": True}),
    ("Flag_HBHENoiseIsoFilter",                   {"forMC": True,   "forData": True}),
    ("Flag_EcalDeadCellTriggerPrimitiveFilter",   {"forMC": True,   "forData": True}),
    ("Flag_BadPFMuonFilter",                      {"forMC": True,   "forData": True}),
    ("Flag_eeBadScFilter",                        {"forMC": False,  "forData": True}),
    ("Flag_ecalBadCalibFilterV2",                 {"forMC": True,   "forData": True}), # not on MEt-POG twiki, but used in HH-analysis
])


runOnSelectedEventsList = "" #"selectedEvents_3SelLeptons_TauVeto_Disprepancy.txt" #"selectedEvents_3SelLeptons_BJetVeto_Disprepancy.txt" #"selEventsToTest_3selLepton_Discripancy_1.txt" # file with run:lumi:event of selected events. Use empty string when want to run on all events






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


def cutFlowHistogram(histo, histo_wtd, sCut, wt=1.0):
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


def isParticleGenMatched(particle, genParticles, dR=0.3):
    isMatch = False
    for genParticle in genParticles:
        if particle.DeltaR(genParticle) < dR:
            isMatch = True
    
    return isMatch

    
def isTriggered(event, triggerList):
    for trig in triggerList:
        #print " trig: ", trig, ": ",getattr(event,trig)
        if getattr(event,trig):
            return True
    return False


def preselMuonSelector(particles):
    selectedParticles = []
    for particle in particles:
        passPOGMVA = False
        if   "Muon_looseId" in MuonID_presel:
            passPOGMVA = particle.looseId
        elif "Muon_mediumId" in MuonID_presel:
            passPOGMVA = particle.mediumId
        elif "Muon_tightId" in MuonID_presel:
            passPOGMVA = particle.tightId
        else:
            print "Invalid MuonID_presel %s set **** ERROR ****" %  MuonID_presel
            exit (0)
        '''
        print "preselMuonSelector::particle: pt %g, eta %g, phi %g, dxy %g, dz %g, sip3d %g, relIso %g, looseId %d, tightId %d"\
            % (particle.pt, particle.eta, particle.phi, \
               particle.dxy, particle.dz, particle.sip3d, \
               particle.miniPFRelIso_all, particle.looseId, particle.tightId)
        '''
        if not particle.pt > 5.0:
            continue
        if not abs(particle.eta) < 2.4:
            continue
        if not abs(particle.dxy) < 0.05:
            continue
        if not abs(particle.dz) < 0.10:
            continue
        if not particle.sip3d < 8.0:
            continue
        if not particle.miniPFRelIso_all < 0.4:
            continue
        if not passPOGMVA:
            continue
        selectedParticles.append(particle)
        
    #print "nPartiles %d, selectedParticles %d" % (len(particles),len(selectedParticles))
    return selectedParticles


def tightMuonSelector(particles):
    selectedParticles = []
    for particle in particles:
        passPOGMVA = False
        if   "Muon_looseId" in MuonID_sel:
            passPOGMVA = particle.looseId
        elif "Muon_mediumId" in MuonID_sel:
            passPOGMVA = particle.mediumId
        elif "Muon_tightId" in MuonID_sel:
            passPOGMVA = particle.tightId
        else:
            print "Invalid MuonID_presel %s set **** ERROR ****" %  MuonID_presel
            exit (0)
        '''
        print "tightMuonSelector::particle: pt %g, eta %g, phi %g, dxy %g, dz %g, sip3d %g, relIso %g, looseId %d, tightId %d"\
            % (particle.pt, particle.eta, particle.phi, \
               particle.dxy, particle.dz, particle.sip3d, \
               particle.miniPFRelIso_all, particle.looseId, particle.tightId)
        '''
        if not particle.pt > 10.0:
            continue
        if not abs(particle.eta) < 2.4:
            continue
        if not abs(particle.dxy) < 0.05:
            continue
        if not abs(particle.dz) < 0.10:
            continue
        if not particle.sip3d < 8.0:
            continue
        if not particle.miniPFRelIso_all < 0.4:
            continue
        if not passPOGMVA:
            continue
        selectedParticles.append(particle)
        
    #print "nPartiles %d, selectedParticles %d" % (len(particles),len(selectedParticles))
    return selectedParticles


def preselElectonSelector(particles):
    selectedParticles = []
    for particle in particles:
        passPOGMVA = False
        #idxEleIDPicked = 0
        if  "Electron_mvaFall17V2Iso" in ElectronID_presel:    
            if "_WPL" in ElectronID_presel:
                passPOGMVA = particle.mvaFall17V2Iso_WPL
                #idxEleIDPicked = 1
            elif "_WP90" in ElectronID_presel:
                passPOGMVA = particle.mvaFall17V2Iso_WP90
                #idxEleIDPicked = 2
            elif "_WP80" in ElectronID_presel:
                passPOGMVA = particle.mvaFall17V2Iso_WP80
                #idxEleIDPicked = 3
            else:
                print "Invalid %s **** ERROR ****" % ElectronID_presel
                exit(0)
        elif "Electron_mvaFall17V2noIso" in ElectronID_presel:
            if "_WPL" in ElectronID_presel:
                passPOGMVA = particle.mvaFall17V2noIso_WPL
                #idxEleIDPicked = 4
            elif "_WP90" in ElectronID_presel:
                passPOGMVA = particle.mvaFall17V2noIso_WP90
                #idxEleIDPicked = 5
            elif "_WP80" in ElectronID_presel:
                passPOGMVA = particle.mvaFall17V2noIso_WP80
                #idxEleIDPicked = 6
            else:
                print "Invalid %s **** ERROR ****" % ElectronID_presel
                exit(0)
        else:
            print "Invalid %s **** ERROR ****" % ElectronID_presel
            exit(0)
        
        if isDEBUG and printLevel >=10:
            print "preselElectonSelector::particle: pt %g, eta %g, phi %g, passPOGMVA: %d, ElectronID_presel %s, idxEleIDPicked %d,  mvaFall17V2Iso %g, mvaFall17V2noIso %g"\
                % (particle.pt, particle.eta, particle.phi, \
                   passPOGMVA, ElectronID_presel,idxEleIDPicked, \
                   particle.mvaFall17V2Iso, particle.mvaFall17V2noIso)
        
        
        if not particle.pt > 7.0:
            continue
        if not abs(particle.eta) < 2.5:
            continue
        if not passPOGMVA:
            continue
        
        selectedParticles.append(particle)
        
    #print "nPartiles %d, selectedParticles %d" % (len(particles),len(selectedParticles))
    return selectedParticles


def tightElectonSelector(particles):
    selectedParticles = []
    for particle in particles:
        passPOGMVA = False
        if  "Electron_mvaFall17V2Iso" in ElectronID_sel:    
            if "_WPL" in ElectronID_sel:
                passPOGMVA = particle.mvaFall17V2Iso_WPL
            elif "_WP90" in ElectronID_sel:
                passPOGMVA = particle.mvaFall17V2Iso_WP90
            elif "_WP80" in ElectronID_sel:
                passPOGMVA = particle.mvaFall17V2Iso_WP80
            else:
                print "Invalid %s **** ERROR ****" % ElectronID_sel
                exit(0)
        elif "Electron_mvaFall17V2noIso" in ElectronID_sel:
            if "_WPL" in ElectronID_sel:
                passPOGMVA = particle.mvaFall17V2noIso_WPL
            elif "_WP90" in ElectronID_sel:
                passPOGMVA = particle.mvaFall17V2noIso_WP90
            elif "_WP80" in ElectronID_sel:
                passPOGMVA = particle.mvaFall17V2noIso_WP80
            else:
                print "Invalid %s **** ERROR ****" % ElectronID_sel
                exit(0)
        else:
            print "Invalid %s **** ERROR ****" % ElectronID_sel
            exit(0)
        
        '''    
        print "tightElectonSelector::particle: pt %g, eta %g, phi %g, %s: %d"\
            % (particle.pt, particle.eta, particle.phi, \
               ElectronID_mvaFall17V2,passPOGMVA)        
        '''
        
        if not particle.pt > 10.0:
            continue
        if not abs(particle.eta) < 2.5:
            continue
        if not passPOGMVA:
            continue
        if not particle.mvaTTH > ElectronID_mvaTTH_sel:
            continue
        
        selectedParticles.append(particle)
        
    #print "nPartiles %d, selectedParticles %d" % (len(particles),len(selectedParticles))
    return selectedParticles






def preselMuonSelector_hh_multilepton_test(particles):
    selectedParticles = []
    for particle in particles:
        passPOGMVA = False
        if   "Muon_looseId" in MuonID_presel:
            passPOGMVA = particle.looseId
        elif "Muon_mediumId" in MuonID_presel:
            passPOGMVA = particle.mediumId
        elif "Muon_tightId" in MuonID_presel:
            passPOGMVA = particle.tightId
        else:
            print "Invalid MuonID_presel %s set **** ERROR ****" %  MuonID_presel
            exit (0)
        '''
        print "preselMuonSelector::particle: pt %g, eta %g, phi %g, dxy %g, dz %g, sip3d %g, relIso %g, looseId %d, tightId %d"\
            % (particle.pt, particle.eta, particle.phi, \
               particle.dxy, particle.dz, particle.sip3d, \
               particle.miniPFRelIso_all, particle.looseId, particle.tightId)
        '''
        if not particle.pt > 10.0:
            continue
        if not abs(particle.eta) < 2.4:
            continue
        if not abs(particle.dxy) < 0.05:
            continue
        if not abs(particle.dz) < 0.10:
            continue
        if not particle.sip3d < 8.0:
            continue
        if not particle.miniPFRelIso_all < 0.4:
            continue
        if not passPOGMVA:
            continue
        selectedParticles.append(particle)
        
    #print "nPartiles %d, selectedParticles %d" % (len(particles),len(selectedParticles))
    return selectedParticles 


def tightMuonSelector_hh_multilepton_test(particles):
    selectedParticles = []
    for particle in particles:
        passPOGMVA = False
        if   "Muon_looseId" in MuonID_sel:
            passPOGMVA = particle.looseId
        elif "Muon_mediumId" in MuonID_sel:
            passPOGMVA = particle.mediumId
        elif "Muon_tightId" in MuonID_sel:
            passPOGMVA = particle.tightId
        else:
            print "Invalid MuonID_presel %s set **** ERROR ****" %  MuonID_presel
            exit (0)
        '''
        print "tightMuonSelector::particle: pt %g, eta %g, phi %g, dxy %g, dz %g, sip3d %g, relIso %g, looseId %d, tightId %d"\
            % (particle.pt, particle.eta, particle.phi, \
               particle.dxy, particle.dz, particle.sip3d, \
               particle.miniPFRelIso_all, particle.looseId, particle.tightId)
        '''
        if not particle.pt >= 10.0:
            continue
        if not abs(particle.eta) <= 2.4:
            continue
        if not abs(particle.dxy) <= 0.05:
            continue
        if not abs(particle.dz) <= 0.10:
            continue
        if not particle.sip3d <= 8.0:
            continue
        if not particle.miniPFRelIso_all <= 0.4:
            continue
        if not passPOGMVA:
            continue
        selectedParticles.append(particle)
        
    #print "nPartiles %d, selectedParticles %d" % (len(particles),len(selectedParticles))
    return selectedParticles


def preselElectonSelector_hh_multilepton_test(particles):
    selectedParticles = []
    for particle in particles:
        passPOGMVA = False        
        if  "Electron_mvaFall17V2Iso" in ElectronID_presel:    
            if "_WPL" in ElectronID_presel:
                passPOGMVA = particle.mvaFall17V2Iso_WPL
            elif "_WP90" in ElectronID_presel:
                passPOGMVA = particle.mvaFall17V2Iso_WP90
            elif "_WP80" in ElectronID_presel:
                passPOGMVA = particle.mvaFall17V2Iso_WP80
            else:
                print "Invalid %s **** ERROR ****" % ElectronID_presel
                exit(0)
        elif "Electron_mvaFall17V2noIso" in ElectronID_presel:
            if "_WPL" in ElectronID_presel:
                passPOGMVA = particle.mvaFall17V2noIso_WPL
            elif "_WP90" in ElectronID_presel:
                passPOGMVA = particle.mvaFall17V2noIso_WP90
            elif "_WP80" in ElectronID_presel:
                passPOGMVA = particle.mvaFall17V2noIso_WP80
            else:
                print "Invalid %s **** ERROR ****" % ElectronID_presel
                exit(0)
        else:
            print "Invalid %s **** ERROR ****" % ElectronID_presel
            exit(0)
        
        '''
        print "preselElectonSelector::particle: pt %g, eta %g, phi %g, %s(looseId): %d"\
            % (particle.pt, particle.eta, particle.phi, \
               ElectronID_mvaFall17V2,passPOGMVA)
        '''
        
        if not particle.pt >= 10.0:
            continue
        if not abs(particle.eta) <= 2.5:
            continue
        if not abs(particle.dxy) <= 0.05:
            continue
        if not abs(particle.dz) <= 0.10:
            continue
        if not particle.sip3d <= 8.0:
            continue
        if not particle.miniPFRelIso_all <= 0.4:
            continue
        if not particle.lostHits <= 1:
            continue
        if not passPOGMVA:
            continue
        
        selectedParticles.append(particle)
        
    #print "nPartiles %d, selectedParticles %d" % (len(particles),len(selectedParticles))
    return selectedParticles


def tightElectonSelector_hh_multilepton_test(particles):
    selectedParticles = []
    for particle in particles:
        passPOGMVA = False
        if  "Electron_mvaFall17V2Iso" in ElectronID_sel:    
            if "_WPL" in ElectronID_sel:
                passPOGMVA = particle.mvaFall17V2Iso_WPL
            elif "_WP90" in ElectronID_sel:
                passPOGMVA = particle.mvaFall17V2Iso_WP90
            elif "_WP80" in ElectronID_sel:
                passPOGMVA = particle.mvaFall17V2Iso_WP80
            else:
                print "Invalid %s **** ERROR ****" % ElectronID_sel
                exit(0)
        elif "Electron_mvaFall17V2noIso" in ElectronID_sel:
            if "_WPL" in ElectronID_sel:
                passPOGMVA = particle.mvaFall17V2noIso_WPL
            elif "_WP90" in ElectronID_sel:
                passPOGMVA = particle.mvaFall17V2noIso_WP90
            elif "_WP80" in ElectronID_sel:
                passPOGMVA = particle.mvaFall17V2noIso_WP80
            else:
                print "Invalid %s **** ERROR ****" % ElectronID_sel
                exit(0)
        else:
            print "Invalid %s **** ERROR ****" % ElectronID_sel
            exit(0)
        
        '''    
        print "tightElectonSelector::particle: pt %g, eta %g, phi %g, %s: %d"\
            % (particle.pt, particle.eta, particle.phi, \
               ElectronID_mvaFall17V2,passPOGMVA)        
        '''
        
        if not particle.pt > 10.0:
            continue
        if not abs(particle.eta) < 2.5:
            continue
        if not abs(particle.dxy) < 0.05:
            continue
        if not abs(particle.dz) < 0.10:
            continue
        if not particle.sip3d < 8.0:
            continue
        if not particle.miniPFRelIso_all < 0.4:
            continue
        if not particle.lostHits <= 1:
            continue
        if not passPOGMVA:
            continue
        
        selectedParticles.append(particle)
        
    #print "nPartiles %d, selectedParticles %d" % (len(particles),len(selectedParticles))
    return selectedParticles





def preselTauSelector(particles):
    selectedParticles = []
    for particle in particles:
        if isDEBUG and printLevel >= 8:
            print "preselTauSelector::particle: pt %g, eta %g, phi %g, dxy %g, dz %g, idDecayMode %d, decayMode %d, \t idDeepTau2017v2p1VSjet: "\
                % (particle.pt, particle.eta, particle.phi, \
                   particle.dxy, particle.dz, \
                   particle.idDecayMode, particle.decayMode), particle.idDeepTau2017v2p1VSjet, \
                   ", isVVLoose: ", particle.idDeepTau2017v2p1VSjet >= DeepTau2017v2p1VSjet_WPVVLoose#, \
                   #", isLoose: ", particle.idDeepTau2017v2p1VSjet >= DeepTau2017v2p1VSjet_WPLoose
        
        if not particle.pt > 20.0:
            continue
        if not abs(particle.eta) < 2.3:
            continue
        if not abs(particle.dxy) < 1000.0:
            continue
        if not abs(particle.dz) < 0.20:
            continue
        #if not particle.idDecayMode: # Decay mode finding # Tallinn group don't use  idDecayMode or idDecayModeNewDMs
        #    continue
        if particle.decayMode in [5, 6]: # Decay modes all except 2-prong decay modes
            continue
        if not particle.idDeepTau2017v2p1VSjet >= DeepTau2017v2p1VSjet_WPVVLoose: # DeepTau vs. jets
            continue
        if particle.idDeepTau2017v2p1VSmu < 1: # corresponds to cut on VLoose WP
            continue
        if particle.idDeepTau2017v2p1VSe < 1: # corresponds to cut on VVVLoose WP
            continue
        
        selectedParticles.append(particle)
        
    if isDEBUG and printLevel >= 8:
        print "nPartiles %d, selectedParticles %d" % (len(particles),len(selectedParticles))
    return selectedParticles


def tightTauSelector(particles):
    selectedParticles = []
    for particle in particles:
        if isDEBUG and printLevel >= 8:
            print "tightTauSelector::particle: pt %g, eta %g, phi %g, dxy %g, dz %g, idDecayMode %d, decayMode %d, \t idDeepTau2017v2p1VSjet: "\
                % (particle.pt, particle.eta, particle.phi, \
                   particle.dxy, particle.dz, \
                   particle.idDecayMode, particle.decayMode), particle.idDeepTau2017v2p1VSjet, \
                  ", isLoose: ", particle.idDeepTau2017v2p1VSjet >= DeepTau2017v2p1VSjet_WPLoose
        
        if not particle.pt > 20.0:
            continue
        if not abs(particle.eta) < 2.3:
            continue
        if not abs(particle.dxy) < 1000.0:
            continue
        if not abs(particle.dz) < 0.20:
            continue
        #if not particle.idDecayMode: # Decay mode finding # Tallinn group don't use  idDecayMode or idDecayModeNewDMs
        #    continue
        if particle.decayMode in [5, 6]: # Decay modes all except 2-prong decay modes
            continue
        if not particle.idDeepTau2017v2p1VSjet >= DeepTau2017v2p1VSjet_WPLoose: # DeepTau vs. jets
            continue
        if particle.idDeepTau2017v2p1VSmu < 1: # corresponds to cut on VLoose WP
            continue
        if particle.idDeepTau2017v2p1VSe < 1: # corresponds to cut on VVVLoose WP
            continue
        
        selectedParticles.append(particle)
        
    if isDEBUG and printLevel >= 8:
        print "nPartiles %d, selectedParticles %d" % (len(particles),len(selectedParticles))
    return selectedParticles





def jetAK4Selector(particles):
    selectedParticles = []
    for particle in particles:
        if isDEBUG and printLevel >= 8:
            print "jetAK4Selector::particle: pt %g, eta %g, phi %g,  jetId: "\
                % (particle.pt, particle.eta, particle.phi), \
                   particle.jetId
        
        #if not particle.pt > 25.0:
        if not particle.pt_nom > 25.0:
            continue
        if not abs(particle.eta) < 2.4:
            continue
        #if not (particle.pt < 60.0  and  abs(particle.eta) > 2.7 and abs(particle.eta) < 3.0): # ECAL-HCAL noice for forward jets
        #    continue
        if not particle.jetId >= 2:
            continue        
        
        selectedParticles.append(particle)
        
    if isDEBUG and printLevel >= 8:
        print "nPartiles %d, selectedParticles %d" % (len(particles),len(selectedParticles))
    return selectedParticles


def jetBtagLooseSelector(particles):
    selectedParticles = []
    for particle in particles:
        if isDEBUG and printLevel >= 6:
            print "jetBtagLooseSelector::particle: pt %g, eta %g, phi %g,  jetId: %d, btagDeepFlavB %g"\
                % (particle.pt, particle.eta, particle.phi, \
                   particle.jetId, particle.btagDeepFlavB)
        
        #if not particle.pt > 25.0:
        if not particle.pt_nom > 25.0:
            continue
        if not abs(particle.eta) < 2.4:
            continue
        #if not (particle.pt < 60.0  and  abs(particle.eta) > 2.7 and abs(particle.eta) < 3.0): # ECAL-HCAL noice for forward jets
        #    continue
        if not particle.jetId >= 2:
            continue
        if not particle.btagDeepFlavB > jetBtagWPLoose:
            continue
        
        selectedParticles.append(particle)
        
    if isDEBUG and printLevel >= 6:
        print "nPartiles %d, selectedParticles %d" % (len(particles),len(selectedParticles))
    return selectedParticles


def jetBtagMediumSelector(particles):
    selectedParticles = []
    for particle in particles:
        if isDEBUG and printLevel >= 6:
            print "jetBtagMediumSelector::particle: pt %g, eta %g, phi %g,  jetId: %d, btagDeepFlavB %g"\
                % (particle.pt, particle.eta, particle.phi, \
                   particle.jetId, particle.btagDeepFlavB)
        
        #if not particle.pt > 25.0:
        if not particle.pt_nom > 25.0:
            continue
        if not abs(particle.eta) < 2.4:
            continue
        #if not (particle.pt < 60.0  and  abs(particle.eta) > 2.7 and abs(particle.eta) < 3.0): # ECAL-HCAL noice for forward jets
        #    continue
        if not particle.jetId >= 2:
            continue
        if not particle.btagDeepFlavB > jetBtagWPMedium:
            continue
        
        selectedParticles.append(particle)
        
    if isDEBUG and printLevel >= 6:
        print "nPartiles %d, selectedParticles %d" % (len(particles),len(selectedParticles))
    return selectedParticles


def getSF_BTag_Shape(particles):
    sf = 1.0
    for particle in particles:
        if abs(particle.btagSF_deepjet_shape - 0.0) > 1e-6:
            sf *= particle.btagSF_deepjet_shape
        
        if isDEBUG and printLevel >= 8:
            print "getSF_BTag_Shape::particle: pt %g, eta %g, phi %g,  jetId: %d, btagDeepFlavB %g, \t SF_b_shape %g,  SF_b_L %g, SF_b_M %g,  sf %g "\
                % (particle.pt, particle.eta, particle.phi, \
                   particle.jetId, particle.btagDeepFlavB, \
                   particle.btagSF_deepjet_shape, \
                   particle.btagSF_deepjet_L, particle.btagSF_deepjet_M, \
                   sf) 

    return sf


def getSF_BTagLoose(particles):
    sf = 1.0
    for particle in particles:
        if particle.btagDeepFlavB > jetBtagWPLoose:
            sf *= particle.btagSF_deepjet_L
        
        if isDEBUG and printLevel >= 8:
            print "getSF_BTagLoose::particle: pt %g, eta %g, phi %g,  jetId: %d, btagDeepFlavB %g, \t SF_b_L %g, SF_b_M %g,  sf %g "\
                % (particle.pt, particle.eta, particle.phi, \
                   particle.jetId, particle.btagDeepFlavB, \
                   particle.btagSF_deepjet_L, particle.btagSF_deepjet_M, sf)

    return sf
    
    
def getSF_BTagMedium(particles):
    sf = 1.0
    for particle in particles:
        if particle.btagDeepFlavB > jetBtagWPMedium:
            sf *= particle.btagSF_deepjet_M
        
        if isDEBUG and printLevel >= 8:
            print "getSF_BTagMedium::particle: pt %g, eta %g, phi %g,  jetId: %d, btagDeepFlavB %g, \t SF_b_L %g, SF_b_M %g,  sf %g "\
                % (particle.pt, particle.eta, particle.phi, \
                   particle.jetId, particle.btagDeepFlavB, \
                   particle.btagSF_deepjet_L, particle.btagSF_deepjet_M, sf)
    
    return sf


def getSF_BTagLooseOrMedium(particles):
    sf = 1.0
    for particle in particles:
        if particle.btagDeepFlavB > jetBtagWPMedium:
            sf *= particle.btagSF_deepjet_M
        elif particle.btagDeepFlavB > jetBtagWPLoose:
            sf *= particle.btagSF_deepjet_L
        
        if isDEBUG and printLevel >= 8:
            print "getSF_BTagMedium::particle: pt %g, eta %g, phi %g,  jetId: %d, btagDeepFlavB %g, \t SF_b_L %g, SF_b_M %g,  sf %g "\
                % (particle.pt, particle.eta, particle.phi, \
                   particle.jetId, particle.btagDeepFlavB, \
                   particle.btagSF_deepjet_L, particle.btagSF_deepjet_M, sf)
    
    return sf


def particleCollectionCleaner(particles, overlaps, dR = 0.4):
    cleanedParticles = []
    if isDEBUG and printLevel >= 8:
        print "particleCollectionCleaner: nParticles %d, nOverlap %d, dR %g" % (len(particles),len(overlaps),dR)
    for particle in particles:
        if isDEBUG and printLevel >= 8:
            print "particleCollectionCleaner::particle: pt %g, eta %g, phi %g, m %g" % (particle.pt, particle.eta, particle.phi, particle.mass)
        isOverlap = False
        for particleOverlap in overlaps:
            dr = particle.DeltaR(particleOverlap)
            if isDEBUG and printLevel >= 8:
                print "\tparticleOverlap: pt %g, eta %g, phi %g, m %g,    dr %g" % (particleOverlap.pt, particleOverlap.eta, particleOverlap.phi, particle.mass, dr)
            if dr < dR:
                isOverlap = True
                break
            
        if not isOverlap:
            cleanedParticles.append(particle)
            
        if isDEBUG and printLevel >= 8:
            if not isOverlap:
                print "\t\t\t noOverlap"
            else:
                print "\t\t\t Overlap"
        
    return cleanedParticles
    

def particleCollectionCleaner_byIndex(particles, overlaps):
    cleanedParticles = []
    if isDEBUG and printLevel >= 8:
        print "particleCollectionCleaner_byIndex: nParticles %d, nOverlap %d, " % (len(particles),len(overlaps))
    for idx in range(0, len(particles)):
        particle = particles[idx]
        if isDEBUG and printLevel >= 8:
            print "particle: pt %g, eta %g, phi %g, m %g,  Idx %d" % (particle.pt, particle.eta, particle.phi, particle.mass, idx)
        isOverlap = False
        for particleOverlap in overlaps:
            dr = particle.DeltaR(particleOverlap)
            if isDEBUG and printLevel >= 8:
                print "\tparticleOverlap: pt %g, eta %g, phi %g, m %g,    dr %g,  jetIdx %d" % (particleOverlap.pt, particleOverlap.eta, particleOverlap.phi, particle.mass, dr, particleOverlap.jetIdx)
            if particleOverlap.jetIdx == idx:
                isOverlap = True
                break
            
        if not isOverlap:
            cleanedParticles.append(particle)
        
        if isDEBUG and printLevel >= 8:
            if not isOverlap:
                print "\t\t\t noOverlap"
            else:
                print "\t\t\t Overlap"
        
    return cleanedParticles


def getIntersectionParticleCollection(collection1, collection2):
    collectionIntersection = []
    for particle1 in collection1:
        for particle2 in collection2:
            if particle1 == particle2:
                collectionIntersection.append(particle1)
    
    return collectionIntersection



def pickFirstNobjects(collection, N):
    n = min(len(collection), N)
    pickCollection = []
    if n == 0:
        return pickCollection
    
    for i in range(0, n):
        pickCollection.append(collection[i])
    
    return pickCollection



def compMHT(leptons, hadTaus, jets):
    mht_p4 = ROOT.TLorentzVector(0.0, 0.0, 0.0, 0.0)
    
    for part in leptons:
        if isDEBUG and printLevel >= 6:
            print "compMHT:: mht (%g, %g, %g, %g) \t lep (%g, %g, %g, %g)" % \
                (mht_p4.Pt(), mht_p4.Eta(), mht_p4.Phi(), mht_p4.E(), \
                part.p4().Pt(), part.p4().Eta(), part.p4().Phi(), part.p4().E())        
        mht_p4 += part.p4()
    
    for part in hadTaus:
        if isDEBUG and printLevel >= 6:
            print "compMHT:: mht (%g, %g, %g, %g) \t tau (%g, %g, %g, %g)" % \
                (mht_p4.Pt(), mht_p4.Eta(), mht_p4.Phi(), mht_p4.E(), \
                part.p4().Pt(), part.p4().Eta(), part.p4().Phi(), part.p4().E())        
        mht_p4 += part.p4()
    
    for part in jets:
        if isDEBUG and printLevel >= 6:
            print "compMHT:: mht (%g, %g, %g, %g) \t jet (%g, %g, %g, %g)" % \
                (mht_p4.Pt(), mht_p4.Eta(), mht_p4.Phi(), mht_p4.E(), \
                part.p4().Pt(), part.p4().Eta(), part.p4().Phi(), part.p4().E())
        mht_p4 += part.p4()
    
    if isDEBUG and printLevel >= 6:
        print "compMHT:: mht (%g, %g, %g, %g)" % \
            (mht_p4.Pt(), mht_p4.Eta(), mht_p4.Phi(), mht_p4.E())
    
    return mht_p4


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

        self.h_Info_bins = OD([
            ("nof_events_NanoAOD_PostProc",  1),
            ("xsection",                     2),
            ("lumi",                         3),
            ("lumiScale",                    4),
            ("nEventsAnalyzed",             11),
            ("nEventsSelected",             12),
            ("nEventsSelected_Wtd",         13),
        ])
        
        # event weight
        self.h_evtWeight = ROOT.TH1D('evtWeight',   'evtWeight',   600, -3.0, 3.0)
        self.addObject(self.h_evtWeight )
        
        self.h_evtWeight_genWeight = ROOT.TH1D('evtWeight_genWeight',   'evtWeight_genWeight',   600, -1000.0, 1000.0)
        self.addObject(self.h_evtWeight_genWeight )
        
        self.h_evtWeight_genWeight_sign = ROOT.TH1D('evtWeight_genWeight_sign',   'evtWeight_genWeight_sign',   600, -3.0, 3.0)
        self.addObject(self.h_evtWeight_genWeight_sign )
        
        self.h_evtWeight_L1PreFiringWeight = ROOT.TH1D('evtWeight_L1PreFiringWeight',   'evtWeight_L1PreFiringWeight',   600, -3.0, 3.0)
        self.addObject(self.h_evtWeight_L1PreFiringWeight )
        
        self.h_evtWeight_LHEScaleWeight = ROOT.TH1D('evtWeight_LHEScaleWeight',   'evtWeight_LHEScaleWeight',   600, -3.0, 3.0)
        self.addObject(self.h_evtWeight_LHEScaleWeight )
        
        self.h_evtWeight_PSWeight = ROOT.TH1D('evtWeight_PSWeight',   'evtWeight_PSWeight',   600, -3.0, 3.0)
        self.addObject(self.h_evtWeight_PSWeight )
        
        self.h_evtWeight_puWeight = ROOT.TH1D('evtWeight_puWeight',   'evtWeight_puWeight',   600, -3.0, 3.0)
        self.addObject(self.h_evtWeight_puWeight )
        
        self.h_evtWeight_lumiScale = ROOT.TH1D('evtWeight_lumiScale',   'evtWeight_lumiScale',   600, -3.0, 3.0)
        self.addObject(self.h_evtWeight_lumiScale )
        
        self.h_evtWeight_sf_leptonID = ROOT.TH1D('evtWeight_sf_leptonID',   'evtWeight_sf_leptonID',   600, -3.0, 3.0)
        self.addObject(self.h_evtWeight_sf_leptonID )
        
        self.h_evtWeight_sf_leptonTrig = ROOT.TH1D('evtWeight_sf_leptonTrig',   'evtWeight_sf_leptonTrig',   600, -3.0, 3.0)
        self.addObject(self.h_evtWeight_sf_leptonTrig )
        
        self.h_evtWeight_sf_btag_shape = ROOT.TH1D('evtWeight_sf_btag_shape',   'evtWeight_sf_btag_shape',   600, -3.0, 3.0)
        self.addObject(self.h_evtWeight_sf_btag_shape )
        
        
        
        
        
        # read histograms for Scale Factors 
        # Muon ID SF ----------------
        self.fSF_MuonID_sel        = ROOT.TFile(MuonSFDetails[MuonID_sel]["file"])
        self.fSF_MuonID_sel_lowPt  = ROOT.TFile(MuonSFDetails[MuonID_sel_lowPt]["file"])
        
        if not self.fSF_MuonID_sel.IsOpen() or \
           not self.fSF_MuonID_sel_lowPt.IsOpen():
            print "fSF_MuonID: file %s or %s couldn't open **** ERROR **** \nTerminating.." % \
                (MuonSFDetails[MuonID_sel]["file"], MuonSFDetails[MuonID_sel_lowPt]["file"])
            exit(0)
        
        self.h_SF_MuonID_sel        = self.fSF_MuonID_sel.Get(MuonSFDetails[MuonID_sel]["histogram"])
        self.h_SF_MuonID_sel_lowPt  = self.fSF_MuonID_sel_lowPt.Get(MuonSFDetails[MuonID_sel_lowPt]["histogram"])        
        
        if not self.h_SF_MuonID_sel or \
           not self.h_SF_MuonID_sel_lowPt:
            print "h_SF_MuonID: histogram %s: %s or %s: %s couldn't fetch**** ERROR **** \nTerminating.." % \
                (MuonSFDetails[MuonID_sel]["file"], MuonSFDetails[MuonID_sel]["histogram"], \
                 MuonSFDetails[MuonID_sel_lowPt]["file"], MuonSFDetails[MuonID_sel_lowPt]["histogram"])
            exit(0)
        
        print "Used SF_MuonID:: \n %s: %s %s \n %s: %s %s " % \
            (MuonID_sel, MuonSFDetails[MuonID_sel]["file"], MuonSFDetails[MuonID_sel]["histogram"], \
             MuonID_sel_lowPt, MuonSFDetails[MuonID_sel_lowPt]["file"], MuonSFDetails[MuonID_sel_lowPt]["histogram"])
        
        
        # Muon trigger SF ----------
        self.fSF_MuonTrig_1mu = ROOT.TFile(MuonSFDetails["Muon_triggerSF_1mu"]["file"])
        if not self.fSF_MuonTrig_1mu.IsOpen():
            print "fSF_MuonID: file %s  couldn't open **** ERROR **** \nTerminating.." % \
                (MuonSFDetails["Muon_triggerSF_1mu"]["file"])
            exit(0)
        
        self.h_SF_MuonTrig_1mu = self.fSF_MuonTrig_1mu.Get(MuonSFDetails["Muon_triggerSF_1mu"]["histogram"])
        if not self.h_SF_MuonTrig_1mu:
            print "h_SF_MuonTrig: %s histogram %s: %s or couldn't fetch**** ERROR **** \nTerminating.." % \
                ("Muon_triggerSF_1mu", MuonSFDetails["Muon_triggerSF_1mu"]["file"], MuonSFDetails["Muon_triggerSF_1mu"]["histogram"])
            exit(0)
        
        print "Used SF_MuonTrigger:: \n %s: %s %s " % \
            ("Muon_triggerSF_1mu", MuonSFDetails["Muon_triggerSF_1mu"]["file"], MuonSFDetails["Muon_triggerSF_1mu"]["histogram"])
        
        
        # Electron ID SF ------------
        self.fSF_ElectronReco_lowEt  = ROOT.TFile(ElectronSFDetails["Electron_passingRECO_lowEt"]["file"])
        self.fSF_ElectronReco        = ROOT.TFile(ElectronSFDetails["Electron_passingRECO"]["file"])
        self.fSF_ElectronID_sel      = None        
        if ElectronID_sel in ElectronSFDetails:
            self.fSF_ElectronID_sel     = ROOT.TFile(ElectronSFDetails[ElectronID_sel]["file"])
        else:
            print "ElectronID ScaleFactors for ElectronID_sel %s not implemented yet ****** ERROR ******" % ElectronID_sel
            exit(0)
            
        if not self.fSF_ElectronReco_lowEt.IsOpen() or \
           not self.fSF_ElectronReco.IsOpen() or \
           (ElectronID_sel in ElectronSFDetails    and not self.fSF_ElectronID_sel.IsOpen()):
            print "fSF_ElectronID: file %s, %s or %s couldn't open **** ERROR **** \nTerminating.." % \
                (ElectronSFDetails["Electron_passingRECO_lowEt"]["file"], ElectronSFDetails["Electron_passingRECO"]["file"], \
                 ElectronSFDetails[ElectronID_sel]["file"])
            exit(0)
        
        self.h_SF_ElectronReco_lowEt = self.fSF_ElectronReco_lowEt.Get(ElectronSFDetails["Electron_passingRECO_lowEt"]["histogram"])
        self.h_SF_ElectronReco       = self.fSF_ElectronReco.Get(ElectronSFDetails["Electron_passingRECO"]["histogram"])
        self.h_SF_ElectronID_sel     = None
        if ElectronID_sel in ElectronSFDetails    and self.fSF_ElectronID_sel.IsOpen():
            self.h_SF_ElectronID_sel = self.fSF_ElectronID_sel.Get(ElectronSFDetails[ElectronID_sel]["histogram"])
            if not self.h_SF_ElectronID_sel:
                print "h_SF_ElectronID: histogram %s: %s couldn't fetch**** ERROR **** \nTerminating.." % \
                    (ElectronSFDetails[ElectronID_sel]["file"], ElectronSFDetails[ElectronID_sel]["histogram"])
                exit(0)        
        
        print "Used SF_ElectronID:: \n %s: %s %s \n %s: %s %s " % \
            ("Electron_passingRECO_lowEt",ElectronSFDetails["Electron_passingRECO_lowEt"]["file"],ElectronSFDetails["Electron_passingRECO_lowEt"]["histogram"],
             "Electron_passingRECO",ElectronSFDetails["Electron_passingRECO"]["file"],ElectronSFDetails["Electron_passingRECO"]["histogram"])
        if ElectronID_sel in ElectronSFDetails:
            print " %s: %s %s " % \
                (ElectronID_sel, ElectronSFDetails[ElectronID_sel]["file"], ElectronSFDetails[ElectronID_sel]["histogram"])
        
        
        self.ofEventNumber_SelectedEvents_All = open("%s/selectedEvents_3SelLeptons_AllEvents.txt" % (output_dir), "w")
        self.ofEventNumber_SelectedEvents_Final = open("%s/selectedEvents_3SelLeptons_Final.txt" % (output_dir), "w")
        
        self.fRunOnselectedEvents = None
        self.listOfSelectedEvent = None
        if runOnSelectedEventsList != "":
            self.fRunOnselectedEvents = open(runOnSelectedEventsList, "r")
            self.listOfSelectedEvent = self.fRunOnselectedEvents.readlines()
            self.fRunOnselectedEvents.close()
            print "listOfSelectedEvent: ",self.listOfSelectedEvent
        








    def endJob(self):
        print "\nendJob()"
        if self.h_Stat1:
            print "nendJob():: printCutFlowTable::"
            printCutFlowTable(self.h_Stat1, self.h_Stat1_wtd)
        
        print "Set h_Info_bins labels:"
        for label, value in self.h_Info_bins.items():
            print "\t{}, {}".format(label,value)
            bin_ = self.h_Info.FindBin(value)
            self.h_Info.GetXaxis().SetBinLabel(bin_, label)
            
            if label in ["nEventsAnalyzed", "nEventsSelected", "nEventsSelected_Wtd"]: # these bins are fill on event level
                continue
            
            if label == "nof_events_NanoAOD_PostProc":
                self.h_Info.SetBinContent(bin_, nof_events_NanoAOD_PostProc)
            
            if label == "xsection":
                self.h_Info.SetBinContent(bin_, process_xsection)
            
            if label == "lumi":
                self.h_Info.SetBinContent(bin_, era_luminosity)
            
            if label == "lumiScale":
                self.h_Info.SetBinContent(bin_, sample_lumiScaleToUse)
        
        print "Print h_Info:" 
        for i in range(1,self.h_Info.GetNbinsX()+1):
            if self.h_Info.GetXaxis().GetBinLabel(i) == "":
                continue
            print " {}  \t {} \t\t\t {}".format(i, self.h_Info.GetXaxis().GetBinLabel(i), self.h_Info.GetBinContent(i))
        
        self.ofEventNumber_SelectedEvents_All.close()
        self.ofEventNumber_SelectedEvents_Final.close() 
        
        print "\nElectronID_presel: ",ElectronID_presel
        print "ElectronID_sel: ",ElectronID_sel
        print "ElectronID_mvaTTH_sel: ",ElectronID_mvaTTH_sel
        nEventsGen   = 0
        nEventsReco  = 0
        enEventsGen  = 0
        enEventsReco = 0
        sLabelGen  = "genHH->4W -> 3l (1qq ?); l, j with CMS pt, eta acceptance; 3 genEle "
        sLabelReco = ">=3 tightEle genMatch"
        for i in range (1, self.h_Stat1.GetNbinsX()+1):
            if sLabelGen in self.h_Stat1.GetXaxis().GetBinLabel(i):
                nEventsGen  = self.h_Stat1.GetBinContent(i)
                enEventsGen = self.h_Stat1.GetBinError(i)
            if sLabelReco in self.h_Stat1.GetXaxis().GetBinLabel(i):
                nEventsReco  = self.h_Stat1.GetBinContent(i)
                enEventsReco = self.h_Stat1.GetBinError(i)
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
        
        print "3 electron selection efficiency = %d / %d = %5.2f +- %.2f percent " % (nEventsReco,nEventsGen, effi*100,eeffi*100)
        print "%s, mvaTTH cut %.1f: 3 electron selection efficiency = %5.2f +- %.2f %% " % (ElectronID_sel,ElectronID_mvaTTH_sel, effi*100,eeffi*100)
        Module.endJob(self)            


    def readSF(self, sfHisto, sfHistoType, pt, eta):
        # sfHistoType: 0: "xaxis": "pt",    "yaxis": "abseta",  for muon SF
        # sfHistoType: 1: "xaxis": "eta",   "yaxis": "pt"       for electron SF
        sf = 1.0
        if   sfHistoType == 0:
            ptBin = sfHisto.GetXaxis().FindBin(pt)
            if (pt >= sfHisto.GetXaxis().GetXmax()):
                ptBin = sfHisto.GetNbinsX()
            etaBin = sfHisto.GetYaxis().FindBin(abs(eta))
            sf = sfHisto.GetBinContent(ptBin, etaBin)
            #print "pt %g, eta %g   bin %d %d  sf %g" % (pt,eta, ptBin,etaBin, sf)
        elif sfHistoType == 1:
            ptBin = sfHisto.GetYaxis().FindBin(pt)
            if (pt >= sfHisto.GetYaxis().GetXmax()):
                ptBin = sfHisto.GetNbinsY()
            etaBin = sfHisto.GetXaxis().FindBin(eta)
            sf = sfHisto.GetBinContent(etaBin, ptBin)
            #print "pt %g, eta %g   bin %d %d  sf %g" % (pt,eta, ptBin,etaBin, sf)
        
        if abs(sf - 0.0) < 1e-5: # pt out-of SF calculated pt range; hence sf = 0
            sf = 1.0
        return sf



    def get_leptonIDSF(self, leptons, nLepsToUse):
        sf = 1.0
        if len(leptons) < nLepsToUse:
            print "get_leptonIDSF():: len(leptons) (%d)  <  nLepsToUse (%d) **** ERROR ****" % (len(leptons), nLepsToUse)
            return sf
        for iL in range(0, nLepsToUse):
            lep = leptons[iL]
            if abs(lep.pdgId) == 11:
                sf_partial_reco = 1.0
                sf_partial_ID = 1.0
                if lep.pt < self.h_SF_ElectronReco_lowEt.GetYaxis().GetXmax():
                    sf_partial_reco = self.readSF(self.h_SF_ElectronReco_lowEt, 1, lep.pt, lep.eta)
                else:
                    sf_partial_reco = self.readSF(self.h_SF_ElectronReco, 1, lep.pt, lep.eta)
                
                if self.h_SF_ElectronID_sel:
                    sf_partial_ID = self.readSF(self.h_SF_ElectronID_sel, 1, lep.pt, lep.eta)
                
                sf *= (sf_partial_reco * sf_partial_ID)
                #print "SF ele: reco %g, ID %g, total %g,  sf_ID %g" % (sf_partial_reco, sf_partial_ID, sf_partial_reco * sf_partial_ID, sf)
                
            elif abs(lep.pdgId) == 13:
                sf_partial = 1.0
                if lep.pt >= self.h_SF_MuonID_sel.GetXaxis().GetXmin():
                    sf_partial = self.readSF(self.h_SF_MuonID_sel, 0, lep.pt, lep.eta)
                else:
                    sf_partial = self.readSF(self.h_SF_MuonID_sel_lowPt, 0, lep.pt, lep.eta)
                sf *= sf_partial
                #print "SF mu: ID %g,   sf_ID %g" % (sf_partial, sf)
        
        return sf



    def get_leptonTrigSF(self, leptons, nLepsToUse):
        sf = 1.0
        if len(leptons) < nLepsToUse:
            print "get_leptonIDSF():: len(leptons) (%d)  <  nLepsToUse (%d) **** ERROR ****" % (len(leptons), nLepsToUse)
            return sf
        
        nMuons     = 0
        nElectrons = 0
        muons      = []
        for iL in range(0, nLepsToUse):
            lep = leptons[iL]
            if   abs(lep.pdgId) == 11:
                nElectrons += 1
            elif abs(lep.pdgId) == 13:
                nMuons += 1
                muons.append(lep)
        
        if nMuons == 1:
            sf_partial = self.readSF(self.h_SF_MuonTrig_1mu, 0, muons[0].pt, muons[0].eta)
            sf *= sf_partial
            #print "SF_trig_1mu: %g,  sf_trig: %g" % (sf_partial, sf)
        
        if nElectrons >= 1:
            sf_partial = ElectronSFDetails["Electron_triggerSF_evtWt"]["sf_evtWt"]
            sf *= sf_partial
            #print "SF_trig_ele: %g,  sf_trig: %g" % (sf_partial, sf)
        
        #print "sf_trig: %g" % (sf)
        return sf



    def analyze(self, event):
        runNumber = getattr(event,"run")
        lumiBlock = getattr(event,"luminosityBlock")
        eventNumber = getattr(event,"event")
        
        if not isMC:
            print "anaHHTo4W_3l_1qq_gen:: Not running on MC mode \t\t ******* ERROR ******* \n"
            exit(0)
        
        if printLevel >= 1: 
            print "\n\n run: %d, lumi: %d, eventNumber: %d" % (runNumber,lumiBlock,eventNumber)
        
        
        genParts = Collection(event, "GenPart")
        
        muons     = Collection(event, "Muon") # slimmedMuons after basic selection (pt > 3 && (passed('CutBasedIdLoose') || passed('SoftCutBasedId') || passed('SoftMvaId') || passed('CutBasedIdGlobalHighPt') || passed('CutBasedIdTrkHighPt')))
        electrons = Collection(event, "Electron") # slimmedElectrons after basic selection (pt > 5 )
        photons   = Collection(event, "Photon") # slimmedPhotons after basic selection (pt > 5 )
        taus      = Collection(event, "Tau") # slimmedTaus after basic selection (pt > 18 && tauID('decayModeFindingNewDMs') && (tauID('byLooseCombinedIsolationDeltaBetaCorr3Hits') || tauID('byVLooseIsolationMVArun2v1DBoldDMwLT2015') || tauID('byVLooseIsolationMVArun2v1DBnewDMwLT') || tauID('byVLooseIsolationMVArun2v1DBdR03oldDMwLT') || tauID('byVVLooseIsolationMVArun2v1DBoldDMwLT') || tauID('byVVLooseIsolationMVArun2v1DBoldDMwLT2017v2') || tauID('byVVLooseIsolationMVArun2v1DBnewDMwLT2017v2') || tauID('byVVLooseIsolationMVArun2v1DBdR03oldDMwLT2017v2') || tauID('byVVVLooseDeepTau2017v2p1VSjet')))
        jetsAK4   = Collection(event, "Jet") # slimmedJets, i.e. ak4 PFJets CHS with JECs applied, after basic selection (pt > 15)
        #met_pt    = getattr(event,    "MET_pt")
        #met_phi   = getattr(event,    "MET_phi")
        met_pt    = getattr(event,    "MET_pt_nom")
        met_phi   = getattr(event,    "MET_phi_nom")
        
        # LHEScaleWeight :
        #  | Float_t LHE scale variation weights (w_var / w_nominal); [0] is mur=0.5 muf=0.5 ; [1] is mur=0.5 muf=1 ; [2] is mur=0.5 muf=2 ; [3] is mur=1 muf=0.5 ; [4] is mur=1 muf=1 ; [5] is mur=1 muf=2 ; [6] is mur=2 muf=0.5 ; [7] is mur=2 muf=1 ; [8] is mur=2 muf=2 
        nLHEScaleWeights = getattr(event, "nLHEScaleWeight")
        #print "nLHEScaleWeights: ",nLHEScaleWeights
        LHEScaleWeights = getattr(event, "LHEScaleWeight")
        #print "LHEScaleWeights[4]: ",LHEScaleWeights[4] 
        # PSWeight  | Float_t dummy PS weight (1.0)
        nPSWeights      = getattr(event, "nPSWeight")
        #print "nPSWeights: ",nPSWeights
        PSWeights       = getattr(event, "PSWeight")
        #print "PSWeights: ",PSWeights
        #print "PSWeights[0]: ",PSWeights[0]
        
        lumiScale           = sample_lumiScaleToUse # 0.00817974994952 #1
        genWeight           = getattr(event, "genWeight")
        L1PreFiringWeight   = getattr(event, "L1PreFiringWeight_Nom") # it should be 1 for 2018 data 
        topPtRwgt           = 1
        #LHEScaleWeight      = LHEScaleWeights[4] if nLHEScaleWeights > 4 else 1.0 #1 # [4] is mur=1 muf=1
        #PSWeight            = PSWeights[0] if nPSWeights > 0 else 1 # 1
        get_puWeight        = getattr(event, "puWeight")
        
        LHEScaleWeight = 1
        PSWeight = 1
        if nLHEScaleWeights > 4 :
            try:
                LHEScaleWeight = LHEScaleWeights[4]
            except:
                LHEScaleWeight = 1
        if nPSWeights > 0 :
            try:
                PSWeight = PSWeights[0]
            except:
                PSWeight = 1 
                
        
        
        
        triggers_1e         = ['HLT_Ele32_WPTight_Gsf', 'HLT_Ele35_WPTight_Gsf']
        use_triggers_1e     = True
        triggers_1mu        = ['HLT_IsoMu24', 'HLT_IsoMu27']
        use_triggers_1mu    = True
        triggers_2e         = ['HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL']
        use_triggers_2e     =  True
        triggers_2mu        = ['HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass3p8', 'HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_Mass8']
        use_triggers_2mu    =  True
        triggers_1e1mu      = ['HLT_Mu8_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ', 'HLT_Mu12_TrkIsoVVL_Ele23_CaloIdL_TrackIdL_IsoVL_DZ', 'HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL', 'HLT_Mu23_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_DZ']
        use_triggers_1e1mu  = True
        triggers_3e         = ['HLT_Ele16_Ele12_Ele8_CaloIdL_TrackIdL']
        use_triggers_3e     = True
        triggers_3mu        = ['HLT_TripleMu_12_10_5']
        use_triggers_3mu    = True
        triggers_1e2mu      = ['HLT_DiMu9_Ele9_CaloIdL_TrackIdL_DZ']
        use_triggers_1e2mu  = True
        triggers_2e1mu      = ['HLT_Mu8_DiEle12_CaloIdL_TrackIdL']
        use_triggers_2e1mu  = True
        
        
        
        
        
        if runOnSelectedEventsList != "":
            sEvt = "%d:%d:%d\n" % (runNumber,lumiBlock,eventNumber)
            if sEvt  in  self.listOfSelectedEvent:
                print "\n\n\n%s event  found in listOfSelectedEvent. Analyze this event" % sEvt
            else:
                return True
        
        
        self.nEventsAnalyzed += 1
        self.h_Info.Fill(self.h_Info_bins["nEventsAnalyzed"])
        self.h_Stat.Fill(0)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "all")
        self.ofEventNumber_SelectedEvents_All.write("%d:%d:%d\n" % (runNumber,lumiBlock,eventNumber))
        
        
        ptThrshLeptons = OD([
            ("ptThrsh_4l",    [25., 15., 15., 10.]),
            ("ptThrsh_3l",    [25., 15., 10.]),
            ("ptThrsh_2l",    [25., 15.]),
            ("ptThrsh_1l",    [30.]),
            ("ptThrsh_l_min", [10.]),
        ])
        ptThresholdJet     = 25.
        #
        CMSEtaMax_Jet      = 2.4;
        CMSEtaMax_Lepton   = 2.4;
        CMSEtaMax_Electron = 2.5;
        CMSEtaMax_Muon     = 2.4;
        
        
        genLeptonsFromHHTo4W = []
        genQuarksFromHHTo4W = []
        
        if isMC:
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
            
            if isDEBUG and printLevel >=10:
                print "\n\n genPartFamily:\n"        
                for key, value in genPartFamily.items():
                    print "key:",key, ",  value:",value
            
            
            firstFamilyMember = list(genPartFamily.keys())[0]
            familyTree =  createTree(genPartFamily, firstFamilyMember)
            if isDEBUG and printLevel >=10:
                print "\n\n printFamilyTree: \n"
                printFamilyTree(genParts, familyTree)
             
            # tag HH->4W -> 3lnu 1qq
            idxGenH = collections.OrderedDict()    # { 'iH0': idxH0,  'iH1': idxH1}
            idxGenWFromHH = collections.OrderedDict()    # { 'iH0': [idxD1, idxD2],  'iH1': [idxD1, idxD2]}
            decayModeGenWFromHH = collections.OrderedDict()    # { 'iH0': ['D1 decay mode', 'D2 decay mode'],  'iH1': ['D1 decay mode', 'D2 decay mode']}
            idxGenQFromWOfHH = [] # list storing gen-particle-idx of GenQuarks from (hadronically decaying) V of HH->4V
            sWDecayModeLeptonic = 'WDecayModeLeptonic'
            sWDecayModeHadronic = 'WDecayModeHadronic'
            sWDecayModeTau      = 'WDecayModeTau'
            
            pdgId_EleMu  = [11, 12, 13, 14]
            pdgId_Tau    = [15, 16]
            pdgId_Quarks = [1, 2, 3, 4, 5, 6]
            
            #print "\n\n genPartFamily:\n"
            iH = 0
            for idxGenPart, GenPartDaughters in genPartFamily.items():
                #print "idxGenPart: ",idxGenPart, "(",genParts[idxGenPart].pdgId, "), daughter: ",GenPartDaughters
                if abs(genParts[idxGenPart].pdgId) == 25:
                    idxGenH['iH%d'%iH] = idxGenPart
                    idxGenWFromHH['iH%d'%iH] = GenPartDaughters
                    decayModeGenWFromHH['iH%d'%iH] = [sWDecayModeHadronic] * len(GenPartDaughters)
                    for iW in range(0, len(GenPartDaughters)):
                        idxW = GenPartDaughters[iW]
                        #print "\t iW:",iW,", WDaughters:",genPartFamily[idxW]
                        for idxWDaughter in genPartFamily[idxW]:
                            if abs(genParts[idxWDaughter].pdgId) in pdgId_EleMu:
                                decayModeGenWFromHH['iH%d'%iH][iW] = sWDecayModeLeptonic
                            if abs(genParts[idxWDaughter].pdgId) in pdgId_Tau:
                                decayModeGenWFromHH['iH%d'%iH][iW] = sWDecayModeTau
                            if abs(genParts[idxWDaughter].pdgId) in pdgId_Quarks:
                                decayModeGenWFromHH['iH%d'%iH][iW] = sWDecayModeHadronic
                                idxGenQFromWOfHH.append(idxWDaughter)                                
                    iH += 1
            
            if isDEBUG and printLevel >=10:
                print "\nlen(idxGenH):",len(idxGenH), ", idxGenH:",idxGenH
                print "len(idxGenWFromHH):",len(idxGenWFromHH), ", idxGenWFromHH:",idxGenWFromHH
                print "len(decayModeGenWFromHH):",len(decayModeGenWFromHH), ", decayModeGenWFromHH:",decayModeGenWFromHH
                print "len(idxGenQFromWOfHH):",len(idxGenQFromWOfHH)," idxGenQFromWOfHH:",idxGenQFromWOfHH
            
            
            # proceed with events with 2 Higgs
            if not len(idxGenH) == 2 or not len(idxGenWFromHH) == 2:
                return True
            #self.h_Stat.Fill(1)
            cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "2 genH")
            
            
            # Now we want to get leptons from WFromHH. But we want final leptons from the W decay chains, so that we can compare them with reco-leptons
            ngenWFromHH = 0
            ngenWFromHH_DMLeptonic = 0
            idxWFromHH_DMLeptonic = []
            ngenWFromHH_DMHadronic = 0
            for iH, idxWsFromHH in idxGenWFromHH.items():
                for iW in range(0, len(idxWsFromHH)):
                    idxWFromHH = idxWsFromHH[iW]
                    #print "\niH:",iH,", daughter: ",daughter,", (",genParts[daughter].pdgId,")"
                    if abs(genParts[idxWFromHH].pdgId) == 24:
                        ngenWFromHH += 1
                    if decayModeGenWFromHH[iH][iW] == sWDecayModeLeptonic:
                        ngenWFromHH_DMLeptonic += 1
                        idxWFromHH_DMLeptonic.append(idxWFromHH)                
                    if decayModeGenWFromHH[iH][iW] == sWDecayModeHadronic:
                        ngenWFromHH_DMHadronic += 1
            
            if isDEBUG and printLevel >=11:
                print "\nngenWFromHH: ",ngenWFromHH, ",  ngenWFromHH_DMLeptonic:",ngenWFromHH_DMLeptonic, ",  ngenWFromHH_DMHadronic:",ngenWFromHH_DMHadronic, ",  len(idxGenQFromWOfHH):",len(idxGenQFromWOfHH)
            
            # HH->4W events
            if not ngenWFromHH == 4:
                return True
            self.h_Stat.Fill(2)
            cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "genHH->4W")
            
            if not ngenWFromHH_DMLeptonic == 3 :
                return True
            self.h_Stat.Fill(3)
            cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "genHH->4W -> 3l (1qq ?)")
            
            if isDEBUG and printLevel >=10:
                print "\nngenWFromHH: ",ngenWFromHH, ",  ngenWFromHH_DMLeptonic:",ngenWFromHH_DMLeptonic, ",  ngenWFromHH_DMHadronic:",ngenWFromHH_DMHadronic, ",  len(idxGenQFromWOfHH):",len(idxGenQFromWOfHH)
                
            idxGenLepFromHHTo4W_3l_1qq = [] # list of gen-particle idx of leptons from HH->4W decay
            for i in range(0, len(idxWFromHH_DMLeptonic)):
                if isDEBUG and printLevel >=10:
                    print "\nPrint WFromHH DMLeptonic Decay chain:"
                firstFamilyMember1 = idxWFromHH_DMLeptonic[i]
                familyTree1 =  createTree(genPartFamily, firstFamilyMember1)
                if isDEBUG and printLevel >=10:
                    printFamilyTree(genParts, familyTree1)
                
                # get idx of final state particles in W decay chain
                idxFamilyTreeFinalMembers = getFamilyTreeFinalMembers(genParts, familyTree1)
                #print "familyTreeFinalMembers: ",idxFamilyTreeFinalMembers
                for idxFinalMember in idxFamilyTreeFinalMembers:
                    if abs(genParts[idxFinalMember].pdgId) in [11, 13]:
                        idxGenLepFromHHTo4W_3l_1qq.append(idxFinalMember)
            
            if isDEBUG and printLevel >=10:
                print "len(idxGenLepFromHHTo4W_3l_1qq)",len(idxGenLepFromHHTo4W_3l_1qq)
                for idx in idxGenLepFromHHTo4W_3l_1qq:
                    print "\t idxGenLepFromHHTo4W_3l_1qq:",idx,", pdgid:",genParts[idx].pdgId,", motherIdx:",genParts[idx].genPartIdxMother
            
            for idx in idxGenLepFromHHTo4W_3l_1qq:
                genLeptonsFromHHTo4W.append(genParts[idx])
            for idx in idxGenQFromWOfHH:
                genQuarksFromHHTo4W.append(genParts[idx])
            
            if isDEBUG and printLevel >=10:
                print "Print genParticles before sorting::"
                printLeptonsCollection("genLeptonsFromHHTo4W",genLeptonsFromHHTo4W)
                printLeptonsCollection("genQuarksFromHHTo4W",genQuarksFromHHTo4W)
            
            genLeptonsFromHHTo4W.sort(key=lambda particle: particle.pt, reverse=True)
            genQuarksFromHHTo4W.sort(key=lambda particle: particle.pt, reverse=True)    
            
            if isDEBUG and printLevel >=10:
                print "Print genParticles after sorting::"
                printLeptonsCollection("genLeptonsFromHHTo4W",genLeptonsFromHHTo4W)
                printLeptonsCollection("genQuarksFromHHTo4W",genQuarksFromHHTo4W)
            
            
            if not len(genLeptonsFromHHTo4W) == 3:
                return True
            cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "genHH->4W -> 3l (1qq ?); genLep=3 ")
            
            if not len(genQuarksFromHHTo4W) >= 1:
                return True
            cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "genHH->4W -> 3l (1qq ?); genLep=3, genQ>=1 ")
            
            isHHTo4WDecayParticlesWithInCMSAcpt = True
            for i in range(0, 3):
                if not genLeptonsFromHHTo4W[i].pt > ptThrshLeptons["ptThrsh_3l"][i]:
                    isHHTo4WDecayParticlesWithInCMSAcpt = False
                if abs(genLeptonsFromHHTo4W[i].pdgId) == 11:
                    if not abs(genLeptonsFromHHTo4W[i].eta) <= CMSEtaMax_Electron:
                        isHHTo4WDecayParticlesWithInCMSAcpt = False
                if abs(genLeptonsFromHHTo4W[i].pdgId) == 13:
                    if not abs(genLeptonsFromHHTo4W[i].eta) <= CMSEtaMax_Muon:
                        isHHTo4WDecayParticlesWithInCMSAcpt = False
            
            if not genQuarksFromHHTo4W[0].pt >= ptThresholdJet:
                isHHTo4WDecayParticlesWithInCMSAcpt = False
            if not abs(genQuarksFromHHTo4W[0].eta) <= CMSEtaMax_Jet:
                isHHTo4WDecayParticlesWithInCMSAcpt = False
            
            if isDEBUG and printLevel >=10:
                print "isHHTo4WDecayParticlesWithInCMSAcpt: ",isHHTo4WDecayParticlesWithInCMSAcpt
            
            if not isHHTo4WDecayParticlesWithInCMSAcpt:                
                return True
            
            cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "genHH->4W -> 3l (1qq ?); l, j with CMS pt, eta acceptance ")
            
            nGenEleFromHHTo4W = 0
            for i in range(0, 3):
                if abs(genLeptonsFromHHTo4W[i].pdgId) == 11:
                    nGenEleFromHHTo4W += 1
            
            if nGenEleFromHHTo4W >=1:
                cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "genHH->4W -> 3l (1qq ?); l, j with CMS pt, eta acceptance; >=1 genEle ")
            if nGenEleFromHHTo4W >=2:
                cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "genHH->4W -> 3l (1qq ?); l, j with CMS pt, eta acceptance; >=2 genEle ")
            if nGenEleFromHHTo4W ==3:
                cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "genHH->4W -> 3l (1qq ?); l, j with CMS pt, eta acceptance; 3 genEle ")
            
                
            if not nGenEleFromHHTo4W == 3:
                return True
            


        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "after gen-cuts")





            



        
        # genWeight # generator weight     boost::math::sign(eventInfo.genWeight)
        # L1PreFiringWeight_Nom # L1 pre-firing event correction weight (1-probability)
        # topPtRwgt ??
        # LHE: LHEScaleWeight
        #      nLHEScaleWeight,
        #      LHEScaleWeight: LHE scale variation weights (w_var / w_nominal); [0] is mur=0.5 muf=0.5 ; [1] is mur=0.5 muf=1 ; [2] is mur=0.5 muf=2 ; [3] is mur=1 muf=0.5 ; [4] is mur=1 muf=1 ; [5] is mur=1 muf=2 ; [6] is mur=2 muf=0.5 ; [7] is mur=2 muf=1 ; [8] is mur=2 muf=2
        # HHanalysis: get_lheScaleWeight(central) = 1
        # PSWeight:
        #      HHanalysis: getWeight_ps(central) = 1
        
        '''
        # evtWeightRecorder.get(central_or_shift_main) in HH-analysis: evtWeight:
        # (isMC_ ? get_inclusive(central_or_shift) * get_data_to_MC_correction(central_or_shift) * prescale_ : 1.) *
        #  get_FR(central_or_shift) * chargeMisIdProb_
        
        # get_inclusive = 
        # isMC_ ? get_genWeight() * get_bmWeight() * get_auxWeight(central_or_shift) * get_lumiScale(central_or_shift, bin) * 
                 get_nom_tH_weight(central_or_shift) * get_puWeight(central_or_shift) *    
                 get_l1PreFiringWeight(central_or_shift) * get_lheScaleWeight(central_or_shift) * 
                 get_dy_rwgt(central_or_shift) * get_rescaling() * get_psWeight(central_or_shift) 
               : 1.
        '''
        
        #include <boost/math/special_functions/sign.hpp> // boost::math::sign()
        evtWeight = 1
        evtWeight *= math.copysign(1, genWeight) # use sign of genWeight
        evtWeight *= L1PreFiringWeight
        #evtWeight *= topPtRwgt
        evtWeight *= LHEScaleWeight
        evtWeight *= PSWeight
        evtWeight *= get_puWeight
        evtWeight *= lumiScale
        
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "all * L1PreFiringWeight",L1PreFiringWeight)
        
        
        isTriggered_1e     = isTriggered(event, triggers_1e)
        isTriggered_1mu    = isTriggered(event, triggers_1mu)
        isTriggered_2e     = isTriggered(event, triggers_2e)
        isTriggered_2mu    = isTriggered(event, triggers_2mu)
        isTriggered_1e1mu  = isTriggered(event, triggers_1e1mu)
        isTriggered_3e     = isTriggered(event, triggers_3e)
        isTriggered_3mu    = isTriggered(event, triggers_3mu)
        isTriggered_1e2mu  = isTriggered(event, triggers_1e2mu)
        isTriggered_2e1mu  = isTriggered(event, triggers_2e1mu)
        
        selTrigger_1e      = use_triggers_1e     and isTriggered_1e
        selTrigger_1mu     = use_triggers_1mu    and isTriggered_1mu
        selTrigger_2e      = use_triggers_2e     and isTriggered_2e
        selTrigger_2mu     = use_triggers_2mu    and isTriggered_2mu
        selTrigger_1e1mu   = use_triggers_1e1mu  and isTriggered_1e1mu
        selTrigger_3e      = use_triggers_3e     and isTriggered_3e
        selTrigger_3mu     = use_triggers_3mu    and isTriggered_3mu
        selTrigger_1e2mu   = use_triggers_1e2mu  and isTriggered_1e2mu
        selTrigger_2e1mu   = use_triggers_2e1mu  and isTriggered_2e1mu
        '''
        print "\t isTriggered_1e: ",isTriggered_1e, selTrigger_1e
        print "\t isTriggered_1mu: ",isTriggered_1mu, selTrigger_1mu
        print "\t isTriggered_2e: ",isTriggered_2e, selTrigger_2e
        print "\t isTriggered_2mu: ",isTriggered_2mu, selTrigger_2mu
        print "\t isTriggered_1e1mu: ",isTriggered_1e1mu, selTrigger_1e1mu
        print "\t isTriggered_3e: ",isTriggered_3e, selTrigger_3e
        print "\t isTriggered_3mu: ",isTriggered_3mu, selTrigger_3mu
        print "\t isTriggered_1e2mu: ",isTriggered_1e2mu, selTrigger_1e2mu
        print "\t isTriggered_2e1mu: ",isTriggered_2e1mu, selTrigger_2e1mu
        '''
        '''
        if (not (selTrigger_1e or selTrigger_1mu or \
                 selTrigger_2e or selTrigger_2mu or selTrigger_1e1mu or \
                 selTrigger_3e or selTrigger_3mu or selTrigger_1e2mu or isTriggered_2e1mu)):
            return True
        '''
        self.h_Stat.Fill(1)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "trigger", evtWeight)
        
        
        cleanedMuons = muons
        preselMuons  = preselMuonSelector(cleanedMuons)
        tightMuons   = tightMuonSelector(preselMuons)        
        #preselMuons  = preselMuonSelector_hh_multilepton_test(cleanedMuons)
        #tightMuons   = tightMuonSelector_hh_multilepton_test(preselMuons)
        
        if isDEBUG and printLevel >= 6:
            print "cleanedMuons:: ",len(cleanedMuons)
            for particle in cleanedMuons:
                print "particle: pt %g, eta %g, phi %g" % (particle.pt, particle.eta, particle.phi)
            print "preselMuons:: ",len(preselMuons)
            for particle in preselMuons:
                print "particle: pt %g, eta %g, phi %g" % (particle.pt, particle.eta, particle.phi)
            print "tightMuons:: ",len(tightMuons)
            for particle in tightMuons:
                print "particle: pt %g, eta %g, phi %g" % (particle.pt, particle.eta, particle.phi)
        
        
        
        cleanedElectrons          = particleCollectionCleaner(electrons, preselMuons, 0.3)
        preselElectrons           = preselElectonSelector(cleanedElectrons)
        preselElectronsUncleaned  = preselElectonSelector(electrons)
        tightElectrons            = tightElectonSelector(preselElectrons)        
        #preselElectrons           = preselElectonSelector_hh_multilepton_test(cleanedElectrons)
        #preselElectronsUncleaned  = preselElectonSelector_hh_multilepton_test(electrons)
        #tightElectrons            = tightElectonSelector_hh_multilepton_test(preselElectrons)
        
        if isDEBUG and printLevel >= 6:
            print "electrons:: ",len(electrons)
            for particle in electrons:
                print "particle: pt %g, eta %g, phi %g" % (particle.pt, particle.eta, particle.phi)
            print "cleanedElectrons:: ",len(cleanedElectrons)
            for particle in cleanedElectrons:
                print "particle: pt %g, eta %g, phi %g" % (particle.pt, particle.eta, particle.phi)
            print "preselElectrons:: ",len(preselElectrons)
            for particle in preselElectrons:
                print "particle: pt %g, eta %g, phi %g" % (particle.pt, particle.eta, particle.phi)
            print "tightElectrons:: ",len(tightElectrons)
            for particle in tightElectrons:
                print "particle: pt %g, eta %g, phi %g" % (particle.pt, particle.eta, particle.phi)
        
        
        if len(tightElectrons) >= 1:
            cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, ">=1 tightEle")
        if len(tightElectrons) >= 2:
            cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, ">=2 tightEle")
        if len(tightElectrons) >= 3:
            cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, ">=3 tightEle")        
        
        nEleGenMatch = 0
        for lep in tightElectrons:
            if isParticleGenMatched(lep, genLeptonsFromHHTo4W, 0.3):
                nEleGenMatch += 1
        
        if nEleGenMatch >=1:
            cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, ">=1 tightEle genMatch")
        if nEleGenMatch >=2:
            cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, ">=2 tightEle genMatch")
        if nEleGenMatch >=3:
            cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, ">=3 tightEle genMatch")
        
        
        return True
        
        
        
        preselLeptons = preselMuons + preselElectrons
        preselLeptons.sort(key=lambda particle: particle.pt, reverse=True)
        
        tightLeptons = tightMuons + tightElectrons
        tightLeptons.sort(key=lambda particle: particle.pt, reverse=True)
        
        
        preselLeptonsFirstN = pickFirstNobjects(preselLeptons, 3)
        selLeptons = getIntersectionParticleCollection(preselLeptonsFirstN, tightLeptons)
        selLeptons.sort(key=lambda particle: particle.pt, reverse=True)
        
        if isDEBUG and printLevel >= 10:
            printLeptonsCollection("\npreselLeptons",preselLeptons)
            printLeptonsCollection("\ntightLeptons",tightLeptons)
            printLeptonsCollection("\npreselLeptonsFirstN",preselLeptonsFirstN)
            printLeptonsCollection("\nselLeptons",selLeptons)        
        
        
        if isDEBUG and printLevel >= 6:
            print "preselLeptons:: ",len(preselLeptons)
            for particle in preselLeptons:
                print "particle: pt %g, eta %g, phi %g" % (particle.pt, particle.eta, particle.phi)
            print "selLeptons:: ",len(selLeptons)
            for particle in selLeptons:
                print "particle: pt %g, eta %g, phi %g" % (particle.pt, particle.eta, particle.phi)
        
        
        cleanedTaus = particleCollectionCleaner(taus, preselLeptons, 0.3)
        preselTaus  = preselTauSelector(cleanedTaus)
        tightTaus   = tightTauSelector(preselTaus)
        
        if isDEBUG and printLevel >= 6:
            print "cleanedTaus:: ",len(cleanedTaus)
            for particle in cleanedTaus:
                print "particle: pt %g, eta %g, phi %g" % (particle.pt, particle.eta, particle.phi)
            print "preselTaus:: ",len(preselTaus)
            for particle in preselTaus:
                print "particle: pt %g, eta %g, phi %g" % (particle.pt, particle.eta, particle.phi)
            print "tightTaus:: ",len(tightTaus)
            for particle in tightTaus:
                print "particle: pt %g, eta %g, phi %g" % (particle.pt, particle.eta, particle.phi)
        
        
        cleanedJetsAK4 = None
        if jetCleaningMethod == "cleanedJetsAK4_bydR":
            cleanedJetsAK4 = particleCollectionCleaner(jetsAK4, preselLeptons + preselTaus, 0.4)
        elif jetCleaningMethod == "cleanedJetsAK4_byIndex":
            cleanedJetsAK4 = particleCollectionCleaner_byIndex(jetsAK4, preselLeptons + preselTaus)
        else:
            print "Invalid jetCleaningMethod: %s ***** ERROR *****" % jetCleaningMethod
            exit(0)
        if isDEBUG and printLevel >= 6:
            print "jetsAK4:: ",len(jetsAK4)
            for particle in jetsAK4:
                print "particle: pt %g, eta %g, phi %g" % (particle.pt, particle.eta, particle.phi)
            print "cleanedJetsAK4 (%s) :: %d" % (jetCleaningMethod, len(cleanedJetsAK4))
            for particle in cleanedJetsAK4:
                print "particle: pt %g, eta %g, phi %g" % (particle.pt, particle.eta, particle.phi)
        
        selJetsAK4        = jetAK4Selector(cleanedJetsAK4)
        selJetsBtagLoose  = jetBtagLooseSelector(cleanedJetsAK4)
        selJetsBtagMedium = jetBtagMediumSelector(cleanedJetsAK4)
        
        if isDEBUG and printLevel >= 6:
            print "selJetsAK4:: ",len(selJetsAK4)
            for particle in selJetsAK4:
                print "particle: pt %g, eta %g, phi %g, jetId: " % (particle.pt, particle.eta, particle.phi), particle.jetId
            print "selJetsBtagLoose:: ",len(selJetsBtagLoose)
            for particle in selJetsBtagLoose:
                print "particle: pt %g, eta %g, phi %g, jetId: " % (particle.pt, particle.eta, particle.phi), particle.jetId        
            print "selJetsBtagMedium:: ",len(selJetsBtagMedium)
            for particle in selJetsBtagMedium:
                print "particle: pt %g, eta %g, phi %g, jetId: " % (particle.pt, particle.eta, particle.phi), particle.jetId
        
        met_0 = ROOT.TLorentzVector()
        met_0.SetPtEtaPhiM(met_pt, 0.0, met_phi, 0.0)
        mht_p4 = compMHT(preselLeptons, preselTaus, selJetsAK4)
        met_LD = 0.6 * met_0.Pt() + 0.4 * mht_p4.Pt()
        
        if isDEBUG and printLevel >= 6:
            print "met_0 (%g, %g, %g, %g) \t mht (%g, %g, %g, %g) \t met_LD %g" % \
                (met_0.Pt(), met_0.Eta(), met_0.Phi(), met_0.E(), \
                 mht_p4.Pt(), mht_p4.Eta(), mht_p4.Phi(), mht_p4.E(), met_LD)
        
        
        
           
        if not (len(preselLeptons) >= 3):
            return True
        
        self.h_Stat.Fill(2)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, ">= 3 presel leptons", evtWeight)
        
        
        
        if not ((len(preselElectrons) >= 3 and                           (selTrigger_3e    or selTrigger_2e  or selTrigger_1e                                      )) or \
	        (len(preselElectrons) >= 2 and len(preselMuons) >= 1 and (selTrigger_2e1mu or selTrigger_2e  or selTrigger_1e1mu or selTrigger_1mu or selTrigger_1e)) or \
	        (len(preselElectrons) >= 1 and len(preselMuons) >= 2 and (selTrigger_1e2mu or selTrigger_2mu or selTrigger_1e1mu or selTrigger_1mu or selTrigger_1e)) or \
	        (                              len(preselMuons) >= 3 and (selTrigger_3mu   or selTrigger_2mu or selTrigger_1mu                                     ))):
            return True        
        
        self.h_Stat.Fill(3)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "presel lepton trigger match", evtWeight)
        
        
        
        if not (len(selLeptons) >= 3):
            return True
        
        self.h_Stat.Fill(4)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, ">= 3 sel leptons", evtWeight)
        
        
        if isDEBUG and printLevel >= 10:
            print "selLeptons:: ",len(selLeptons)
            for particle in selLeptons:
                print "particle: pt %g, eta %g, phi %g \t pdgId %d" % (particle.pt, particle.eta, particle.phi, particle.pdgId)
        
        sf_leptonID   = self.get_leptonIDSF(selLeptons, 3)
        sf_leptonTrig = self.get_leptonTrigSF(selLeptons, 3)
        sf_btag_shape = getSF_BTag_Shape(selJetsAK4)
        #sf_btag_L     = getSF_BTagLoose(selJetsBtagLoose)
        #sf_btag_M     = getSF_BTagMedium(selJetsBtagMedium)
        #sf_btag_LorM  = getSF_BTagLooseOrMedium(selJetsBtagLoose)
        
        evtWeight *= sf_leptonID
        evtWeight *= sf_leptonTrig
        evtWeight *= sf_btag_shape
        
        if not (len(tightLeptons) <= 3):
            return True
        
        self.h_Stat.Fill(5)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "<= 3 tight leptons", evtWeight)
        
        
        
        if len(selJetsBtagLoose) >= 2 or len(selJetsBtagMedium) >= 1:
            return True
        
        self.h_Stat.Fill(6)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "b-jet veto", evtWeight)
        
        
        
        if len(tightTaus) >= 1:
            return True
        
        self.h_Stat.Fill(7)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "tau veto", evtWeight)
        
        
        if not (selLeptons[0].pt > 25 and selLeptons[1].pt > 15 and selLeptons[2].pt > 10):
            return True
        
        self.h_Stat.Fill(8)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "sellepton pt > 25 / 15 / 10", evtWeight)
        
        
        sumLeptonCharge_3l = selLeptons[0].charge + selLeptons[1].charge + selLeptons[2].charge 
        isCharge_SS = abs(sumLeptonCharge_3l) >  1;
        isCharge_OS = abs(sumLeptonCharge_3l) <= 1;
        
        if not (isCharge_OS):
            return True
        
        self.h_Stat.Fill(9)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "sel lepton charge", evtWeight)
        
        
        
        if not (len(selJetsAK4) >= 1):
            return True
        
        self.h_Stat.Fill(10)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, ">= 1 jets from W->jj", evtWeight)
        
        
        # LowMassVeto
        failsLowMassVeto = False
        preselLeptonsUncleaned = preselMuons + preselElectronsUncleaned
        for i in range(0, len(preselLeptonsUncleaned)):
            for j in range(i+1, len(preselLeptonsUncleaned)):
                m_ll = (preselLeptonsUncleaned[i].p4() + preselLeptonsUncleaned[j].p4()).M() 
                if (m_ll < 12.0):
                    failsLowMassVeto = True
        
        if failsLowMassVeto:
            return True
        
        self.h_Stat.Fill(11)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "m(ll) > 12 GeV", evtWeight)
        
        
        # Zmass veto
        isSameFlavor_OS = False
        massSameFlavor_OS = -1.0        
        for i in range(0, len(preselLeptons)):
            for j in range(i+1, len(preselLeptons)):
                if preselLeptons[i].pdgId == (-1 * preselLeptons[j].pdgId): # same-flavor opposite sign
                    isSameFlavor_OS = True
                    m_ll = (preselLeptons[i].p4() + preselLeptons[j].p4()).M() 
                    if abs(m_ll - z_mass) < abs(massSameFlavor_OS - z_mass):
                        massSameFlavor_OS = m_ll
        
        failsZbosonMassVeto = isSameFlavor_OS and abs(massSameFlavor_OS - z_mass) < z_window
        
        if failsZbosonMassVeto:
            return True
        
        self.h_Stat.Fill(12)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "Z-boson mass veto", evtWeight)
        
        
        
        #isfailsHtoZZVeto
        failsHtoZZVeto = False
        for iL1 in range(0, len(preselLeptons)):
            for iL2 in range(iL1+1, len(preselLeptons)):
                if not (preselLeptons[iL1].pdgId == (-1 * preselLeptons[iL2].pdgId)): # same-flavor opposite sign
                    continue
                
                for iL3 in range(0, len(preselLeptons)):
                    if iL3 == iL1 or iL3 == iL2:
                        continue
                    for iL4 in range(iL3+1, len(preselLeptons)):
                        if iL4 == iL1 or iL4 == iL2:
                            continue
                        
                        if not (preselLeptons[iL3].pdgId == (-1 * preselLeptons[iL4].pdgId)): # same-flavor opposite sign
                            continue
                        
                        m_4l = (preselLeptons[iL1].p4() + preselLeptons[iL2].p4() + preselLeptons[iL3].p4() + preselLeptons[iL4].p4()).M()
                        if m_4l < 140.0:
                            failsHtoZZVeto = True
        
        if failsHtoZZVeto:
            return True
        
        self.h_Stat.Fill(13)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "H->ZZ*->4l veto", evtWeight)
        
        
        
        isSameFlavor_OS_FO = False
        for i in range(0, len(preselLeptons)):
            for j in range(i+1, len(preselLeptons)):
                if preselLeptons[i].pdgId == (-1 * preselLeptons[j].pdgId): # same-flavor opposite sign
                    isSameFlavor_OS_FO = True
                    break
        
        met_LD_cut = 0.0;
        if    len(selJetsAK4) >= 4 :
            met_LD_cut = -1.; # MET LD cut not applied
        elif  isSameFlavor_OS_FO:
            met_LD_cut = 45.;
        else:
            met_LD_cut = 30.;
        
        if met_LD_cut > 0.0  and  met_LD < met_LD_cut:
            return True
        
        self.h_Stat.Fill(14)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "met LD", evtWeight)
        
        
        
        
        ## MEt filters cut 
        passMEtFilters = True
        for keyFilter in MEtFiltersToApply:
            if isDEBUG and printLevel >= 6:
                print "filter: ",keyFilter,",  ",MEtFiltersToApply[keyFilter],", data: ",MEtFiltersToApply[keyFilter]["forData"], ", mc: ",MEtFiltersToApply[keyFilter]["forMC"], ",  value: ",getattr(event,keyFilter)
            if isMC and MEtFiltersToApply[keyFilter]["forMC"]:
                if not getattr(event,keyFilter):
                    passMEtFilters = False
                    break
            elif (not isMC) and MEtFiltersToApply[keyFilter]["forData"]:
                if not getattr(event,keyFilter):
                    passMEtFilters = False
                    break    
        if isDEBUG and printLevel >= 6: 
            print "passMEtFilters: ", passMEtFilters

        if not passMEtFilters:
            return True
        
        self.h_Stat.Fill(16)
        cutFlowHistogram(self.h_Stat1,self.h_Stat1_wtd, "MEt filters", evtWeight)
        
        self.nEventsSelected     += 1
        self.nEventsSelected_Wtd += evtWeight
        self.h_Info.Fill(self.h_Info_bins["nEventsSelected"])
        self.h_Info.Fill(self.h_Info_bins["nEventsSelected_Wtd"], evtWeight)
        self.ofEventNumber_SelectedEvents_Final.write("%d:%d:%d\n" % (runNumber,lumiBlock,eventNumber))
        
        # fill event weight histogram
        self.h_evtWeight_genWeight.Fill(genWeight)
        self.h_evtWeight_genWeight_sign.Fill(math.copysign(1, genWeight))
        self.h_evtWeight_L1PreFiringWeight.Fill(L1PreFiringWeight)
        self.h_evtWeight_LHEScaleWeight.Fill(LHEScaleWeight)
        self.h_evtWeight_PSWeight.Fill(PSWeight)
        self.h_evtWeight_puWeight.Fill(get_puWeight)
        self.h_evtWeight_lumiScale.Fill(lumiScale)
        #
        self.h_evtWeight_sf_leptonID.Fill(sf_leptonID)
        self.h_evtWeight_sf_leptonTrig.Fill(sf_leptonTrig)
        self.h_evtWeight_sf_btag_shape.Fill(sf_btag_shape)
        self.h_evtWeight.Fill(evtWeight)
        
        
        if isDEBUG and printLevel >= 5:
            printLeptonsCollection("\ncleanedMuons",cleanedMuons)
            printLeptonsCollection("\npreselMuons",preselMuons)
            printLeptonsCollection("\ntightMuons",tightMuons)
            printLeptonsCollection("\nelectrons",electrons)
            printLeptonsCollection("\ncleanedElectrons",cleanedElectrons)
            printLeptonsCollection("\npreselElectrons",preselElectrons)
            printLeptonsCollection("\ntightElectrons",tightElectrons)
            printLeptonsCollection("\npreselLeptons",preselLeptons)
            printLeptonsCollection("\nselLeptons",selLeptons)
            #
            printLeptonsCollection("\ntaus",taus, "Tau")
            printLeptonsCollection("\ncleanedTaus",cleanedTaus, "Tau")
            printLeptonsCollection("\npreselTaus",preselTaus, "Tau")
            printLeptonsCollection("\ntightTaus",tightTaus, "Tau")
            #
            printLeptonsCollection("\njetsAK4",jetsAK4, "Jet")
            printLeptonsCollection("\ncleanedJetsAK4",cleanedJetsAK4, "Jet")
            printLeptonsCollection("\nselJetsAK4",selJetsAK4, "Jet") 
            printLeptonsCollection("\nselJetsBtagLoose",selJetsBtagLoose, "Jet")
            printLeptonsCollection("\nselJetsBtagMedium",selJetsBtagMedium, "Jet")

        if isDEBUG and printLevel >= 1:
            evtWeight_inclusive = (math.copysign(1, genWeight) * L1PreFiringWeight * LHEScaleWeight * PSWeight * get_puWeight * lumiScale)
            evtWeight_dataMCCor = (sf_leptonID * sf_leptonTrig * sf_btag_shape)
            print "EventWeight:: \n genWt (",genWeight,") \t\t",math.copysign(1, genWeight),
            print " L1PreFiringWeight \t",L1PreFiringWeight
            print " LHEScaleWeight \t",LHEScaleWeight
            print " PSWeight \t\t",PSWeight
            print " get_puWeight \t\t",get_puWeight
            print " lumiScale \t\t",lumiScale
            print " inclusive wt \t\t", evtWeight_inclusive
            print " sf_leptonID \t\t",sf_leptonID
            print " sf_leptonTrig \t\t",sf_leptonTrig
            print " sf_leptonID*Trig \t", (sf_leptonID * sf_leptonTrig)
            print " sf_btag_shape \t\t",sf_btag_shape
            #print " sf_btag_L \t\t",sf_btag_L
            #print " sf_btag_M \t\t",sf_btag_M
            #print " sf_btag_LorM \t\t",sf_btag_LorM
            print " dataMCCor \t\t",evtWeight_dataMCCor
            print "evtWeight \t\t",evtWeight
        
        return True   




if __name__ == "__main__":
    start_time = time.time()
    print "\nanaHHTo4W_3l_1qq_gen.py: datetime: {} start_time {}, ".format(datetime.datetime.now(), start_time)
    
    print "anaHHTo4W_3l_1qq_gen.py:  commandline arguments: ",sys.argv
    if len(sys.argv) != 2:
        print "anaHHTo4W_3l_1qq_gen.py: 1 command line argument (anaConfir.json) is expected to run anaHHTo4W_3l_1qq_gen.py  ***** ERROR ****"
        exit(0)

    analysisSettings = None
    with open(sys.argv[1]) as fAnaSetting:
        analysisSettings = json.load(fAnaSetting)
        
    #analysisSettings[""]
    # = analysisSettings[""]
    
    ERA                           = analysisSettings["era"]
    isMC                          = True if analysisSettings["type"] == "mc" else False
    
    process_name_specific         = analysisSettings["process_name_specific"]
    sample_category               = analysisSettings["sample_category"]
    sample_use_it                 = True if analysisSettings["use_it"] in ["True", "true"] else False
    process_xsection              = analysisSettings["xsection"]
    NanoAOD_PostProc_Files        = analysisSettings["NanoAOD_PostProc"]
    nof_events_NanoAOD_PostProc   = analysisSettings["nof_events_NanoAOD_PostProc"]
    output_dir                    = analysisSettings["output_dir"]
    
    ElectronID_sel                = analysisSettings["ElectronID_sel"]
    ElectronID_presel             = ElectronID_sel.split("_WP")[0] + "_WPL"
    ElectronID_mvaTTH_sel         = analysisSettings["ElectronID_mvaTTH_sel"]

    output_histFileName           = "%s/hist_stage1_%s_%s.root" % (output_dir,process_name_specific,ElectronID_sel)
    output_histDirName            = "%s" % (sample_category)
    
    
    if not sample_use_it:
        print "Sample %s,  use_it: False" % process_name_specific
        exit(0)
    if len(NanoAOD_PostProc_Files) == 0:
        print "No input NanoAOD_PostProc_Files \t\t\t ******* ERROR ********"
        exit(0)
    if nof_events_NanoAOD_PostProc < 1:
        print "No nof_events_NanoAOD_PostProc: %d \t\t\t ******* ERROR ********" % nof_events_NanoAOD_PostProc
        exit(0)
    if process_xsection <= 0.0:
        print "No process_xsection: %g \t\t\t ******* ERROR ********" % process_xsection
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
    
    
    era_luminosity = None
    
    MuonID_presel = "Muon_looseId" # WP: Muon_looseId, Muon_mediumId, Muon_tightId
    MuonID_sel    = "Muon_mediumId" # WP: Muon_looseId, Muon_mediumId, Muon_tightId
    MuonID_sel_lowPt = MuonID_sel + "_lowPt"
    
    jmeCorrections = None
    
    if ERA == 2017:
        era_luminosity  = lumi_2017
        
        jetBtagWPLoose  = jetBtagWPLoose_2017
        jetBtagWPMedium = jetBtagWPMedium_2017

        jmeCorrections = createJMECorrector(isMC=isMC, dataYear=2017, redojec=False, jetType = "AK4PFchs", applySmearing=True) 
        
        MEtFiltersToApply = MEtFiltersToApply_2017
        
        MuonSFDetails = {
            "Muon_looseId": {
                "file":      "data/leptonSF/muonSF/2017/RunBCDEF_SF_ID.root",
                "histogram": "NUM_LooseID_DEN_genTracks_pt_abseta",
                "xaxis":     "pt",
                "yaxis":     "abseta",
            },
            "Muon_mediumId": {
                "file":      "data/leptonSF/muonSF/2017/RunBCDEF_SF_ID.root",
                "histogram": "NUM_MediumID_DEN_genTracks_pt_abseta",
                "xaxis":     "pt",
                "yaxis":     "abseta",
            },
            "Muon_tightId": {
                "file":      "data/leptonSF/muonSF/2017/RunBCDEF_SF_ID.root",
                "histogram": "NUM_TightID_DEN_genTracks_pt_abseta",
                "xaxis":     "pt",
                "yaxis":     "abseta",
            },
            #
             "Muon_looseId_lowPt": {
                "file":      "data/leptonSF/muonSF/2017/RunBCDEF_SF_ID_JPsi.root",
                "histogram": "NUM_LooseID_DEN_genTracks_pt_abseta",
                "xaxis":     "pt",
                "yaxis":     "abseta",
            },
            "Muon_mediumId_lowPt": {
                "file":      "data/leptonSF/muonSF/2017/RunBCDEF_SF_ID_JPsi.root",
                "histogram": "NUM_MediumID_DEN_genTracks_pt_abseta",
                "xaxis":     "pt",
                "yaxis":     "abseta",
            },
            "Muon_tightId_lowPt": {
                "file":      "data/leptonSF/muonSF/2017/RunBCDEF_SF_ID_JPsi.root",
                "histogram": "NUM_TightID_DEN_genTracks_pt_abseta",
                "xaxis":     "pt",
                "yaxis":     "abseta",
            },
            ######
            "Muon_triggerSF_1mu": {
                "file":      "data/triggerSF/muonTrigSF/2017/EfficienciesAndSF_RunBtoF_Nov17Nov2017.root",
                "histogram": "IsoMu27_PtEtaBins/pt_abseta_ratio",
                "xaxis":     "pt",
                "yaxis":     "abseta",
            },
        }
        
        ElectronSFDetails = {
            "Electron_passingRECO_lowEt": {
                "file":      "data/leptonSF/electronSF/2017/egammaEffi.txt_EGM2D_runBCDEF_passingRECO_lowEt.root",
                "histogram": "EGamma_SF2D",
                "xaxis":     "eta",
                "yaxis":     "pt",
            },
            "Electron_passingRECO": {
                "file":      "data/leptonSF/electronSF/2017/egammaEffi.txt_EGM2D_runBCDEF_passingRECO.root",
                "histogram": "EGamma_SF2D",
                "xaxis":     "eta",
                "yaxis":     "pt",
            },
            ##
            "Electron_mvaFall17V2Iso_WP90": {
                "file":      "data/leptonSF/electronSF/2017/2017_ElectronMVA90.root",
                "histogram": "EGamma_SF2D",
                "xaxis":     "eta",
                "yaxis":     "pt",
            },
            "Electron_mvaFall17V2Iso_WP80": {
                "file":      "data/leptonSF/electronSF/2017/2017_ElectronMVA80.root",
                "histogram": "EGamma_SF2D",
                "xaxis":     "eta",
                "yaxis":     "pt",
            },
            "Electron_mvaFall17V2noIso_WP90": {
                "file":      "data/leptonSF/electronSF/2017/2017_ElectronMVA90noiso.root",
                "histogram": "EGamma_SF2D",
                "xaxis":     "eta",
                "yaxis":     "pt",
            },
            "Electron_mvaFall17V2noIso_WP80": {
                "file":      "data/leptonSF/electronSF/2017/2017_ElectronMVA80noiso.root",
                "histogram": "EGamma_SF2D",
                "xaxis":     "eta",
                "yaxis":     "pt",
            },
            ######
            "Electron_triggerSF_evtWt": {
                "sf_evtWt":   0.991
            }
            
        }
        ElectronSFDetails["Electron_mvaFall17V2Iso_WPL"]   = ElectronSFDetails["Electron_mvaFall17V2Iso_WP90"]
        ElectronSFDetails["Electron_mvaFall17V2noIso_WPL"] = ElectronSFDetails["Electron_mvaFall17V2noIso_WP90"]
        
    
    print "ElectronSFDetails:: ",json.dumps(ElectronSFDetails, sort_keys = False, indent = 4)
    
    sample_lumiScaleToUse = era_luminosity * process_xsection / nof_events_NanoAOD_PostProc
    
    print "anaHHTo4W_3l_1qq_gen:: Settings"
    print "pwd: ",os.getcwd()
    print "ERA %d, lumi: %g" % (ERA, era_luminosity)
    print "Sample: {}, category: {}, isMc: {}, use_it: {}, \t xsection: {}, nEvents: {}, lumiScale: {} ".format(\
        process_name_specific,sample_category,isMC,sample_use_it, \
        process_xsection,nof_events_NanoAOD_PostProc, sample_lumiScaleToUse)
    print "NanoAOD_PostProc_Files: nTrees {}: {}".format(len(NanoAOD_PostProc_Files),NanoAOD_PostProc_Files)
    print "output_dir: %s, output_histFileName: %s, output_histDirName: %s" % (output_dir, output_histFileName, output_histDirName)
    
    print "\nElectronID_presel: \t\t",  ElectronID_presel
    print "ElectronID_sel: \t\t",       ElectronID_sel
    print "ElectronID_mvaTTH_sel: \t",  ElectronID_mvaTTH_sel
    print "ElectronSFDetails: {}: {}".format("Electron_passingRECO_lowEt",  ElectronSFDetails["Electron_passingRECO_lowEt"])
    print "ElectronSFDetails: {}: {}".format("Electron_passingRECO",        ElectronSFDetails["Electron_passingRECO"])
    print "ElectronSFDetails: {}: {}".format(ElectronID_sel,                ElectronSFDetails[ElectronID_sel])
    print "ElectronSFDetails: {}: {}".format("Electron_triggerSF_evtWt",    ElectronSFDetails["Electron_triggerSF_evtWt"])
    
    print "\nMuonID_presel: ",MuonID_presel
    print "MuonID_sel: ",MuonID_sel
    print "MuonSFDetails: {}: {}".format(MuonID_sel_lowPt,       MuonSFDetails[MuonID_sel_lowPt])
    print "MuonSFDetails: {}: {}".format(MuonID_sel,             MuonSFDetails[MuonID_sel])
    print "MuonSFDetails: {}: {}".format("Muon_triggerSF_1mu",   MuonSFDetails["Muon_triggerSF_1mu"])
    
    print "\njetBtagWPLoose: ",jetBtagWPLoose
    print "jetBtagWPMedium: ",jetBtagWPMedium
    print "MEtFiltersToApply: ",json.dumps(MEtFiltersToApply, sort_keys = False, indent = 4)
    
    
    
    os.system("mkdir -p %s" % output_dir)
    
    
    
    preselection=""
    
    #p=PostProcessor(".",files,cut=preselection,branchsel=None,modules=[jmeCorrections(), ExampleAnalysis()],noOut=False,histFileName=sHistFileName,histDirName="plots")
    #p=PostProcessor(".",files,cut=preselection,branchsel=None,modules=[ExampleAnalysis()],noOut=True,histFileName=sHistFileName,histDirName="plots",maxEntries=10000)
    #p=PostProcessor(".",files,cut=preselection,branchsel=None,modules=[ExampleAnalysis()],noOut=True,histFileName=sHistFileName,histDirName="plots")
    
    #p=PostProcessor(".", NanoAOD_PostProc_Files, cut="", branchsel=None, modules=[ExampleAnalysis()], noOut=True, histFileName=output_histFileName, histDirName=output_histDirName, maxEntries=10000)
    p=PostProcessor(".", NanoAOD_PostProc_Files, cut="", branchsel=None, modules=[ExampleAnalysis()], noOut=True, histFileName=output_histFileName, histDirName=output_histDirName)
    
    
    p.run()
    
    time_now = time.time()
    #print "anaHHTo4W_3l_1qq_gen.py:  time_now {}".format(time_now)
    exec_time = time_now - start_time
    #print "anaHHTo4W_3l_1qq_gen.py:  exec_now {}".format(exec_time)
    print "anaHHTo4W_3l_1qq_gen.py:  datetime: {}, \t execution time: {}".format(datetime.datetime.now(), str(datetime.timedelta(seconds=exec_time)))
