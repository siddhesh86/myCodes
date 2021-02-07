

declare -a anaVersions=("20201102_hh_3l_2017_CheckBDTVariables" "20201103_hh_3l_2017_CheckBDTVariables_TauWPMedium")

anaType="hh_3l"
anaSelection="Tight_OS" 


declare -a eras=("2017")


for anaVersion in "${anaVersions[@]}"
do
    echo "anaVersion ", ${anaVersion}

    for era in "${eras[@]}"
    do
	echo "era ",${era}

	file='/hdfs/local/ssawant/hhAnalysis/'${era}'/'${anaVersion}'/histograms/'${anaType}'/'${anaSelection}'/hadd/hadd_stage2_'${anaSelection}'.root'

	if [ ! -f ${file} ]; then
	    echo "File ${file} not found!"
	    continue
	fi
	
	
	root -l -b -q dumpEventYields_Stage2_v8.C'("/hdfs/local/ssawant/hhAnalysis/'${era}'/'${anaVersion}'/histograms/'${anaType}'/'${anaSelection}'/hadd", "hadd_stage2_'${anaSelection}'.root")' 2>&1 | tee cout_dumpEventYields_Stage2_v8_${anaVersion}_stage2_Tight_OS.txt
	
	
    done

done




