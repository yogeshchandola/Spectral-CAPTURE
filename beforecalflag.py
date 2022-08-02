#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 12:45:02 2020

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
###################################


class flagbeforecal:
        def __init__(self,msfilename,flagbadants,flaginit,flagbadfreq,gainspw, mygoodchans, flagspw, mypol,poltypes, myampcals, mypcals, mytargets,setquackinterval,clipfluxcal,clipphasecal,cliptarget,target):
            self.msfilename=msfilename
            self.flagbadants=flagbadants
            self.flaginit=flaginit
            self.gainspw=gainspw
            self.flagbadfreq=flagbadfreq
            self.mygoodchans=mygoodchans
            self.flagspw=flagspw
            self.mypol=mypol
            self.poltypes=poltypes
            self.myampcals=myampcals
            self.mypcals=mypcals
            self.mytargets=mytargets
            self.setquackinterval=setquackinterval
            self.clipfluxcal=clipfluxcal
            self.clipphasecal=clipphasecal
            self.cliptarget=cliptarget
            self.target=target
        def flagbadantennas(self):
            # need a condition to see if the pcal is same as 
            ampcalscans =[]
            for i in range(0,len(self.myampcals)):
                ampcalscans.extend(ugf.getscans(self.msfilename,self.myampcals[i]))
            pcalscans=[]
            for i in range(0,len(self.mypcals)):
                pcalscans.extend(ugf.getscans(self.msfilename, self.mypcals[i]))
            tgtscans=[]
            for i in range(0,len(self.mytargets)):
                tgtscans.extend(ugf.getscans(self.msfilename,self.mytargets[i]))
#	print(ampcalscans)
            logging.info("Amplitude calibrator scans are:")
            logging.info(ampcalscans)
#	print(pcalscans)
            logging.info("Phase calibrator scans are:")
            logging.info(pcalscans)
#	print(tgtscans)
            logging.info("Target source scans are:")
            logging.info(tgtscans)
            allscanlist= ampcalscans+pcalscans+tgtscans
# get a list of antennas
            antsused = ugf.getantlist(self.msfilename,int(allscanlist[0]))
            logging.info("Antennas in the file:")
            logging.info(antsused)
###################################
# find band ants
            if self.flagbadants==True:
                findbadants = True
            if findbadants == True:
                myantlist = antsused
                mycmds = []
#############
                #meancutoff = ugf.getbandcut(self.msfilename)
#############
                mycorr1='rr'
                mycorr2='ll'
 #               mygoodchans1=self.mygoodchans
                mycalscans = ampcalscans+pcalscans
#		print(mycalscans)
                logging.info("Calibrator scan numbers:")
                logging.info(mycalscans)
                allbadants=[]
            for j in range(0,len(mycalscans)):
                myantmeans = []
                myantmeds=[]
                badantlist = []
                ante=''
                meancutoff, sigma,median, mad=ugf.myvisstatampraw(self.msfilename,self.mygoodchans,ante,mycorr2,str(mycalscans[j]))
                print('mean:',meancutoff,'std:',sigma,'median:',median,'mad:',mad)
                logging.info("The cutoff used for flagging bad antennas is ")
                logging.info(median-mad)
                
                for i in range(0,len(myantlist)):
                    if self.mypol == 1:
                        if self.poltypes[0] == 5:
                            oneantmean1,sig1,median1,mad1 = ugf.myvisstatampraw(self.msfilename,self.mygoodchans,myantlist[i],mycorr1,str(mycalscans[j]))
                            oneantmead2 =oneantmean1*100.
                            median2=median1*100
                        elif self.poltypes[0] == 8:
                            oneantmean2,sig2,median2,mad2 = ugf.myvisstatampraw(self.msfilename,self.mygoodchans,myantlist[i],mycorr2,str(mycalscans[j]))
                            oneantmean1=oneantmean2*100.
                            median1=median2*100
                    else:
                        oneantmean1,sig1,median1,mad1 = ugf.myvisstatampraw(self.msfilename,self.mygoodchans,myantlist[i],mycorr1,str(mycalscans[j]))
                        oneantmean2,sig2,median2,mad2 = ugf.myvisstatampraw(self.msfilename,self.mygoodchans,myantlist[i],mycorr2,str(mycalscans[j]))                       
                    oneantmean = min(oneantmean1,oneantmean2)
                    oneantmed=min(median1,median2)
                    myantmeans.append(oneantmean)
                    myantmeds.append(oneantmed)
                    if oneantmed < (median-mad):
                        badantlist.append(myantlist[i])
                        allbadants.append(myantlist[i])
                logging.info("The following antennas are bad for the given scan numbers.")
                logging.info('%s, %s',str(badantlist), str(mycalscans[j]))
                if badantlist!=[]:
                    myflgcmd = "mode='manual' antenna='%s' scan='%s'" % (str(';'.join(badantlist)), str(mycalscans[j]))
                    mycmds.append(myflgcmd)
                    logging.info(myflgcmd)
                    onelessscan = mycalscans[j] - 1
                    onemorescan = mycalscans[j] + 1
                    if onelessscan in tgtscans:
                        myflgcmd = "mode='manual' antenna='%s' scan='%s'" % (str(';'.join(badantlist)), str(mycalscans[j]-1))
                        mycmds.append(myflgcmd)
                        logging.info(myflgcmd)
                    if onemorescan in tgtscans:
                        myflgcmd = "mode='manual' antenna='%s' scan='%s'" % (str(';'.join(badantlist)), str(mycalscans[j]+1))
                        mycmds.append(myflgcmd)
                        logging.info(myflgcmd)
# execute the flagging commands accumulated in cmds
            if self.flagbadants==True:
                logging.info("Now flagging the bad antennas.")
                print(mycmds)
                casatasks.flagdata(vis=self.msfilename, mode='list', inpfile=mycmds)	
######### Bad channel flagging for known persistent RFI.
            if self.flagbadfreq==True:
                findbadchans = True
            if findbadchans ==True:
                rfifreqall =[0.36E09,0.3796E09,0.486E09,0.49355E09,0.8808E09,0.885596E09,0.7646E09,0.769092E09] # always bad
                myfreqs =  ugf.freq_info(self.msfilename)
                mybadchans=[]
                for j in range(0,len(rfifreqall)-1,2):
                    for i in range(0,len(myfreqs)):
                        if (myfreqs[i] > rfifreqall[j] and myfreqs[i] < rfifreqall[j+1]): #(myfreqs[i] > 0.486E09 and myfreqs[i] < 0.49355E09):
                            mybadchans.append('0:'+str(i))
                mychanflag = str(', '.join(mybadchans))
            if mybadchans!=[]:
                myflgcmd =["mode='manual' spw='%s'" % (mychanflag)]
                if self.flagbadfreq==True:
                    casatasks.flagdata(vis=self.msfilename,mode='list', inpfile=myflgcmd)
            else:
                    logging.info("None of the well-known RFI-prone frequencies were found in the data.")
############ Initial flagging ################
            if self.flaginit == True:
                 try:
                     assert os.path.isdir(self.msfilename), "flaginit = True but ms file not found."
                 except AssertionError:
                     logging.info("flaginit = True but ms file not found.")
                     sys.exit()
 #                 casalog.filter('INFO')
              #Step 1 : Flag the first channel.
 #             default(casatasks.flagdata)
            casatasks.flagdata(vis=self.msfilename, mode='manual', field='', spw='0:0', antenna='', correlation='', action='apply', savepars=True,
                       cmdreason='badchan', outfile='')
#Step 3: Do a quack step 
 #               default(casatasks.flagdata)
            casatasks.flagdata(vis=self.msfilename, mode='quack', field='', spw='0', antenna='', correlation='', timerange='',
                         quackinterval=self.setquackinterval, quackmode='beg', action='apply', savepars=True, cmdreason='quackbeg',
                         outfile='')
 #               default(casatasks.flagdata)
            casatasks.flagdata(vis=self.msfilename, mode='quack', field='', spw='0', antenna='', correlation='', timerange='', quackinterval=self.setquackinterval,
                         quackmode='endb', action='apply', savepars=True, cmdreason='quackendb', outfile='')
# Clip at high amp levels
            if self.myampcals !=[]:
 #                       default(casatasks.flagdata)
                        casatasks.flagdata(vis=self.msfilename,mode="clip", spw=self.flagspw,field=str(','.join(self.myampcals)), clipminmax=self.clipfluxcal, datacolumn="DATA",clipoutside=True, clipzeros=True, extendpols=False, 
                        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
            if self.mypcals !=[]:
 #                       default(casatasks.flagdata)
                        casatasks.flagdata(vis=self.msfilename,mode="clip", spw=self.flagspw,field=str(','.join(self.mypcals)), clipminmax=self.clipphasecal, datacolumn="DATA",clipoutside=True, clipzeros=True, extendpols=False, 
                        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
# After clip, now flag using 'tfcrop' option for flux and phase cal tight flagging
                        casatasks.flagdata(vis=self.msfilename,mode="tfcrop", datacolumn="DATA", field=str(','.join(self.mypcals)), ntime="scan",
                        timecutoff=5.0, freqcutoff=5.0, timefit="line",freqfit="line",flagdimension="freqtime",extendflags=False, timedevscale=5.0,freqdevscale=5.0, extendpols=False,growaround=False,action="apply", flagbackup=True,overwrite=True, writeflags=True)
# Now extend the flags (80% more means full flag, change if required)
                        casatasks.flagdata(vis=self.msfilename,mode="extend",spw=self.flagspw,field=str(','.join(self.mypcals)),datacolumn="DATA",clipzeros=True,
                        ntime="scan", extendflags=False, extendpols=True,growtime=80.0, growfreq=80.0,growaround=False,
                        flagneartime=False, flagnearfreq=False, action="apply", flagbackup=True,overwrite=True, writeflags=True)
######### target flagging ### clip first
            if self.target == True:
                if self.mytargets !=[]:
                            casatasks.flagdata(vis=self.msfilename,mode="clip", spw=self.flagspw,field=str(','.join(self.mytargets)), clipminmax=self.cliptarget, datacolumn="DATA",clipoutside=True, clipzeros=True, extendpols=False, 
                                     action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
# flagging with tfcrop before calibration
#                        default(casatasks.flagdata)
            casatasks.flagdata(vis=self.msfilename,mode="tfcrop", datacolumn="DATA", field=str(','.join(self.mytargets)), ntime="scan",
                                     timecutoff=6.0, freqcutoff=6.0, timefit="poly",freqfit="poly",flagdimension="freqtime", 
                                     extendflags=False, timedevscale=5.0,freqdevscale=5.0, extendpols=False,growaround=False,
                                     action="apply", flagbackup=True,overwrite=True, writeflags=True)
# Now extend the flags (80% more means full flag, change if required)
            casatasks.flagdata(vis=self.msfilename,mode="extend",spw=self.flagspw,field=str(','.join(self.mytargets)),datacolumn="DATA",clipzeros=True,
                                 ntime="scan", extendflags=False, extendpols=True,growtime=80.0, growfreq=80.0,growaround=False,
                                 flagneartime=False, flagnearfreq=False, action="apply", flagbackup=True,overwrite=True, writeflags=True)
# Now summary
            casatasks.flagdata(vis=self.msfilename,mode="summary",datacolumn="DATA", extendflags=True, 
            name=self.msfilename+'summary.split', action="apply", flagbackup=True,overwrite=True, writeflags=True)	
            logging.info("A flagging summary is provided for the MS file.")
            
            return mycmds, myflgcmd
#                        flagsummary(self.msfilename) 
##################################################################### 
