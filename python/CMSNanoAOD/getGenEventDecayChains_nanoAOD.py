#!/usr/bin/env python
import os, sys
import itertools
import collections

import ROOT
ROOT.PyConfig.IgnoreCommandLineOptions = True
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import PostProcessor


from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
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

        
class ExampleAnalysis(Module):
    def __init__(self):
        self.writeHistFile=True

    def beginJob(self,histFile=None,histDirName=None):
        Module.beginJob(self,histFile,histDirName)

        self.h_vpt=ROOT.TH1F('sumpt',   'sumpt',   100, 0, 1000)
        self.addObject(self.h_vpt )

    def analyze(self, event):
        #run = Collection(event, "run")
        #lumi = Collection(event, "luminosityBlock")
        #eventNumber  = Collection(event, "event")
        
        genParts = Collection(event, "GenPart")

        #print "\n\n run:",run, ", lumi:",lumi, ", event:",event
        print "\n\n event:\n"

        #stoge gen particle index into dictionary to get genParticle family tree
        genPartFamily = collections.OrderedDict()                
        
        for iGenPart in range(0,len(genParts)):
            genPart = genParts[iGenPart]
            print "genPart %d: pt %f, eta %f, phi %f, m %f,  pdgId %d, genPartIdxMother %d, status %d, statusFlags %d" % (iGenPart, genPart.pt, genPart.eta, genPart.phi, genPart.mass, genPart.pdgId, genPart.genPartIdxMother, genPart.status, genPart.statusFlags)
            
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
        print "\n\n printFamilyTree: particleIdx (pdgId) [pt, eta, phi]\n"
        printFamilyTree(genParts, familyTree)

        
        return True

        
   


preselection=""
#files=[" root://cms-xrd-global.cern.ch//store/mc/RunIISummer16NanoAOD/TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/NANOAODSIM/PUMoriond17_05Feb2018_94X_mcRun2_asymptotic_v2-v1/40000/2CE738F9-C212-E811-BD0E-EC0D9A8222CE.root"]
files=[" root://cms-xrd-global.cern.ch//store/mc/RunIIFall17NanoAODv6/GluGluToRadionToHHTo4V_M-400_narrow_13TeV-madgraph_correctedcfg/NANOAODSIM/PU2017_12Apr2018_Nano25Oct2019_102X_mc2017_realistic_v7-v1/70000/D6A8EF07-3425-3346-96C4-D000C58E4735.root"]
p=PostProcessor(".",files,cut=preselection,branchsel=None,modules=[ExampleAnalysis()],noOut=True,histFileName="histOut.root",histDirName="plots")
p.run()
