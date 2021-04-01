

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

  
  sipFile = "denominator_histos_PetrBinning/denom_2017.root";
  sHistoName = "signal_ggf_nonresonant_node_sm_hh_4v_private";
  sLegend = "#mu QCD  (mvaTTH cut 0.85)";
  sXaxis = "reco p_{T} [GeV]";
  sYaxis = "mvaTTH";
  sSaveAs = "test";


  

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


  TAxis *axis;

  axis = h->GetXaxis();
  printf("\nX-axis binning:: %i [",axis->GetNbins());
  for (int i=1; i<=axis->GetNbins(); i++)
  {
    printf(" %g,",axis->GetBinLowEdge(i));
    if (i == axis->GetNbins()) printf(" %g] \n",axis->GetBinUpEdge(i));
  }
  
  axis = h->GetYaxis();
  printf("\nY-axis binning:: %i [",axis->GetNbins());
  for (int i=1; i<=axis->GetNbins(); i++)
  {
    printf(" %g,",axis->GetBinLowEdge(i));
    if (i == axis->GetNbins()) printf(" %g] \n",axis->GetBinUpEdge(i));
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
