

void PlotHistos1DAndRatioPlot() {
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);
  
  std::string sipFile      = "sipFile";
  std::string sHistoName   = "sHistoName";
  std::string sLegend      = "sLegend";
  std::string sLineColor   = "sLineColor";
  std::string sMarkerColor = "sMarkerColor";
  std::string sMarkerStyle = "sMarkerStyle";

  // ------- Settings --------------------------------------------------------
  std::vector<std::map<std::string, std::string>> vHistoDetails;
  vHistoDetails.push_back({			  
      {sipFile,      "hadd_stage2_Tight_OS.root"},
      {sHistoName,   "hh_3l_OS_Tight/sel/evt/TT_fake/mvaOutput_xgb_hh_3l_SUMBk_HH"},
      {sLegend,      "Signal region"},
      {sLineColor,   "1"},
      {sMarkerColor, "1"},
      {sMarkerStyle, "20"}
    });
  
  vHistoDetails.push_back({			  
      {sipFile,      "hadd_stage2_Fakeable_mcClosure_e_wFakeRateWeights_OS.root"},
      {sHistoName,   "hh_3l_OS_Fakeable_mcClosure_e_wFakeRateWeights/sel/evt/TT_fake/mvaOutput_xgb_hh_3l_SUMBk_HH"},
      {sLegend,      "Fakeable_mcClosure_e_wFakeRateWeights"},
      {sLineColor,   "2"},
      {sMarkerColor, "2"},
      {sMarkerStyle, "20"}
    });

  vHistoDetails.push_back({			  
      {sipFile,      "hadd_stage2_Fakeable_mcClosure_m_wFakeRateWeights_OS.root"},
      {sHistoName,   "hh_3l_OS_Fakeable_mcClosure_m_wFakeRateWeights/sel/evt/TT_fake/mvaOutput_xgb_hh_3l_SUMBk_HH"},
      {sLegend,      "Fakeable_mcClosure_m_wFakeRateWeight"},
      {sLineColor,   "4"},
      {sMarkerColor, "4"},
      {sMarkerStyle, "20"}
    });

  vHistoDetails.push_back({			  
      {sipFile,      "hadd_stage2_Fakeable_wFakeRateWeights_OS.root"},
      {sHistoName,   "hh_3l_OS_Fakeable_wFakeRateWeights/sel/evt/TT_fake/mvaOutput_xgb_hh_3l_SUMBk_HH"},
      {sLegend,      "Fakeable_wFakeRateWeights"},
      {sLineColor,   "6"},
      {sMarkerColor, "6"},
      {sMarkerStyle, "20"}
    });
  
  std::string sXaxisName = "BDT score";
  std::string sYaxisName = "No. of events";
  std::string sSaveAs = "Lepton_FR_MCClosure_TTfake_BDT_wRatio";
  double      rangeXaxis[3] = {0, -1.0, -1.0}; // rangeXaxis[0]: set axis range flag
  int         rebin = 2;
  double      normalizeHistos[2] = {0, 100}; // normalizeHistos[0]: mode, normalizeHistos[1]: norm. value
                                             // mode 0: don't scale/normalize histograms
                                             // mode 1: normalize w.r.t. area under histo
                                             // mode 2: normalize w.r.t. height of the histo
  int         setLogY = 0;
  int         makeRatioPlots = 1; // compare shapes by making ratio plot w.r.t. the 1st histogram
                                  // 0: disable ratio plot



  // ------- Settings - xxxxxxxx ------------------------------------------------




  
  
  double yMax = -99999.0;
  double yMin =  99999.0;
  

  std::vector<TH1D*> vHistos;
  std::vector<TH1D*> vHistosRatio;
  for (size_t iHisto=0; iHisto < vHistoDetails.size(); iHisto++) {
    std::map<std::string, std::string> iHistoDetails = vHistoDetails[iHisto];
    std::string sipFile1    = iHistoDetails[sipFile];
    std::string sHistoName1 = iHistoDetails[sHistoName];
    
    TFile *tFIn = new TFile(sipFile1.data());
    if ( ! tFIn->IsOpen()) {
      printf("File %s couldn't open \t\t\t *** ERROR **** \n",sipFile1.data());
      continue;
    }

    TH1D *histo = nullptr;
    histo = (TH1D*)tFIn->Get(sHistoName1.data());
    if ( ! histo) {
      printf("Couldn't fetch histogram %s from file %s  \t\t\t *** ERROR **** \n",sHistoName1.data(),sipFile1.data());
      continue;
    }

    histo->Rebin(rebin);

    double scale = 1.;
    if (std::abs(normalizeHistos[0] - 1) < 1e-3) { // normalize histo w.r.t. area
      double hArea = histo->Integral(1, histo->GetNbinsX());
      scale = normalizeHistos[1] / hArea;
      histo->Scale(scale);
    }
    if (std::abs(normalizeHistos[0] - 2) < 1e-3) { // normalize histo w.r.t. height
      double hHeight = histo->GetBinContent(histo->GetMaximumBin());
      scale = normalizeHistos[1] / hHeight;
      histo->Scale(scale);
    }


    
    //if (histo->GetMaximum() > yMax) yMax = histo->GetMaximum();
    if (histo->GetMaximum() > yMax) yMax = histo->GetBinContent(histo->GetMaximumBin());
    if (histo->GetMinimum() > yMin) yMin = histo->GetMinimum(); 
    
    vHistos.push_back(histo);

    if (makeRatioPlots != 0 && iHisto > 0) {
      TH1D *histoRatio = (TH1D*)histo->Clone(Form("%s_ratio",histo->GetName()));

      // normalize histoRatio w.r.t. histo=0 area
      double hArea0  = vHistos[0]->Integral(1, vHistos[0]->GetNbinsX());
      double hArea   = histoRatio->Integral(1, histoRatio->GetNbinsX());
      double scale1  = hArea0 / hArea;
      histoRatio->Scale(scale1);

      // ratio
      histoRatio->Divide(vHistos[0]);
      vHistosRatio.push_back(histoRatio);
    }
    
  }

  //TCanvas *c1 = new TCanvas("c1","c1", 550, 450);
  TCanvas *c1 = new TCanvas();
  c1->SetWindowSize(c1->GetWw(), 1.3*c1->GetWh());
  c1->cd();
  TPad *pad1 = new TPad("pad1", "pad1", 0, 0.3, 1, 1);
  pad1->Draw();
  pad1->SetLogy(setLogY);
  TPad *pad2 = new TPad("pad2", "pad2", 0, 0, 1, 0.3);
  pad2->Draw();
  //gPad->SetLogy(setLogY);
  
  pad1->SetBottomMargin(0.02);
    
  pad2->SetTopMargin(0.05);
  pad2->SetBottomMargin(0.3);
  
 
  TLegend *leg = new TLegend(0.3,0.73,0.95,0.95);


  yMax = yMax * 0.6;
  if (yMin > 0) yMin = yMin * 0.8;
  else          yMin = yMin * 1.2;

  
  for (size_t iHisto=0; iHisto < vHistoDetails.size(); iHisto++) {
    std::map<std::string, std::string> iHistoDetails = vHistoDetails[iHisto];
    std::string sLegend1 = iHistoDetails[sLegend];
    std::string sLineColor1 = iHistoDetails[sLineColor];
    std::string sMarkerColor1 = iHistoDetails[sMarkerColor];
    std::string sMarkerStyle1 = iHistoDetails[sMarkerStyle];
    //std::string  = iHistoDetails[];

    TH1D *h = vHistos[iHisto];

    if ( ! sLineColor1.empty()) {
      int x = std::stoi(sLineColor1);
      h->SetLineColor(x);
    }
    if ( ! sMarkerColor1.empty()) {
      int x = std::stoi(sMarkerColor1);
      h->SetMarkerColor(x);
    }
    if ( ! sMarkerStyle1.empty()) {
      int x = std::stoi(sMarkerStyle1);
      h->SetMarkerStyle(x);
    }

    if (std::abs(rangeXaxis[0] - 1) < 1e-3) {
      h->GetXaxis()->SetRangeUser(rangeXaxis[1], rangeXaxis[2]);
    }
    h->GetYaxis()->SetRangeUser(yMin, yMax);
    
    if ( ! sXaxisName.empty()) {
      h->GetXaxis()->SetTitle(sXaxisName.data());
    }
    if ( ! sYaxisName.empty()) {
      h->GetYaxis()->SetTitle(sYaxisName.data());
    }

    pad1->cd();
    if ((int)iHisto == 0) h->Draw("EP");
    else                  h->Draw("same EP");

    if ( ! sLegend1.empty()) {
      leg->AddEntry(h, sLegend1.data(), "l");
    }

    // ratio plots
    if (makeRatioPlots != 0 && iHisto > 0) {
      TH1D *hRatio = vHistosRatio[iHisto - 1];
      
      if ( ! sLineColor1.empty()) {
	int x = std::stoi(sLineColor1);
	hRatio->SetLineColor(x);
      }
      if ( ! sMarkerColor1.empty()) {
	int x = std::stoi(sMarkerColor1);
	hRatio->SetMarkerColor(x);
      }
      if ( ! sMarkerStyle1.empty()) {
	int x = std::stoi(sMarkerStyle1);
	hRatio->SetMarkerStyle(x);
      }

      if (std::abs(rangeXaxis[0] - 1) < 1e-3) {
	hRatio->GetXaxis()->SetRangeUser(rangeXaxis[1], rangeXaxis[2]);
      }
      hRatio->GetYaxis()->SetRangeUser(0, 2);
    
      if ( ! sXaxisName.empty()) {
	hRatio->GetXaxis()->SetTitle(sXaxisName.data());
      }
      hRatio->GetYaxis()->SetTitle("Ratio w.r.t signal region");

      auto xLabSize = hRatio->GetXaxis()->GetLabelSize();
      auto xTitleSize = hRatio->GetXaxis()->GetTitleSize();
      auto yLabSize = hRatio->GetYaxis()->GetLabelSize();
      auto yTitleSize = hRatio->GetYaxis()->GetTitleSize();
      auto yOffSet = hRatio->GetYaxis()->GetTitleOffset();

      hRatio->GetXaxis()->SetTitleSize(0.7*xTitleSize/0.3);
      hRatio->GetXaxis()->SetLabelSize(0.7*xLabSize/0.3);

      hRatio->GetYaxis()->SetTitleSize(0.7*yTitleSize/0.3);
      hRatio->GetYaxis()->SetLabelSize(0.7*yLabSize/0.3);

      //hRatio->GetYaxis()->SetTitleOffset(0.3*yOffSet/0.7);
      hRatio->GetYaxis()->SetTitleOffset(0.6);

      hRatio->GetYaxis()->SetNdivisions(505);
      
          
      pad2->cd();
      if ((int)iHisto == 1) hRatio->Draw("EP");
      else                  hRatio->Draw("same EP");
    }
  }
  pad1->cd();
  leg->Draw();

  
  c1->SaveAs(Form("%s.png",sSaveAs.data()));
  
}
