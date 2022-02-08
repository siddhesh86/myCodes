
#include <TFile.h>
#include <TString.h>
#include <TH1.h>
#include <TMath.h>
#include <TROOT.h>
#include <TStyle.h>

#include <string>
#include <vector>
#include <map>
#include <iostream>
#include <iomanip>
#include <assert.h>
#include <algorithm>
#include <iomanip>
#include <boost/algorithm/string.hpp>


TH1* loadHistogram(TFile* inputFile, const std::string& histogramName)
{
  TH1* histogram = dynamic_cast<TH1*>(inputFile->Get(histogramName.data()));
  if ( !histogram ) {
    //std::cerr << "Failed to load histogram = " << histogramName << " from file = " << inputFile->GetName() << " !!" << std::endl;
    //assert(0);
    return 0;
  }
  if ( !histogram->GetSumw2N() ) histogram->Sumw2();
  return histogram;
}

double
compIntegral(const TH1 * histogram,
             bool includeUnderflowBin = false,
             bool includeOverflowBin = false)
{
  const int numBins  = histogram->GetNbinsX();
  const int firstBin = includeUnderflowBin ? 0           : 1;
  const int lastBin  = includeOverflowBin  ? numBins + 1 : numBins;

  double sumBinContent = 0.;
  for(int iBin = firstBin; iBin <= lastBin; ++iBin)
  {
    sumBinContent += histogram->GetBinContent(iBin);
  }
  return sumBinContent;
}

double 
square(double x)
{
  return x*x;
}

double
compIntegralErr(const TH1 * histogram,
		bool includeUnderflowBin = false,
		bool includeOverflowBin = false)
{
  const int numBins  = histogram->GetNbinsX();
  const int firstBin = includeUnderflowBin ? 0           : 1;
  const int lastBin  = includeOverflowBin  ? numBins + 1 : numBins;
  
  double sumBinErr2 = 0.;
  for(int iBin = firstBin; iBin <= lastBin; ++iBin)
    {
      sumBinErr2 += square(histogram->GetBinError(iBin));
    }
  return std::sqrt(sumBinErr2);
}

std::string replaceInString(std::string s0, const char *sFind0, const char *sReplace0) {
  //void replaceInString(string &s, string sFind, string sReplace) {
  string s = s0;
  string sFind = sFind0;
  string sReplace = sReplace0;
  //std::replace( s.begin(), s.end(), sFind, sReplace);
  while (s.find(sFind) != std::string::npos) {
    s.replace(s.find(sFind), sFind.size(), sReplace);
  }
  return s;
}


void dumpEventYields_Stage2_v8(std::string inputFilePath, std::string inputFileName11)
{
  //std::cout << "inputFilePath: "<< inputFilePath << std::endl;
  std::vector<std::string> inputFilePath_parts;
  boost::split(inputFilePath_parts, inputFilePath, boost::is_any_of("/"));
  std::string anaVersion = inputFilePath_parts.size() > 6 ? inputFilePath_parts[6] : "";
  /*std::cout << "inputFilePath_parts size: " << inputFilePath_parts.size() << "\n";
  for (int i=0; i<inputFilePath_parts.size(); i++)
  {
    std::cout << "\t " <<  inputFilePath_parts[i] << "\n";
    }
  
  std::cout << "anaVersion: " << anaVersion << "\n";*/
  
  gROOT->SetBatch(true);
  
  TH1::AddDirectory(false);
  
  typedef std::vector<std::string> vstring;
  vstring channels;
  channels.push_back("hh_3l");
  
  //std::string inputFilePath = "/hdfs/local/ssawant/hhAnalysis/2017/20200805_CompareAnaNanoAOD_LepMvaCut0p0_Try9/histograms/hh_3l/Tight_OS/hadd";
 
  
  //std::vector<std::string> vmHH = {"250", "260", "270", "280", "300", "350", "400", "450", "500", "550", "600", "650", "700", "750", "800", "850", "900", "1000", "nonresonant"}; 
  //std::vector<std::string> vmHH = {"250", "400", "700", "1000"};
  std::vector<std::string> vmHH = {"400"};
    
  std::map<std::string, std::string> inputFileNames; // key = channel
  inputFileNames["hh_3l"] = inputFileName11;
  
  //cout<<"inputFile: "<<inputFilePath<<"/"<<inputFileNames["hh_3l"]<<"\n\n";
  
  std::map<std::string, vstring> directories; // key = channel 
  
  if (inputFileName11.find("Tight") != std::string::npos) {

    // for DefaultLepton selection
    directories["hh_3l"].push_back("hh_3l_OS_Tight/sel/evt"); 

    directories["hh_3l"].push_back("hh_3mu_OS_Tight/sel/evt"); 
    directories["hh_3l"].push_back("hh_3e_OS_Tight/sel/evt");
    directories["hh_3l"].push_back("hh_1e2mu_OS_Tight/sel/evt");
    directories["hh_3l"].push_back("hh_2e1mu_OS_Tight/sel/evt");
    
    
  } else if (inputFileName11.find("Fakeable_mcClosure_e_wFakeRateWeights") != std::string::npos) {
    directories["hh_3l"].push_back("hh_3l_OS_Fakeable_mcClosure_e_wFakeRateWeights/sel/evt");
    directories["hh_3l"].push_back("hh_3e_OS_Fakeable_mcClosure_e_wFakeRateWeights/sel/evt");
    directories["hh_3l"].push_back("hh_3mu_OS_Fakeable_mcClosure_e_wFakeRateWeights/sel/evt");

  } else if (inputFileName11.find("Fakeable_mcClosure_m_wFakeRateWeights") != std::string::npos) {
    directories["hh_3l"].push_back("hh_3l_OS_Fakeable_mcClosure_m_wFakeRateWeights/sel/evt");
    directories["hh_3l"].push_back("hh_3e_OS_Fakeable_mcClosure_m_wFakeRateWeights/sel/evt");
    directories["hh_3l"].push_back("hh_3mu_OS_Fakeable_mcClosure_m_wFakeRateWeights/sel/evt");
    
  } else if (inputFileName11.find("Fakeable_wFakeRateWeights") != std::string::npos) {
    directories["hh_3l"].push_back("hh_3l_OS_Fakeable_wFakeRateWeights/sel/evt");
    directories["hh_3l"].push_back("hh_3e_OS_Fakeable_wFakeRateWeights/sel/evt");
    directories["hh_3l"].push_back("hh_3mu_OS_Fakeable_wFakeRateWeights/sel/evt");
    
  }
  
  
  std::map<std::string, vstring> signal_processes; // key = channel
  for (int imHH = 0; imHH < vmHH.size(); imHH++) {
    //std::cout << "mHH: " << vmHH[imHH] << std::endl;
    if (vmHH[imHH].find("nonresonant") != std::string::npos) {
      /*signal_processes["hh_3l"].push_back("signal_ggf_nonresonant_hh_tttt");
      signal_processes["hh_3l"].push_back("signal_ggf_nonresonant_hh_wwtt");
      signal_processes["hh_3l"].push_back("signal_ggf_nonresonant_hh_wwww");*/
      continue;
    }
    
    signal_processes["hh_3l"].push_back(Form("signal_ggf_spin0_%s_hh_tttt",vmHH[imHH].data()));
    signal_processes["hh_3l"].push_back(Form("signal_ggf_spin0_%s_hh_wwtt",vmHH[imHH].data()));
    signal_processes["hh_3l"].push_back(Form("signal_ggf_spin0_%s_hh_wwww",vmHH[imHH].data()));
    signal_processes["hh_3l"].push_back(Form("signal_spin0_%s_hh",vmHH[imHH].data()));

    /*
    signal_processes["hh_3l"].push_back(Form("signal_ggf_spin2_%s_hh_tttt",vmHH[imHH].data()));
    signal_processes["hh_3l"].push_back(Form("signal_ggf_spin2_%s_hh_wwtt",vmHH[imHH].data()));
    signal_processes["hh_3l"].push_back(Form("signal_ggf_spin2_%s_hh_wwww",vmHH[imHH].data()));
    //signal_processes["hh_3l"].push_back(Form("signal_spin2_%i_hh",vmHH[imHH]));
    */
  }
  
  //signal_processes["hh_3l"].push_back("signal_ggf_nonresonant_hh_tttt");
  //signal_processes["hh_3l"].push_back("signal_ggf_nonresonant_hh_wwtt");
  //signal_processes["hh_3l"].push_back("signal_ggf_nonresonant_hh_wwww");


  std::vector<std::string> signal_process_parts;
  signal_process_parts.push_back("");
  signal_process_parts.push_back("_Convs");
  signal_process_parts.push_back("_fake");
  
  std::map<std::string, vstring> background_processes; // key = channel
  background_processes["hh_3l"].push_back("TTH");
  background_processes["hh_3l"].push_back("TH");
  background_processes["hh_3l"].push_back("ggH");
  background_processes["hh_3l"].push_back("qqH");
  background_processes["hh_3l"].push_back("TTZ");
  background_processes["hh_3l"].push_back("TTW");
  background_processes["hh_3l"].push_back("TTWW");
  background_processes["hh_3l"].push_back("TT");
  background_processes["hh_3l"].push_back("TTWH");
  background_processes["hh_3l"].push_back("TTZH");
  background_processes["hh_3l"].push_back("Other");
  background_processes["hh_3l"].push_back("XGamma");
  background_processes["hh_3l"].push_back("VH");
  background_processes["hh_3l"].push_back("DY");
  background_processes["hh_3l"].push_back("W");
  background_processes["hh_3l"].push_back("WW");
  background_processes["hh_3l"].push_back("WZ");
  background_processes["hh_3l"].push_back("ZZ");
  
  /*
  background_processes["hh_3l"].push_back("TT"); 
  background_processes["hh_3l"].push_back("TTW");
  background_processes["hh_3l"].push_back("TTWW");
  background_processes["hh_3l"].push_back("TTZ");
  background_processes["hh_3l"].push_back("TTH");
  background_processes["hh_3l"].push_back("TH");
  background_processes["hh_3l"].push_back("TTWH");
  background_processes["hh_3l"].push_back("TTZH");

  background_processes["hh_3l"].push_back("W");
  background_processes["hh_3l"].push_back("WW");
  background_processes["hh_3l"].push_back("WZ");
  background_processes["hh_3l"].push_back("ZZ");
  background_processes["hh_3l"].push_back("DY");
  
  background_processes["hh_3l"].push_back("VH");
  background_processes["hh_3l"].push_back("ggH");
  background_processes["hh_3l"].push_back("qqH");
  background_processes["hh_3l"].push_back("XGamma");
  background_processes["hh_3l"].push_back("Other");*/
  
  /*background_processes["hh_3l"].push_back("bbtt");
  background_processes["hh_3l"].push_back("bbww");
  background_processes["hh_3l"].push_back("bbzz");
  background_processes["hh_3l"].push_back("tttt");
  background_processes["hh_3l"].push_back("ttWW");
  background_processes["hh_3l"].push_back("ttzz");
  background_processes["hh_3l"].push_back("wwww");
  background_processes["hh_3l"].push_back("zzww");*/
  


  std::map<std::string, vstring> background_processes1; // key = channel
  background_processes1["hh_3l"].push_back("Convs"); // conversions
  background_processes1["hh_3l"].push_back("fakes_mc");
  background_processes1["hh_3l"].push_back("data_fakes");
  //background_processes1["hh_3l"].push_back("flips_mc");
  //background_processes1["hh_3l"].push_back("data_flips");
  
  std::vector<std::string> background_process_parts;
  background_process_parts = signal_process_parts;
  
  int widthProcessPrint = 30;
  int widthEventNumPrint = 15;
  
  double lumi_datacard = 41.5;
  double lumi_projection = 41.5;
  double lumi_SF = lumi_projection/lumi_datacard;
  //std::cout << "scaling signal and background yields to L=" << lumi_projection << "fb^-1 @ 13 TeV." << std::endl;
  
  
  std::map<std::string, std::map<std::string, double>> eventYieldCatwise;
  
  
  
  
  
  for ( vstring::const_iterator channel = channels.begin();
	channel != channels.end(); ++channel ) {		
    TString inputFileName_full = inputFilePath.data();
    if ( !inputFileName_full.EndsWith("/") ) inputFileName_full.Append("/");
    inputFileName_full.Append(inputFileNames[*channel].data());
    std::cout << "channel = " << inputFileName_full.Data() << std::endl;
    TFile* inputFile = new TFile(inputFileName_full.Data());
    //if ( !inputFile ) {
    if ( !inputFile->IsOpen() ) {
      std::cerr << "Failed to open input file = " << inputFileName_full.Data() << " !!" << std::endl;
      assert(0);
      return;
    }
    
    for ( vstring::const_iterator directory = directories[*channel].begin();
	  directory != directories[*channel].end(); ++directory ) {
      std::vector<std::string> directory_parts;
      boost::split(directory_parts, *directory, boost::is_any_of("/"));
      
      printf("\n\nCategory = %s,   %s \n",directory_parts[0].data(),anaVersion.data());
      
      double *totalSig = new double[vmHH.size()];
      double totalBk;
      double Total = 0;
      double Non_Fake = 0;
      double Fake = 0;
      double Convs = 0;
      int    nEvents = 0;
      double err2totalBk;
      double err2Total = 0;
      double err2Non_Fake = 0;
      double err2Fake = 0;
      double err2Convs = 0;
      
      //std::cout << "\\begin{table}[htbp]" << std::endl;
      //std::cout << "\\begin{tabular}{|l|c|c|c|c|c|}\\hline " << std::endl;
      //std::cout << "Process   & Total (unweighted) & Non Fakes & Fakes & Conversions \\\\ \\hline" << std::endl;
      std::cout << "Process   & Total & Total unweighted & Non Fakes & Fakes & Conversions \\\\ \\hline" << std::endl;

      for (int imHH = 0; imHH < vmHH.size(); imHH++) {
	Total = 0;
	Non_Fake = 0;
	Fake = 0;
	Convs = 0;
	nEvents = 0;
	err2Total = 0;
	err2Non_Fake = 0;
	err2Fake = 0;
	err2Convs = 0;
	for ( vstring::const_iterator signal_process = signal_processes[*channel].begin();
	      signal_process != signal_processes[*channel].end(); ++signal_process ) {
	  //std::cout << " mHH: " << vmHH[imHH] << ",  signal_process: " << *signal_process << std::endl;
	  //if (signal_process->find(std::to_string(vmHH[imHH])) == std::string::npos) continue;
	  if (signal_process->find(vmHH[imHH]) == std::string::npos) continue;
	  //std::cout << " mHH: " << vmHH[imHH] << ",  signal_process: " << *signal_process << " \t passed " << std::endl;
	  
	  std::map<std::string, double> integral_parts;
	  std::map<std::string, double> integralErr_parts;
	  double integral_sum = 0.;
	  double integralErr2_sum = 0.;
	  nEvents = 0;
	  
	  //cout<<"here1"<< endl;
	  for ( std::vector<std::string>::const_iterator signal_process_part = signal_process_parts.begin();
		signal_process_part != signal_process_parts.end(); ++signal_process_part ) {
	    std::string histogramName = Form("%s/%s%s/EventCounter", 
					     directory->data(), signal_process->data(), signal_process_part->data());
	    TH1* histogram = loadHistogram(inputFile, histogramName);
	    if ( histogram ) {
	      nEvents += histogram->GetEntries();
	      histogram->Scale(lumi_SF);
	      double integral = compIntegral(histogram);
	      integral_parts[*signal_process_part] = integral;
	      integral_sum += integral;
	      double integralErr = compIntegralErr(histogram);
	      integralErr_parts[*signal_process_part] = integralErr;
	      integralErr2_sum += square(integralErr);
	    }
	    delete histogram;
	  }
	  //cout<<"here3"<< endl;
	  //std::cout << (*signal_process) << " & " << integral_sum << " & " << integral_parts[""] << " & " << integral_parts["_fake"] << " & " << integral_parts["_Convs"] << " \\\\ " << std::endl;			
	  //std::cout << replaceInString((*signal_process),"_"," ") << " & " << integral_sum << " (" << nEvents << ") & " << integral_parts[""] << " & " << integral_parts["_fake"] << " & " << integral_parts["_Convs"] << " \\\\ " << std::endl;
	  //std::cout << replaceInString((*signal_process),"_"," ") << " & " << integral_sum << " & " << nEvents << " & " << integral_parts[""] << " & " << integral_parts["_fake"] << " & " << integral_parts["_Convs"] << " \\\\ " << std::endl;
	  /*std::cout << replaceInString((*signal_process),"_"," ") << " & "
		    << integral_sum             << " +- " << std::sqrt(integralErr2_sum) << " & " << nEvents << " & "
		    << integral_parts[""]       << " +- " << integralErr_parts[""] << " & "
		    << integral_parts["_fake"]  << " +- " << integralErr_parts["_fake"] << " & "
		    << integral_parts["_Convs"] << " +- " << integralErr_parts["_Convs"] << " \\\\ " << std::endl;*/

	  printf("%-20s & %13.3f +- %7.3f & %13d & %13.3f +- %7.3f & %13.3f +- %7.3f & %13.3f +- %7.3f  \\\\  \n",
		 replaceInString((*signal_process),"_"," ").c_str(),
		 integral_sum,std::sqrt(integralErr2_sum),nEvents,
		 integral_parts[""],integralErr_parts[""],
		 integral_parts["_fake"],integralErr_parts["_fake"],
		 integral_parts["_Convs"],integralErr_parts["_Convs"]
	    );

	       
	  // consider yield from 'hh_xyz' decay directories for 'total event yield'
	  if (signal_process->find("_hh_tttt") != std::string::npos ||
	      signal_process->find("_hh_wwtt") != std::string::npos ||
	      signal_process->find("_hh_wwww") != std::string::npos )
	  {
	    Total    += integral_parts[""];
	    Non_Fake += integral_parts[""];
	    Fake     += integral_parts["_fake"];
	    Convs    += integral_parts["_Convs"];
	  
	    err2Total    += square(integralErr_parts[""]);
	    err2Non_Fake += square(integralErr_parts[""]);
	    err2Fake     += square(integralErr_parts["_fake"]);
	    err2Convs    += square(integralErr_parts["_Convs"]);
	  }
	  
	  //eventYieldCatwise[*directory][*signal_process] = integral_sum;
	  eventYieldCatwise[*directory][*signal_process] = integral_parts[""];
	}
	std::cout << "\\hline " << std::endl;		
	//std::cout << "Total Sig at mHH="<< vmHH[imHH] << " & " << Total << " & " << Non_Fake << " & " << Fake << " & " << Convs << " \\\\ " << " \\hline " << std::endl;
	totalSig[imHH] = Total;
      }

            
      Total = 0;
      Non_Fake = 0;
      Fake = 0;
      Convs = 0;
      nEvents = 0;
      err2Total = 0;
      err2Non_Fake = 0;
      err2Fake = 0;
      err2Convs = 0;
      for ( vstring::const_iterator background_process = background_processes[*channel].begin();
	    background_process != background_processes[*channel].end(); ++background_process ) {
	std::map<std::string, double> integral_parts;
	std::map<std::string, double> integralErr_parts;
	double integral_sum = 0.;
	double integralErr2_sum = 0.;
	nEvents = 0;
	
	for ( std::vector<std::string>::const_iterator background_process_part = background_process_parts.begin();
	      background_process_part != background_process_parts.end(); ++background_process_part ) {
	  std::string histogramName = Form("%s/%s%s/EventCounter", 
					   directory->data(), background_process->data(), background_process_part->data());
	  TH1* histogram = loadHistogram(inputFile, histogramName);
	  if ( histogram ) {
	    nEvents += histogram->GetEntries();
	    histogram->Scale(lumi_SF);
	    double integral = compIntegral(histogram);
	    integral_parts[*background_process_part] = integral;
	    integral_sum += integral;
	    double integralErr = compIntegralErr(histogram);
	    integralErr_parts[*background_process_part] = integralErr;
	    integralErr2_sum += square(integralErr); 
	  }
	  delete histogram;
	}			
	//std::cout << (*background_process) << " & " << integral_sum << " & " << integral_parts[""] << " & " << integral_parts["_fake"] << " & " << integral_parts["_Convs"] << " \\\\ " << std::endl;
	//std::cout << replaceInString((*background_process),"_"," ") << " & " << integral_sum << " (" << nEvents << ") & " << integral_parts[""] << " & " << integral_parts["_fake"] << " & " << integral_parts["_Convs"] << " \\\\ " << std::endl;
	//std::cout << replaceInString((*background_process),"_"," ") << " & " << integral_sum << " & " << nEvents << " & " << integral_parts[""] << " & " << integral_parts["_fake"] << " & " << integral_parts["_Convs"] << " \\\\ " << std::endl;
	/*std::cout << replaceInString((*background_process),"_"," ") << " & "
		  << integral_sum             << " +- " << std::sqrt(integralErr2_sum) << " & " << nEvents << " & "
		  << integral_parts[""]       << " +- " << integralErr_parts[""] << " & "
		  << integral_parts["_fake"]  << " +- " << integralErr_parts["_fake"] << " & "
		  << integral_parts["_Convs"] << " +- " << integralErr_parts["_Convs"] << " \\\\ " << std::endl;*/
	printf("%-20s & %13.3f +- %7.3f & %13d & %13.3f +- %7.3f & %13.3f +- %7.3f & %13.3f +- %7.3f  \\\\  \n",
		 replaceInString((*background_process),"_"," ").c_str(),
		 integral_sum,std::sqrt(integralErr2_sum),nEvents,
		 integral_parts[""],integralErr_parts[""],
		 integral_parts["_fake"],integralErr_parts["_fake"],
		 integral_parts["_Convs"],integralErr_parts["_Convs"]
	  );


	//Total += integral_sum;


	// use XGamma for conversion only
	if ((*background_process).compare("XGamma") != 0)
	{
	  Total    += integral_parts[""];
	  Non_Fake += integral_parts[""];
	  Fake     += integral_parts["_fake"];

	  err2Total    += square(integralErr_parts[""]);
	  err2Non_Fake += square(integralErr_parts[""]);
	  err2Fake     += square(integralErr_parts["_fake"]);	  
	} else {
	  Convs    += integral_parts["_Convs"];

	  err2Convs    += square(integralErr_parts["_Convs"]);
	}
	
	//eventYieldCatwise[*directory][*background_process] = integral_sum;
	eventYieldCatwise[*directory][*background_process] = integral_parts[""];
      }
      
      
      
      for ( vstring::const_iterator background_process = background_processes1[*channel].begin();
	    background_process != background_processes1[*channel].end(); ++background_process ) {
	std::string histogramName = Form("%s/%s/EventCounter", 
					 directory->data(), background_process->data());
	TH1* histogram = loadHistogram(inputFile, histogramName);
	double integral = 0., integralErr = 0.;
	nEvents = 0;
	if ( histogram ) {
	  nEvents += histogram->GetEntries();
	  histogram->Scale(lumi_SF);
	  integral = compIntegral(histogram);
	  integralErr = compIntegralErr(histogram);
	}
	delete histogram;
	/*std::cout << replaceInString((*background_process),"_"," ") << " & "
		  << integral << " +- " << integralErr
		  << " &  &  &  \\\\ " << std::endl;*/
	printf("%-20s & %13.3f +- %7.3f &  &  &  &   \\\\  \n",
	       replaceInString((*background_process),"_"," ").c_str(),
	       integral,integralErr
	  );

	if ( ! ( (*background_process).compare("fakes_mc") == 0  || (*background_process).compare("flips_mc") == 0 ) ) { // don't add fakes_mc into total bk
	  Total += integral;
	  err2Total += square(integralErr);
	}  else {
	  //printf(" *** fakes_mc: not adding into total bk");
	}
	eventYieldCatwise[*directory][*background_process] = integral;
      }


      totalBk = Total;
      std::cout << "\\hline \n";
      /*std::cout << "Total Bk " << " & "
		<< Total    << " +- " << std::sqrt(err2Total) << " & "
		<< Non_Fake << " +- " << std::sqrt(err2Non_Fake) << " & "
		<< Fake     << " +- " << std::sqrt(err2Fake) << " & "
		<< Convs    << " +- " << std::sqrt(err2Convs) << " \\\\ " << " \\hline " << std::endl;*/
      printf("%-20s & %13.3f +- %7.3f &               & %13.3f +- %7.3f & %13.3f +- %7.3f & %13.3f +- %7.3f  \\\\  \\hline \n",
	     "Total Bk",
	     Total,     std::sqrt(err2Total),
	     Non_Fake,  std::sqrt(err2Non_Fake),
	     Fake,      std::sqrt(err2Fake),
	     Convs,     std::sqrt(err2Convs)
	);
      
      
      double Data_Observed = 0;
      double errData_Observed = 0;
      std::string histogramName = Form("%s/%s/EventCounter", 
				       directory->data(), "data_obs");
      TH1* histogram = loadHistogram(inputFile, histogramName);
      if ( histogram ) {
	histogram->Scale(lumi_SF);
	Data_Observed    = compIntegral(histogram);
	errData_Observed = compIntegralErr(histogram);
	//std::cout << "Data Observed : " << Data_Observed << " \\\\" << std::endl;
      }
      std::cout << "\\hline " << std::endl;
      //std::cout << replaceInString("data_obs","_"," ") << " & " << Data_Observed << " &  &  &  \\\\ \n";
      printf("%-20s & %13.3f +- %7.3f  & &  &  &  \\\\ \n",
	     replaceInString("data_obs","_"," ").c_str(),
	     Data_Observed, errData_Observed);
      eventYieldCatwise[*directory]["data_obs"] = Data_Observed;
      
      std::cout << "\\hline " << std::endl;
     
      double DataMCResidual = (Data_Observed - totalBk) / totalBk;
      printf("%-20s & %13.3f & & & & \\\\  \\hline \n",
	     "(Data - MC(Bkg))/MC(Bkg) ", DataMCResidual);

      for (int imHH = 0; imHH < vmHH.size(); imHH++)
      {
	double SByB = totalSig[imHH] / sqrt(totalBk);
	std::string sSByB = Form("S/sqrt(B) at S %s",vmHH[imHH].c_str());
	printf("%-20s & %13.3f & & & & \\\\   \n",
	       sSByB.c_str(), SByB);

      }
      

      //std::cout << "\\end{tabular} " << std::endl;
      //std::cout << "\\end{table} " << std::endl;		
      
       
      
      //double Total_Background = Non_Fake + Conversions + Fakes_Data +Flips_data ;
      //std::cout << "Total Background = Non Fake + Conversion + Fakes Data + Flips Data = " << Total_Background << std::endl;
      //std::cout << "Total MC signal + background = " << totalSig + totalBk << std::endl;
      for (int i=0; i<50; i++) printf("-");
      printf("\n");
    }
    

    return;
    

    //printf("Terminating mid-way and not executing table of event yield for different categories\n");
    //return;
    
    
    printf("\n\nCompare event yield by categories::\n");
    std::string sLine1,sLine2;
    int nCategories = directories["hh_3l"].size();
    cout << "size " << nCategories << endl;
    std::cout << "\\begin{table}[htbp]" << std::endl;
    sLine1 = "\\begin{tabular}{|l|";
    sLine2 = "Process   ";
    for ( vstring::const_iterator directory = directories[*channel].begin();
	  directory != directories[*channel].end(); ++directory ) {
      sLine1 += "c|";
      //sLine2 += Form("& %s ",directory->data());
      sLine2 += Form("& %s ",replaceInString(directory->data(),"_","").c_str());
    }
    sLine1 += "}\\hline ";
    sLine2 += "\\\\ \n\\hline ";
    std::cout << sLine1 << std::endl;
    std::cout << sLine2 << std::endl;
    
    
    std::map<std::string, double> totalEventsCatwise;
    
    for ( vstring::const_iterator directory = directories[*channel].begin();
	  directory != directories[*channel].end(); ++directory ) {
      totalEventsCatwise[*directory] = 0.;
    }		
    for ( vstring::const_iterator signal_process = signal_processes[*channel].begin();
	  signal_process != signal_processes[*channel].end(); ++signal_process ) {
      std::cout << left << setw(widthProcessPrint) << replaceInString((*signal_process),"_"," ") << right;
      
      for ( vstring::const_iterator directory = directories[*channel].begin();
	    directory != directories[*channel].end(); ++directory ) {
	std::cout << "  & " << setw(widthEventNumPrint) << eventYieldCatwise[*directory][*signal_process];
	totalEventsCatwise[*directory] += eventYieldCatwise[*directory][*signal_process];				
      }
      std::cout << " \\\\ " << std::endl;		
    }
    std::cout << "\\hline " << std::endl;
    /*std::cout << left << setw(widthProcessPrint) << "Total Sig " << right;
    for ( vstring::const_iterator directory = directories[*channel].begin();
	  directory != directories[*channel].end(); ++directory ) {
      std::cout << "  & " << setw(widthEventNumPrint) << totalEventsCatwise[*directory]; 				
    }
    std::cout << " \\\\ " << "\n\\hline " << std::endl;	
    */
    // bk
    for ( vstring::const_iterator directory = directories[*channel].begin();
	  directory != directories[*channel].end(); ++directory ) {
      totalEventsCatwise[*directory] = 0.;
    }	
    for ( vstring::const_iterator background_process = background_processes[*channel].begin();
	  background_process != background_processes[*channel].end(); ++background_process ) {
      std::cout << left << setw(widthProcessPrint) << replaceInString((*background_process),"_"," ") << right;
      
      for ( vstring::const_iterator directory = directories[*channel].begin();
	    directory != directories[*channel].end(); ++directory ) {			
	std::cout << "  & " << setw(widthEventNumPrint) << eventYieldCatwise[*directory][*background_process];
	totalEventsCatwise[*directory] += eventYieldCatwise[*directory][*background_process];								
      }
      std::cout << " \\\\ " << std::endl;		
    }
    std::cout << "\\hline " << std::endl;
    std::cout << left << setw(widthProcessPrint) << "Total Bk " << right;
    for ( vstring::const_iterator directory = directories[*channel].begin();
	  directory != directories[*channel].end(); ++directory ) {
      std::cout << "  & " << setw(widthEventNumPrint) << totalEventsCatwise[*directory]; 				
    }
    std::cout << " \\\\ " << "\n\\hline " << std::endl;	
    
    // bk1
    for ( vstring::const_iterator background_process = background_processes1[*channel].begin();
	  background_process != background_processes1[*channel].end(); ++background_process ) {
      std::cout << left << setw(widthProcessPrint) << replaceInString((*background_process),"_"," ") << right;
      
      for ( vstring::const_iterator directory = directories[*channel].begin();
	    directory != directories[*channel].end(); ++directory ) {			
	std::cout << "  & " << setw(widthEventNumPrint) << eventYieldCatwise[*directory][*background_process];
	if ((*background_process).compare("fakes_mc") != 0) { // don't add fakes_mc into total bk
	  totalEventsCatwise[*directory] += eventYieldCatwise[*directory][*background_process];
	} else {
	  //printf(" *** fakes_mc: not adding into total bk");
	}
      }
      std::cout << " \\\\ " << std::endl;		
    }
    std::cout << "\\hline " << std::endl;
    std::cout << left << setw(widthProcessPrint) << "Total Bk " << right;
    for ( vstring::const_iterator directory = directories[*channel].begin();
	  directory != directories[*channel].end(); ++directory ) {
      std::cout << "  & " << setw(widthEventNumPrint) << totalEventsCatwise[*directory]; 				
    }
    std::cout << " \\\\ " << "\n\\hline " << std::endl;	

    
    std::cout << left << setw(widthProcessPrint) << replaceInString("data_obs","_"," ") << right;
    for ( vstring::const_iterator directory = directories[*channel].begin();
	  directory != directories[*channel].end(); ++directory ) {
      std::cout << "  & " << setw(widthEventNumPrint) << eventYieldCatwise[*directory]["data_obs"] ; 				
    }
    std::cout << " \\\\ " << "\n\\hline " << std::endl;	
    std::cout << "\\end{tabular} " << std::endl;
    std::cout << "\\end{table} " << std::endl;	
    
    delete inputFile;
  }
  
  
  
  
	
  
}
