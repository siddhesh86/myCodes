#!/bin/env python


import os
import sys
import math 
from array import array
import ROOT as R
R.gROOT.SetBatch(False)  ## Don't print histograms to screen while processing
from collections import OrderedDict
from collections import OrderedDict as OD
import math


sDir = "plots_troubleshootPhiRingPU"


def printHistoBinContent(h, sSaveAs):
    if not os.path.exists(sDir): os.mkdir(sDir)
    with open("%s/%s.csv" % (sDir, sSaveAs), 'w') as fOut:
        for binY in range(h.GetNbinsY(), 0, -1):
            for binX in range(1, h.GetNbinsX()+1):
                n = h.GetBinContent(binX, binY)
                sTmp = str(n) if n>0 else " "
                fOut.write( "%s\t" % (sTmp) )
            fOut.write( "\n" )


def plotHisto2D(
    h, 
    sSaveAs,
    sXaxisTitle='x',
    sYaxisTitle='y',
    plotLogX=False,
    plotLogY=False,
):

    c1 = R.TCanvas("c1","c1",600,500)
    c1.cd()

    h.GetXaxis().SetTitle(sXaxisTitle)
    h.GetYaxis().SetTitle(sYaxisTitle)
    
    #hEffi.SetMaximum(0.5)
    #hEffi.SetMinimum(0.0)

    #R.gStyle.SetPaintTextFormat("4.2f");
    #h.SetMarkerColor(2)
    h.SetMarkerSize(0.5)
    #h.Draw('colz TEXT') 
    h.Draw('colz')

    #c1.GetPadSave().SetLogX(plotLogX)
    c1.SetLogx(plotLogX)
    c1.SetLogy(plotLogY)


    line = R.TLine()
    line.SetLineStyle(2)
    line.SetLineColor(R.kBlack)
    line.SetLineWidth(2)
    line.DrawLine(0, 0, 1000,1000)

    c1.Update()
    
    #if not os.path.exists(sDir): os.mkdir(sDir)
    #c1.SaveAs("%s/%s.png" % (sDir, sSaveAs))
    c1.SaveAs("%s.png" % (sSaveAs))
    
    

if __name__ == '__main__':
    useAbsEtaBins = True
    ETA_Bins = []
    for iEta in range(-41,42):
        if iEta in [-29, 0, 29]:        continue;
        if useAbsEtaBins and iEta < 0:  continue;
        ETA_Bins.append(str(iEta))
    ETA_Bins.append('HBEF')


    
    #sInFile = "L1T_HCALL2Calib_stage1_l1NtupleChunkyDonut_QCD_126X_hadded.root"
    
    #sVersion = "QCD_122X_sample"
    #sInFile  = "L1T_HCALL2Calib_stage1_l1NtupleChunkyDonut_QCD_122X_hadded.root"
    
    sVersion = "QCD_126X_sample"
    sInFile  = "L1T_HCALL2Calib_stage1_l1NtupleChunkyDonut_QCD_126X_hadded.root"

    sOpDir = "plots_TrblshtTT28LowSFs/L1JetPtRawPUS_vs_RefJetPt"
           
    sHistos_dict = OD()
    for src in ['emu']: # ['unp','emu']:
        for Eta_Bin in ETA_Bins:
            sHistoName = "L1JetPt/hL1JetPtRawPUS_vs_RefJetPt_iEta%s_%s" % (Eta_Bin, src)
            sSaveAs    = "%s/L1JetPtRawPUS_vs_RefJetPt_iEta%s_%s_%s" % (sOpDir, Eta_Bin, src, sVersion)
            sHistos_dict[sSaveAs] = sHistoName

    os.makedirs(sOpDir, exist_ok=True)
    
    

    R.gStyle.SetOptStat(0)
    
    fIn = R.TFile(sInFile)
    if not fIn.IsOpen():
        print("{} could not open".format(sInFile))


    for sSaveAs, sHistoName in sHistos_dict.items():
        h = fIn.Get(sHistoName)
        if not h:
            print("%s<<histogram not found" % (sHistoName))
            continue
            
        h.SetTitle(h.GetTitle() + " " + sVersion)
        
        plotHisto2D(
            h, 
            sSaveAs,
            sXaxisTitle='GEN pT [GeV]',
            sYaxisTitle='(L1T Raw pT - PU)*0.5 [GeV]',
            plotLogX=False,
            plotLogY=False
        )

        plotHisto2D(
            h, 
            sSaveAs + "_logXY",
            sXaxisTitle='GEN pT [GeV]',
            sYaxisTitle='(L1T Raw pT - PU)*0.5 [GeV]',
            plotLogX=True,
            plotLogY=True
        )
        