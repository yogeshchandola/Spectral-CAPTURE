#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 13:08:20 2020

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
ms=casatools.ms()
msmd=casatools.msmetadata()

#############################################################
# SPLIT step
#############################################################

def split(msfilename,mytargets,workdir,dosplit,gainspw1,flagsplitfile):
    if dosplit == True:
        #	assert os.path.isdir(msfilename), "dosplit = True but ms file not found."
        try:
                assert os.path.isdir(msfilename), "dosplit = True but ms file not found."
        except AssertionError:
                logging.info("dosplit = True but ms file not found.")
                sys.exit()
        logging.info("The data on targets will be split into separate files.")
#        casalog.filter('INFO')

        
        for i in range(0,len(mytargets)):
            if os.path.isdir(str(workdir)+mytargets[i]+'split.ms') == True:
                        logging.info("The existing split file will be deleted.")
                        os.system('rm -rf '+str(workdir)+mytargets[i]+'split.ms')
            logging.info("Splitting target source data.")
            logging.info(gainspw1)
            splitfilename = ugf.mysplitinit(msfilename,workdir,mytargets[i],gainspw1,1)
#############################################################
# Flagging on split file
#############################################################
            if flagsplitfile == True:
                try:
                    assert os.path.isdir(splitfilename), "flagsplitfile = True but the split file not found."
                except AssertionError:
                    logging.info("flagsplitfile = True but the split file not found.")
                    sys.exit()
                logging.info("Now proceeding to flag on the split file.")
                myantselect =''
                ugf.mytfcrop(splitfilename,'',myantselect,8.0,8.0,'DATA','')
                a, b = ugf.getbllists(splitfilename)
                tdev = 6.0
                fdev = 6.0
                ugf.myrflag(splitfilename,'',a[0],tdev,fdev,'DATA','')
                tdev = 5.0
                fdev = 5.0
                ugf.myrflag(splitfilename,'',b[0],tdev,fdev,'DATA','')
                logging.info("A flagging summary is provided for the MS file.")
                #os.system('aoflagger -indirect-read -strategy S20rfistr.rfis '+splitfilename)
                os.system('aoflagger -indirect-read '+splitfilename)
                casatasks.flagdata(vis=splitfilename,mode='extend',growtime=100,growfreq=40)
 #       ugf.flagsummary(splitfilename)
#############################################################