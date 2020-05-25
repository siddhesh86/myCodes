#!/usr/bin/env python
import os, sys
import itertools
import collections

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor


from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection, Event
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module


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



def cutFlowHistogram(histo, sCut):
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

    x = histo.GetBinCenter(cutBin)
    histo.Fill(x)
    return


def printCutFlowTable(histo):
    if not histo.GetNbinsX() >= 1:
        print "def cutFlowHistogram():: histo not defined \t *** ERROR *** \nTerminating\n"
        exit ()

    print "Cut-flow table:: \n entries \t cuts"
    for i in range(1,histo.GetNbinsX()+1):
        if histo.GetXaxis().GetBinLabel(i) == "":
            break

        print "%10d  %s" % (histo.GetBinContent(i), histo.GetXaxis().GetBinLabel(i))

    return


        
class ExampleAnalysis(Module):
    def __init__(self):
        self.writeHistFile=True
  
    
    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)

        self.h_Stat=ROOT.TH1F('Stat',   'Stat',   101, -0.5, 100.5)
        self.addObject(self.h_Stat )

        self.h_Stat1=ROOT.TH1F('Stat1',   'Stat1',   101, -0.5, 100.5)
        self.addObject(self.h_Stat1 )

        self.h_nEle=ROOT.TH1F('nElectron',   'nElectron',   21, -0.5, 20.5)
        self.addObject(self.h_nEle )

        self.h_nEleGenMatch=ROOT.TH1F('nElectronGenMatch',   'nElectronGenMatch',   21, -0.5, 20.5)
        self.addObject(self.h_nEleGenMatch )

        self.h_mvaFall17V2Iso_WPL_EB=ROOT.TH1F('mvaFall17V2Iso_WPL_EB',   'mvaFall17V2Iso_WPL_EB',   100, -1.2, 1.2)
        self.addObject(self.h_mvaFall17V2Iso_WPL_EB )

        self.h_mvaFall17V2Iso_WP90_EB=ROOT.TH1F('mvaFall17V2Iso_WP90_EB',   'mvaFall17V2Iso_WP90_EB',   100, -1.2, 1.2)
        self.addObject(self.h_mvaFall17V2Iso_WP90_EB )
        
        self.h_mvaFall17V2Iso_WP80_EB=ROOT.TH1F('mvaFall17V2Iso_WP80_EB',   'mvaFall17V2Iso_WP80_EB',   100, -1.2, 1.2)
        self.addObject(self.h_mvaFall17V2Iso_WP80_EB )
        #
        self.h_mvaFall17V2Iso_WPL_EE=ROOT.TH1F('mvaFall17V2Iso_WPL_EE',   'mvaFall17V2Iso_WPL_EE',   100, -1.2, 1.2)
        self.addObject(self.h_mvaFall17V2Iso_WPL_EE )

        self.h_mvaFall17V2Iso_WP90_EE=ROOT.TH1F('mvaFall17V2Iso_WP90_EE',   'mvaFall17V2Iso_WP90_EE',   100, -1.2, 1.2)
        self.addObject(self.h_mvaFall17V2Iso_WP90_EE )
        
        self.h_mvaFall17V2Iso_WP80_EE=ROOT.TH1F('mvaFall17V2Iso_WP80_EE',   'mvaFall17V2Iso_WP80_EE',   100, -1.2, 1.2)
        self.addObject(self.h_mvaFall17V2Iso_WP80_EE )
        #        
        #
        self.h_mvaFall17V2noIso_WPL_EB=ROOT.TH1F('mvaFall17V2noIso_WPL_EB',   'mvaFall17V2noIso_WPL_EB',   100, -1.2, 1.2)
        self.addObject(self.h_mvaFall17V2noIso_WPL_EB )

        self.h_mvaFall17V2noIso_WP90_EB=ROOT.TH1F('mvaFall17V2noIso_WP90_EB',   'mvaFall17V2noIso_WP90_EB',   100, -1.2, 1.2)
        self.addObject(self.h_mvaFall17V2noIso_WP90_EB )
        
        self.h_mvaFall17V2noIso_WP80_EB=ROOT.TH1F('mvaFall17V2noIso_WP80_EB',   'mvaFall17V2noIso_WP80_EB',   100, -1.2, 1.2)
        self.addObject(self.h_mvaFall17V2noIso_WP80_EB )
        #
        self.h_mvaFall17V2noIso_WPL_EE=ROOT.TH1F('mvaFall17V2noIso_WPL_EE',   'mvaFall17V2noIso_WPL_EE',   100, -1.2, 1.2)
        self.addObject(self.h_mvaFall17V2noIso_WPL_EE )

        self.h_mvaFall17V2noIso_WP90_EE=ROOT.TH1F('mvaFall17V2noIso_WP90_EE',   'mvaFall17V2noIso_WP90_EE',   100, -1.2, 1.2)
        self.addObject(self.h_mvaFall17V2noIso_WP90_EE )
        
        self.h_mvaFall17V2noIso_WP80_EE=ROOT.TH1F('mvaFall17V2noIso_WP80_EE',   'mvaFall17V2noIso_WP80_EE',   100, -1.2, 1.2)
        self.addObject(self.h_mvaFall17V2noIso_WP80_EE )
        #
        #
        self.h_sieie_AfterCutBasedTight_EB=ROOT.TH1F('h_sieie_AfterCutBasedTight_EB',   'h_sieie_AfterCutBasedTight_EB',   100, -0.05, 0.05)
        self.addObject(self.h_sieie_AfterCutBasedTight_EB )
        
        self.h_deltaEtaSC_AfterCutBasedTight_EB=ROOT.TH1F('h_deltaEtaSC_AfterCutBasedTight_EB',   'h_deltaEtaSC_AfterCutBasedTight_EB',   100, -0.01, 0.01)
        self.addObject(self.h_deltaEtaSC_AfterCutBasedTight_EB )

        self.h_hoe_AfterCutBasedTight_EB=ROOT.TH1F('h_hoe_AfterCutBasedTight_EB',   'h_hoe_AfterCutBasedTight_EB',   100, 0, 0.5)
        self.addObject(self.h_hoe_AfterCutBasedTight_EB )
        
        self.h_pfRelIso03_all_AfterCutBasedTight_EB=ROOT.TH1F('h_pfRelIso03_all_AfterCutBasedTight_EB',   'h_pfRelIso03_all_AfterCutBasedTight_EB',   100, 0,0.45)
        self.addObject(self.h_pfRelIso03_all_AfterCutBasedTight_EB )
        
        self.h_jetRelIso_AfterCutBasedTight_EB=ROOT.TH1F('h_jetRelIso_AfterCutBasedTight_EB',   'h_jetRelIso_AfterCutBasedTight_EB',   100, -1,3.0)
        self.addObject(self.h_jetRelIso_AfterCutBasedTight_EB )

        self.h_eInvMinusPInv_AfterCutBasedTight_EB=ROOT.TH1F('h_eInvMinusPInv_AfterCutBasedTight_EB',   'h_eInvMinusPInv_AfterCutBasedTight_EB',   100, -0.4,0.4)
        self.addObject(self.h_eInvMinusPInv_AfterCutBasedTight_EB )
        
        self.h_lostHits_AfterCutBasedTight_EB=ROOT.TH1F('h_lostHits_AfterCutBasedTight_EB',   'h_lostHits_AfterCutBasedTight_EB',   21, -0.5,20.5)
        self.addObject(self.h_lostHits_AfterCutBasedTight_EB )

        self.h_convVeto_AfterCutBasedTight_EB=ROOT.TH1F('h_convVeto_AfterCutBasedTight_EB',   'h_convVeto_AfterCutBasedTight_EB',   3, -0.5,2.5)
        self.addObject(self.h_convVeto_AfterCutBasedTight_EB )
        
        self.h_dxy_AfterCutBasedTight_EB=ROOT.TH1F('h_dxy_AfterCutBasedTight_EB',   'h_dxy_AfterCutBasedTight_EB',   100, 0, 0.25)
        self.addObject(self.h_dxy_AfterCutBasedTight_EB )

        self.h_dz_AfterCutBasedTight_EB=ROOT.TH1F('h_dz_AfterCutBasedTight_EB',   'h_dz_AfterCutBasedTight_EB',   100, 0, 0.25)
        self.addObject(self.h_dz_AfterCutBasedTight_EB )
        
        self.h_sip3d_AfterCutBasedTight_EB=ROOT.TH1F('h_sip3d_AfterCutBasedTight_EB',   'h_sip3d_AfterCutBasedTight_EB',   100, -15, 15)
        self.addObject(self.h_sip3d_AfterCutBasedTight_EB )
        #
        self.h_sieie_AfterMvaFall17V2Iso80_EB=ROOT.TH1F('h_sieie_AfterMvaFall17V2Iso80_EB',   'h_sieie_AfterMvaFall17V2Iso80_EB',   100, -0.05, 0.05)
        self.addObject(self.h_sieie_AfterMvaFall17V2Iso80_EB )
        
        self.h_deltaEtaSC_AfterMvaFall17V2Iso80_EB=ROOT.TH1F('h_deltaEtaSC_AfterMvaFall17V2Iso80_EB',   'h_deltaEtaSC_AfterMvaFall17V2Iso80_EB',   100, -0.01, 0.01)
        self.addObject(self.h_deltaEtaSC_AfterMvaFall17V2Iso80_EB )

        self.h_hoe_AfterMvaFall17V2Iso80_EB=ROOT.TH1F('h_hoe_AfterMvaFall17V2Iso80_EB',   'h_hoe_AfterMvaFall17V2Iso80_EB',   100, 0, 0.5)
        self.addObject(self.h_hoe_AfterMvaFall17V2Iso80_EB )
        
        self.h_pfRelIso03_all_AfterMvaFall17V2Iso80_EB=ROOT.TH1F('h_pfRelIso03_all_AfterMvaFall17V2Iso80_EB',   'h_pfRelIso03_all_AfterMvaFall17V2Iso80_EB',   100, 0,0.45)
        self.addObject(self.h_pfRelIso03_all_AfterMvaFall17V2Iso80_EB )
        
        self.h_jetRelIso_AfterMvaFall17V2Iso80_EB=ROOT.TH1F('h_jetRelIso_AfterMvaFall17V2Iso80_EB',   'h_jetRelIso_AfterMvaFall17V2Iso80_EB',   100, -1,3.0)
        self.addObject(self.h_jetRelIso_AfterMvaFall17V2Iso80_EB )

        self.h_eInvMinusPInv_AfterMvaFall17V2Iso80_EB=ROOT.TH1F('h_eInvMinusPInv_AfterMvaFall17V2Iso80_EB',   'h_eInvMinusPInv_AfterMvaFall17V2Iso80_EB',   100, -0.4,0.4)
        self.addObject(self.h_eInvMinusPInv_AfterMvaFall17V2Iso80_EB )
        
        self.h_lostHits_AfterMvaFall17V2Iso80_EB=ROOT.TH1F('h_lostHits_AfterMvaFall17V2Iso80_EB',   'h_lostHits_AfterMvaFall17V2Iso80_EB',   21, -0.5,20.5)
        self.addObject(self.h_lostHits_AfterMvaFall17V2Iso80_EB )

        self.h_convVeto_AfterMvaFall17V2Iso80_EB=ROOT.TH1F('h_convVeto_AfterMvaFall17V2Iso80_EB',   'h_convVeto_AfterMvaFall17V2Iso80_EB',   3, -0.5,2.5)
        self.addObject(self.h_convVeto_AfterMvaFall17V2Iso80_EB )
        
        self.h_dxy_AfterMvaFall17V2Iso80_EB=ROOT.TH1F('h_dxy_AfterMvaFall17V2Iso80_EB',   'h_dxy_AfterMvaFall17V2Iso80_EB',   100, 0, 0.25)
        self.addObject(self.h_dxy_AfterMvaFall17V2Iso80_EB )

        self.h_dz_AfterMvaFall17V2Iso80_EB=ROOT.TH1F('h_dz_AfterMvaFall17V2Iso80_EB',   'h_dz_AfterMvaFall17V2Iso80_EB',   100, 0, 0.25)
        self.addObject(self.h_dz_AfterMvaFall17V2Iso80_EB )
        
        self.h_sip3d_AfterMvaFall17V2Iso80_EB=ROOT.TH1F('h_sip3d_AfterMvaFall17V2Iso80_EB',   'h_sip3d_AfterMvaFall17V2Iso80_EB',   100, -15, 15)
        self.addObject(self.h_sip3d_AfterMvaFall17V2Iso80_EB )
        #
        #
        self.h_sieie_AfterCutBasedTight_EE=ROOT.TH1F('h_sieie_AfterCutBasedTight_EE',   'h_sieie_AfterCutBasedTight_EE',   100, -0.05, 0.05)
        self.addObject(self.h_sieie_AfterCutBasedTight_EE )
        
        self.h_deltaEtaSC_AfterCutBasedTight_EE=ROOT.TH1F('h_deltaEtaSC_AfterCutBasedTight_EE',   'h_deltaEtaSC_AfterCutBasedTight_EE',   100, -0.01, 0.01)
        self.addObject(self.h_deltaEtaSC_AfterCutBasedTight_EE )

        self.h_hoe_AfterCutBasedTight_EE=ROOT.TH1F('h_hoe_AfterCutBasedTight_EE',   'h_hoe_AfterCutBasedTight_EE',   100, 0, 0.5)
        self.addObject(self.h_hoe_AfterCutBasedTight_EE )
        
        self.h_pfRelIso03_all_AfterCutBasedTight_EE=ROOT.TH1F('h_pfRelIso03_all_AfterCutBasedTight_EE',   'h_pfRelIso03_all_AfterCutBasedTight_EE',   100, 0,0.45)
        self.addObject(self.h_pfRelIso03_all_AfterCutBasedTight_EE )
        
        self.h_jetRelIso_AfterCutBasedTight_EE=ROOT.TH1F('h_jetRelIso_AfterCutBasedTight_EE',   'h_jetRelIso_AfterCutBasedTight_EE',   100, -1,3.0)
        self.addObject(self.h_jetRelIso_AfterCutBasedTight_EE )

        self.h_eInvMinusPInv_AfterCutBasedTight_EE=ROOT.TH1F('h_eInvMinusPInv_AfterCutBasedTight_EE',   'h_eInvMinusPInv_AfterCutBasedTight_EE',   100, -0.4,0.4)
        self.addObject(self.h_eInvMinusPInv_AfterCutBasedTight_EE )
        
        self.h_lostHits_AfterCutBasedTight_EE=ROOT.TH1F('h_lostHits_AfterCutBasedTight_EE',   'h_lostHits_AfterCutBasedTight_EE',   21, -0.5,20.5)
        self.addObject(self.h_lostHits_AfterCutBasedTight_EE )

        self.h_convVeto_AfterCutBasedTight_EE=ROOT.TH1F('h_convVeto_AfterCutBasedTight_EE',   'h_convVeto_AfterCutBasedTight_EE',   3, -0.5,2.5)
        self.addObject(self.h_convVeto_AfterCutBasedTight_EE )
        
        self.h_dxy_AfterCutBasedTight_EE=ROOT.TH1F('h_dxy_AfterCutBasedTight_EE',   'h_dxy_AfterCutBasedTight_EE',   100, 0, 0.25)
        self.addObject(self.h_dxy_AfterCutBasedTight_EE )

        self.h_dz_AfterCutBasedTight_EE=ROOT.TH1F('h_dz_AfterCutBasedTight_EE',   'h_dz_AfterCutBasedTight_EE',   100, 0, 0.25)
        self.addObject(self.h_dz_AfterCutBasedTight_EE )
        
        self.h_sip3d_AfterCutBasedTight_EE=ROOT.TH1F('h_sip3d_AfterCutBasedTight_EE',   'h_sip3d_AfterCutBasedTight_EE',   100, -15, 15)
        self.addObject(self.h_sip3d_AfterCutBasedTight_EE )
        #
        self.h_sieie_AfterMvaFall17V2Iso80_EE=ROOT.TH1F('h_sieie_AfterMvaFall17V2Iso80_EE',   'h_sieie_AfterMvaFall17V2Iso80_EE',   100, -0.05, 0.05)
        self.addObject(self.h_sieie_AfterMvaFall17V2Iso80_EE )
        
        self.h_deltaEtaSC_AfterMvaFall17V2Iso80_EE=ROOT.TH1F('h_deltaEtaSC_AfterMvaFall17V2Iso80_EE',   'h_deltaEtaSC_AfterMvaFall17V2Iso80_EE',   100, -0.01, 0.01)
        self.addObject(self.h_deltaEtaSC_AfterMvaFall17V2Iso80_EE )

        self.h_hoe_AfterMvaFall17V2Iso80_EE=ROOT.TH1F('h_hoe_AfterMvaFall17V2Iso80_EE',   'h_hoe_AfterMvaFall17V2Iso80_EE',   100, 0, 0.5)
        self.addObject(self.h_hoe_AfterMvaFall17V2Iso80_EE )
        
        self.h_pfRelIso03_all_AfterMvaFall17V2Iso80_EE=ROOT.TH1F('h_pfRelIso03_all_AfterMvaFall17V2Iso80_EE',   'h_pfRelIso03_all_AfterMvaFall17V2Iso80_EE',   100, 0,0.45)
        self.addObject(self.h_pfRelIso03_all_AfterMvaFall17V2Iso80_EE )
        
        self.h_jetRelIso_AfterMvaFall17V2Iso80_EE=ROOT.TH1F('h_jetRelIso_AfterMvaFall17V2Iso80_EE',   'h_jetRelIso_AfterMvaFall17V2Iso80_EE',   100, -1,3.0)
        self.addObject(self.h_jetRelIso_AfterMvaFall17V2Iso80_EE )

        self.h_eInvMinusPInv_AfterMvaFall17V2Iso80_EE=ROOT.TH1F('h_eInvMinusPInv_AfterMvaFall17V2Iso80_EE',   'h_eInvMinusPInv_AfterMvaFall17V2Iso80_EE',   100, -0.4,0.4)
        self.addObject(self.h_eInvMinusPInv_AfterMvaFall17V2Iso80_EE )
        
        self.h_lostHits_AfterMvaFall17V2Iso80_EE=ROOT.TH1F('h_lostHits_AfterMvaFall17V2Iso80_EE',   'h_lostHits_AfterMvaFall17V2Iso80_EE',   21, -0.5,20.5)
        self.addObject(self.h_lostHits_AfterMvaFall17V2Iso80_EE )

        self.h_convVeto_AfterMvaFall17V2Iso80_EE=ROOT.TH1F('h_convVeto_AfterMvaFall17V2Iso80_EE',   'h_convVeto_AfterMvaFall17V2Iso80_EE',   3, -0.5,2.5)
        self.addObject(self.h_convVeto_AfterMvaFall17V2Iso80_EE )
        
        self.h_dxy_AfterMvaFall17V2Iso80_EE=ROOT.TH1F('h_dxy_AfterMvaFall17V2Iso80_EE',   'h_dxy_AfterMvaFall17V2Iso80_EE',   100, 0, 0.25)
        self.addObject(self.h_dxy_AfterMvaFall17V2Iso80_EE )

        self.h_dz_AfterMvaFall17V2Iso80_EE=ROOT.TH1F('h_dz_AfterMvaFall17V2Iso80_EE',   'h_dz_AfterMvaFall17V2Iso80_EE',   100, 0, 0.25)
        self.addObject(self.h_dz_AfterMvaFall17V2Iso80_EE )
        
        self.h_sip3d_AfterMvaFall17V2Iso80_EE=ROOT.TH1F('h_sip3d_AfterMvaFall17V2Iso80_EE',   'h_sip3d_AfterMvaFall17V2Iso80_EE',   100, -15, 15)
        self.addObject(self.h_sip3d_AfterMvaFall17V2Iso80_EE )

      
            

    def endJob(self):
        print "\nendJob()"
        if self.h_Stat1:
            print "nendJob():: printCutFlowTable::"
            printCutFlowTable(self.h_Stat1)
            
        Module.endJob(self)

            

    def analyze(self, event):
        #run = Collection(event, "run","run")
        #lumi = Collection(event, "luminosityBlock","luminosityBlock")
        #eventNumber  = Collection(event, "event","event")
        #run = Event()
        #runNumber = readBranch(inputTree,"run")
        
        genParts = Collection(event, "GenPart")

        electrons = Collection(event, "Electron")
        #eventSum = ROOT.TLorentzVector()

        #print "\n\n run:",run.__len__(), ", lumi:",lumi, ", event:",eventNumber
        #print "\n\n run:",run.__getitem__(0), ", lumi:",lumi, ", event:",eventNumber
        #print "\n\n event:"

        #stoge gen particle index into dictionary to get genParticle family tree
        genPartFamily = collections.OrderedDict()    # { idxPart: [idxDaughter0, idxDaughter1, ..], }            

        self.h_Stat.Fill(0)

        cutFlowHistogram(self.h_Stat1, "all")
        
        for iGenPart in range(0,len(genParts)):
            genPart = genParts[iGenPart]
            #print "genPart %d: pt %f, eta %f, phi %f, m %f,  pdgId %d, genPartIdxMother %d, status %d, statusFlags %d" % (iGenPart, genPart.pt, genPart.eta, genPart.phi, genPart.mass, genPart.pdgId, genPart.genPartIdxMother, genPart.status, genPart.statusFlags)
            
            if genPart.genPartIdxMother < 0:
                continue
            
            if not genPart.genPartIdxMother in genPartFamily:
                genPartFamily[genPart.genPartIdxMother] = [iGenPart]
            else:
                genPartFamily[genPart.genPartIdxMother].append(iGenPart)

        '''
        print "\n\n genPartFamily:\n"        
        for key, value in genPartFamily.items():
            print "key:",key, ",  value:",value
        '''
        
        firstFamilyMember = list(genPartFamily.keys())[0]
        familyTree =  createTree(genPartFamily, firstFamilyMember)
        #print "\n\n printFamilyTree: \n"
        #printFamilyTree(genParts, familyTree)

        # tag HH->4W -> 1lnu 3qq
        idxGenH = collections.OrderedDict()    # { 'iH0': idxH0,  'iH1': idxH1}
        idxGenWFromHH = collections.OrderedDict()    # { 'iH0': [idxD1, idxD2],  'iH1': [idxD1, idxD2]}
        decayModeGenWFromHH = collections.OrderedDict()    # { 'iH0': ['D1 decay mode', 'D2 decay mode'],  'iH1': ['D1 decay mode', 'D2 decay mode']}
        sWDecayModeLeptonic = 'WDecayModeLeptonic'
        sWDecayModeHadronic = 'WDecayModeHadronic'
        
        pdgId_EleMu = [11, 12, 13, 14]
        
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
                iH += 1

        '''        
        print "\nlen(idxGenH):",len(idxGenH), ", idxGenH:",idxGenH
        print "\nlen(idxGenWFromHH):",len(idxGenWFromHH), ", idxGenWFromHH:",idxGenWFromHH
        print "\nlen(decayModeGenWFromHH):",len(decayModeGenWFromHH), ", decayModeGenWFromHH:",decayModeGenWFromHH        
        '''

        # proceed with events with 2 Higgs
        if not len(idxGenH) == 2 or not len(idxGenWFromHH) == 2:
            return True
        self.h_Stat.Fill(1)
        cutFlowHistogram(self.h_Stat1, "2 genH")


        ngenWFromHH = 0
        ngenWFromHH_DMLeptonic = 0
        idxWFromHH_DMLeptonic = []
        for iH, idxWsFromHH in idxGenWFromHH.items():
            for iW in range(0, len(idxWsFromHH)):
                idxWFromHH = idxWsFromHH[iW]
                #print "\niH:",iH,", daughter: ",daughter,", (",genParts[daughter].pdgId,")"
                if abs(genParts[idxWFromHH].pdgId) == 24:
                    ngenWFromHH += 1
                if decayModeGenWFromHH[iH][iW] == sWDecayModeLeptonic:
                    ngenWFromHH_DMLeptonic += 1
                    idxWFromHH_DMLeptonic.append(idxWFromHH)
                    

        #print "\nngenWFromHH: ",ngenWFromHH, ",  ngenWFromHH_DMLeptonic:",ngenWFromHH_DMLeptonic
        # HH->4W events
        if not ngenWFromHH == 4:
            return True
        self.h_Stat.Fill(2)
        cutFlowHistogram(self.h_Stat1, "genHH->4W")
        
        if not ngenWFromHH_DMLeptonic == 1:
            return True
        self.h_Stat.Fill(3)
        cutFlowHistogram(self.h_Stat1, "genHH->4W -> 1l_3qq")
        

        #print "\nPrint WFromHH DMLeptonic Decay chain:"
        firstFamilyMember1 = idxWFromHH_DMLeptonic[0]
        familyTree1 =  createTree(genPartFamily, firstFamilyMember1)
        #printFamilyTree(genParts, familyTree1)

        # get idx of final state particles in W decay chain
        idxFamilyTreeFinalMembers = getFamilyTreeFinalMembers(genParts, familyTree1)
        #print "familyTreeFinalMembers: ",idxFamilyTreeFinalMembers
        for idxFinalMember in idxFamilyTreeFinalMembers:
            if abs(genParts[idxFinalMember].pdgId) in [11, 13]:
                idxGenLepFromHHTo4W_1l_3qq = idxFinalMember

        #print "idxGenLepFromHHTo4W_1l_3qq:",idxGenLepFromHHTo4W_1l_3qq,", pdgid:",genParts[idxGenLepFromHHTo4W_1l_3qq].pdgId,", motherIdx:",genParts[idxGenLepFromHHTo4W_1l_3qq].genPartIdxMother

        if not abs(genParts[idxGenLepFromHHTo4W_1l_3qq].pdgId) == 11:
            return True
        self.h_Stat.Fill(4)

        if not (genParts[idxGenLepFromHHTo4W_1l_3qq].eta <= 2.5 and genParts[idxGenLepFromHHTo4W_1l_3qq].pt > 10.0):
            return True
        self.h_Stat.Fill(5)

        nEleToRec = 1
        etaECALBarrel = 1.479

        if genParts[idxGenLepFromHHTo4W_1l_3qq].eta <= etaECALBarrel:
            self.h_Stat.Fill(6)
        else:
            self.h_Stat.Fill(7)

            
        LVGenLepFromHHTo4W_1l_3qq = genParts[idxGenLepFromHHTo4W_1l_3qq].p4()
        genLepFromHHTo4W_1l_3qq = genParts[idxGenLepFromHHTo4W_1l_3qq]


        self.h_nEle.Fill(len(electrons))
        nEleGenMatch = 0
        nEleGenMatch_EB = 0
        nEleGenMatch_EE = 0
        #
        nEleGenMatch_mvaFall17V2Iso_WPL_EB  = 0
        nEleGenMatch_mvaFall17V2Iso_WP90_EB = 0
        nEleGenMatch_mvaFall17V2Iso_WP80_EB = 0
        nEleGenMatch_mvaFall17V2noIso_WPL_EB  = 0
        nEleGenMatch_mvaFall17V2noIso_WP90_EB = 0
        nEleGenMatch_mvaFall17V2noIso_WP80_EB = 0
        #
        nEleGenMatch_mvaFall17V2Iso_WPL_EE  = 0
        nEleGenMatch_mvaFall17V2Iso_WP90_EE = 0
        nEleGenMatch_mvaFall17V2Iso_WP80_EE = 0
        nEleGenMatch_mvaFall17V2noIso_WPL_EE  = 0
        nEleGenMatch_mvaFall17V2noIso_WP90_EE = 0
        nEleGenMatch_mvaFall17V2noIso_WP80_EE = 0
        #
        #
        nEleGenMatch_cutBasedFail_EB = 0
        nEleGenMatch_cutBasedVeto_EB = 0
        nEleGenMatch_cutBasedLoose_EB = 0
        nEleGenMatch_cutBasedMedium_EB = 0
        nEleGenMatch_cutBasedTight_EB = 0
        #
        nEleGenMatch_cutBasedFail_EE = 0
        nEleGenMatch_cutBasedVeto_EE = 0
        nEleGenMatch_cutBasedLoose_EE = 0
        nEleGenMatch_cutBasedMedium_EE = 0
        nEleGenMatch_cutBasedTight_EE = 0
        
        
        for iL in range(0, len(electrons)):
            lep = electrons[iL]
            #print "iL: ",iL, ", pT:",lep.pt
            if not lep.DeltaR(genLepFromHHTo4W_1l_3qq) < 0.3:
                continue
            nEleGenMatch += 1

            # considered high pT GenMatched lepton only
            if nEleGenMatch > 1:
                continue

            
            if lep.eta <= etaECALBarrel:
                nEleGenMatch_EB += 1
                if lep.mvaFall17V2Iso_WPL:
                    nEleGenMatch_mvaFall17V2Iso_WPL_EB += 1
                    self.h_mvaFall17V2Iso_WPL_EB.Fill(lep.mvaFall17V2Iso)

                if lep.mvaFall17V2Iso_WP90:
                    nEleGenMatch_mvaFall17V2Iso_WP90_EB += 1
                    self.h_mvaFall17V2Iso_WP90_EB.Fill(lep.mvaFall17V2Iso)

                if lep.mvaFall17V2Iso_WP80:
                    nEleGenMatch_mvaFall17V2Iso_WP80_EB += 1
                    self.h_mvaFall17V2Iso_WP80_EB.Fill(lep.mvaFall17V2Iso)
                #
                if lep.mvaFall17V2noIso_WPL:
                    nEleGenMatch_mvaFall17V2noIso_WPL_EB += 1
                    self.h_mvaFall17V2noIso_WPL_EB.Fill(lep.mvaFall17V2noIso)
                if lep.mvaFall17V2noIso_WP90:
                    nEleGenMatch_mvaFall17V2noIso_WP90_EB += 1
                    self.h_mvaFall17V2noIso_WP90_EB.Fill(lep.mvaFall17V2noIso)

                if lep.mvaFall17V2noIso_WP80:
                    nEleGenMatch_mvaFall17V2noIso_WP80_EB += 1
                    self.h_mvaFall17V2noIso_WP80_EB.Fill(lep.mvaFall17V2noIso)
                # 
                if lep.cutBased == 0: # cut-based ID Fall17 V2 (0:fail, 1:veto, 2:loose, 3:medium, 4:tight)
                    nEleGenMatch_cutBasedFail_EB += 1
                if lep.cutBased >= 1:
                    nEleGenMatch_cutBasedVeto_EB += 1
                if lep.cutBased >= 2:
                    nEleGenMatch_cutBasedLoose_EB += 1
                if lep.cutBased >= 3:
                    nEleGenMatch_cutBasedMedium_EB += 1
                if  lep.cutBased == 4: 
                    nEleGenMatch_cutBasedTight_EB += 1


                pT = lep.pt
                sigmaIetaIetaThrsh_EB     = 0.0104
                dEtaSeedThrsh_EB          = 0.00255
                dPhiInThrsh_EB            = 0.022
                relIsoWithEAThrsh_EB      = 0.0287 + (0.506/pT)
                EInvMinusPInvThrsh_EB     = 0.159
                lostHitsThrsh_EB          = 1
                conversionVeto            = True
                HoEThrsh_EB               = 0.10 # from ttH analysis
                dxyThrsh_EB               = 0.05
                dzThrsh_EB                = 0.10

                '''
                if lep.sieie < sigmaIetaIetaThrsh_EB:
                    nEleGenMatch_sieie_EB += 1
                if abs(lep.deltaEtaSC) < dEtaSeedThrsh_EB:
                    nEleGenMatch_deltaEtaSC_EB += 1
                '''

                if lep.cutBased == 4: # cutBased Tight selection
                    self.h_sieie_AfterCutBasedTight_EB.Fill(lep.sieie)
                    self.h_deltaEtaSC_AfterCutBasedTight_EB.Fill(lep.deltaEtaSC)
                    self.h_hoe_AfterCutBasedTight_EB.Fill(lep.hoe)
                    self.h_pfRelIso03_all_AfterCutBasedTight_EB.Fill(lep.pfRelIso03_all)
                    self.h_jetRelIso_AfterCutBasedTight_EB.Fill(lep.jetRelIso)
                    self.h_eInvMinusPInv_AfterCutBasedTight_EB.Fill(lep.eInvMinusPInv)
                    self.h_lostHits_AfterCutBasedTight_EB.Fill(lep.lostHits)
                    self.h_convVeto_AfterCutBasedTight_EB.Fill(lep.convVeto)
                    self.h_dxy_AfterCutBasedTight_EB.Fill(lep.dxy)
                    self.h_dz_AfterCutBasedTight_EB.Fill(lep.dz)
                    self.h_sip3d_AfterCutBasedTight_EB.Fill(lep.sip3d)

                if lep.mvaFall17V2Iso_WP80:
                    self.h_sieie_AfterMvaFall17V2Iso80_EB.Fill(lep.sieie)
                    self.h_deltaEtaSC_AfterMvaFall17V2Iso80_EB.Fill(lep.deltaEtaSC)
                    self.h_hoe_AfterMvaFall17V2Iso80_EB.Fill(lep.hoe)
                    self.h_pfRelIso03_all_AfterMvaFall17V2Iso80_EB.Fill(lep.pfRelIso03_all)
                    self.h_jetRelIso_AfterMvaFall17V2Iso80_EB.Fill(lep.jetRelIso)
                    self.h_eInvMinusPInv_AfterMvaFall17V2Iso80_EB.Fill(lep.eInvMinusPInv)
                    self.h_lostHits_AfterMvaFall17V2Iso80_EB.Fill(lep.lostHits)
                    self.h_convVeto_AfterMvaFall17V2Iso80_EB.Fill(lep.convVeto)
                    self.h_dxy_AfterMvaFall17V2Iso80_EB.Fill(lep.dxy)
                    self.h_dz_AfterMvaFall17V2Iso80_EB.Fill(lep.dz)
                    self.h_sip3d_AfterMvaFall17V2Iso80_EB.Fill(lep.sip3d)

                    
                   

                
            else:
                nEleGenMatch_EE += 1
                if lep.mvaFall17V2Iso_WPL:
                    nEleGenMatch_mvaFall17V2Iso_WPL_EE += 1
                    self.h_mvaFall17V2Iso_WPL_EE.Fill(lep.mvaFall17V2Iso)
                if lep.mvaFall17V2Iso_WP90:
                    nEleGenMatch_mvaFall17V2Iso_WP90_EE += 1
                    self.h_mvaFall17V2Iso_WP90_EE.Fill(lep.mvaFall17V2Iso)
                if lep.mvaFall17V2Iso_WP80:
                    nEleGenMatch_mvaFall17V2Iso_WP80_EE += 1
                    self.h_mvaFall17V2Iso_WP80_EE.Fill(lep.mvaFall17V2Iso)
                #
                if lep.mvaFall17V2noIso_WPL:
                    nEleGenMatch_mvaFall17V2noIso_WPL_EE += 1
                    self.h_mvaFall17V2noIso_WPL_EE.Fill(lep.mvaFall17V2noIso)
                if lep.mvaFall17V2noIso_WP90:
                    nEleGenMatch_mvaFall17V2noIso_WP90_EE += 1
                    self.h_mvaFall17V2noIso_WP90_EE.Fill(lep.mvaFall17V2noIso)
                if lep.mvaFall17V2noIso_WP80:
                    nEleGenMatch_mvaFall17V2noIso_WP80_EE += 1
                    self.h_mvaFall17V2noIso_WP80_EE.Fill(lep.mvaFall17V2noIso)
                # 
                if lep.cutBased == 0: # cut-based ID Fall17 V2 (0:fail, 1:veto, 2:loose, 3:medium, 4:tight)
                    nEleGenMatch_cutBasedFail_EE += 1
                if lep.cutBased >= 1:
                    nEleGenMatch_cutBasedVeto_EE += 1
                if lep.cutBased >= 2:
                    nEleGenMatch_cutBasedLoose_EE += 1
                if lep.cutBased >= 3:
                    nEleGenMatch_cutBasedMedium_EE += 1
                if  lep.cutBased == 4: 
                    nEleGenMatch_cutBasedTight_EE += 1

                if lep.cutBased == 4: # cutBased Tight selection
                    self.h_sieie_AfterCutBasedTight_EE.Fill(lep.sieie)
                    self.h_deltaEtaSC_AfterCutBasedTight_EE.Fill(lep.deltaEtaSC)
                    self.h_hoe_AfterCutBasedTight_EE.Fill(lep.hoe)
                    self.h_pfRelIso03_all_AfterCutBasedTight_EE.Fill(lep.pfRelIso03_all)
                    self.h_jetRelIso_AfterCutBasedTight_EE.Fill(lep.jetRelIso)
                    self.h_eInvMinusPInv_AfterCutBasedTight_EE.Fill(lep.eInvMinusPInv)
                    self.h_lostHits_AfterCutBasedTight_EE.Fill(lep.lostHits)
                    self.h_convVeto_AfterCutBasedTight_EE.Fill(lep.convVeto)
                    self.h_dxy_AfterCutBasedTight_EE.Fill(lep.dxy)
                    self.h_dz_AfterCutBasedTight_EE.Fill(lep.dz)
                    self.h_sip3d_AfterCutBasedTight_EE.Fill(lep.sip3d)

                if lep.mvaFall17V2Iso_WP80:
                    self.h_sieie_AfterMvaFall17V2Iso80_EE.Fill(lep.sieie)
                    self.h_deltaEtaSC_AfterMvaFall17V2Iso80_EE.Fill(lep.deltaEtaSC)
                    self.h_hoe_AfterMvaFall17V2Iso80_EE.Fill(lep.hoe)
                    self.h_pfRelIso03_all_AfterMvaFall17V2Iso80_EE.Fill(lep.pfRelIso03_all)
                    self.h_jetRelIso_AfterMvaFall17V2Iso80_EE.Fill(lep.jetRelIso)
                    self.h_eInvMinusPInv_AfterMvaFall17V2Iso80_EE.Fill(lep.eInvMinusPInv)
                    self.h_lostHits_AfterMvaFall17V2Iso80_EE.Fill(lep.lostHits)
                    self.h_convVeto_AfterMvaFall17V2Iso80_EE.Fill(lep.convVeto)
                    self.h_dxy_AfterMvaFall17V2Iso80_EE.Fill(lep.dxy)
                    self.h_dz_AfterMvaFall17V2Iso80_EE.Fill(lep.dz)
                    self.h_sip3d_AfterMvaFall17V2Iso80_EE.Fill(lep.sip3d)
                   

                

        self.h_nEleGenMatch.Fill(nEleGenMatch)
        if nEleGenMatch_EB >= nEleToRec:
            self.h_Stat.Fill(8)
        if nEleGenMatch_EE >= nEleToRec:
            self.h_Stat.Fill(9)
        ##
        if nEleGenMatch_mvaFall17V2Iso_WPL_EB >= nEleToRec:
            self.h_Stat.Fill(10)
        if nEleGenMatch_mvaFall17V2Iso_WP90_EB >= nEleToRec:
            self.h_Stat.Fill(11)
        if nEleGenMatch_mvaFall17V2Iso_WP80_EB >= nEleToRec:
            self.h_Stat.Fill(12)
        #
        if nEleGenMatch_mvaFall17V2Iso_WPL_EE >= nEleToRec:
            self.h_Stat.Fill(13)
        if nEleGenMatch_mvaFall17V2Iso_WP90_EE >= nEleToRec:
            self.h_Stat.Fill(14)
        if nEleGenMatch_mvaFall17V2Iso_WP80_EE >= nEleToRec:
            self.h_Stat.Fill(15)
        ##
        if nEleGenMatch_mvaFall17V2noIso_WPL_EB >= nEleToRec:
            self.h_Stat.Fill(20)
        if nEleGenMatch_mvaFall17V2noIso_WP90_EB >= nEleToRec:
            self.h_Stat.Fill(21)
        if nEleGenMatch_mvaFall17V2noIso_WP80_EB >= nEleToRec:
            self.h_Stat.Fill(22)
        #
        if nEleGenMatch_mvaFall17V2noIso_WPL_EE >= nEleToRec:
            self.h_Stat.Fill(23)
        if nEleGenMatch_mvaFall17V2noIso_WP90_EE >= nEleToRec:
            self.h_Stat.Fill(24)
        if nEleGenMatch_mvaFall17V2noIso_WP80_EE >= nEleToRec:
            self.h_Stat.Fill(25)
        ##
        if nEleGenMatch_cutBasedFail_EB >= nEleToRec:
            self.h_Stat.Fill(30)
        if nEleGenMatch_cutBasedVeto_EB >= nEleToRec:
            self.h_Stat.Fill(31)
        if nEleGenMatch_cutBasedLoose_EB >= nEleToRec:
            self.h_Stat.Fill(32)
        if nEleGenMatch_cutBasedMedium_EB >= nEleToRec:
            self.h_Stat.Fill(33)
        if nEleGenMatch_cutBasedTight_EB >= nEleToRec:
            self.h_Stat.Fill(34)
        #
        if nEleGenMatch_cutBasedFail_EE >= nEleToRec:
            self.h_Stat.Fill(35)
        if nEleGenMatch_cutBasedVeto_EE >= nEleToRec:
            self.h_Stat.Fill(36)
        if nEleGenMatch_cutBasedLoose_EE >= nEleToRec:
            self.h_Stat.Fill(37)
        if nEleGenMatch_cutBasedMedium_EE >= nEleToRec:
            self.h_Stat.Fill(38)
        if nEleGenMatch_cutBasedTight_EE >= nEleToRec:
            self.h_Stat.Fill(39)
            
        
        



                
        return True
            

   


preselection=""
#files=[" root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAOD/TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/40000/2CE738F9-C212-E811-BD0E-EC0D9A8222CE.root"]
#files=["root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv6/GluGluToRadionToHHTo4V_M-400_narrow_13TeV-madgraph_correctedcfg/NANOAODSIM/PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/70000/D6A8EF07-3425-3346-96C4-D000C58E4735.root"]

files=["/home/ssawant/dataFiles/GluGluToRadionToHHTo4V_M-400_narrow_13TeV-madgraph_correctedcfg/NanoAODSIM/D6A8EF07-3425-3346-96C4-D000C58E4735.root"] # gpu@indiacms
sHistFileName="histOut_HHTo4W_400.root"
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

p=PostProcessor(".",files,cut=preselection,branchsel=None,modules=[ExampleAnalysis()],noOut=True,histFileName=sHistFileName,histDirName="plots")
p.run()
