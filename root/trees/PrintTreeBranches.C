

void PrintTreeBranches(std::string sFileName, std::string sTreeName)
{

  TFile *f = new TFile(sFileName.c_str());

  TTree *tree = (TTree*)f->Get(sTreeName.c_str());
  //std::cout << "Print tree: \n" << tree->Print() << std::endl;
  tree->Print();
}
