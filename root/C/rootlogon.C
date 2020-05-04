
{
	cout << endl << "Welcome to rootlogon.C " << endl;
	cout << "For approved plots use: gROOT->SetStyle(\"WASA\");"
			 << endl << endl;

	
//..BABAR style from RooLogon.C in workdir
	TStyle *wasaStyle= new TStyle("WASA","WASA plot style");

// use plain black on white colors
	wasaStyle->SetFrameBorderMode(0);
	wasaStyle->SetCanvasBorderMode(0);
	wasaStyle->SetPadBorderMode(0);
	wasaStyle->SetPadColor(0);
	wasaStyle->SetCanvasColor(0);
	wasaStyle->SetStatColor(0); 
	//wasaStyle->SetFillColor(0); 
	 
 // set the paper & margin sizes
	wasaStyle->SetPaperSize(20,26);
	wasaStyle->SetPadTopMargin(0.055);
	wasaStyle->SetPadRightMargin(0.05);
	wasaStyle->SetPadBottomMargin(0.12);
	wasaStyle->SetPadLeftMargin(0.12);
	
  // use large Times-Roman fonts
	wasaStyle->SetTextFont(132);
	wasaStyle->SetTextSize(0.05);
	
	wasaStyle->SetLabelFont(132,"x");
	wasaStyle->SetLabelFont(132,"y");
	wasaStyle->SetLabelFont(132,"z");
	
	wasaStyle->SetLabelSize(0.05,"x");
	wasaStyle->SetLabelSize(0.05,"y");
	wasaStyle->SetLabelSize(0.05,"z");
	
	wasaStyle->SetTitleSize(0.06,"x");
	wasaStyle->SetTitleSize(0.06,"y");
	wasaStyle->SetTitleSize(0.06,"z");

	wasaStyle->SetTitleOffset(0.85,"x");
	wasaStyle->SetTitleOffset(1.0,"y");

	wasaStyle->SetNdivisions(505, "x");
	wasaStyle->SetNdivisions(505, "y");

	// legend attributes
	wasaStyle->SetLegendFillColor(-1);
	wasaStyle->SetLegendBorderSize(1);
	//wasaStyle->SetLegendTextSize(0.5);

		
  // use bold lines and markers
	//wasaStyle->SetMarkerStyle(20);
	//wasaStyle->SetMarkerSize(0.5); // or 0.6
	
	//wasaStyle->SetHistLineWidth(1.85);
	wasaStyle->SetLineStyleString(2,"[12 12]"); // postscript dashes
	
	
  // get rid of X error bars and y error bar caps
	//wasaStyle->SetErrorX(0.001);
	
  // do not display any of the standard histogram decorations
	wasaStyle->SetOptTitle(0);  //wasaStyle->SetOptTitle(0);
	wasaStyle->SetOptStat(0);
	//wasaStyle->SetOptFit(0);
	wasaStyle->SetOptFit(1);
	
// put tick marks on top and RHS of plots
	wasaStyle->SetPadTickX(1);
	wasaStyle->SetPadTickY(1);
	
	//gROOT->SetStyle("Plain");
	//gStyle->SetOptStat(1111111);
	gStyle->SetPadTickX(1);
	gStyle->SetPadTickY(1);


	gStyle->SetPalette(1);

	//gROOT->SetStyle("WASA");
	
	wasaStyle->cd();
	gROOT->ForceStyle();
	gStyle->ls();
	

	/*
	 // retain this part of the file only to make small adjustement in the already save ThesisPlots
	gStyle->SetOptTitle(0);  //wasaStyle->SetOptTitle(0);
	gStyle->SetOptStat(0); */
	
}

