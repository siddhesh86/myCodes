#!/bin/bash

sFileName=tree_1.root
sTreeName=Events
sOpFileName="Tallinn_signal_ggf_nonresonant_cHHH1_hh_4v"


#root -l -q -b PrintTreeBranches.C'("${sFileName}", "${sTreeName}")' 2>&1 | tee TreeBranches_${sOpFileName}_0.txt # didn't work

#root -l -q -b PrintTreeBranches.C'("tree_1.root", "Events")' 2>&1 | tee TreeBranches_${sOpFileName}_0.txt
root -l -q -b PrintTreeBranches.C'("tree_1.root", "Events")' | grep "*Br \|*   " 2>&1 | tee TreeBranches_${sOpFileName}_1.txt



