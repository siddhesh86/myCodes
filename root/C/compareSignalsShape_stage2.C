
#include <cstdlib>
//#include "ordered_map.h"
#include <unordered_map>

void getHistoIntegral(TH1* h, double &integral, double &eIntegral)
{
  //double integral, eIntegral;
  integral = h->IntegralAndError(1, h->GetNbinsX(), eIntegral);
  //printf(" %f +- %f ",integral,eIntegral);
}

void getHistogramsYRange(std::vector<TH1*> histograms, double &yMin, double &yMax)
{ 
  yMax = -9999;
  yMin =  9999;
  for (const auto& histogram: histograms)
  {
    double yMax_tmp = histogram->GetMaximum();
    double yMin_tmp = histogram->GetMinimum();
    if (yMax_tmp > yMax) yMax = yMax_tmp;
    if (yMin_tmp < yMin && yMin_tmp > -9990.) yMin = yMin_tmp;
  }
}

void plotHistograms(std::vector<TH1*> histograms,
		    std::vector<std::string> histogram_labels,
		    std::string xaxis_label,
		    std::string yaxis_label, 
		    bool setLogY,
		    double normalizeHistos[],
		    bool printHistogramIntegrals,
		    std::string sSaveAs
  )
{

  std::vector<int> histo_line_color   = { 1,  2,  4,  6,  8,  9, 28, 46, 38};
  std::vector<int> histo_marker_style = {20, 20, 20, 20, 20, 20, 20, 20, 20};


  
  int         makeRatioPlots = 1; // compare shapes by making ratio plot w.r.t. the 1st histogram
                                  // 0: disable ratio plot
  
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
  
  pad1->SetBottomMargin(0.01);
    
  pad2->SetTopMargin(0.03);
  pad2->SetBottomMargin(0.3);
  
 
  TLegend *leg = new TLegend(0.3,0.73,0.95,0.95);


  std::vector<TH1*>   vHistos;
  std::vector<TH1*>   vHistosRatio;
  std::vector<double> vHistos_integral;
  std::vector<double> vHistos_integralError;
  for (size_t iHisto=0; iHisto < histograms.size(); iHisto++)
  {
    TH1 *histo = histograms[iHisto];

    double histoIntegral, histoIntegralError;
    getHistoIntegral(histo, histoIntegral, histoIntegralError);
    vHistos_integral.push_back(histoIntegral);
    vHistos_integralError.push_back(histoIntegralError);


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

    
    vHistos.push_back(histo);

    
    if (makeRatioPlots != 0 && iHisto > 0) {
      TH1 *histoRatio = (TH1*)histo->Clone(Form("%s_ratio",histo->GetName()));

      /*
      // normalize histoRatio w.r.t. histo=0 area
      double hArea0  = vHistos[0]->Integral(1, vHistos[0]->GetNbinsX());
      double hArea   = histoRatio->Integral(1, histoRatio->GetNbinsX());
      double scale1  = hArea0 / hArea;
      histoRatio->Scale(scale1);
      */
      
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
  getHistogramsYRange(vHistos, yMin, yMax);
  printf("yRange: %f to %f\n",yMin,yMax);
  getHistogramsYRange(vHistosRatio, yMin_ratio, yMax_ratio);
  printf("yRange ratio: %f to %f\n",yMin_ratio,yMax_ratio);
  
  yMax = yMax * 1.4;
  yMax_ratio = yMax_ratio * 1.3;
  yMin_ratio = yMin_ratio * 1.3;
  if (yMax_ratio >  1.5 ) yMax_ratio =  1.5;
  if (yMin_ratio < -1.5 ) yMin_ratio = -1.5;
  if (yMax_ratio <  0.5 ) yMax_ratio =  0.5;
  if (yMin_ratio > -0.5 ) yMin_ratio = -0.5;
  
  
  
  for (size_t iHisto=0; iHisto < vHistos.size(); iHisto++)
  {
    TH1 *h = vHistos[iHisto];
    std::string sLegend1 = histogram_labels[iHisto];
    double histoIntegral = vHistos_integral[iHisto];
    double histoIntegralError = vHistos_integralError[iHisto];
    
    h->SetLineColor(histo_line_color[iHisto]);
    h->SetMarkerColor(histo_line_color[iHisto]);
    h->SetMarkerStyle(histo_marker_style[iHisto]);
    
    h->GetXaxis()->SetTitleSize(0.06);
    h->GetXaxis()->SetLabelSize(0.05);
    h->GetXaxis()->SetTitleOffset(0.85);

    h->GetYaxis()->SetTitleSize(0.06);
    h->GetYaxis()->SetLabelSize(0.05);
    h->GetYaxis()->SetTitleOffset(0.85);

    h->GetYaxis()->SetRangeUser(yMin, yMax);

    h->GetXaxis()->SetTitle(xaxis_label.c_str());
    h->GetYaxis()->SetTitle(yaxis_label.c_str());
    if (std::abs(normalizeHistos[0] - 1) < 1e-3) h->GetYaxis()->SetTitle("A.U.");

    pad1->cd();
    if ((int)iHisto == 0) h->Draw("EP");
    else                  h->Draw("same EP");

    if ( ! sLegend1.empty()) {
      if ( ! printHistogramIntegrals )
      {
	leg->AddEntry(h, sLegend1.data(), "lep");
      }
      else {
	leg->AddEntry(h, Form("%s (n=%.2f #pm %.2f)",sLegend1.data(),histoIntegral, histoIntegralError), "lep");
      }
    }

    // ratio plots
    if (makeRatioPlots != 0 && iHisto > 0) {
      TH1 *hRatio = vHistosRatio[iHisto - 1];

      hRatio->SetLineColor(histo_line_color[iHisto]);
      hRatio->SetMarkerColor(histo_line_color[iHisto]);
      hRatio->SetMarkerStyle(histo_marker_style[iHisto]);

      hRatio->GetYaxis()->SetRangeUser(yMin_ratio, yMax_ratio);

      hRatio->GetXaxis()->SetTitle(xaxis_label.c_str());
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

      hRatio->GetYaxis()->SetTitleOffset(0.35);

      hRatio->GetYaxis()->SetNdivisions(505);
      
          
      pad2->cd();
      if ((int)iHisto == 1) hRatio->Draw("EP");
      else                  hRatio->Draw("same EP");

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



class SpecialMap {
public:
  void Insert(const std::string& key, std::vector<std::string> value);
  int  NEntries() { return vKeys.size(); };
  void GetValue(int index, std::string& key, std::vector<std::string> &value);
  
private:
  std::vector<std::string> vKeys;
  std::map<std::string, std::vector<std::string>> data_;
};


void SpecialMap::Insert(const std::string& key, std::vector<std::string> value) {
  vKeys.push_back(key);
  data_[key] = value;
}


void SpecialMap::GetValue(int index, std::string& key, std::vector<std::string> &value)
{
  key   = vKeys[index];
  value = data_[key];
}

void compareSignalsShape_stage2()
{
  SpecialMap sHistos_signals;  

  //std::string sInFile = "addSystFakeRates_hh_3l_hh_3l_OS_MVAOutput_SM_RUN2_ram_2021Feb12_hh_multilepton_3ldatacards_era2017.root";
  //std::string sInFile = "addSystFakeRates_hh_2lss_hh_2lss_SS_MVAOutput_SM_RUN2_2021Feb10_2lss0tau_2017datacards_wLFRFullSysts.root";


  //std::string sInFile = "/hdfs/local/ram/hhAnalysis/2017/2021Feb12_hh_multilepton_3ldatacards_era2017/histograms/hh_3l/Tight_OS/hadd/hadd_stage2_Tight_OS_RUN2.root";


    /*
  std::string sSaveAs = "MVAOutput_SM_BMs_LO_3l_test";
  sHistos_signals.Insert(
    "LO_SM",
    {
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_hh/MVAOutput_SM"
    }
    );

  sHistos_signals.Insert(
    "LO_SM_total",            // label for signal_total_i histogrsls
    {
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_hh_tttt/MVAOutput_SM", // histograms directory/name for all signal components pass as vector<string>, which will be added to get signal_total_i
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_hh_ttww/MVAOutput_SM",
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_hh_ttzz/MVAOutput_SM",
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_hh_wwww/MVAOutput_SM",
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_hh_zzww/MVAOutput_SM",
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_hh_zzzz/MVAOutput_SM",
    }
    );

   */

  /*
  std::string sSaveAs = "MVAOutput_SM_BMs_LO_3l";
  sHistos_signals.Insert(
    "LO_SM", // label for total signal histogrsls
    {
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_hh/MVAOutput_SM" // histograms directory/name for all signal component 
    }
    );

  sHistos_signals.Insert(
    "LO_BM2",
    {
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_hh/MVAOutput_BM2"
    }
    );

  sHistos_signals.Insert(
    "LO_BM5",
    {
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_hh/MVAOutput_BM5"
    }
    );

  sHistos_signals.Insert(
    "LO_BM9",
    {
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_hh/MVAOutput_BM9"
    }
    );
  
  sHistos_signals.Insert(
    "LO_BM12",
    {
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_hh/MVAOutput_BM12"
    }
    );
  */

  /*
  std::string sSaveAs = "MVAOutput_SM_BMs_NLO_3l";
  sHistos_signals.Insert(
    "NLO_SM",
    {
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_cHHH1_hh/MVAOutput_SM"
    }
    );

  sHistos_signals.Insert(
    "NLO_BM2",
    {
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_cHHH1_hh/MVAOutput_BM2"
    }
    );

  sHistos_signals.Insert(
    "NLO_BM5",
    {
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_cHHH1_hh/MVAOutput_BM5"
    }
    );

  sHistos_signals.Insert(
    "NLO_BM9",
    {
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_cHHH1_hh/MVAOutput_BM9"
    }
    );
   
  sHistos_signals.Insert(
    "NLO_BM12",
    {
      "hh_3l_OS_Tight/sel/datacard/signal_ggf_nonresonant_cHHH1_hh/MVAOutput_BM12"
    }
    );
  */

  
  // 'm3l', 'diHiggsVisMass', 'mSFOS2l_closestToZ', 'dr_LeptonIdx3_AK4jNear_Approach2', 'dr_LeptonIdx3_2j_inclusive1j_Approach2', 'dr_los_min', 'dr_los_max', 'nSFOS_3l', 'met_LD',
  std::string sInFile = "/hdfs/local/ram/hhAnalysis/2017/2021Feb12_hh_multilepton_3ldatacards_era2017/histograms/hh_3l/Tight_OS/hadd/hadd_stage2_Tight_OS_RUN2.root";
  //std::string sInFile = "/hdfs/local/ram/hhAnalysis/2017/2021Feb12_hh_multilepton_3ldatacards_era2017/histograms/hh_3l/Tight_OS/hadd/hadd_stage2_Tight_OS_RUN2.root";
  //std::string sVariable = "m3l";  int rebin = 4;
  //std::string sVariable = "dihiggsVisMass_sel"; int rebin = 4;
  //std::string sVariable = "mSFOS2l_closestToZ"; int rebin = 1;
  //std::string sVariable = "dr_LeptonIdx3_AK4jNear_Approach2"; int rebin = 4;
  //std::string sVariable = "dr_LeptonIdx3_2j_inclusive1j_Approach2"; int rebin = 4;
  //std::string sVariable = "dr_los_min"; int rebin = 4;
  //std::string sVariable = "dr_los_max"; int rebin = 4;
  std::string sVariable = "numSameFlavor_OS_3l"; int rebin = 1;
  //std::string sVariable = "met_LD"; int rebin = 4;
  //std::string sVariable = "";
  
  std::string sSaveAs = Form("ggHH_SM_LO_vs_NLO_3l_%s",sVariable.c_str());
  sHistos_signals.Insert(
    "ggHH SM LO (1 pb)",
    {
      Form("hh_3l_OS_Tight/sel/evt/signal_ggf_nonresonant_hh/%s",sVariable.c_str())
    }
    );

  sHistos_signals.Insert(
    "ggHH SM NLO (1 pb)",
    {
      Form("hh_3l_OS_Tight/sel/evt/signal_ggf_nonresonant_cHHH1_hh/%s",sVariable.c_str())
    }
    );
  

  /*
  //'leptonPairMass_sel', 'dihiggsVisMass_sel', 'met_LD', 'dR_ll', 'dR_l_Wjets_min', 'dR_l_leadWjet_min', 'dR_l_Wjets_max', 'dR_l_leadWjet_max', 'dR_2j_fromW1', 'mT_lep1', 
  std::string sInFile = "/hdfs/local/ssawant/hhAnalysis/2017/20210213_hh_2lss_leq1tau_2017_Datacards_XGammaNonFakeFix/histograms/hh_2lss_leq1tau/Tight_SS/hadd/hadd_stage2_Tight_SS_RUN2.root";
  //std::string sVariable = "leptonPairMass"; int rebin = 4;
  //std::string sVariable = "dihiggsVisMass"; int rebin = 4;
  //std::string sVariable = "met_LD"; int rebin = 4;
  //std::string sVariable = "dR_ll"; int rebin = 4;
  //std::string sVariable = "dR_l_Wjets_min"; int rebin = 4;
  //std::string sVariable = "dR_l_leadWjet_min"; int rebin = 4;
  //std::string sVariable = "dR_l_Wjets_max"; int rebin = 4;
  //std::string sVariable = "dR_l_leadWjet_max"; int rebin = 4;
  //std::string sVariable = "dR_2j_fromW1"; int rebin = 4;
  std::string sVariable = "mT_lep1_met"; int rebin = 4;

  std::string sSaveAs = Form("ggHH_SM_LO_vs_NLO_2lss_leq1tau_%s",sVariable.c_str());
  sHistos_signals.Insert(
    "ggHH SM LO (1 pb)",
    {
      Form("hh_2lss_leq1tau_SS_Tight/sel/evt/signal_ggf_nonresonant_hh/%s",sVariable.c_str())
    }
    );

  sHistos_signals.Insert(
    "ggHH SM NLO (1 pb)",
    {
      Form("hh_2lss_leq1tau_SS_Tight/sel/evt/signal_ggf_nonresonant_cHHH1_hh/%s",sVariable.c_str())
    }
    );
  */

  

  std::string xaxis_label = sVariable;
  std::string yaxis_label = "Events"; 

  bool setLogY = false;
  bool printHistogramIntegrals = true;
  double xsection_HH_SM_NLO = 31.05; // fb
  std::string sKey_HH_SM_NLO = "ggHH SM NLO (1 pb)";

  std::vector<std::string> histogram_labels;

  //int rebin = 4;
  double      normalizeHistos[2] = {1, 1}; // normalizeHistos[0]: mode, normalizeHistos[1]: norm. value
                                             // mode 0: don't scale/normalize histograms
                                             // mode 1: normalize w.r.t. area under histo
                                             // mode 2: normalize w.r.t. height of the histo


  

  std::vector<TH1*> histograms;
  

  TFile *fIn = new TFile(sInFile.c_str());
  printf("fIn: %s \n",sInFile.c_str());
  if ( ! fIn->IsOpen() )
  {
    printf("File %s couldn't open \t **** ERROR **** \n",sInFile.c_str());
    return;
  }

  for (int iHistos_signal = 0; iHistos_signal < sHistos_signals.NEntries(); iHistos_signal++)
  {
    std::string sSignal;
    std::vector<std::string> signal_list;
    sHistos_signals.GetValue(iHistos_signal, sSignal, signal_list);
    
    double histoIntegral, histoIntegralError;
    TH1D *hSignalTotal = 0;
    for(const auto& sHisto: signal_list)
    {
      //std::cout << "sSignal: " << sSignal << " \t " << sHisto << "\n";

      TH1D *hSignal_component = 0;
      hSignal_component = (TH1D*)fIn->Get(sHisto.c_str());
      if ( ! hSignal_component )
      {
	printf("Couldn't read histo %s  \t **** ERROR **** \n",sHisto.c_str());
	continue;
      }

      if ( ! hSignalTotal )
      {
	hSignalTotal = (TH1D*)hSignal_component->Clone(Form("h%s",sSignal.c_str()));
      }
      else
      {
	hSignalTotal->Add(hSignal_component);
      }
      getHistoIntegral(hSignal_component, histoIntegral, histoIntegralError);
      printf("sSignal: %s \t %s \t %f +- %f \n",sSignal.c_str(),sHisto.c_str(),histoIntegral, histoIntegralError);
    }
    getHistoIntegral(hSignalTotal, histoIntegral, histoIntegralError);
    printf("sSignal: %s \t %f +- %f \n",sSignal.c_str(),histoIntegral, histoIntegralError);

    if (sSignal.compare(sKey_HH_SM_NLO) == 0)
    {
      double scale = 1000. / xsection_HH_SM_NLO;
      hSignalTotal->Scale(scale);
      printf("HH_SM_NLO histogram scale to %f (i.e. 1000. / (%f fb)) \n",scale,xsection_HH_SM_NLO);

      getHistoIntegral(hSignalTotal, histoIntegral, histoIntegralError);
      printf("Now sSignal: %s \t %f +- %f \n",sSignal.c_str(),histoIntegral, histoIntegralError);
    }

    if (rebin > 1) hSignalTotal->Rebin(rebin);
    
    histograms.push_back(hSignalTotal);
    histogram_labels.push_back(sSignal);
  }



  plotHistograms(
    histograms,
    histogram_labels,
    xaxis_label,
    yaxis_label, 
    setLogY,
    normalizeHistos,
    printHistogramIntegrals,
    sSaveAs
    );

}
