#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 12:11:50 2020

@author: yogesh
"""
import casatasks
import casatools
import os
import logging
from datetime import datetime
import configparser
import  inputdata as inp
import  beforecalflag as bcflg
import  aftercalflag as acflg
import  calibration as cal
import  split as split
import  splat as splat
import  image as image
import  ugfunctions as ugf
import  numpy as np

logfile_name = datetime.now().strftime('capture_%H_%M_%S_%d_%m_%Y.log')
logging.basicConfig(filename=logfile_name,level=logging.DEBUG)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)

logging.info("#######################################################################################")
logging.info("You are using mCAPTURE: modified CAsa Pipeline-cum-Toolkit for Upgraded GMRT data REduction.")
logging.info("")
logging.info("#######################################################################################")
logging.info("LOGFILE = %s", logfile_name)
logging.info("CASA_LOGFILE = %s", 'casa-'+logfile_name)
logging.info("#################################################################################")

config = configparser.ConfigParser() 
config.read('config_example.ini')

fromlta = config.getboolean('basic', 'fromlta')
fromfits = config.getboolean('basic', 'fromfits')
frommultisrcms = config.getboolean('basic','frommultisrcms')
findbadants = config.getboolean('basic','findbadants')                          
flagbadants= config.getboolean('basic','flagbadants')                      
findbadchans = config.getboolean('basic','findbadchans')                         
flagbadfreq= config.getboolean('basic','flagbadfreq')                           
flaginit = config.getboolean('basic','flaginit')                             
doinitcal = config.getboolean('basic','doinitcal')                              
doflag = config.getboolean('basic','doflag')                              
redocal = config.getboolean('basic','redocal')                              
dosplit = config.getboolean('basic','dosplit')                               
flagsplitfile = config.getboolean('basic','flagsplitfile')                            
dosplitavg = config.getboolean('basic','dosplitavg')                             
doflagavg = config.getboolean('basic','doflagavg')                             
dospectralcube = config.getboolean('basic','dospectralcube')  
makedirty = config.getboolean('basic','makedirty')                            
doselfcal = config.getboolean('basic','doselfcal')                              
usetclean = config.getboolean('default','usetclean')                        
ltafile =config.get('basic','ltafile')
gvbinpath = config.get('basic', 'gvbinpath').split(',')
workdir=config.get('basic', 'workdir')
fits_file = config.get('basic','fits_file')
msfilename =config.get('basic','msfilename')
#splitfilename =config.get('basic','splitfilename')
#splitavgfilename = config.get('basic','splitavgfilename')
setquackinterval = config.getfloat('basic','setquackinterval')
ref_ant = config.get('basic','ref_ant')
clipfluxcal = [float(config.get('basic','clipfluxcal').split(',')[0]),float(config.get('basic','clipfluxcal').split(',')[1])]
clipphasecal =[float(config.get('basic','clipphasecal').split(',')[0]),float(config.get('basic','clipphasecal').split(',')[1])]
cliptarget =[float(config.get('basic','cliptarget').split(',')[0]),float(config.get('basic','cliptarget').split(',')[1])]   
clipresid=[float(config.get('basic','clipresid').split(',')[0]),float(config.get('basic','clipresid').split(',')[1])]
chanavg = config.getint('basic','chanavg')
imcellsize = [config.get('basic','imcellsize')]
imsize_pix = int(config.get('basic','imsize_pix'))
scaloops = config.getint('basic','scaloops')
mJythreshold = float(config.get('basic','mJythreshold'))
pcaloops = config.getint('basic','pcaloops')
scalsolints = config.get('basic','scalsolints').split(',')
niter_start = int(config.get('basic','niter_start'))
use_nterms = config.getint('basic','use_nterms')
nwprojpl = config.getint('basic','nwprojpl')
z=float(config.get('basic','redshift'))
uvracal=config.get('default','uvracal')
uvrascal=config.get('default','uvrascal')
target = config.getboolean('default','target')
print(fits_file,msfilename)
################################################################################################
l=inp.inputdata(fromlta,fromfits,ltafile,fits_file,msfilename,gvbinpath)
l.checkdata() # donot run if msfile exists
m=inp.readdata(frommultisrcms,msfilename)
m.listfile()
gainspw, gainspw2, mygoodchans, flagspw, mypol, poltypes, myampcals, mypcals, mytargets=m.listread()
###############################################################################################
n=bcflg.flagbeforecal(msfilename, flagbadants, flaginit, flagbadfreq, gainspw, mygoodchans, flagspw, mypol, poltypes, myampcals, mypcals, mytargets, setquackinterval, clipfluxcal, clipphasecal, cliptarget, target)
mycmds,myflagcmd=n.flagbadantennas()
##############################################################################################
o=cal.calibration(msfilename,doinitcal,myampcals,flagspw,mypcals,myampcals,ref_ant,gainspw,uvracal,target,mytargets)
p=acflg.aftercalflag(msfilename,gainspw, mygoodchans,doflag, flagspw, mypol,poltypes, myampcals, mypcals, mytargets,setquackinterval,clipfluxcal,clipphasecal,cliptarget,target)
###################################################################################################
o=cal.calibration(msfilename,doinitcal,myampcals,flagspw,mypcals,myampcals,ref_ant,gainspw,uvracal,target,mytargets)

i=0
for i in range(0,len(myampcals)):
            mean,sig,median,mad=ugf.myvisstatampafcal(msfilename,myampcals[i],'0:155~155')
            clipfluxcal=[mean-5*sig,mean+5*sig]
            logging.info("The clipping range for flux calibrator:%s",myampcals[i])
            logging.info(clipfluxcal)
            casatasks.flagdata(vis=msfilename,mode="clip", spw=flagspw,field=myampcals[i], clipminmax=clipfluxcal,
                datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
                action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
            i=i+1

i=0
for i in range(0,len(mypcals)):
            mean,sig,median,mad=ugf.myvisstatampafcal(msfilename,mypcals[i],'0:155~155')
            clipphasecal=[mean-5*sig,mean+5*sig]
            logging.info("The clipping range for phase calibrator:%s",mypcals[i])
            logging.info(clipphasecal)
            casatasks.flagdata(vis=msfilename,mode="clip", spw=flagspw,field=mypcals[i], clipminmax=clipphasecal,
                datacolumn="corrected",clipoutside=True, clipzeros=True, extendpols=False, 
                action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
            i=i+1
o=cal.calibration(msfilename,doinitcal,myampcals,flagspw,mypcals,myampcals,ref_ant,gainspw,uvracal,target,mytargets)
###############################################################################################
i=0
for i in range(0,len(myampcals)):
            mean,sig,median,mad=ugf.myvisstatphaseafcal(msfilename,myampcals[i],'0:155~155')
            clipfluxcal=[(mean-5*sig),(mean+5*sig)]
            logging.info("The clipping range for flux calibrator:%s",myampcals[i])
            logging.info(clipfluxcal)
            casatasks.flagdata(vis=msfilename,mode="clip", spw=flagspw,field=myampcals[i], clipminmax=clipfluxcal, correlation='ARG_ALL',
                datacolumn="corrected",clipoutside=True, clipzeros=False, extendpols=False, 
                action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
            i=i+1

i=0
for i in range(0,len(mypcals)):
            mean,sig,median,mad=ugf.myvisstatphaseafcal(msfilename,mypcals[i],'0:155~155')
            clipphasecal=[(mean-5*sig),(mean+5*sig)]
            logging.info("The clipping range for phase calibrator: %s",mypcals[i])
            logging.info(clipphasecal)
            casatasks.flagdata(vis=msfilename,mode="clip", spw=flagspw,field=mypcals[i], clipminmax=clipphasecal, correlation='ARG_ALL',
                datacolumn="corrected",clipoutside=True, clipzeros=False, extendpols=False, 
                action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
            i=i+1
o=cal.calibration(msfilename,doinitcal,myampcals,flagspw,mypcals,myampcals,ref_ant,gainspw,uvracal,target,mytargets)

##############################################################################################
q=split.split(msfilename,mytargets,workdir,dosplit,gainspw2,flagsplitfile)
###############################################################Check manually for ripples and remove antennas with ripples##################
######################### Continuum imaging for self calibration ##################################################
r=splat.splat(dosplitavg,msfilename,mytargets,workdir,flagspw,chanavg,doflagavg,cliptarget)

file,gt,im=image.image(msfilename,mytargets,workdir,gainspw2,makedirty,doselfcal,usetclean,mJythreshold,imcellsize,imsize_pix,use_nterms,nwprojpl,ref_ant,scaloops,pcaloops,scalsolints,clipresid,niter_start,chanavg,uvrascal,z,flagspw)

######################### Spectral line imaging ###############################################
if (dospectralcube==True):
    spfitspw='0:101~480'
    s=image.spectralcube(mytargets, workdir, im, spfitspw, mJythreshold, imcellsize, imsize_pix, z)

