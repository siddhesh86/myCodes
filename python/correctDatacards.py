#!/usr/bin/python3

import subprocess

Years=['2016']
Channel, AnaLepCharge = '3l', 'OS'
#AnaLepCharge='OS'
AnaVersion='20220204_hh_$CHANNEL_$YEAR_Datacards'
HistosToFit=['m3l']

PathPrearedatacardCfg='/scratch-persistent/ssawant/hhAnalysis/$YEAR/$ANAVERSION/cfgs/hh_$CHANNEL/prepareDatacards/prepareDatacards_hh_$CHANNEL_hh_$CHANNEL_$ANALEPCHARGE_$HISTOGRAMNAME_cfg.py'
PathAddsystfakesCfg='/scratch-persistent/ssawant/hhAnalysis/$YEAR/$ANAVERSION/cfgs/hh_$CHANNEL/addSystFakeRates/addSystFakeRates_hh_$CHANNEL_hh_$CHANNEL_$ANALEPCHARGE_$HISTOGRAMNAME_cfg.py'
#addSystFakeRates /scratch-persistent/ssawant/hhAnalysis/2016/20220204_hh_3l_2016_Datacards/cfgs/hh_3l/addSystFakeRates/addSystFakeRates_hh_3l_hh_3l_OS_m3l_cfg.py

appendTexts='''process.prepareDatacards.processesToCopy = cms.vstring(['data_obs', 'signal_ggf_nonresonant_cHHH1_hh', 'signal_ggf_nonresonant_cHHH5_hh', 'signal_ggf_nonresonant_hh', 'signal_vbf_nonresonant_1_1_1_hh', 'signal_vbf_nonresonant_1_0_1_hh', 'signal_vbf_nonresonant_1p5_1_1_hh', 'signal_ggf_nonresonant_cHHH2p45_hh', 'signal_vbf_nonresonant_1_1_0_hh', 'signal_vbf_nonresonant_0p5_1_1_hh', 'signal_vbf_nonresonant_1_1_2_hh', 'signal_ggf_nonresonant_nlo_hh', 'signal_ggf_nonresonant_cHHH0_hh', 'signal_vbf_nonresonant_1_2_1_hh', 'ZH', 'WH', 'TTH', 'ggH', 'qqH', 'tHq', 'tHW', 'ggZZ', 'qqZZ', 'WZ', 'WW', 'TT', 'TTW', 'TTWW', 'TTZ', 'DY', 'W', 'Other', 'Convs', 'data_fakes', 'fakes_mc'])'''
PathCfgToConcatenate='/home/ssawant/hhAnalysis/2016/20220204_hh_3l_2016_Datacards/manipulation/prepareDatacards_processToCopy_2.txt'


def execute_command(cmd):
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    print('\ncmd:',cmd,'\n output: ',str(output), '\n error: ',error)
    print('cmd.split(): ',cmd.split())
    

for Year in Years:
    print("Year:",Year)

    for HistoToFit in HistosToFit:
        print("HistoToFit:", HistoToFit)

        PathPrearedatacardCfg_0 = PathPrearedatacardCfg 
        PathPrearedatacardCfg_0 = PathPrearedatacardCfg_0.replace('$ANAVERSION',AnaVersion)
        PathPrearedatacardCfg_0 = PathPrearedatacardCfg_0.replace('$YEAR',Year)
        PathPrearedatacardCfg_0 = PathPrearedatacardCfg_0.replace('$CHANNEL',Channel)
        PathPrearedatacardCfg_0 = PathPrearedatacardCfg_0.replace('$ANALEPCHARGE',AnaLepCharge)
        PathPrearedatacardCfg_0 = PathPrearedatacardCfg_0.replace('$HISTOGRAMNAME',HistoToFit)

        PathPrearedatacardCfg_1 = PathPrearedatacardCfg_0.replace('.py','_1.py')        
        print("PathPrearedatacardCfg_0: ", PathPrearedatacardCfg_0)
    
        #execute_command('ls %s' % (PathPrearedatacardCfg_0))
        #execute_command('ls %s' % (str(PathPrearedatacardCfg_0.split('/')[:-1])) )
        execute_command('ls %s' % ( PathPrearedatacardCfg_0[:(PathPrearedatacardCfg_0.rindex('/'))] ) )
        execute_command('cp %s %s' % (PathPrearedatacardCfg_0,PathPrearedatacardCfg_1))
        execute_command('ls %s' % ( PathPrearedatacardCfg_0[:(PathPrearedatacardCfg_0.rindex('/'))] ) )

        #print("appendTexts: %s" % (appendTexts))
        #execute_command('echo \"%s\" \>\> %s' % (appendTexts, PathPrearedatacardCfg_1))
        execute_command('cat %s %s > %s' % (PathPrearedatacardCfg_0, PathCfgToConcatenate, PathPrearedatacardCfg_1) )
