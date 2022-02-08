

void GetListOfDirectoriesFromFile() {

  TString sIpFile = "hadd_stage2_Tight_OS.root";
  TString sDirectory = "hh_3l_OS_Tight/sel/evt";

  TFile *fIpFile = new TFile(sIpFile);
  if ( ! fIpFile->IsOpen()) {
    printf("File %s couldn't open.. \t *** ERROR *** \nTerminating..\n",sIpFile.Data());
    return;
  }

  TDirectory *dir1 = (TDirectory*) fIpFile->Get(sDirectory);
  if ( ! dir1) {
    printf("Couldn't fetch %s directory.. \t *** ERROR *** \nTerminating..\n",sDirectory.Data());
  }

  TIter next0(fIpFile->GetListOfKeys());
  TIter next1(dir1->GetListOfKeys());
  TIter next;
  if (sDirectory.IsNull()) next = next0;
  else                     next = next1;
  TKey key;
  while (TObject *obj = next()) {
    /*
    std::cout << "obj: " << obj
	      << ", " << obj->ClassName()
	      << ", " << obj->IsA()->GetName()
	      << ", " << obj->GetName()
      //<< ", " << obj->GetTitle()
	      << ", " << obj->InheritsFrom("TH1D")
	      << std::endl;
    */
    
    std::cout <<  obj->GetName() << std::endl;
    
  }
  
}
