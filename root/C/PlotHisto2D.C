

void PlotHisto2D() {
  
  gStyle->SetOptStat(0);
  gStyle->SetOptTitle(0);
  gStyle->SetPadTopMargin(0.10);
  gStyle->SetPadRightMargin(0.12);
  gStyle->SetPadBottomMargin(0.12);
  gStyle->SetPadLeftMargin(0.12);
	
  // use large Times-Roman fonts
  gStyle->SetTextFont(132);
  gStyle->SetTextSize(0.05);
	
  gStyle->SetLabelFont(132,"x");
  gStyle->SetLabelFont(132,"y");
  gStyle->SetLabelFont(132,"z");
	
  gStyle->SetLabelSize(0.05,"x");
  gStyle->SetLabelSize(0.05,"y");
  gStyle->SetLabelSize(0.05,"z");
  gROOT->ForceStyle();
  

  std::string sipFile, sHistoName, sLegend, sXaxis, sYaxis, sSaveAs;
  int setLogZ;

  // muon
  if (1==0) {
  sipFile = "leptonCutEffi_FR_runIndividually_QCD_mu_20200906_5_TEST4_wTTToHadronic_test.root";
  sHistoName = "QCD/muon_mvaTTH0p85_CriteriaDefault/hmvaTTH_vs_pt_mu_mvaTTH0p85_CriteriaDefault_genMatchedToFake";
  sLegend = "#mu QCD  (mvaTTH cut 0.85)";
  sXaxis = "reco p_{T} [GeV]";
  sYaxis = "mvaTTH";
  sSaveAs = "mvaTTH_vs_reco_pt_mu_mvaTTH0p85_QCD";
  }
  if (1==0) {
  sipFile = "leptonCutEffi_FR_runIndividually_QCD_mu_20200906_5_TEST4_wTTToHadronic_test.root";
  sHistoName = "QCD/muon_mvaTTH0p85_CriteriaDefault/hmvaTTH_vs_cone_pt_mu_mvaTTH0p85_CriteriaDefault_genMatchedToFake";
  sLegend = "#mu QCD  (mvaTTH cut 0.85)";
  sXaxis = "cone p_{T} [GeV]";
  sYaxis = "mvaTTH";
  sSaveAs = "mvaTTH_vs_cone_pt_mu_mvaTTH0p85_QCD";
  }
  if (1==0) {
  sipFile = "leptonCutEffi_FR_runIndividually_QCD_mu_20200906_5_TEST4_wTTToHadronic_test.root";
  sHistoName = "QCD/muon_mvaTTH0p5_POGWPL_DeepJetWPI_JetRelIso0p5/hmvaTTH_vs_pt_mu_mvaTTH0p5_POGWPL_DeepJetWPI_JetRelIso0p5_genMatchedToFake";
  sLegend = "#mu QCD  (mvaTTH cut 0.5)";
  sXaxis = "reco p_{T} [GeV]";
  sYaxis = "mvaTTH";
  sSaveAs = "mvaTTH_vs_reco_pt_mu_mvaTTH0p5_QCD";
  }
  if (1==1) {
  sipFile = "leptonCutEffi_FR_runIndividually_QCD_mu_20200906_5_TEST4_wTTToHadronic_test.root";
  sHistoName = "QCD/muon_mvaTTH0p5_POGWPL_DeepJetWPI_JetRelIso0p5/hmvaTTH_vs_cone_pt_mu_mvaTTH0p5_POGWPL_DeepJetWPI_JetRelIso0p5_genMatchedToFake";
  sLegend = "#mu QCD  (mvaTTH cut 0.5)";
  sXaxis = "cone p_{T} [GeV]";
  sYaxis = "mvaTTH";
  sSaveAs = "mvaTTH_vs_cone_pt_mu_mvaTTH0p5_QCD";
  }



  // electron
  if (1==0) {
  sipFile = "leptonCutEffi_FR_runIndividually_QCD_e_20200906_5_TEST4_wTTToHadronic_test.root";
  sHistoName = "QCD/electron_mvaTTH0p8_CriteriaDefault/hmvaTTH_vs_pt_e_mvaTTH0p8_CriteriaDefault_genMatchedToFake";
  sLegend = "e QCD  (mvaTTH cut 0.8)";
  sXaxis = "reco p_{T} [GeV]";
  sYaxis = "mvaTTH";
  sSaveAs = "mvaTTH_vs_reco_pt_e_mvaTTH0p8_QCD";
  }
  if (1==0) {
  sipFile = "leptonCutEffi_FR_runIndividually_QCD_e_20200906_5_TEST4_wTTToHadronic_test.root";
  sHistoName = "QCD/electron_mvaTTH0p8_CriteriaDefault/hmvaTTH_vs_cone_pt_e_mvaTTH0p8_CriteriaDefault_genMatchedToFake";
  sLegend = "e QCD  (mvaTTH cut 0.8)";
  sXaxis = "cone p_{T} [GeV]";
  sYaxis = "mvaTTH";
  sSaveAs = "mvaTTH_vs_cone_pt_e_mvaTTH0p8_QCD";
  }
  if (1==0) {
  sipFile = "leptonCutEffi_FR_runIndividually_QCD_e_20200906_5_TEST4_wTTToHadronic_test.root";
  sHistoName = "QCD/electron_mvaTTH0p3_POGWPL_DeepJetWPT_JetRelIso0p7/hmvaTTH_vs_pt_e_mvaTTH0p3_POGWPL_DeepJetWPT_JetRelIso0p7_genMatchedToFake";
  sLegend = "e QCD  (mvaTTH cut 0.3)";
  sXaxis = "reco p_{T} [GeV]";
  sYaxis = "mvaTTH";
  sSaveAs = "mvaTTH_vs_reco_pt_e_mvaTTH0p3_QCD";
  }
  if (1==0) {
  sipFile = "leptonCutEffi_FR_runIndividually_QCD_e_20200906_5_TEST4_wTTToHadronic_test.root";
  sHistoName = "QCD/electron_mvaTTH0p3_POGWPL_DeepJetWPT_JetRelIso0p7/hmvaTTH_vs_cone_pt_e_mvaTTH0p3_POGWPL_DeepJetWPT_JetRelIso0p7_genMatchedToFake";
  sLegend = "e QCD  (mvaTTH cut 0.3)";
  sXaxis = "cone p_{T} [GeV]";
  sYaxis = "mvaTTH";
  sSaveAs = "mvaTTH_vs_cone_pt_e_mvaTTH0p3_QCD";
  }


  

  setLogZ = 1;

  
  TFile *tFIn = new TFile(sipFile.data());
  if ( ! tFIn->IsOpen()) {
    printf("File %s couldn't open \t\t\t *** ERROR **** \n",sipFile.data());
    return;
  }

  TH2D *h = nullptr;
  h = (TH2D*)tFIn->Get(sHistoName.data());
  if ( ! h) {
    printf("Couldn't fetch histogram %s from file %s  \t\t\t *** ERROR **** \n",sHistoName.data(),sipFile.data());
    return;
  }  

  TCanvas *c1 = new TCanvas("c1","c1", 600, 450);
  c1->cd();


  gPad->SetLogz(setLogZ);

  h->GetXaxis()->SetTitle(sXaxis.data());
  h->GetYaxis()->SetTitle(sYaxis.data());

  h->Draw("colz");
  
  
  TLegend *leg = new TLegend(0.2,0.89,0.8,0.99);
  leg->SetHeader(sLegend.data());

  leg->Draw();

  c1->SaveAs(Form("%s.png",sSaveAs.data()));
}
