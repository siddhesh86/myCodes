


void PrintHistoBinning()
{
  std::string sipFile, sHistoName;
  
  sipFile = "denominator_histos_PetrBinning/denom_2017.root";
  sHistoName = "signal_ggf_nonresonant_node_sm_hh_4v_private";

  int histogramDimension = 2;


  
  TFile *tFIn = new TFile(sipFile.data());
  if ( ! tFIn->IsOpen()) {
    printf("File %s couldn't open \t\t\t *** ERROR **** \n",sipFile.data());
    return;
  }

  
  if (histogramDimension == 1)
  {
    TH1 *h = nullptr;
    h = (TH1*)tFIn->Get(sHistoName.data());
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
  }


  if (histogramDimension == 2)
  {
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
  }
  
}
