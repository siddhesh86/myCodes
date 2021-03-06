

void PlotHistos1D() {
  std::string sipFile      = "sipFile";
  std::string sHistoName   = "sHistoName";
  std::string sLegend      = "sLegend";
  std::string sLineColor   = "sLineColor";
  std::string sMarkerColor = "sMarkerColor";
  std::string sMarkerStyle = "sMarkerStyle";

  // ------- Settings --------------------------------------------------------
  std::vector<std::map<std::string, std::string>> vHistoDetails;
  vHistoDetails.push_back({			  
      {sipFile,      "analyze_signal_ggf_spin0_250_hh_4v_Tight_OS_central_1.root"},
      {sHistoName,   "hh_3l_OS_Tight/sel/study/signal_ggf_spin0_250_hh_wwww/hptGenJet_all_HHTo4W"},
      {sLegend,      "X(250, spin-0)#rightarrow HH#rightarrow 4W#rightarrow 1(l #nu) 3(qq)"},
      {sLineColor,   "1"},
      {sMarkerColor, ""},
      {sMarkerStyle, ""}
    });

  vHistoDetails.push_back({			  
      {sipFile,      "analyze_signal_ggf_spin0_400_hh_4v_Tight_OS_central_1.root"},
      {sHistoName,   "hh_3l_OS_Tight/sel/study/signal_ggf_spin0_400_hh_wwww/hptGenJet_all_HHTo4W"},
      {sLegend,      "X(400, spin-0)#rightarrow HH#rightarrow 4W#rightarrow 1(l #nu) 3(qq)"},
      {sLineColor,   "2"},
      {sMarkerColor, ""},
      {sMarkerStyle, ""}
    });

  vHistoDetails.push_back({			  
      {sipFile,      "analyze_signal_ggf_spin0_700_hh_4v_Tight_OS_central_1.root"},
      {sHistoName,   "hh_3l_OS_Tight/sel/study/signal_ggf_spin0_700_hh_wwww/hptGenJet_all_HHTo4W"},
      {sLegend,      "X(700, spin-0)#rightarrow HH#rightarrow 4W#rightarrow 1(l #nu) 3(qq)"},
      {sLineColor,   "4"},
      {sMarkerColor, ""},
      {sMarkerStyle, ""}
    });

  vHistoDetails.push_back({			  
      {sipFile,      "analyze_signal_ggf_spin0_1000_hh_4v_Tight_OS_central_1.root"},
      {sHistoName,   "hh_3l_OS_Tight/sel/study/signal_ggf_spin0_1000_hh_wwww/hptGenJet_all_HHTo4W"},
      {sLegend,      "X(1000, spin-0)#rightarrow HH#rightarrow 4W#rightarrow 1(l #nu) 3(qq)"},
      {sLineColor,   "6"},
      {sMarkerColor, ""},
      {sMarkerStyle, ""}
    });

  std::string sXaxisName = "pT (Jet_{gen}) [GeV]";
  std::string sYaxisName = "a.u.";
  std::string sSaveAs = "ptGenJet_HHTo4W_1l_3qq";
  double      rangeXaxis[3] = {0, -1.0, -1.0}; // rangeXaxis[0]: set axis range flag
  int         rebin = 2;
  double      normalizeHistos[2] = {1, 100}; // normalizeHistos[0]: mode, normalizeHistos[1]: norm. value
                                             // mode 0: don't scale/normalize histograms
                                             // mode 1: normalize w.r.t. area under histo
                                             // mode 2: normalize w.r.t. height of the histo
  int         setLogY = 0;
  



  // ------- Settings - xxxxxxxx ------------------------------------------------




  
  
  double yMax = -99999.0;
  double yMin =  99999.0;
  

  std::vector<TH1D*> vHistos;
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
  }

  TCanvas *c1 = new TCanvas("c1","c1", 550, 450);
  c1->cd();
  gPad->SetLogy(setLogY);
  

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
    //h->GetYaxis()->SetRangeUser(yMin, yMax);
    
    if ( ! sXaxisName.empty()) {
      h->GetXaxis()->SetTitle(sXaxisName.data());
    }
    if ( ! sYaxisName.empty()) {
      h->GetYaxis()->SetTitle(sYaxisName.data());
    }
    
    if ((int)iHisto == 0) h->Draw("HIST");
    else                  h->Draw("same HIST");

    if ( ! sLegend1.empty()) {
      leg->AddEntry(h, sLegend1.data(), "l");
    }
  }

  leg->Draw();

  
  c1->SaveAs(Form("%s.png",sSaveAs.data()));
  
}
