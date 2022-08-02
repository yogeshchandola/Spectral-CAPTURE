#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 12:55:41 2020

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

def calibration(msfilename,doinitcal,myampcals,flagspw,mypcals,mybpcals,ref_ant,gainspw,uvracal,target,mytargets):
# Calibration begins.
    if doinitcal == True:
        assert os.path.isdir(msfilename)
        try:
              assert os.path.isdir(msfilename), "doinitcal = True but ms file not found."
        except AssertionError:
              logging.info("doinitcal = True but ms file not found.")
              sys.exit()
        mycalsuffix = ''
 #       casalog.filter('INFO')
        casatasks.clearcal(vis=msfilename)
        for i in range(0,len(myampcals)):
#            default(setjy)
            casatasks.setjy(vis=msfilename, spw=flagspw, field=myampcals[i])
# Delay calibration  using the first flux calibrator in the list - should depend on which is less flagged
        if os.path.isdir(str(msfilename)+'.K1'+mycalsuffix) == True:
            os.system('rm -rf '+str(msfilename)+'.K1'+mycalsuffix)
            casatasks.gaincal(vis=msfilename, caltable=str(msfilename)+'.K1'+mycalsuffix, spw =gainspw, field=myampcals[0], 
                    solint='60s', refant=ref_ant,	solnorm= True, gaintype='K', gaintable=[], parang=True)
        else:
            casatasks.gaincal(vis=msfilename, caltable=str(msfilename)+'.K1'+mycalsuffix, spw =gainspw, field=myampcals[0], 
                    solint='60s', refant=ref_ant,	solnorm= True, gaintype='K', gaintable=[], parang=True) #changed flagspw to gainspw
        kcorrfield =myampcals[0]
        
# an initial bandpass
        if os.path.isdir(str(msfilename)+'.AP.G0'+mycalsuffix) == True:
            os.system('rm -rf '+str(msfilename)+'.AP.G0'+mycalsuffix)
 #           default(gaincal)
            casatasks.gaincal(vis=msfilename, caltable=str(msfilename)+'.AP.G0'+mycalsuffix, append=True, field=str(','.join(mybpcals)), 
                    spw =gainspw, solint = 'int', refant = ref_ant, minsnr = 2.0, solmode = 'L1R', gaintype = 'G', calmode = 'ap', gaintable = [str(msfilename)+'.K1'+mycalsuffix],
                    interp = ['nearest,nearestflag', 'nearest,nearestflag' ], parang = True)
        else:
            casatasks.gaincal(vis=msfilename, caltable=str(msfilename)+'.AP.G0'+mycalsuffix, append=True, field=str(','.join(mybpcals)), 
                    spw =gainspw, solint = 'int', refant = ref_ant, minsnr = 2.0, solmode = 'L1R', gaintype = 'G', calmode = 'ap', gaintable = [str(msfilename)+'.K1'+mycalsuffix],
                    interp = ['nearest,nearestflag', 'nearest,nearestflag' ], parang = True)
        if os.path.isdir(str(msfilename)+'.B1'+mycalsuffix) == True:
            os.system('rm -rf '+str(msfilename)+'.B1'+mycalsuffix)
#            default(bandpass)
            casatasks.bandpass(vis=msfilename, caltable=str(msfilename)+'.B1'+mycalsuffix, spw =flagspw, field=str(','.join(mybpcals)), solint='inf', refant=ref_ant, solnorm = True,
             minsnr=2.0, fillgaps=8, parang = True, gaintable=[str(msfilename)+'.K1'+mycalsuffix,str(msfilename)+'.AP.G0'+mycalsuffix], interp=['nearest,nearestflag','nearest,nearestflag'])
        else:
            casatasks.bandpass(vis=msfilename, caltable=str(msfilename)+'.B1'+mycalsuffix, spw =flagspw, field=str(','.join(mybpcals)), solint='inf', refant=ref_ant, solnorm = True,
             minsnr=2.0, fillgaps=8, parang = True, gaintable=[str(msfilename)+'.K1'+mycalsuffix,str(msfilename)+'.AP.G0'+mycalsuffix], interp=['nearest,nearestflag','nearest,nearestflag'])
# do a gaincal on all calibrators
        if mypcals !=[]:
            mycals=myampcals+mypcals
        else:
            mycals=myampcals+mytargets
            mypcals=mytargets
        i=0
        if os.path.isdir(str(msfilename)+'.AP.G'+mycalsuffix) == True:
            os.system('rm -rf '+str(msfilename)+'.AP.G'+mycalsuffix)
        for i in range(0,len(mycals)):
            ugf.mygaincal_ap2(msfilename,mycals[i],ref_ant,gainspw,uvracal,mycalsuffix)
# Get flux scale
        if os.path.isdir(str(msfilename)+'.fluxscale'+mycalsuffix) == True:
            os.system('rm -rf '+str(msfilename)+'.fluxscale'+mycalsuffix)
######################################
        if mypcals !=[]:
            if '3C286' in myampcals:
                myfluxscale= ugf.getfluxcal2(msfilename,'3C286',str(', '.join(mypcals)),mycalsuffix)
                myfluxscaleref = '3C286'
            elif '3C147' in myampcals:
                myfluxscale= ugf.getfluxcal2(msfilename,'3C147',str(', '.join(mypcals)),mycalsuffix)
                myfluxscaleref = '3C147'
            else:
                myfluxscale= ugf.getfluxcal2(msfilename,myampcals[0],str(', '.join(mypcals)),mycalsuffix)
                myfluxscaleref = myampcals[0]
            logging.info(myfluxscale)        
            mygaintables =[str(msfilename)+'.fluxscale'+mycalsuffix,str(msfilename)+'.K1'+mycalsuffix, str(msfilename)+'.B1'+mycalsuffix]
        else:
            mygaintables =[str(msfilename)+'.AP.G'+mycalsuffix,str(msfilename)+'.K1'+mycalsuffix, str(msfilename)+'.B1'+mycalsuffix]
##############################
        for i in range(0,len(myampcals)):
 #           default(applycal)
            casatasks.applycal(vis=msfilename, field=myampcals[i], spw = flagspw, gaintable=mygaintables, gainfield=[myampcals[i],'',''], 
                 interp=['nearest','',''], calwt=[False], parang=False)
#For phase calibrator:
        if mypcals !=[]:
 #           default(applycal)
            casatasks.applycal(vis=msfilename, field=str(', '.join(mypcals)), spw = flagspw, gaintable=mygaintables, gainfield=str(', '.join(mypcals)), 
                 interp=['nearest','','nearest'], calwt=[False], parang=False)
   
#For the target:
        if target ==True:
            if mypcals !=[]:
#                default(applycal)
                casatasks.applycal(vis=msfilename, field=str(', '.join(mytargets)), spw = flagspw, gaintable=mygaintables,
                     gainfield=[str(', '.join(mypcals)),'',''],interp=['linear','','nearest'], calwt=[False], parang=False)
            else:
#                default(applycal)
                casatasks.applycal(vis=msfilename, field=str(', '.join(mytargets)), spw = flagspw, gaintable=mygaintables,
                     gainfield=[str(', '.join(mytargets)),'',''],interp=['linear','','nearest'], calwt=[False], parang=False)	
        logging.info("Finished initial calibration.")
        logging.info("A flagging summary is provided for the MS file.")
 #           flagsummary(msfilename)
        return