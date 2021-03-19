
#include <boost/algorithm/string.hpp> // include Boost, a C++ library


TFile* getTFile(std::string sipFile)
{
  if (sipFile.find("*") == std::string::npos)
  {
    TFile *tFIn = new TFile(sipFile.data());
    return tFIn;
  }

  // filename with '*'
  // files to hadd
  std::string sipFile_hadded = sipFile;
  boost::replace_all(sipFile_hadded, "*", "-x-");
  boost::replace_all(sipFile_hadded, "/", "_");
  if (sipFile_hadded.rfind("_", 0) == 0)  sipFile_hadded =  sipFile_hadded.substr(1,sipFile_hadded.length()-1);
  if (sipFile_hadded.length() > 250)
  { // string > 255 gives error
    int skip_charecters = sipFile_hadded.length() - 250;
    sipFile_hadded =  sipFile_hadded.substr(skip_charecters,sipFile_hadded.length()-1);
  }


  std::cout << "\nsipFile: " << sipFile << "  -->  " << sipFile_hadded << "\n";
  printf("\nCommand: No. of files to hadd");   std::cout << std::endl;
  gSystem->Exec(Form("ls %s | wc -l",sipFile.c_str()));
  printf("Command: ls files to hadd");   std::cout << std::endl;
  gSystem->Exec(Form("ls %s",sipFile.c_str()));


  
  printf("\nCommand: time hadd -f %s %s",sipFile_hadded.c_str(),sipFile.c_str());   std::cout << std::endl;
  gSystem->Exec(Form("time hadd -f %s %s",sipFile_hadded.c_str(),sipFile.c_str()));
  //gSystem->Exec(Form("time hadd -f -v  %s %s ",sipFile_hadded.c_str(),sipFile.c_str()));
  
  printf("\nCommand: ls %s",sipFile_hadded.c_str());   std::cout << std::endl;
  gSystem->Exec(Form("ls %s",sipFile_hadded.c_str()));

  TFile *tFIn1 = new TFile(sipFile_hadded.data());
  return tFIn1;
}

void getHistogramsYRange(std::vector<TH1*> histograms, double &yMin, double &yMax, int setLogY=0)
{ 
  yMax = -9999;
  yMin =  9999;
  for (const auto& histogram: histograms)
  {
    double yMax_tmp = histogram->GetMaximum();
    double yMin_tmp = histogram->GetMinimum();
    double kZeroValue = 1e-10;
    if (setLogY && (std::abs(yMin_tmp) - 0) < kZeroValue) 
    { // yMin_tmp = 0 in LogY mode: find yMin_tmp other than 0
      yMin_tmp = 9999;
      for (int i=1; i<=histogram->GetNbinsX(); i++)
      {
	double y = histogram->GetBinContent(i);
	if (y > 0 && (std::abs(y) - 0) > kZeroValue && y < yMin_tmp) yMin_tmp = y;
      }
    }
    
    if (yMax_tmp > yMax) yMax = yMax_tmp;
    if (yMin_tmp < yMin && yMin_tmp > -9990.) yMin = yMin_tmp;
  }
}

void divideByBinWidth(TH1* histogram)
{
  if(! (histogram && histogram->GetDimension() == 1))
  {
    return;
  }
  TH1 *h_0 = (TH1*)histogram->Clone(Form("%s_0",histogram->GetName()));
  const TAxis * const xAxis = histogram->GetXaxis();
  const int numBins = xAxis->GetNbins();
  for(int idxBin = 1; idxBin <= numBins; ++idxBin)
  {
    const double binContent = histogram->GetBinContent(idxBin);
    const double binError = histogram->GetBinError(idxBin);
    const double binWidth = xAxis->GetBinWidth(idxBin);
    histogram->SetBinContent(idxBin, binContent/binWidth);
    histogram->SetBinError(idxBin, binError/binWidth);
  }
  /*
  double n, en;
  n = h_0->IntegralAndError(1,numBins, en);
  printf("histo integral: %g +- %g, ",n,en);
  n = histogram->IntegralAndError(1,numBins, en);
  printf("\t after divideByBinWidth %g +- %g \n",n,en);
  */
}

void PlotHistos1DAndRatioPlot() {
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);


  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);

  gStyle->SetPadTickX(1);
  gStyle->SetPadTickY(1);

  // use large Times-Roman fonts
  gStyle->SetTextFont(132);
  gStyle->SetTextSize(0.05);
	
  gStyle->SetLabelFont(132,"x");
  gStyle->SetLabelFont(132,"y");
  gStyle->SetLabelFont(132,"z");
	
  gStyle->SetLabelSize(0.05,"x");
  gStyle->SetLabelSize(0.05,"y");
  gStyle->SetLabelSize(0.05,"z");
	
  gStyle->SetTitleSize(0.06,"x");
  gStyle->SetTitleSize(0.06,"y");
  gStyle->SetTitleSize(0.06,"z");

  gStyle->SetTitleOffset(0.85,"x");
  gStyle->SetTitleOffset(1.0,"y");

  gStyle->SetNdivisions(505, "x");
  gStyle->SetNdivisions(505, "y");





  
  
  std::string sipFile        = "sipFile";
  std::string sHistoName     = "sHistoName";
  std::string sLegend        = "sLegend";
  std::string sHistoNorm     = "sHistoNorm";
  std::string sLineColor     = "sLineColor";
  std::string sMarkerColor   = "sMarkerColor";
  std::string sMarkerStyle   = "sMarkerStyle";

  // ------- Settings --------------------------------------------------------
  std::vector<std::map<std::string, std::string>> vHistoDetails;
  std::string sEra = "2018";
  
  /*
  // OPT1
  std::string sExt = "wCouplingFix";
  std::string sExt1 = "HHWgtIntr2getReWgt_wCouplingFix"; int histoVersion = 2; // histoVersion: 1 for HHWgtIntr2getWgt, 2 for HHWgtIntr2getReWgt. OPT1
  */
  
  // OPT2
  std::string sExt = "woCouplingFix";
  std::string sExt1 = "HHWgtIntr2getWgt_woCouplingFix"; int histoVersion = 1; // histoVersion: 1 for HHWgtIntr2getWgt, 2 for HHWgtIntr2getReWgt. OPT2
  
  
  std::string sVersion0 = Form("%s_20210312_hh_3l_%s_Check_SM_LOtoNLOrwgt_4v",sEra.c_str(),sEra.c_str());
  std::string sVersion = Form("%s_20210312_hh_3l_%s_Check_SM_LOtoNLOrwgt_4v_%s",sEra.c_str(),sEra.c_str(),sExt.c_str());
  std::string sHHDecayMode = "hh_4v";
  std::string sSelection = "Tight_OS";
  
  /*
  std::string sVersion0 = Form("%s_hh_bb1l_snandan_final_LBN_w_correct_LO_weight_ggf_vbf_no_split_sigweight0p8_hh_2b2v_sl",sEra.c_str());
  std::string sVersion = Form("%s_hh_bb1l_snandan_final_LBN_w_correct_LO_weight_ggf_vbf_no_split_sigweight0p8_hh_2b2v_sl_%s",sEra.c_str(),sExt.c_str());
  std::string sHHDecayMode = "hh_2b2v_sl";
  std::string sSelection = "Tight";
  */
  
  double xsection_HH_SM_NLO = 31.05; // fb
 
  // analyze_HHLOvsNLO:
  vHistoDetails.push_back({			  
      {sipFile,      Form("/home/ssawant/ana/hhwwww/20201102_BDTTraining/Datacards_3l/ggHH_SM_LO_vs_NLO/analyze_HHatLOvsNLO/%s/analyze_signal_ggf_nonresonant_cHHH1_%s*.root",sVersion.c_str(),sHHDecayMode.c_str())},
      {sHistoName,   Form("HHatLOvsNLO_OS_Tight/sel/evt/signal_ggf_nonresonant_cHHH1_hh/gen_mHH_%i",histoVersion)},
      {sLegend,      "NLO"},
      {sHistoNorm,   Form("%g",1000. / xsection_HH_SM_NLO)},
      {sLineColor,   "1"},
      {sMarkerColor, "1"},
      {sMarkerStyle, "24"}
    });
  
  vHistoDetails.push_back({			  
      {sipFile,      Form("/home/ssawant/ana/hhwwww/20201102_BDTTraining/Datacards_3l/ggHH_SM_LO_vs_NLO/analyze_HHatLOvsNLO/%s/analyze_signal_ggf_nonresonant_node_*%s*.root",sVersion.c_str(),sHHDecayMode.c_str())},
      {sHistoName,   Form("HHatLOvsNLO_OS_Tight/sel/evt/signal_ggf_nonresonant_hh/gen_mHH_HHrwgt_LOtoNLOrwgt_%i",histoVersion)},
      {sLegend,      "LO #Sigma (HH reweights) * LOtoNLO weight"},
      {sHistoNorm,   "1."},
      {sLineColor,   "3"},
      {sMarkerColor, "3"},
      {sMarkerStyle, "20"}
    });

  vHistoDetails.push_back({			  
      {sipFile,      Form("/home/ssawant/ana/hhwwww/20201102_BDTTraining/Datacards_3l/ggHH_SM_LO_vs_NLO/analyze_HHatLOvsNLO/%s/analyze_signal_ggf_nonresonant_node_sm_%s*.root",sVersion.c_str(),sHHDecayMode.c_str())},
      {sHistoName,   Form("HHatLOvsNLO_OS_Tight/sel/evt/signal_ggf_nonresonant_hh/gen_mHH_HHrwgt_%i",histoVersion)},
      {sLegend,      "LO SM (HH reweights)"},
      {sHistoNorm,   "1."},
      {sLineColor,   "28"},
      {sMarkerColor, "28"},
      {sMarkerStyle, "25"}
    });

  vHistoDetails.push_back({			  
      {sipFile,      Form("/home/ssawant/ana/hhwwww/20201102_BDTTraining/Datacards_3l/ggHH_SM_LO_vs_NLO/analyze_HHatLOvsNLO/%s/analyze_signal_ggf_nonresonant_node_sm_%s*.root",sVersion.c_str(),sHHDecayMode.c_str())},
      {sHistoName,   Form("HHatLOvsNLO_OS_Tight/sel/evt/signal_ggf_nonresonant_hh/gen_mHH_HHrwgt_LOtoNLOrwgt_%i",histoVersion)},
      {sLegend,      "LO SM (HH reweights) * LOtoNLO weight"},
      {sHistoNorm,   "1."},
      {sLineColor,   "4"},
      {sMarkerColor, "4"},
      {sMarkerStyle, "23"}
    });

  
  
  std::string sXaxisName = "gen m_{HH} [GeV]";
  std::string sYaxisName = "No. of events";
  std::string sSaveAs = Form("gen_mHH_SM_LO_vs_NLO_%s_%s_%s_20210317_3_logX",sEra.c_str(),sVersion0.c_str(),sExt1.c_str());
  double      rangeXaxis[3] = {0, 250, 1200}; // rangeXaxis[0]: set axis range flag
  double      rangeYaxis[3] = {1, 1e-7, 1e-2}; // rangeYaxis[0]: set axis range flag
  double      rangeYaxisRatioPlot[3] = {1, -1, 1}; // rangeYaxis[0]: set axis range flag
  int         rebin = 1;
  double      normalizeHistos[2] = {1, 1}; // normalizeHistos[0]: mode, normalizeHistos[1]: norm. value
                                             // mode 0: don't scale/normalize histograms
                                             // mode 1: normalize w.r.t. area under histo
                                             // mode 2: normalize w.r.t. height of the histo
                                             // mode 3: normalize by a factor set with 'sHistoNorm' variable
  int         setLogX = 1;
  int         setLogY = 1;
  int         makeRatioPlots = 1; // compare shapes by making ratio plot w.r.t. the 1st histogram
                                  // 0: disable ratio plot
  bool        normalizeRatioPlots = false;
  bool        histoDivideByBinWidth = true;

  double      markerSize = 0.9;

  if ( histoDivideByBinWidth ) rebin = 1;
  // ------- Settings - xxxxxxxx ------------------------------------------------




  
  

  std::vector<TH1*> vHistos;
  std::vector<TH1*> vHistosRatio;
  for (size_t iHisto=0; iHisto < vHistoDetails.size(); iHisto++) {
    std::map<std::string, std::string> iHistoDetails = vHistoDetails[iHisto];
    std::string sipFile1    = iHistoDetails[sipFile];
    std::string sHistoName1 = iHistoDetails[sHistoName];
    std::cout << std::endl;
    printf("inFile: %s\n  histo: %s\n",sipFile1.c_str(),sHistoName1.c_str());
    
    //TFile *tFIn = new TFile(sipFile1.data());
    TFile *tFIn = getTFile(sipFile1.data());
    if ( ! (tFIn && tFIn->IsOpen()) ) {
      printf("File %s couldn't open \t\t\t *** ERROR **** \n",sipFile1.data());
      continue;
    }

        
    TH1 *histo = nullptr;
    histo = (TH1*)tFIn->Get(sHistoName1.data());
    if ( ! histo) {
      printf("Couldn't fetch histogram %s from file %s  \t\t\t *** ERROR **** \n",sHistoName1.data(),sipFile1.data());
      continue;
    }

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
    if (std::abs(normalizeHistos[0] - 3) < 1e-3) { // normalize by a factor set with 'sHistoNorm' variable
      double scale = std::stod(iHistoDetails[sHistoNorm]);
      printf("  kNormalize: %g",scale);
      std::cout << std::endl;
      histo->Scale(scale);
    }

    if ( histoDivideByBinWidth ) divideByBinWidth(histo);
    
    histo->Rebin(rebin);
   

    vHistos.push_back(histo);

    if (makeRatioPlots != 0 && iHisto > 0) {
      TH1 *histoRatio = (TH1*)histo->Clone(Form("%s_ratio",histo->GetName()));

      // normalize histoRatio w.r.t. histo=0 area
      double hArea0  = vHistos[0]->Integral(1, vHistos[0]->GetNbinsX());
      double hArea   = histoRatio->Integral(1, histoRatio->GetNbinsX());
      double scale1  = hArea0 / hArea;
      if (normalizeRatioPlots) histoRatio->Scale(scale1);

      // ratio
      histoRatio->Divide(vHistos[0]);
      for (int i = 1; i <= histoRatio->GetNbinsX(); i++)
      {
	double binContent = histoRatio->GetBinContent(i);
	if (std::abs(binContent - 0.) < 1e-6) histoRatio->SetBinContent(i, -9999.);
	else                                  histoRatio->SetBinContent(i, binContent - 1.);
      }
      vHistosRatio.push_back(histoRatio);
    }
    
  }

  
  double yMin, yMax, yMin_ratio, yMax_ratio;
  getHistogramsYRange(vHistos, yMin, yMax, setLogY);
  printf("  yRange: %f to %f\n",yMin,yMax);
  getHistogramsYRange(vHistosRatio, yMin_ratio, yMax_ratio);
  printf("  yRange ratio: %f to %f\n",yMin_ratio,yMax_ratio);

  if (setLogY)
  {
    yMax = (yMax) * 10;
  }
  else
    yMax = yMax * 1.4;
  yMax_ratio = yMax_ratio * 1.3;
  yMin_ratio = yMin_ratio * 1.3;
  if (yMax_ratio >  1.5 ) yMax_ratio =  1.5;
  if (yMin_ratio < -1.5 ) yMin_ratio = -1.5;
  if (yMax_ratio <  0.5 ) yMax_ratio =  0.5;
  if (yMin_ratio > -0.5 ) yMin_ratio = -0.5;

  

  TCanvas *c1 = new TCanvas("c1","c1", 600, 700);
  //TCanvas *c1 = new TCanvas();
  //c1->SetWindowSize(c1->GetWw(), 1.3*c1->GetWh());
  c1->cd();
  TPad *pad1 = new TPad("pad1", "pad1", 0, 0.3, 1, 1);
  pad1->Draw();
  pad1->SetLogx(setLogX);
  pad1->SetLogy(setLogY);
  TPad *pad2 = new TPad("pad2", "pad2", 0, 0, 1, 0.3);
  pad2->Draw();
  //gPad->SetLogy(setLogY);
  pad2->SetLogx(setLogX);
  
  pad1->SetBottomMargin(0.01);
    
  pad2->SetTopMargin(0.03);
  pad2->SetBottomMargin(0.3);

  pad1->SetRightMargin(0.05);
  pad2->SetRightMargin(0.05);
  
  pad1->SetLeftMargin(0.13);
  pad2->SetLeftMargin(0.13);


 
  TLegend *leg = new TLegend(0.5,0.75,1.0,1.0);
  leg->SetBorderSize(0);
  leg->SetFillColor(0);
  leg->SetMargin(0.1);
  
  for (size_t iHisto=0; iHisto < vHistoDetails.size(); iHisto++) {
    std::map<std::string, std::string> iHistoDetails = vHistoDetails[iHisto];
    std::string sLegend1 = iHistoDetails[sLegend];
    std::string sLineColor1 = iHistoDetails[sLineColor];
    std::string sMarkerColor1 = iHistoDetails[sMarkerColor];
    std::string sMarkerStyle1 = iHistoDetails[sMarkerStyle];
    //std::string  = iHistoDetails[];

    TH1 *h = vHistos[iHisto];

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
    h->SetMarkerSize(markerSize);

    h->GetXaxis()->SetTitleSize(0.06);
    h->GetXaxis()->SetLabelSize(0.05);
    h->GetXaxis()->SetTitleOffset(0.85);
    if (std::abs(rangeXaxis[0] - 1) < 1e-3) {
      h->GetXaxis()->SetRangeUser(rangeXaxis[1], rangeXaxis[2]);
    }

    h->GetYaxis()->SetTitleSize(0.06);
    h->GetYaxis()->SetLabelSize(0.05);
    h->GetYaxis()->SetTitleOffset(1.0);    
    h->GetYaxis()->SetRangeUser(yMin, yMax);
    if (std::abs(rangeYaxis[0] - 1) < 1e-3) {
      h->GetYaxis()->SetRangeUser(rangeYaxis[1], rangeYaxis[2]);
    }
    
    if ( ! sXaxisName.empty()) {
      h->GetXaxis()->SetTitle(sXaxisName.data());
    }
    if ( ! sYaxisName.empty()) {
      h->GetYaxis()->SetTitle(sYaxisName.data());
    }
    if (std::abs(normalizeHistos[0] - 1) < 1e-3) h->GetYaxis()->SetTitle("A.U.");
    
    pad1->cd();
    if ((int)iHisto == 0) h->Draw("E1P");
    else                  h->Draw("same E1P");

    if ( ! sLegend1.empty()) {
      leg->AddEntry(h, sLegend1.data(), "p");
    }

    // ratio plots
    if (makeRatioPlots != 0 && iHisto > 0) {
      TH1 *hRatio = vHistosRatio[iHisto - 1];
      
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
      hRatio->SetMarkerSize(markerSize);

      if (std::abs(rangeXaxis[0] - 1) < 1e-3) {
	hRatio->GetXaxis()->SetRangeUser(rangeXaxis[1], rangeXaxis[2]);
      }
      hRatio->GetYaxis()->SetRangeUser(-1, 1);
      if (std::abs(rangeYaxisRatioPlot[0] - 1) < 1e-3) {
	hRatio->GetYaxis()->SetRangeUser(rangeYaxisRatioPlot[1], rangeYaxisRatioPlot[2]);
      }
    
      if ( ! sXaxisName.empty()) {
	hRatio->GetXaxis()->SetTitle(sXaxisName.data());
      }
      hRatio->GetYaxis()->SetTitle("Ratio");

      auto xLabSize = hRatio->GetXaxis()->GetLabelSize();
      auto xTitleSize = hRatio->GetXaxis()->GetTitleSize();
      auto xOffSet = hRatio->GetXaxis()->GetTitleOffset();
      auto yLabSize = hRatio->GetYaxis()->GetLabelSize();
      auto yTitleSize = hRatio->GetYaxis()->GetTitleSize();
      //auto yOffSet = hRatio->GetYaxis()->GetTitleOffset();


      hRatio->GetXaxis()->SetTitleSize(4.0*xTitleSize);
      hRatio->GetXaxis()->SetLabelSize(3.0*xLabSize);
      hRatio->GetXaxis()->SetTitleOffset(0.8*xOffSet);

      hRatio->GetYaxis()->SetTitleSize(4.0*yTitleSize);
      hRatio->GetYaxis()->SetLabelSize(3.0*yLabSize);

      hRatio->GetYaxis()->SetTitleOffset(0.4);

      hRatio->GetYaxis()->SetNdivisions(505);

      

      
          
      pad2->cd();
      if ((int)iHisto == 1) hRatio->Draw("E1P");
      else                  hRatio->Draw("same E1P");

      if ((int)iHisto == 1)
      {
	TAxis* xAxis_bottom = hRatio->GetXaxis();
	TF1 *line = new TF1("line","0", xAxis_bottom->GetXmin(), xAxis_bottom->GetXmax());
	line->SetLineStyle(3);
	//line->SetLineWidth(1.5);
	line->SetLineColor(kBlack);
	line->Draw("same");
      }
    }
  }
  pad1->cd();
  leg->Draw();

  
  c1->SaveAs(Form("%s.png",sSaveAs.data()));
  
}
