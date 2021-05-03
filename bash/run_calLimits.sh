#!/bin/bash


declare -a Years=(2016 2017 2018) # (2016 2017 2018)
declare -a Channels=(3l) # (3l 2lss)
declare -a LimitsTypes=(nonresLO nonresNLO) # (spin0 spin2 nonresLO nonresNLO)
declare -a LimitsDatasets=(RUN2) # (RUN2 2016 2017 2018)
declare -a stepsToRun=(rebin_quantiles rename_procs writeCards combineYear calcLimits) # (rebin_quantiles rename_procs writeCards combineYear calcLimits)

rebinOption="binningFromRun2Comb" # "binningFromRun2Comb"  "binningFromRefFiles"  ""
refFilesPathForBinning="" #"/home/ssawant/ana/hhwwww/20201130_Datacards/CalLimits/dataCardsHH_3l_wHHrewgtFix/rawRootFiles/3l/hadded/" # path to rootfiles that should be use to decide binning of MVAoutput hitograms
binningThrsh="0.15" #"0.15"

systOption="FullSyst" # "withoutFullSyst" "FullSyst"
asimovDataset="False" # "True" "False"

runMode="local" # sbatch: submit job on batch. local: run locally

declare -i MaxNJobsToRunInBkg=4

dir_base=`pwd`

run_job() {
    # argument 1: run_mode, 2: run_cmd, 3: run_script
    
    echo "$1"
    echo "$2"
    echo "$3"
    run_mode="$1"
    run_cmd="$2"
    run_scriptName="$3"
    sbatch_submit_file="sbatch_submit_${run_scriptName}_${run_mode}.sh"
    echo "run_mode: ${run_mode}, run_cmd: ${run_cmd}, sbatch_submit_file: ${sbatch_submit_file}"
    
    
    if [[ "$runMode" == "sbatch" ]];
    then

	echo "#!/bin/bash " > ${sbatch_submit_file}
	echo "" >> ${sbatch_submit_file}
	echo "#SBATCH --job-name=${run_scriptName}    # Job name     " >> ${sbatch_submit_file}
	#echo "#SBATCH --nodes=1                    # Run all processes on a single node" >> ${sbatch_submit_file}
	#echo "#SBATCH --ntasks=1                    # Run on a single CPU " >> ${sbatch_submit_file}
	#echo "#SBATCH --cpus-per-task=4            # Number of CPU cores per task" >> ${sbatch_submit_file}
	#echo "#SBATCH --mem=2gb                     # Job memory request " >> ${sbatch_submit_file}
	echo "#SBATCH --time=24:00:00               # Time limit hrs:min:sec" >> ${sbatch_submit_file}
	echo "#SBATCH --output=${run_scriptName}_%j.log   # Standard output and error log" >> ${sbatch_submit_file}
	echo "#SBATCH --error=${run_scriptName}_error_%j.log   # Standard output and error log" >> ${sbatch_submit_file}
	echo "pwd; hostname; date " >> ${sbatch_submit_file}
	#echo "export OMP_NUM_THREADS=8 " >> ${sbatch_submit_file}
	echo "" >> ${sbatch_submit_file}
	echo "${run_cmd} " >> ${sbatch_submit_file}
	echo "date" >> ${sbatch_submit_file}
    
	echo "Submit job:"
	sbatch ${sbatch_submit_file}
    else
	printf "\n\nRun ${sbatch_submit_file} locally..\n"
	#time source ${sbatch_submit_file} 2>&1 | tee cout_${run_scriptName}_${run_mode}.log &
	${run_cmd}
    fi

}

declare -i kJobToRunInBkg=0
for channel in "${Channels[@]}"
do
    printf "\n\n"
    echo "channel: ${channel}"

    kJobToRunInBkg=0


    if [[ " ${stepsToRun[@]} " =~ "rebin_quantiles" ]];
    then
	# time python rebin_quantiles_wRefFiles.py --inputPaths=rawRootFiles/3l/2016/:rawRootFiles/3l/2017/:rawRootFiles/3l/2018/ --quantSig --binningFromRun2Comb 2>&1 | tee cout_tmp.txt
	inputPaths=""
	for year in "${Years[@]}"
	do
	    if [[ "${year}" == "RUN2" ]]
	    then
		continue
	    fi
	    
	    if [ ! -z "$inputPaths" ]
	    then
		inputPaths="${inputPaths}:"
	    fi
	    inputPaths="${inputPaths}rawRootFiles/${channel}/${year}/"
	done    
	#run_job local "time python rebin_quantiles_wRefFiles.py --inputPaths=${inputPaths} --quantSig --binningFromRun2Comb 2>&1 | tee cout_rebin_quantiles_wRefFiles_${channel}.txt " rebin_quantiles_wRefFiles_${channel}
	#time python rebin_quantiles_wRefFiles.py --inputPaths=${inputPaths} --quantSig --binningFromRun2Comb 2>&1 | tee cout_rebin_quantiles_wRefFiles_${channel}.txt
	if [ -z ${rebinOption} ]
	then
	    # empty rebinOption
	    command_1="time python rebin_quantiles_wRefFiles.py --inputPaths=${inputPaths} --quantSig "
	else
	    if [[ "${rebinOption}" == "binningFromRun2Comb" ]];
	    then
		 command_1="time python rebin_quantiles_wRefFiles.py --inputPaths=${inputPaths} --quantSig --binningFromRun2Comb "
	    else
		if [ "${rebinOption}" == "binningFromRefFiles" ] && [ -n ${refFilesPathForBinning} ];
		then
		    command_1="time python rebin_quantiles_wRefFiles.py --inputPaths=${inputPaths} --quantSig --refFilesPath=${refFilesPathForBinning} --threshold=${binningThrsh} "
		fi
	    fi
	fi
	echo "`date`: Running: ${command_1}"
	${command_1}  2>&1 | tee cout_rebin_quantiles_wRefFiles_${channel}.txt
	echo "`date`: Done: ${command_1}"
    fi

    kJobToRunInBkg=0
    if [[ " ${stepsToRun[@]} " =~ "rename_procs" ]];
    then
	# time python rename_procs.py --inputPath=rawRootFiles/3l/2016/rebinned_quantile/ 2>&1 | tee cout_rename_procs_2016_3l.txt
	for year in "${Years[@]}"
	do
	    if [[ "${year}" == "RUN2" ]]
	    then
		continue
	    fi

	    # add & at the end of command to run the command in background
	    #time python rename_procs.py --inputPath=rawRootFiles/${channel}/${year}/rebinned_quantile/ 2>&1 | tee cout_rename_procs_${channel}_${year}.txt &
	    command_1="time python rename_procs.py --inputPath=rawRootFiles/${channel}/${year}/rebinned_quantile/ "
	    echo "`date`: Running: ${command_1}"
	    echo "kJobToRunInBkg: ${kJobToRunInBkg}"
	    ${command_1}  2>&1 | tee cout_rename_procs_${channel}_${year}.txt &

	    kJobToRunInBkg=kJobToRunInBkg+1
	    if [ "$kJobToRunInBkg" -ge "$MaxNJobsToRunInBkg" ]
	    then
		echo "`date`: kJobToRunInBkg: ${kJobToRunInBkg}.  waiting for running jobs to get done"
		wait
		kJobToRunInBkg=0
		echo "`date`: kJobToRunInBkg: ${kJobToRunInBkg} reset."
	    fi
	done

	wait
	kJobToRunInBkg=0
	echo "`date`: Done rename_procs_${channel}_${year} "
	printf "\n\n"
    fi

    kJobToRunInBkg=0
    if [[ " ${stepsToRun[@]} " =~ "writeCards" ]];
    then
	# writeResCards ~~~~~~~~~~
	for limitType in "${LimitsTypes[@]}"
	do
	    for year in "${Years[@]}"
	    do
		if [[ "${year}" == "RUN2" ]]
		then
		    continue
		fi

		if [[ "${limitType}" == "spin0"  || "${limitType}" == "spin2" ]];
		then
		    # python writeResCards.py --channel=3l --era=2016 --spinCase=spin0 --inputPath=rawRootFiles/3l/2016/rebinned_quantile/newProcName/ --outPath=dataCards_spin0/3l/2016 2>&1 | tee cout_writeResCards_spin0_2016_3l.txt
		    # python writeResCards.py --channel=3l --era=2016 --spinCase=spin2 --inputPath=rawRootFiles/3l/2016/rebinned_quantile/newProcName/ --outPath=dataCards_spin2/3l/2016 2>&1 | tee cout_writeResCards_spin2_2016_3l.txt
		    #run_job local "time python python writeResCards.py --channel=${channel} --era=${year} --spinCase=${limitType} --inputPath=rawRootFiles/${channel}/${year}/rebinned_quantile/newProcName/ --outPath=dataCards_${limitType}/${channel}/${year} 2>&1 | tee ${dir_base}/cout_writeResCards_${channel}_${year}_${limitType}.txt  &" writeResCards_${channel}_${year}_${limitType}
		    #time python writeResCards.py --channel=${channel} --era=${year} --spinCase=${limitType} --inputPath=rawRootFiles/${channel}/${year}/rebinned_quantile/newProcName/ --outPath=dataCards_${limitType}/${channel}/${year} 2>&1 | tee ${dir_base}/cout_writeResCards_${channel}_${year}_${limitType}.txt  &
		    command_1="time python writeResCards.py --channel=${channel} --era=${year} --spinCase=${limitType} --inputPath=rawRootFiles/${channel}/${year}/rebinned_quantile/newProcName/ --outPath=dataCards_${limitType}/${channel}/${year} "
		    echo "`date`: Running: ${command_1}"
		    echo "kJobToRunInBkg: ${kJobToRunInBkg}"
		    ${command_1}  2>&1 | tee ${dir_base}/cout_writeResCards_${channel}_${year}_${limitType}.txt  &
		fi

		if [[ "${limitType}" == "nonresLO"  || "${limitType}" == "nonresNLO" ]];
		then
		    # time python writenonresCards.py --sigtype nonresLO --era 2016 --channel 3l --outPath dataCards_nonRes_LO/3l/2016 --inputPath rawRootFiles/3l/2016/rebinned_quantile/newProcName/ 2>&1 | tee cout_writenonresCards_LO_2016_3l.txt
		    # time python writenonresCards.py --sigtype nonresNLO --era 2016 --channel 3l --outPath dataCards_nonRes_NLO/3l/2016 --inputPath rawRootFiles/3l/2016/rebinned_quantile/newProcName/ 2>&1 | tee cout_writenonresCards_NLO_2016_3l.txt
		    #run_job local "time python writenonresCards.py --sigtype ${limitType} --era ${year} --channel ${channel} --inputPath rawRootFiles/${channel}/${year}/rebinned_quantile/newProcName/ --outPath dataCards_${limitType}/${channel}/${year}  2>&1 | tee ${dir_base}/cout_writenonresCards_${channel}_${year}_${limitType}.txt  &" writenonresCards_${channel}_${year}_${limitType}
		    #time python writenonresCards.py --sigtype ${limitType} --era ${year} --channel ${channel} --inputPath rawRootFiles/${channel}/${year}/rebinned_quantile/newProcName/ --outPath dataCards_${limitType}/${channel}/${year}  2>&1 | tee ${dir_base}/cout_writenonresCards_${channel}_${year}_${limitType}.txt  &
		    command_1="time python writenonresCards.py --sigtype ${limitType} --era ${year} --channel ${channel} --inputPath rawRootFiles/${channel}/${year}/rebinned_quantile/newProcName/ --outPath dataCards_${limitType}/${channel}/${year} "
		    if [[ "${systOption}" == "withoutFullSyst" ]];
		    then
			command_1="${command_1}  --withoutFullSyst "
		    fi
		    echo "`date`: Running: ${command_1}"
		    echo "kJobToRunInBkg: ${kJobToRunInBkg}"
		    ${command_1}  2>&1 | tee ${dir_base}/cout_writenonresCards_${channel}_${year}_${limitType}.txt  &
		fi

		kJobToRunInBkg=kJobToRunInBkg+1
		if [ "$kJobToRunInBkg" -ge "$MaxNJobsToRunInBkg" ]
		then
		    echo "`date`: kJobToRunInBkg: ${kJobToRunInBkg}.  waiting for running jobs to get done"
		    wait
		    kJobToRunInBkg=0
		    echo "`date`: kJobToRunInBkg: ${kJobToRunInBkg} reset."
		fi	    
	    done	
	done

	wait
	kJobToRunInBkg=0
	echo "`date`: Done  writeResCards/writenonresCards "
	printf "\n\n"
    fi

    
    kJobToRunInBkg=0
    if [[ " ${stepsToRun[@]} " =~ "combineYear" ]];
    then
	# combineYear ~~~~~~~~~
	for limitType in "${LimitsTypes[@]}"
	do
	    # time python combineYear.py --inputPath dataCards_spin0/3l/ --channel 3l 2>&1 | tee cout_combineYear_spin0.txt
	    # time python combineYear.py --inputPath dataCards_spin2/3l/ --channel 3l 2>&1 | tee cout_combineYear_spin2.txt
	    # time python combineYear.py --inputPath dataCards_nonRes_LO/3l/ --channel 3l 2>&1 | tee cout_combineYear_nonRes_LO.txt
	    # time python combineYear.py --inputPath dataCards_nonRes_NLO/3l/ --channel 3l 2>&1 | tee cout_combineYear_nonRes_NLO.txt
	    #run_job local "time python combineYear.py --inputPath dataCards_${limitType}/${channel}/ --channel 3l 2>&1 | tee cout_combineYear_${channel}_${limitType}.txt  &" combineYear_${channel}_${limitType}
	    #time python combineYear.py --inputPath dataCards_${limitType}/${channel}/ --channel ${channel} 2>&1 | tee cout_combineYear_${channel}_${limitType}.txt  &
	    command_1="time python combineYear.py --inputPath dataCards_${limitType}/${channel}/ --channel ${channel} "
	    echo "`date`: Running: ${command_1}"
	    echo "kJobToRunInBkg: ${kJobToRunInBkg}"
	    ${command_1}  2>&1 | tee cout_combineYear_${channel}_${limitType}.txt  &

	    kJobToRunInBkg=kJobToRunInBkg+1
	    if [ "$kJobToRunInBkg" -ge "$MaxNJobsToRunInBkg" ]
	    then
		echo "`date`: kJobToRunInBkg: ${kJobToRunInBkg}.  waiting for running jobs to get done"
		wait
		kJobToRunInBkg=0
		echo "`date`: kJobToRunInBkg: ${kJobToRunInBkg} reset."
	    fi	    		
	done
	
	wait
	kJobToRunInBkg=0
	echo "`date`: Done combineYear "
	printf "\n\n"
    fi


    kJobToRunInBkg=0
    if [[ " ${stepsToRun[@]} " =~ "calcLimits" ]];
    then    
	# calcResLimits ~~~~~~
	for limitType in "${LimitsTypes[@]}"
	do
	    for year in "${LimitsDatasets[@]}"
	    do
		# time python calcResLimits.py --inputPath=dataCards_spin0/3l/2016 --outPath combineResults_spin0/3l/2016 --era 2016 --spinCase spin0 --channel 3l 2>&1 | tee cout_calcResLimits_spin0_2016_3l.txt
		# time python calcResLimits.py --inputPath=dataCards_spin2/3l/2016 --outPath combineResults_spin2/3l/2016 --era 2016 --spinCase spin2 --channel 3l 2>&1 | tee cout_calcResLimits_spin2_2016_3l.txt
		# time python calcnoResLimits.py --inputPath dataCards_nonRes_LO/3l/2016/ --channel 3l --era 2016 --outPath combineResults_nonRes_LO/3l/2016 2>&1 | tee cout_calcResLimits_nonRes_LO_2016_3l.txt
		if [[ "${limitType}" == "spin0"  || "${limitType}" == "spin2" ]];
		then
	    	    #run_job local "time python calcResLimits.py --inputPath dataCards_${limitType}/${channel}/${year}/ --outPath combineResults_${limitType}/${channel}/${year} --channel ${channel} --era ${year} --spinCase ${limitType}  2>&1 | tee cout_calcResLimits_${channel}_${year}_${limitType}.txt  &" calcnoResLimits_${channel}_${year}_${limitType}
		    command_1="time python calcResLimits.py --inputPath dataCards_${limitType}/${channel}/${year}/ --outPath combineResults_${limitType}/${channel}/${year} --channel ${channel} --era ${year} --spinCase ${limitType}   "
		    if [[ ${runMode} == "sbatch" ]];
		    then
			command_1="${command_1}  --batchMode "
		    fi
		    echo "`date`: Running: 	${command_1}"
		    echo "kJobToRunInBkg: ${kJobToRunInBkg}"
		    ${command_1} 2>&1 | tee cout_calcResLimits_${channel}_${year}_${limitType}.txt  &
		fi
		
		if [[ "${limitType}" == "nonresLO"  ]];
		then
	    	    #run_job local "time python calcnoResLimits.py --inputPath dataCards_${limitType}/${channel}/${year}/ --outPath combineResults_${limitType}/${channel}/${year} --channel ${channel} --era ${year}  2>&1 | tee cout_calcResLimits_${channel}_${year}_${limitType}.txt  &" calcnoResLimits_${channel}_${year}_${limitType}
		    command_1="python calcnoResLimits.py --inputPath dataCards_${limitType}/${channel}/${year}/ --outPath combineResults_${limitType}/${channel}/${year} --channel ${channel} --era ${year} "
		    if [[ ${asimovDataset} == "True" ]];
		    then
			command_1="${command_1}  --asimovDataset "
		    fi
		    if [[ ${runMode} == "sbatch" ]];
		    then
			command_1="${command_1}  --batchMode "
		    fi
		    echo "`date`: Running: 	${command_1}"
		    echo "kJobToRunInBkg: ${kJobToRunInBkg}"
		    ${command_1} 2>&1 | tee cout_calcnoResLimits_${channel}_${year}_${limitType}.txt  &
		fi

		kJobToRunInBkg=kJobToRunInBkg+1
		if [ "$kJobToRunInBkg" -ge "$MaxNJobsToRunInBkg" ]
		then
		    echo "`date`: kJobToRunInBkg: ${kJobToRunInBkg}.  waiting for running jobs to get done"
		    wait
		    kJobToRunInBkg=0
		    echo "`date`: kJobToRunInBkg: ${kJobToRunInBkg} reset."
		fi	    		
	    done
	done


	wait
	kJobToRunInBkg=0
	echo "`date`:  calLimits done"
	printf "\n\n"
    fi
done

: '

if [[ " ${Years[@]} " =~ "2017" ]];
then
    echo "2017 year exist"
fi

if [[ " ${Years[@]} " =~ "RUN2" ]];
then
    echo "RUN2 year exist"
fi
'

#exit 0

: '
python rebin_quantiles.py --inputPath=rawRootFiles/3l/2016/ --quantSig 2>&1 | tee cout_rebin_quantiles_2016_3l.txt
python rebin_quantiles.py --inputPath=rawRootFiles/3l/2017/ --quantSig 2>&1 | tee cout_rebin_quantiles_2017_3l.txt
python rebin_quantiles.py --inputPath=rawRootFiles/3l/2018/ --quantSig 2>&1 | tee cout_rebin_quantiles_2018_3l.txt

python rename_procs.py --inputPath=rawRootFiles/3l/2016/rebinned_quantile/ 2>&1 | tee cout_rename_procs_2016_3l.txt
python rename_procs.py --inputPath=rawRootFiles/3l/2017/rebinned_quantile/ 2>&1 | tee cout_rename_procs_2017_3l.txt
python rename_procs.py --inputPath=rawRootFiles/3l/2018/rebinned_quantile/ 2>&1 | tee cout_rename_procs_2018_3l.txt


python writeResCards.py --channel=3l --era=2016 --spinCase=spin0 --inputPath=rawRootFiles/3l/2016/rebinned_quantile/newProcName/ --outPath=dataCards_spin0/3l/2016 2>&1 | tee cout_writeResCards_spin0_2016_3l.txt
python writeResCards.py --channel=3l --era=2017 --spinCase=spin0 --inputPath=rawRootFiles/3l/2017/rebinned_quantile/newProcName/ --outPath=dataCards_spin0/3l/2017 2>&1 | tee cout_writeResCards_spin0_2017_3l.txt
python writeResCards.py --channel=3l --era=2018 --spinCase=spin0 --inputPath=rawRootFiles/3l/2018/rebinned_quantile/newProcName/ --outPath=dataCards_spin0/3l/2018 2>&1 | tee cout_writeResCards_spin0_2018_3l.txt

python writeResCards.py --channel=3l --era=2016 --spinCase=spin2 --inputPath=rawRootFiles/3l/2016/rebinned_quantile/newProcName/ --outPath=dataCards_spin2/3l/2016 2>&1 | tee cout_writeResCards_spin2_2016_3l.txt
python writeResCards.py --channel=3l --era=2017 --spinCase=spin2 --inputPath=rawRootFiles/3l/2017/rebinned_quantile/newProcName/ --outPath=dataCards_spin2/3l/2017 2>&1 | tee cout_writeResCards_spin2_2017_3l.txt
python writeResCards.py --channel=3l --era=2018 --spinCase=spin2 --inputPath=rawRootFiles/3l/2018/rebinned_quantile/newProcName/ --outPath=dataCards_spin2/3l/2018 2>&1 | tee cout_writeResCards_spin2_2018_3l.txt

python writenonresCards.py --sigtype nonresLO --era 2016 --channel 3l --outPath dataCards_nonRes_LO/3l/2016 --inputPath rawRootFiles/3l/2016/rebinned_quantile/newProcName/ 2>&1 | tee cout_writenonresCards_LO_2016_3l.txt
python writenonresCards.py --sigtype nonresLO --era 2017 --channel 3l --outPath dataCards_nonRes_LO/3l/2017 --inputPath rawRootFiles/3l/2017/rebinned_quantile/newProcName/ 2>&1 | tee cout_writenonresCards_LO_2017_3l.txt
python writenonresCards.py --sigtype nonresLO --era 2018 --channel 3l --outPath dataCards_nonRes_LO/3l/2018 --inputPath rawRootFiles/3l/2018/rebinned_quantile/newProcName/ 2>&1 | tee cout_writenonresCards_LO_2018_3l.txt

python writenonresCards.py --sigtype nonresNLO --era 2016 --channel 3l --outPath dataCards_nonRes_NLO/3l/2016 --inputPath rawRootFiles/3l/2016/rebinned_quantile/newProcName/ 2>&1 | tee cout_writenonresCards_NLO_2016_3l.txt
python writenonresCards.py --sigtype nonresNLO --era 2017 --channel 3l --outPath dataCards_nonRes_NLO/3l/2017 --inputPath rawRootFiles/3l/2017/rebinned_quantile/newProcName/ 2>&1 | tee cout_writenonresCards_NLO_2017_3l.txt
python writenonresCards.py --sigtype nonresNLO --era 2018 --channel 3l --outPath dataCards_nonRes_NLO/3l/2018 --inputPath rawRootFiles/3l/2018/rebinned_quantile/newProcName/ 2>&1 | tee cout_writenonresCards_NLO_2018_3l.txt

python combineYear.py --inputPath dataCards_spin0/3l/ --channel 3l 2>&1 | tee cout_combineYear_spin0.txt
python combineYear.py --inputPath dataCards_spin2/3l/ --channel 3l 2>&1 | tee cout_combineYear_spin2.txt
python combineYear.py --inputPath dataCards_nonRes_LO/3l/ --channel 3l 2>&1 | tee cout_combineYear_nonRes_LO.txt
#python combineYear.py --inputPath dataCards_nonRes_NLO/3l/ --channel 3l 2>&1 | tee cout_combineYear_nonRes_NLO.txt

python calcResLimits.py --inputPath=dataCards_spin0/3l/2016 --outPath combineResults_spin0/3l/2016 --era 2016 --spinCase spin0 --channel 3l 2>&1 | tee cout_calcResLimits_spin0_2016_3l.txt
python calcResLimits.py --inputPath=dataCards_spin0/3l/2017 --outPath combineResults_spin0/3l/2017 --era 2017 --spinCase spin0 --channel 3l 2>&1 | tee cout_calcResLimits_spin0_2017_3l.txt
python calcResLimits.py --inputPath=dataCards_spin0/3l/2018 --outPath combineResults_spin0/3l/2018 --era 2018 --spinCase spin0 --channel 3l 2>&1 | tee cout_calcResLimits_spin0_2018_3l.txt
python calcResLimits.py --inputPath=dataCards_spin0/3l/RUN2 --outPath combineResults_spin0/3l/RUN2 --era RUN2 --spinCase spin0 --channel 3l 2>&1 | tee cout_calcResLimits_spin0_RUN2_3l.txt

python calcResLimits.py --inputPath=dataCards_spin2/3l/2016 --outPath combineResults_spin2/3l/2016 --era 2016 --spinCase spin2 --channel 3l 2>&1 | tee cout_calcResLimits_spin2_2016_3l.txt
python calcResLimits.py --inputPath=dataCards_spin2/3l/2017 --outPath combineResults_spin2/3l/2017 --era 2017 --spinCase spin2 --channel 3l 2>&1 | tee cout_calcResLimits_spin2_2017_3l.txt
python calcResLimits.py --inputPath=dataCards_spin2/3l/2018 --outPath combineResults_spin2/3l/2018 --era 2018 --spinCase spin2 --channel 3l 2>&1 | tee cout_calcResLimits_spin2_2018_3l.txt
python calcResLimits.py --inputPath=dataCards_spin2/3l/RUN2 --outPath combineResults_spin2/3l/RUN2 --era RUN2 --spinCase spin2 --channel 3l 2>&1 | tee cout_calcResLimits_spin2_RUN2_3l.txt

python calcnoResLimits.py --inputPath dataCards_nonRes_LO/3l/2016/ --channel 3l --era 2016 --outPath combineResults_nonRes_LO/3l/2016 2>&1 | tee cout_calcResLimits_nonRes_LO_2016_3l.txt
python calcnoResLimits.py --inputPath dataCards_nonRes_LO/3l/2017/ --channel 3l --era 2017 --outPath combineResults_nonRes_LO/3l/2017 2>&1 | tee cout_calcResLimits_nonRes_LO_2017_3l.txt
python calcnoResLimits.py --inputPath dataCards_nonRes_LO/3l/2018/ --channel 3l --era 2018 --outPath combineResults_nonRes_LO/3l/2018 2>&1 | tee cout_calcResLimits_nonRes_LO_2018_3l.txt
python calcnoResLimits.py --inputPath dataCards_nonRes_LO/3l/RUN2/ --channel 3l --era RUN2 --outPath combineResults_nonRes_LO/3l/RUN2 2>&1 | tee cout_calcResLimits_nonRes_LO_RUN2_3l.txt

python plotResLimit.py --inputPath combineResults_spin0/3l/2016/ --outPath plots_spin0/3l/2016/massScan_spin0_3l_2016.pdf --spinCase spin0 --ylabel "hh-multilepton 3l (35.9 fb^{-1}) @13 TeV" --log --min 0.1 2>&1 | tee cout_plotResLimit_spin0_2016.txt
python plotResLimit.py --inputPath combineResults_spin0/3l/2017/ --outPath plots_spin0/3l/2017/massScan_spin0_3l_2017.pdf --spinCase spin0 --ylabel "hh-multilepton 3l (41.5 fb^{-1}) @13 TeV" --log --min 0.1 2>&1 | tee cout_plotResLimit_spin0_2017.txt
python plotResLimit.py --inputPath combineResults_spin0/3l/2018/ --outPath plots_spin0/3l/2018/massScan_spin0_3l_2018.pdf --spinCase spin0 --ylabel "hh-multilepton 3l (59.7 fb^{-1}) @13 TeV" --log --min 0.1 2>&1 | tee cout_plotResLimit_spin0_2018.txt
python plotResLimit.py --inputPath combineResults_spin0/3l/RUN2/ --outPath plots_spin0/3l/RUN2/massScan_spin0_3l_RUN2.pdf --spinCase spin0 --ylabel "hh-multilepton 3l (137.2 fb^{-1}) @13 TeV" --log --min 0.01 2>&1 | tee cout_plotResLimit_spin0_RUN2.txt

python plotResLimit.py --inputPath combineResults_spin2/3l/2016/ --outPath plots_spin2/3l/2016/massScan_spin2_3l_2016.pdf --spinCase spin2 --ylabel "hh-multilepton 3l (35.9 fb^{-1}) @13 TeV" --log --min 0.1 2>&1 | tee cout_plotResLimit_spin2_2016.txt
python plotResLimit.py --inputPath combineResults_spin2/3l/2017/ --outPath plots_spin2/3l/2017/massScan_spin2_3l_2017.pdf --spinCase spin2 --ylabel "hh-multilepton 3l (41.5 fb^{-1}) @13 TeV" --log --min 0.1 2>&1 | tee cout_plotResLimit_spin2_2017.txt
python plotResLimit.py --inputPath combineResults_spin2/3l/2018/ --outPath plots_spin2/3l/2018/massScan_spin2_3l_2018.pdf --spinCase spin2 --ylabel "hh-multilepton 3l (59.7 fb^{-1}) @13 TeV" --log --min 0.1 2>&1 | tee cout_plotResLimit_spin2_2018.txt
python plotResLimit.py --inputPath combineResults_spin2/3l/RUN2/ --outPath plots_spin2/3l/RUN2/massScan_spin2_3l_RUN2.pdf --spinCase spin2 --ylabel "hh-multilepton 3l (137.2 fb^{-1}) @13 TeV" --log --min 0.01 2>&1 | tee cout_plotResLimit_spin2_RUN2.txt

python plotnonResLimit.py --inputPath combineResults_nonRes_LO/3l/2016/ --outPath plots_nonRes_LO/3l/2016/bmScan_3l_2016.pdf --ylabel "hh-multilepton 3l (35.9 fb^{-1}) @13 TeV" --log --min 0.01 2>&1 | tee cout_plotResLimit_nonRes_LO_2016.txt
python plotnonResLimit.py --inputPath combineResults_nonRes_LO/3l/2017/ --outPath plots_nonRes_LO/3l/2017/bmScan_3l_2017.pdf --ylabel "hh-multilepton 3l (41.5 fb^{-1}) @13 TeV" --log --min 0.01 2>&1 | tee cout_plotResLimit_nonRes_LO_2017.txt
python plotnonResLimit.py --inputPath combineResults_nonRes_LO/3l/2018/ --outPath plots_nonRes_LO/3l/2018/bmScan_3l_2018.pdf --ylabel "hh-multilepton 3l (59.7 fb^{-1}) @13 TeV" --log --min 0.01 2>&1 | tee cout_plotResLimit_nonRes_LO_2018.txt
python plotnonResLimit.py --inputPath combineResults_nonRes_LO/3l/RUN2/ --outPath plots_nonRes_LO/3l/RUN2/bmScan_3l_RUN2.pdf --ylabel "hh-multilepton 3l (137.2 fb^{-1}) @13 TeV" --log --min 0.01 2>&1 | tee cout_plotResLimit_nonRes_LO_RUN2.txt
'

: '
python prefitplot.py --inputCard dataCards_spin0/3l/2016/datacard_3l_2016_spin0_400.txt --Bin HH_3l --sigDesc "m#Chi 400 GeV(1 pb)" --outPath plots_spin0/3l/2016/ --ylabel "hh-multilepton 3l (35.9 fb^{-1}) @ 13 TeV" --Info "3l_2016_spin0_400" --log
python prefitplot.py --inputCard dataCards_spin0/3l/2016/datacard_3l_2016_spin0_400.txt --Bin HH_3l --sigDesc "m#Chi 400 GeV(1 pb)" --outPath plots_spin0/3l/2016/ --ylabel "hh-multilepton 3l (35.9 fb^{-1}) @ 13 TeV" --Info "3l_2016_spin0_400" --skipCombine
python prefitplot.py --inputCard dataCards_spin0/3l/2017/datacard_3l_2017_spin0_400.txt --Bin HH_3l --sigDesc "m#Chi 400 GeV(1 pb)" --outPath plots_spin0/3l/2017/ --ylabel "hh-multilepton 3l (41.5 fb^{-1}) @ 13 TeV" --Info "3l_2017_spin0_400" --log
python prefitplot.py --inputCard dataCards_spin0/3l/2017/datacard_3l_2017_spin0_400.txt --Bin HH_3l --sigDesc "m#Chi 400 GeV(1 pb)" --outPath plots_spin0/3l/2017/ --ylabel "hh-multilepton 3l (41.5 fb^{-1}) @ 13 TeV" --Info "3l_2017_spin0_400" --skipCombine
python prefitplot.py --inputCard dataCards_spin0/3l/2018/datacard_3l_2018_spin0_400.txt --Bin HH_3l --sigDesc "m#Chi 400 GeV(1 pb)" --outPath plots_spin0/3l/2018/ --ylabel "hh-multilepton 3l (59.7 fb^{-1}) @ 13 TeV" --Info "3l_2018_spin0_400" --log
python prefitplot.py --inputCard dataCards_spin0/3l/2018/datacard_3l_2018_spin0_400.txt --Bin HH_3l --sigDesc "m#Chi 400 GeV(1 pb)" --outPath plots_spin0/3l/2018/ --ylabel "hh-multilepton 3l (59.7 fb^{-1}) @ 13 TeV" --Info "3l_2018_spin0_400" --skipCombine
python prefitplot.py --inputCard dataCards_spin0/3l/2016/datacard_3l_2016_spin0_700.txt --Bin HH_3l --sigDesc "m#Chi 700 GeV(1 pb)" --outPath plots_spin0/3l/2016/ --ylabel "hh-multilepton 3l (35.9 fb^{-1}) @ 13 TeV" --Info "3l_2016_spin0_700" --log
python prefitplot.py --inputCard dataCards_spin0/3l/2016/datacard_3l_2016_spin0_700.txt --Bin HH_3l --sigDesc "m#Chi 700 GeV(1 pb)" --outPath plots_spin0/3l/2016/ --ylabel "hh-multilepton 3l (35.9 fb^{-1}) @ 13 TeV" --Info "3l_2016_spin0_700" --skipCombine
python prefitplot.py --inputCard dataCards_spin0/3l/2017/datacard_3l_2017_spin0_700.txt --Bin HH_3l --sigDesc "m#Chi 700 GeV(1 pb)" --outPath plots_spin0/3l/2017/ --ylabel "hh-multilepton 3l (41.5 fb^{-1}) @ 13 TeV" --Info "3l_2017_spin0_700" --log
python prefitplot.py --inputCard dataCards_spin0/3l/2017/datacard_3l_2017_spin0_700.txt --Bin HH_3l --sigDesc "m#Chi 700 GeV(1 pb)" --outPath plots_spin0/3l/2017/ --ylabel "hh-multilepton 3l (41.5 fb^{-1}) @ 13 TeV" --Info "3l_2017_spin0_700" --skipCombine
python prefitplot.py --inputCard dataCards_spin0/3l/2018/datacard_3l_2018_spin0_700.txt --Bin HH_3l --sigDesc "m#Chi 700 GeV(1 pb)" --outPath plots_spin0/3l/2018/ --ylabel "hh-multilepton 3l (59.7 fb^{-1}) @ 13 TeV" --Info "3l_2018_spin0_700" --log
python prefitplot.py --inputCard dataCards_spin0/3l/2018/datacard_3l_2018_spin0_700.txt --Bin HH_3l --sigDesc "m#Chi 700 GeV(1 pb)" --outPath plots_spin0/3l/2018/ --ylabel "hh-multilepton 3l (59.7 fb^{-1}) @ 13 TeV" --Info "3l_2018_spin0_700" --skipCombine
python prefitplot.py --inputCard dataCards_spin2/3l/2016/datacard_3l_2016_spin2_400.txt --Bin HH_3l --sigDesc "m#Chi 400 GeV(1 pb)" --outPath plots_spin2/3l/2016/ --ylabel "hh-multilepton 3l (35.9 fb^{-1}) @ 13 TeV" --Info "3l_2016_spin2_400" --log
python prefitplot.py --inputCard dataCards_spin2/3l/2016/datacard_3l_2016_spin2_400.txt --Bin HH_3l --sigDesc "m#Chi 400 GeV(1 pb)" --outPath plots_spin2/3l/2016/ --ylabel "hh-multilepton 3l (35.9 fb^{-1}) @ 13 TeV" --Info "3l_2016_spin2_400" --skipCombine
python prefitplot.py --inputCard dataCards_spin2/3l/2017/datacard_3l_2017_spin2_400.txt --Bin HH_3l --sigDesc "m#Chi 400 GeV(1 pb)" --outPath plots_spin2/3l/2017/ --ylabel "hh-multilepton 3l (41.5 fb^{-1}) @ 13 TeV" --Info "3l_2017_spin2_400" --log
python prefitplot.py --inputCard dataCards_spin2/3l/2017/datacard_3l_2017_spin2_400.txt --Bin HH_3l --sigDesc "m#Chi 400 GeV(1 pb)" --outPath plots_spin2/3l/2017/ --ylabel "hh-multilepton 3l (41.5 fb^{-1}) @ 13 TeV" --Info "3l_2017_spin2_400" --skipCombine
python prefitplot.py --inputCard dataCards_spin2/3l/2018/datacard_3l_2018_spin2_400.txt --Bin HH_3l --sigDesc "m#Chi 400 GeV(1 pb)" --outPath plots_spin2/3l/2018/ --ylabel "hh-multilepton 3l (59.7 fb^{-1}) @ 13 TeV" --Info "3l_2018_spin2_400" --log
python prefitplot.py --inputCard dataCards_spin2/3l/2018/datacard_3l_2018_spin2_400.txt --Bin HH_3l --sigDesc "m#Chi 400 GeV(1 pb)" --outPath plots_spin2/3l/2018/ --ylabel "hh-multilepton 3l (59.7 fb^{-1}) @ 13 TeV" --Info "3l_2018_spin2_400" --skipCombine
python prefitplot.py --inputCard dataCards_spin2/3l/2016/datacard_3l_2016_spin2_700.txt --Bin HH_3l --sigDesc "m#Chi 700 GeV(1 pb)" --outPath plots_spin2/3l/2016/ --ylabel "hh-multilepton 3l (35.9 fb^{-1}) @ 13 TeV" --Info "3l_2016_spin2_700" --log
python prefitplot.py --inputCard dataCards_spin2/3l/2016/datacard_3l_2016_spin2_700.txt --Bin HH_3l --sigDesc "m#Chi 700 GeV(1 pb)" --outPath plots_spin2/3l/2016/ --ylabel "hh-multilepton 3l (35.9 fb^{-1}) @ 13 TeV" --Info "3l_2016_spin2_700" --skipCombine
python prefitplot.py --inputCard dataCards_spin2/3l/2017/datacard_3l_2017_spin2_700.txt --Bin HH_3l --sigDesc "m#Chi 700 GeV(1 pb)" --outPath plots_spin2/3l/2017/ --ylabel "hh-multilepton 3l (41.5 fb^{-1}) @ 13 TeV" --Info "3l_2017_spin2_700" --log
python prefitplot.py --inputCard dataCards_spin2/3l/2017/datacard_3l_2017_spin2_700.txt --Bin HH_3l --sigDesc "m#Chi 700 GeV(1 pb)" --outPath plots_spin2/3l/2017/ --ylabel "hh-multilepton 3l (41.5 fb^{-1}) @ 13 TeV" --Info "3l_2017_spin2_700" --skipCombine
python prefitplot.py --inputCard dataCards_spin2/3l/2018/datacard_3l_2018_spin2_700.txt --Bin HH_3l --sigDesc "m#Chi 700 GeV(1 pb)" --outPath plots_spin2/3l/2018/ --ylabel "hh-multilepton 3l (59.7 fb^{-1}) @ 13 TeV" --Info "3l_2018_spin2_700" --log
python prefitplot.py --inputCard dataCards_spin2/3l/2018/datacard_3l_2018_spin2_700.txt --Bin HH_3l --sigDesc "m#Chi 700 GeV(1 pb)" --outPath plots_spin2/3l/2018/ --ylabel "hh-multilepton 3l (59.7 fb^{-1}) @ 13 TeV" --Info "3l_2018_spin2_700" --skipCombine
python prefitplot.py --inputCard dataCards_nonRes_LO/3l/2016/datacard_3l_2016_SM.txt --Bin HH_3l --sigDesc "SM ggHH LO (1 pb)" --outPath plots_nonRes_LO/3l/2016 --ylabel "hh-multilepton 3l (35.9 fb^{-1}) @ 13 TeV" --Info "3l_2016_nonResLO_SM" --log
python prefitplot.py --inputCard dataCards_nonRes_LO/3l/2016/datacard_3l_2016_SM.txt --Bin HH_3l --sigDesc "SM ggHH LO (1 pb)" --outPath plots_nonRes_LO/3l/2016 --ylabel "hh-multilepton 3l (35.9 fb^{-1}) @ 13 TeV" --Info "3l_2016_nonResLO_SM" --skipCombine
python prefitplot.py --inputCard dataCards_nonRes_LO/3l/2017/datacard_3l_2017_SM.txt --Bin HH_3l --sigDesc "SM ggHH LO (1 pb)" --outPath plots_nonRes_LO/3l/2017 --ylabel "hh-multilepton 3l (41.5 fb^{-1}) @ 13 TeV" --Info "3l_2017_nonResLO_SM" --log
python prefitplot.py --inputCard dataCards_nonRes_LO/3l/2017/datacard_3l_2017_SM.txt --Bin HH_3l --sigDesc "SM ggHH LO (1 pb)" --outPath plots_nonRes_LO/3l/2017 --ylabel "hh-multilepton 3l (41.5 fb^{-1}) @ 13 TeV" --Info "3l_2017_nonResLO_SM" --skipCombine
python prefitplot.py --inputCard dataCards_nonRes_LO/3l/2018/datacard_3l_2018_SM.txt --Bin HH_3l --sigDesc "SM ggHH LO (1 pb)" --outPath plots_nonRes_LO/3l/2018 --ylabel "hh-multilepton 3l (59.7 fb^{-1}) @ 13 TeV" --Info "3l_2018_nonResLO_SM" --log
python prefitplot.py --inputCard dataCards_nonRes_LO/3l/2018/datacard_3l_2018_SM.txt --Bin HH_3l --sigDesc "SM ggHH LO (1 pb)" --outPath plots_nonRes_LO/3l/2018 --ylabel "hh-multilepton 3l (59.7 fb^{-1}) @ 13 TeV" --Info "3l_2018_nonResLO_SM" --skipCombine
python prefitplot.py --inputCard dataCards_nonRes_NLO/3l/2016/datacard_3l_2016_SM.txt --Bin HH_3l --sigDesc "SM ggHH + qqHH" --outPath plots_nonRes_NLO/3l/2016 --ylabel "hh-multilepton 3l (35.9 fb^{-1}) @ 13 TeV" --Info "3l_2016_nonResNLO_SM" --log --NLO
python prefitplot.py --inputCard dataCards_nonRes_NLO/3l/2016/datacard_3l_2016_SM.txt --Bin HH_3l --sigDesc "SM ggHH + qqHH" --outPath plots_nonRes_NLO/3l/2016 --ylabel "hh-multilepton 3l (35.9 fb^{-1}) @ 13 TeV" --Info "3l_2016_nonResNLO_SM" --skipCombine --NLO
python prefitplot.py --inputCard dataCards_nonRes_NLO/3l/2017/datacard_3l_2017_SM.txt --Bin HH_3l --sigDesc "SM ggHH + qqHH" --outPath plots_nonRes_NLO/3l/2017 --ylabel "hh-multilepton 3l (41.5 fb^{-1}) @ 13 TeV" --Info "3l_2017_nonResNLO_SM" --log --NLO
python prefitplot.py --inputCard dataCards_nonRes_NLO/3l/2017/datacard_3l_2017_SM.txt --Bin HH_3l --sigDesc "SM ggHH + qqHH" --outPath plots_nonRes_NLO/3l/2017 --ylabel "hh-multilepton 3l (41.5 fb^{-1}) @ 13 TeV" --Info "3l_2017_nonResNLO_SM" --skipCombine --NLO
python prefitplot.py --inputCard dataCards_nonRes_NLO/3l/2018/datacard_3l_2018_SM.txt --Bin HH_3l --sigDesc "SM ggHH + qqHH" --outPath plots_nonRes_NLO/3l/2018 --ylabel "hh-multilepton 3l (59.7 fb^{-1}) @ 13 TeV" --Info "3l_2018_nonResNLO_SM" --log --NLO
python prefitplot.py --inputCard dataCards_nonRes_NLO/3l/2018/datacard_3l_2018_SM.txt --Bin HH_3l --sigDesc "SM ggHH + qqHH" --outPath plots_nonRes_NLO/3l/2018 --ylabel "hh-multilepton 3l (59.7 fb^{-1}) @ 13 TeV" --Info "3l_2018_nonResNLO_SM" --skipCombine --NLO
'

#python goodnessOfFitPlots.py --inputPath dataCards_nonRes_LO/3l/RUN2/datacard_3l_Run2_SM.txt --era RUN2 --channel 3l --analysis nonRes_LO_SM --ntoys 500 --outPath plots_nonRes_LO/3l/RUN2/ --minx 0 --maxx 75 
