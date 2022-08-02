#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 12:56:18 2020

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

#######Ishwar post calibration flagging
def aftercalflag(msfilename,gainspw, mygoodchans,doflag, flagspw, mypol,poltypes, myampcals, mypcals, mytargets,setquackinterval,clipfluxcal,clipphasecal,cliptarget,target):
    if doflag == True:
        try:
                    assert os.path.isdir(msfilename)
                    logging.info("You have chosen to flag after the initial calibration.")
        except AssertionError:
                    logging.info("doflag = True but ms file not found.")
                    sys.exit()
#        default(flagdata)
        if myampcals !=[]:
                casatasks.flagdata(vis=msfilename,mode="clip", spw=flagspw,field=str(', '.join(myampcals)), clipminmax=clipfluxcal,
                datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
                action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
        if mypcals !=[]:
                casatasks.flagdata(vis=msfilename,mode="clip", spw=flagspw,field=str(', '.join(mypcals)), clipminmax=clipphasecal,
                datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
                action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
# After clip, now flag using 'tfcrop' option for flux and phase cal tight flagging
                casatasks.flagdata(vis=msfilename,mode="tfcrop", datacolumn="corrected", field=str(', '.join(mypcals)), ntime="scan",
                timecutoff=6.0, freqcutoff=5.0, timefit="line",freqfit="line",flagdimension="freqtime", 
                extendflags=False, timedevscale=5.0,freqdevscale=5.0, extendpols=False,growaround=False,
                action="apply", flagbackup=True,overwrite=True, writeflags=True)
# now flag using 'rflag' option  for flux and phase cal tight flagging
                casatasks.flagdata(vis=msfilename,mode="rflag",datacolumn="corrected",field=str(', '.join(mypcals)), timecutoff=5.0, 
                freqcutoff=5.0,timefit="poly",freqfit="line",flagdimension="freqtime", extendflags=False,
                timedevscale=4.0,freqdevscale=4.0,spectralmax=500.0,extendpols=False, growaround=False,
                flagneartime=False,flagnearfreq=False,action="apply",flagbackup=True,overwrite=True, writeflags=True)
# Now extend the flags (70% more means full flag, change if required)
                casatasks.flagdata(vis=msfilename,mode="extend",spw=flagspw,field=str(', '.join(mypcals)),datacolumn="corrected",clipzeros=True,
                 ntime="scan", extendflags=False, extendpols=False,growtime=90.0, growfreq=90.0,growaround=False,
                 flagneartime=False, flagnearfreq=False, action="apply", flagbackup=True,overwrite=True, writeflags=True)
# Now flag for target - moderate flagging, more flagging in self-cal cycles
        if mytargets !=[]:
                casatasks.flagdata(vis=msfilename,mode="clip", spw=flagspw,field=str(', '.join(mytargets)), clipminmax=cliptarget,
                datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
                action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
# C-C baselines are selected
                a, b = ugf.getbllists(msfilename)
                casatasks.flagdata(vis=msfilename,mode="tfcrop", datacolumn="corrected", field=str(', '.join(mytargets)), antenna=a[0],
                                   ntime="scan", timecutoff=8.0, freqcutoff=8.0, timefit="poly",freqfit="line",flagdimension="freqtime", 
                extendflags=False, timedevscale=5.0,freqdevscale=5.0, extendpols=False,growaround=False,
                action="apply", flagbackup=True,overwrite=True, writeflags=True)
# C- arm antennas and arm-arm baselines are selected.
                casatasks.flagdata(vis=msfilename,mode="tfcrop", datacolumn="corrected", field=str(', '.join(mytargets)), antenna=b[0],
                                   ntime="scan", timecutoff=6.0, freqcutoff=5.0, timefit="poly",freqfit="line",flagdimension="freqtime", 
                extendflags=False, timedevscale=5.0,freqdevscale=5.0, extendpols=False,growaround=False,
                action="apply", flagbackup=True,overwrite=True, writeflags=True)
# now flag using 'rflag' option
# C-C baselines are selected
                casatasks.flagdata(vis=msfilename,mode="rflag",datacolumn="corrected",field=str(', '.join(mytargets)), timecutoff=5.0, antenna=a[0],
                freqcutoff=8.0,timefit="poly",freqfit="poly",flagdimension="freqtime", extendflags=False,
                timedevscale=8.0,freqdevscale=5.0,spectralmax=500.0,extendpols=False, growaround=False,
                flagneartime=False,flagnearfreq=False,action="apply",flagbackup=True,overwrite=True, writeflags=True)
# C- arm antennas and arm-arm baselines are selected.
                casatasks.flagdata(vis=msfilename,mode="rflag",datacolumn="corrected",field=str(', '.join(mytargets)), timecutoff=5.0, antenna=b[0],
                freqcutoff=5.0,timefit="poly",freqfit="poly",flagdimension="freqtime", extendflags=False,
                timedevscale=5.0,freqdevscale=5.0,spectralmax=500.0,extendpols=False, growaround=False,
                flagneartime=False,flagnearfreq=False,action="apply",flagbackup=True,overwrite=True, writeflags=True)
# Now summary
                casatasks.flagdata(vis=msfilename,mode="summary",datacolumn="corrected", extendflags=True, 
                               name=msfilename+'summary.split', action="apply", flagbackup=True,overwrite=True, writeflags=True)
                logging.info("A flagging summary is provided for the MS file.")
#        flagsummary(msfilename)
    return