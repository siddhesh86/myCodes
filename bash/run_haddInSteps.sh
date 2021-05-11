
#!/bin/bash

declare -a ipFiles=(analyze_signal_*_nonresonant_*.root)
ipFiles_addition=hadd_stage2_Tight_SS.root
opFileName=hadd_stage2_Tight_SS_HHNLOwMVASpin0


declare -i MaxFilesHaddAtATime=4
declare -i MaxNJobsToRunInBkg=10



declare -i nIpFiles=0
# count total number of input files
for ipFile in "${ipFiles[@]}"
do
    nIpFiles=nIpFiles+1
done


## 0: hadd ipfiles to intermediate files
skIpFiles=""
declare -i iIpFile=0
declare -i kFilesForHadd_0=0
declare -i kStageInHadd_0=0
declare -i kJobToRunInBkg=0 
for ipFile in "${ipFiles[@]}"
do
    
    skIpFiles="${skIpFiles} ${ipFile}"
    echo "  ipFile for stage 0: ${kStageInHadd_0} ${kFilesForHadd_0}: ${ipFile}"
    iIpFile=iIpFile+1
    kFilesForHadd_0=kFilesForHadd_0+1
    
    if [ "$kFilesForHadd_0" -ge "$MaxFilesHaddAtATime" ] || [ "$iIpFile" -ge "$nIpFiles" ]
    then
	opFileName_stage="${opFileName}_tmpStage_0_${kStageInHadd_0}.root"
	command_1="time hadd  ${opFileName_stage}   ${skIpFiles}  "
	echo "`date`: ${command_1} 2>&1 | tee cout_hadd_tmpStage_${kStageInHadd_0}.txt "
	echo
	${command_1}  2>&1 | tee cout_hadd_tmpStage_${kStageInHadd_0}.txt &

	skIpFiles=""
	kFilesForHadd_0=0
	kStageInHadd_0=kStageInHadd_0+1

	kJobToRunInBkg=kJobToRunInBkg+1
	if [ "$kJobToRunInBkg" -ge "$MaxNJobsToRunInBkg" ]
	then
	    echo "`date`: kJobToRunInBkg: ${kJobToRunInBkg}.  waiting for running jobs to get done"
	    wait
	    kJobToRunInBkg=0
	    echo "`date`: hadd stage 0: kJobToRunInBkg: ${kJobToRunInBkg} reset."
	fi
    fi
done
wait
kJobToRunInBkg=0
echo "`date`: hadd stage 0 done.  kJobToRunInBkg: ${kJobToRunInBkg} reset."
echo "nIpFiles: ${nIpFiles},    kStageInHadd_0:${kStageInHadd_0}"
printf "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n\n"


## i: hadd intermediate root files
declare -i stage_i=0
declare -i nFilesToHadd_stage_i=kStageInHadd_0
while [ "$nFilesToHadd_stage_i" -gt "$MaxFilesHaddAtATime" ]
do
    skIpFiles=""
    declare -i kFilesForHadd_stage_iplus1=0
    declare -i kStageInHadd_stage_iplus1=0
    declare -i stage_iplus1=stage_i+1    
    declare -i nFilesToHadd_stage_i_minus_1=nFilesToHadd_stage_i-1

    printf "Running for stage_iplus1: %d:: \n" "$stage_iplus1"
    for ((kIpFile=0; kIpFile < nFilesToHadd_stage_i; kIpFile++));
    #for kIpFile in $(seq 0 ${nFilesToHadd_stage_i})
    do
	ipFile="${opFileName}_tmpStage_${stage_i}_${kIpFile}.root"
	skIpFiles="${skIpFiles} ${ipFile}"
	echo "  ipFile for stage ${stage_iplus1}: ${kStageInHadd_stage_iplus1} ${kFilesForHadd_stage_iplus1}: ${ipFile}"
	kFilesForHadd_stage_iplus1=kFilesForHadd_stage_iplus1+1

	
	if [ "$kFilesForHadd_stage_iplus1" -ge "$MaxFilesHaddAtATime" ] || [ "$kIpFile" -ge "$nFilesToHadd_stage_i_minus_1" ]
	then    
	    opFileName_stage="${opFileName}_tmpStage_${stage_iplus1}_${kStageInHadd_stage_iplus1}.root"
	    command_1="time hadd  ${opFileName_stage}   ${skIpFiles}  "
	    echo "`date`: ${command_1} 2>&1 | tee cout_hadd_tmpStage_${stage_iplus1}_${kStageInHadd_stage_iplus1}.txt "
	    echo
	    ${command_1}  2>&1 | tee cout_hadd_tmpStage_${stage_iplus1}_${kStageInHadd_stage_iplus1}.txt &
	    
	    skIpFiles=""
	    kFilesForHadd_stage_iplus1=0
	    kStageInHadd_stage_iplus1=kStageInHadd_stage_iplus1+1

	    kJobToRunInBkg=kJobToRunInBkg+1
	    if [ "$kJobToRunInBkg" -ge "$MaxNJobsToRunInBkg" ]
	    then
		echo "`date`: kJobToRunInBkg: ${kJobToRunInBkg}.  waiting for running jobs to get done"
		wait
		kJobToRunInBkg=0
		echo "`date`: hadd stage 0: kJobToRunInBkg: ${kJobToRunInBkg} reset."
	    fi	    
	fi	
    done
    
    wait
    kJobToRunInBkg=0
    echo "`date`: hadd stage ${stage_iplus1} done.  kJobToRunInBkg: ${kJobToRunInBkg} reset."

    nFilesToHadd_stage_i=kStageInHadd_stage_iplus1
    stage_i=stage_iplus1
    printf "\n\n Finally  for stage_i: %d, nFilesToHadd_stage_i: %d \n" "$stage_i" "$nFilesToHadd_stage_i"
    printf "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n\n\n"
done

wait
kJobToRunInBkg=0
echo "`date`: hadd intermediate stages done.  kJobToRunInBkg: ${kJobToRunInBkg} reset."

## final hadd of intermediate hadded files
skIpFiles=""
for ((kIpFile=0; kIpFile < nFilesToHadd_stage_i; kIpFile++));
do
    ipFile="${opFileName}_tmpStage_${stage_i}_${kIpFile}.root"
    skIpFiles="${skIpFiles} ${ipFile}"
    echo "  ipFile for stage final: ${kIpFile}: ${ipFile}"
done
command_1="time hadd  ${opFileName}.root   ${skIpFiles} ${ipFiles_addition} "
echo "`date`: ${command_1} 2>&1 | tee cout_hadd_tmpStage_final.txt "
echo
${command_1}  2>&1 | tee cout_hadd_tmpStage_final.txt 

printf "\n\n haddging to %s.root done" "${opFileName}"


