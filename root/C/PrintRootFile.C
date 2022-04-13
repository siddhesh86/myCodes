
#include <iostream>

{
  std::string sipFile, sDir;
  
  //std::string sipFile = "/home/ssawant/hhAnalysis/2016/20220204_hh_3l_2016_Datacards/datacards/hh_3l/prepareDatacards/prepareDatacards_hh_3l_hh_3l_OS_m3l.root";
  //std::string sipFile = "/home/ssawant/hhAnalysis/2016/20220204_hh_3l_2016_Datacards/datacards/hh_3l/prepareDatacards/prepareDatacards_hh_3l_hh_3l_OS_MVAOutput_SM.root";
  //std::string sipFile = "/home/ssawant/ana/hhwwww/20201102_BDTTraining/Datacards_3l/tmp/prepareDatacards_hh_3l_hh_3l_OS_m3l_tmp.root";
  //std::string sipFile = "/hdfs/local/ssawant/hhAnalysis/2016/20220204_hh_3l_2016_Datacards/histograms/hh_3l/Tight_OS/hadd/hadd_stage2_Tight_OS.root";


  //std::string sDir = "hh_3l_OS_Tight/sel/evt";
  //std::string sDir = "hh_3l_OS_Tight/sel/evt/signal_ggf_nonresonant_cHHH1_hh";
  //std::string sDir = "hh_3l_OS_Tight/sel/datacard";

  //sipFile="/home/ssawant/hhAnalysis/2016/20220204_hh_3l_2016_Datacards/datacards/hh_3l/prepareDatacards/prepareDatacards_hh_3l_hh_3l_OS_m3l.root"; sDir="";
  sipFile="/home/ssawant/hhAnalysis/2016/20220204_hh_3l_2016_Datacards/datacards/hh_3l/addSystFakeRates/addSystFakeRates_hh_3l_hh_3l_OS_m3l.root"; sDir="";
  
  
  TFile *f=new TFile(sipFile.c_str());
  if ( ! f->IsOpen() )
  {
    printf("%s couldn't open\n",sipFile.c_str());
    return;
  }

  printf("File %s:\n",sipFile.c_str());


  TDirectory *dir1 = (TDirectory*)f->Get(sDir.c_str());

  if (sDir.empty())
  {
    std::cout << "f->ls()::" << std::endl;
    gROOT->ProcessLine("f->ls()");
  }
  else
  {
    std::cout << sDir << "  dir->ls():: " << dir1 << std::endl;
    gROOT->ProcessLine("dir1->ls()");
  }
}
