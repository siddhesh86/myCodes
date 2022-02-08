#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <math.h>
//#include "TFit.hh"
#include "TH1.h"
#include "TH2.h"
#include "TTree.h"
#include "TFile.h"
#include "TString.h"
#include "TVector3.h"
#include "TLorentzVector.h"
#include <iostream>
#include "TObjArray.h"
#include "TObject.h"


void ana_treer()
{
  TH1 *hDummy = new TH1F("hDummy","",1,0,1);
  hDummy->SetDefaultSumw2();

  std::vector<std::string> sFIns = {
    "/hdfs/local/ssawant/hhAnalysis/2016/20210610_hh_3l_2016_NtuplesBDTOutput/histograms/hh_3l/Tight_OS/hadd/hadd_stage1_5_Tight_OS.root",
    "/hdfs/local/ssawant/hhAnalysis/2017/20210610_hh_3l_2017_NtuplesBDTOutput/histograms/hh_3l/Tight_OS/hadd/hadd_stage1_5_Tight_OS.root",
    "/hdfs/local/ssawant/hhAnalysis/2018/20210610_hh_3l_2018_NtuplesBDTOutput/histograms/hh_3l/Tight_OS/hadd/hadd_stage1_5_Tight_OS.root"
  };
  std::string sTree = "hh_3l_OS_Tight/sel/evtntuple_BDTOutput/data_obs/evtTree";
  std::string sFOut = "BDTOutput_data_hh_3l_RUN2.root";
  
  TChain *treeEventBDTOutput = new TChain(sTree.c_str());
  for (auto sFIn : sFIns)
  {
    printf("sFIn: %s \n",sFIn.c_str());
    treeEventBDTOutput->Add(sFIn.c_str());
  }
    printf("tree: %s\n",sTree.c_str());

  

  /*
   TFile *f = new TFile("analyze_signal_ggf_spin0_400_hh_4v_Tight_OS_central_1.root");
   TTree *treeEventBDTOutput = (TTree*)f->Get("hh_3l_OS_Tight/sel/evtntuple_BDTOutput/signal_ggf_spin0_400_hh/evtTree");
  */

  /*
  std::vector<int> gen_mHHs = {500, 700, 900};
  std::vector<string> res_spins = {"spin0", "spin2"};
  
  Float_t bdtOutput[3][30]; // [iSpin][imHH]::    iSpin: spin-case,  imHH: mHH

  for (size_t iSpin = 0; iSpin < res_spins.size(); iSpin++)
  {
    for (size_t imHH = 0; imHH < gen_mHHs.size(); imHH++)
    {
      TString varName = Form("BDTOutput_%d_%s",gen_mHHs[imHH],res_spins[iSpin].c_str());
      treeEventBDTOutput->SetBranchAddress(varName.Data(), &bdtOutput[iSpin][imHH]);
    }
  }
  */

  Float_t evtWeight;
  Float_t bdtOutput_500_spin2;
  Float_t bdtOutput_700_spin2;
  Float_t bdtOutput_900_spin2;
  treeEventBDTOutput->SetBranchAddress("evtWeight",           &evtWeight);
  treeEventBDTOutput->SetBranchAddress("BDTOutput_500_spin2", &bdtOutput_500_spin2);
  treeEventBDTOutput->SetBranchAddress("BDTOutput_700_spin2", &bdtOutput_700_spin2);
  treeEventBDTOutput->SetBranchAddress("BDTOutput_900_spin2", &bdtOutput_900_spin2);

  TH2F *hBDTOutput_500_spin2_vs_700_spin2_ = new TH2F("BDTOutput_500_spin2_vs_700_spin2",                      "BDTOutput_500_spin2_vs_700_spin2",         100,0,1, 100,0,1);
  TH2F *hBDTOutput_500_spin2_vs_900_spin2_ = new TH2F("BDTOutput_500_spin2_vs_900_spin2",                      "BDTOutput_500_spin2_vs_900_spin2",         100,0,1, 100,0,1);
  TH2F *hBDTOutput_700_spin2_vs_900_spin2_ = new TH2F("BDTOutput_700_spin2_vs_900_spin2",                      "BDTOutput_700_spin2_vs_900_spin2",         100,0,1, 100,0,1);

  Long64_t nEnties = treeEventBDTOutput->GetEntries();
  std::cout << "nEnties: " << nEnties << "\n";
  for (Long64_t iEntry=0; iEntry < nEnties; iEntry++)
  {
    if (iEntry % 1000 == 0) std::cout << "entry: " << iEntry << "\n";
    treeEventBDTOutput->GetEntry(iEntry);
       
    //std::cout << iEntry << ", bdt: " << bdtOutput[0] << ",  bdt: " << bdt1[1] << "\n";
    /*
    std::cout << iEntry;
    for (size_t imHH = 0; imHH < gen_mHHs.size(); imHH++)
    {
      for (size_t iSpin = 0; iSpin < res_spins.size(); iSpin++)
      {
	TString varName = Form("%d_%s",gen_mHHs[imHH],res_spins[iSpin].c_str());
	std::cout << varName << ": " << bdtOutput[iSpin][imHH] << ", ";
      }
    }
    std::cout << "\n";
    */

    //std::cout << iEntry << ", bdt: " << bdtOutput_500_spin2 << ",  evtWeight: " << evtWeight << "\n";

    
    hBDTOutput_500_spin2_vs_700_spin2_->Fill(bdtOutput_500_spin2, bdtOutput_700_spin2, evtWeight);
    hBDTOutput_500_spin2_vs_900_spin2_->Fill(bdtOutput_500_spin2, bdtOutput_900_spin2, evtWeight);
    hBDTOutput_700_spin2_vs_900_spin2_->Fill(bdtOutput_700_spin2, bdtOutput_900_spin2, evtWeight);
  }


  TFile *fOut = new TFile(sFOut.c_str(), "RECREATE");
  fOut->cd();
  hBDTOutput_500_spin2_vs_700_spin2_->Write();
  hBDTOutput_500_spin2_vs_900_spin2_->Write();
  hBDTOutput_700_spin2_vs_900_spin2_->Write();
  fOut->Close();
  
  printf("sFOut: %s \n",sFOut.c_str());
}
