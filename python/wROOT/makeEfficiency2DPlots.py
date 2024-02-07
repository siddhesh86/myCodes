#!/bin/env python


import os
import sys
import math 
from array import array
import ROOT as R
R.gROOT.SetBatch(False)  ## Don't print histograms to screen while processing
from collections import OrderedDict
import math

sDir = "plots"

def printHistoDetails(h):
    print("Histo {}: nBinsX {}, nBinsY {}".format(h.GetName(), h.GetNbinsX(), h.GetNbinsY()))

def printHistosBinContent( heffi_num, heffi_den):
    printHistoDetails(heffi_num)
    printHistoDetails(heffi_den)

    for iBinX in range(1, (heffi_den.GetNbinsX())):
        for iBinY in range(1, (heffi_den.GetNbinsY())):
            sTmp = ""
            if (heffi_num.GetBinContent(iBinX, iBinY) > heffi_den.GetBinContent(iBinX, iBinY)):
                sTmp = "num > den"
            print("\t({}, {}) \t ({}, {}): \t {} \t {} \t\t\t {}".format(
                iBinX, iBinY,
                heffi_den.GetXaxis().GetBinCenter(iBinX),  heffi_den.GetYaxis().GetBinCenter(iBinY),
                heffi_den.GetBinContent(iBinX, iBinY), heffi_num.GetBinContent(iBinX, iBinY),
                sTmp
                ) )
            

def makeHistsBinContentNonnegative(histo_list):
    for h in histo_list:
        for iBinX in range(1, (h.GetNbinsX())):
            for iBinY in range(1, (h.GetNbinsY())):
                if h.GetBinContent(iBinX, iBinY) < 0:
                    h.SetBinContent(iBinX, iBinY, 0.0)
                    

def scale2DHistoToPower(h, power1):
    for iBinX in range(1, (h.GetNbinsX())):
        for iBinY in range(1, (h.GetNbinsY())):
            x = h.GetBinContent(iBinX, iBinY)
            h.SetBinContent(iBinX, iBinY, math.pow(x, power1))
    #return     
    

    
def calculateEfficiency2D(effiName, heffi_num, heffi_den, nLeptons):
    print("type(heffi_num) {}".format(type(heffi_num)))
    print("heffi_num.GetNbinsX() {}".format(heffi_num.GetNbinsX()))
    print("heffi_den.GetNbinsX() {}".format(heffi_den.GetNbinsX()))
    hEffi = R.TEfficiency(heffi_num, heffi_den)
    #hEffi = heffi_den.Clone(effiName);     hEffi.Divide(heffi_num, heffi_den)
    hEffi.SetName(effiName)
    hEffi.SetUseWeightedEvents();
    hEffi.SetStatisticOption(R.TEfficiency.kFNormal);

    #hEffi.    
    
    c1 = R.TCanvas("c1","c1",600,500)
    c1.cd()

    #hEffi.SetMaximum(0.5)
    #hEffi.SetMinimum(0.0)

    hEffi.Draw('colz text')

    c1.Update()

    
    if not os.path.exists(sDir): os.mkdir(sDir)
    c1.SaveAs("%s/%s.png" % (sDir, effiName))

    return hEffi
    


    
def calculateEfficiency2D_v2(effiName, heffi_num, heffi_den, nLeptons):
    print("type(heffi_num) {}".format(type(heffi_num)))
    print("heffi_num.GetNbinsX() {}".format(heffi_num.GetNbinsX()))
    print("heffi_den.GetNbinsX() {}".format(heffi_den.GetNbinsX()))
    hEffi = heffi_den.Clone(effiName);     hEffi.Divide(heffi_num, heffi_den)
    hEffi.SetName(effiName)
    hEffi.SetTitle(effiName)

    #hEffi.    
    
    c1 = R.TCanvas("c1","c1",800,500)
    c1.cd()

    #hEffi.SetMaximum(0.5)
    #hEffi.SetMinimum(0.0)

    R.gStyle.SetPaintTextFormat("4.2f");
    hEffi.SetMarkerSize(1.3)
    hEffi.Draw('colz TEXTE')

    c1.Update()


    if not os.path.exists(sDir): os.mkdir(sDir)
    c1.SaveAs("%s/%s_v2.png" % (sDir, effiName))

    return hEffi



if __name__ == '__main__':

    
    
    nLeptons = 3 # sclane TEfficiency by 1/nLeptons
    
    sInFile = "analyze_signal_ggf_nonresonant_cHHH1_hh_4v_Tight_OS_central_1.root"
    sHistoDir = "hh_3l_OS_Tight/sel/evt_1/signal_ggf_nonresonant_cHHH1_hh"

    sDir = "plots_hh_%dlepton_channel" % (nLeptons)
    

    rebinX, rebinY = [1, 1]
    
    sEffi_dict = OrderedDict([
        ("EleIDEffi_pT_vs_eta_woWgt", ["%s/hEleIDEffi_pT_vs_eta_num_woWgt"%(sHistoDir), "%s/hEleIDEffi_pT_vs_eta_den_woWgt"%(sHistoDir)]),
        ("MuIDEffi_pT_vs_eta_woWgt",  ["%s/hMuIDEffi_pT_vs_eta_num_woWgt"%(sHistoDir),  "%s/hMuIDEffi_pT_vs_eta_den_woWgt"%(sHistoDir)]),
        #
        ("EleIDEffi_pT_vs_eta", ["%s/hEleIDEffi_pT_vs_eta_num"%(sHistoDir), "%s/hEleIDEffi_pT_vs_eta_den"%(sHistoDir)]),
        ("MuIDEffi_pT_vs_eta",  ["%s/hMuIDEffi_pT_vs_eta_num"%(sHistoDir),  "%s/hMuIDEffi_pT_vs_eta_den"%(sHistoDir)]),
        #
        ("EleIDEffi_pT_vs_eta_wFullWgt", ["%s/hEleIDEffi_pT_vs_eta_num_wFullWgt"%(sHistoDir), "%s/hEleIDEffi_pT_vs_eta_den_wFullWgt"%(sHistoDir)]),
        ("MuIDEffi_pT_vs_eta_wFullWgt",  ["%s/hMuIDEffi_pT_vs_eta_num_wFullWgt"%(sHistoDir),  "%s/hMuIDEffi_pT_vs_eta_den_wFullWgt"%(sHistoDir)]),
   ])

    R.gStyle.SetOptStat(0)

    fIn = R.TFile(sInFile)
    if not fIn.IsOpen():
        print("{} could not open".format(sInFile))

    for effiName, effiCalHistos in sEffi_dict.items():
        effi_num_histoName = effiCalHistos[0]
        effi_den_histoName = effiCalHistos[1]
        print("{}: {} {}".format(effiName, effi_num_histoName,effi_den_histoName))

        heffi_num = fIn.Get(effi_num_histoName)
        heffi_den = fIn.Get(effi_den_histoName)

        heffi_num.Sumw2();
        heffi_den.Sumw2();

        heffi_num.GetXaxis().SetTitle("GEN-lepton pT")
        heffi_num.GetYaxis().SetTitle("|GEN-lepton #eta|")
        heffi_den.GetXaxis().SetTitle("GEN-lepton pT")
        heffi_den.GetYaxis().SetTitle("|GEN-lepton #eta|")

        heffi_num.Rebin2D(rebinX, rebinY)
        heffi_den.Rebin2D(rebinX, rebinY)

        print("printHistosBinContent() initial"); sys.stdout.flush();
        printHistosBinContent( heffi_num, heffi_den); sys.stdout.flush();

        print("makeHistsBinContentNonnegative() "); sys.stdout.flush();
        makeHistsBinContentNonnegative([heffi_num, heffi_den]); sys.stdout.flush();

        print("printHistosBinContent() after Histo correction"); sys.stdout.flush();
        printHistosBinContent( heffi_num, heffi_den); sys.stdout.flush();

        scale2DHistoToPower(heffi_num,  1.0/nLeptons)
        scale2DHistoToPower(heffi_den,  1.0/nLeptons)

        print("printHistosBinContent() after Histo scaling"); sys.stdout.flush();
        printHistosBinContent( heffi_num, heffi_den); sys.stdout.flush();

        
        #hEffi_nLepton = calculateEfficiency2D(effiName, heffi_num, heffi_den, nLeptons)

        calculateEfficiency2D_v2(effiName, heffi_num, heffi_den, nLeptons)

        ## single lepton efficiency
        #printHistoDetails(hEffi_nLepton)
        
        
