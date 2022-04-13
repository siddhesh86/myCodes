#!/bin/bash

: '
# hh_3l
declare -a Years=(2016 2017 2018)
Channel="3l" # (3l 2lss) 
AnaLepCharge="OS"
AnaVersion="20220204_hh_CHANNEL_YEAR_Datacards"
#declare -a HistosToFit=("m3l")
declare -a HistosToFit=("m3l" "dihiggsVisMass_sel"  "mSFOS2l_closestToZ" "dr_LeptonIdx3_AK4jNear_Approach2" "dr_LeptonIdx3_2j_inclusive1j_Approach2"  "dr_los_min"  "dr_los_max" "numSameFlavor_OS_3l"  "met_LD")

PathPrearedatacardCfg="/scratch-persistent/ssawant/hhAnalysis/YEAR/ANAVERSION/cfgs/hh_CHANNEL/prepareDatacards/prepareDatacards_hh_CHANNEL_hh_CHANNEL_ANALEPCHARGE_HISTOGRAMNAME_cfg.py"
PathAddsystfakesCfg="/scratch-persistent/ssawant/hhAnalysis/YEAR/ANAVERSION/cfgs/hh_CHANNEL/addSystFakeRates/addSystFakeRates_hh_CHANNEL_hh_CHANNEL_ANALEPCHARGE_HISTOGRAMNAME_cfg.py"
PathCfgToConcatenate="/home/ssawant/hhAnalysis/2016/20220204_hh_3l_2016_Datacards/manipulation/prepareDatacards_processToCopy_2.txt"
'


# hh_2lss_leq1tau
declare -a Years=(2016 2017 2018)
Channel="2lss_leq1tau" # (3l 2lss) 
AnaLepCharge="SS"
AnaVersion="20220204_hh_CHANNEL_YEAR_Datacards_BDTVarPlotsWFullSyst"
declare -a HistosToFit=("leptonPairMass" "dihiggsVisMass" "met_LD" "dR_ll" "dR_l_Wjets_min" "dR_l_leadWjet_min" "dR_l_Wjets_max" "dR_l_leadWjet_max" "dR_2j_fromW1" "mT_lep1_met" "lep1_conePt" "lep2_conePt" "mindr_lep1_jet" "mindr_lep2_jet" "HT" "mht" "mass_2j_fromW1")

PathPrearedatacardCfg="/scratch-persistent/ssawant/hhAnalysis/YEAR/ANAVERSION/cfgs/hh_CHANNEL/prepareDatacards/prepareDatacards_hh_CHANNEL_hh_CHANNEL_ANALEPCHARGE_HISTOGRAMNAME_cfg.py"
PathAddsystfakesCfg="/scratch-persistent/ssawant/hhAnalysis/YEAR/ANAVERSION/cfgs/hh_CHANNEL/addSystFakeRates/addSystFakeRates_hh_CHANNEL_hh_CHANNEL_ANALEPCHARGE_HISTOGRAMNAME_cfg.py"
PathCfgToConcatenate="/home/ssawant/hhAnalysis/2016/20220204_hh_2lss_leq1tau_2016_Datacards_BDTVarPlotsWFullSyst/manipulation/prepareDatacards_processToCopy_2.txt"



dir_base=`pwd`



for Year in "${Years[@]}"
do
    printf "Year: ${Year}\n"

    for HistoToFit in "${HistosToFit[@]}"
    do
	printf "HistoToFit: ${HistoToFit}\n"
	printf "AnaVersion: ${AnaVersion}\n"

	#continue

	PathPrearedatacardCfg_0=$PathPrearedatacardCfg

	# replace substring
	# To replace all occurrences, use ${parameter//pattern/string}
	# https://stackoverflow.com/questions/13210880/replace-one-substring-for-another-string-in-shell-script
	printf "PathPrearedatacardCfg_0: ${PathPrearedatacardCfg_0}\n"
	PathPrearedatacardCfg_0="${PathPrearedatacardCfg_0//ANAVERSION/$AnaVersion}"
	PathPrearedatacardCfg_0="${PathPrearedatacardCfg_0//YEAR/$Year}"
	PathPrearedatacardCfg_0="${PathPrearedatacardCfg_0//CHANNEL/$Channel}"
	PathPrearedatacardCfg_0="${PathPrearedatacardCfg_0//ANALEPCHARGE/$AnaLepCharge}"
	PathPrearedatacardCfg_0="${PathPrearedatacardCfg_0//HISTOGRAMNAME/$HistoToFit}"
	printf "PathPrearedatacardCfg_0: ${PathPrearedatacardCfg_0}\n"

	PathPrearedatacardCfg_1=${PathPrearedatacardCfg_0}
	PathPrearedatacardCfg_1="${PathPrearedatacardCfg_1//.py/_1.py}"
	printf "PathPrearedatacardCfg_1: ${PathPrearedatacardCfg_1}\n"
	
	command_1="cat ${PathPrearedatacardCfg_0} ${PathCfgToConcatenate} > ${PathPrearedatacardCfg_1}"
	printf "Running command: ${command_1} \n"
	#${command_1}
	cat ${PathPrearedatacardCfg_0} ${PathCfgToConcatenate} > ${PathPrearedatacardCfg_1}

	
	# prepareDatacards
	command_1="time prepareDatacards ${PathPrearedatacardCfg_1} 2>&1 | tee cout_prepareDatacards_hh_${Channel}_${Year}_${HistoToFit}.log"
	printf "Running command: ${command_1} \n"
	time prepareDatacards ${PathPrearedatacardCfg_1} 2>&1 | tee cout_prepareDatacards_hh_${Channel}_${Year}_${HistoToFit}.log

	
	# addSystFakeRates
	PathAddsystfakesCfg_0=$PathAddsystfakesCfg
	printf "PathAddsystfakesCfg_0: ${PathAddsystfakesCfg_0}\n"
	PathAddsystfakesCfg_0="${PathAddsystfakesCfg_0//ANAVERSION/$AnaVersion}"
	PathAddsystfakesCfg_0="${PathAddsystfakesCfg_0//YEAR/$Year}"
	PathAddsystfakesCfg_0="${PathAddsystfakesCfg_0//CHANNEL/$Channel}"
	PathAddsystfakesCfg_0="${PathAddsystfakesCfg_0//ANALEPCHARGE/$AnaLepCharge}"
	PathAddsystfakesCfg_0="${PathAddsystfakesCfg_0//HISTOGRAMNAME/$HistoToFit}"
	printf "PathAddsystfakesCfg_0: ${PathAddsystfakesCfg_0}\n"

	command_1="time addSystFakeRates ${PathAddsystfakesCfg_0} 2>&1 | tee cout_addSystFakeRates_hh_${Channel}_${Year}_${HistoToFit}.log"
	printf "Running command: ${command_1} \n"
	time addSystFakeRates ${PathAddsystfakesCfg_0} 2>&1 | tee cout_addSystFakeRates_hh_${Channel}_${Year}_${HistoToFit}.log

    done
done
