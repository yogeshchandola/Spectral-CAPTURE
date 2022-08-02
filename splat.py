#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 13:08:58 2020

@author: yogesh
"""
import casatasks
import casatools
import os
import logging
from modules import ugfunctions as ugf
from datetime import datetime
from os import sys
import numpy as np
# SPLIT AVERAGE
#############################################################
def splat(dosplitavg,msfilename,mytargets,workdir,gainspw1,chanavg,doflagavg,cliptarget):
    for i in range(0,len(mytargets)):
            splitfilename = str(workdir)+mytargets[i]+'split.ms'
            if dosplitavg == True:
                try:
                    assert os.path.isdir(splitfilename), "dosplitavg = True but the split file not found."
                except AssertionError:
                    logging.info("dosplitavg = True but the split file not found.")
                    sys.exit()
                logging.info("Your data will be averaged in frequency.")
                if os.path.isdir(str(workdir)+str(mytargets[i])+'splat.ms') == True:
                    os.system('rm -rf '+str(workdir)+str(mytargets[i])+'splat.ms')
                if os.path.isdir(str(workdir)+str(mytargets[i])+'splat.ms'+'.flagversions') == True:
                    os.system('rm -rf'+str(workdir)+str(mytargets[i])+'splat.ms'+'.flagversions')
                splitavgfilename = ugf.mysplitavg(splitfilename,workdir,mytargets[i],gainspw1,chanavg)

            if doflagavg == True:
                try:
                    assert os.path.isdir(splitavgfilename), "doflagavg = True but the splitavg file not found."
                except AssertionError:
                    logging.info("doflagavg = True but the splitavg file not found.")
                    sys.exit()
                logging.info("Flagging on freqeuncy averaged data.")
                a, b = ugf.getbllists(splitavgfilename)
                ugf.myrflagavg(splitavgfilename,'',b[0],6.0,6.0,'DATA','',cliptarget)
                ugf.myrflagavg(splitavgfilename,'',a[0],6.0,6.0,'DATA','',cliptarget)
 #               mean,sig,median,mad=ugf.myvisstatampafcal(splitavgfilename,mytargets[i],'')
 #               cliptarget1=[0,median+20*mad]
 #               casatasks.flagdata(vis=splitavgfilename,mode="clip", spw='',field=mytargets[i], clipminmax=cliptarget1,
 #               datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
 #               action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
                logging.info("A flagging summary is provided for the MS file.")
                os.system('aoflagger -indirect-read '+splitavgfilename)
                
 #       flagsummary(splitavgfilename)

############################################################

