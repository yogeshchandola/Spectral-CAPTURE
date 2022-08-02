import casatasks
import casatools
import os
import logging
from modules import ugfunctions as ugf
from datetime import datetime
from os import sys
import numpy as np


def image(msfilename,mytargets,workdir,gainspw1,makedirty,doselfcal,usetclean,mJythreshold,imcellsize,imsize_pix,use_nterms,nwprojpl,ref_ant,scaloops,pcaloops,scalsolints,clipresid,niter_start,chanavg,uvrascal,z,flagspw):
    for i in range(0,len(mytargets)):
        splitfilename=str(workdir)+mytargets[i]+'split.ms'
        splitavgfilename=str(workdir)+mytargets[i]+'splat.ms'
        if makedirty == True:
            try:
                assert os.path.isdir(splitavgfilename), "makedirty = True but the splitavg file not found."
            except AssertionError:
                logging.info("makedirty = True but the splitavg file not found.")
                sys.exit()
            myfile2 = splitavgfilename
#            logging.info("A flagging summary is provided for the MS file.")
#            ugf.flagsummary(splitavgfilename)
            ugf.mytclean(myfile2,0,mJythreshold,0,imcellsize,imsize_pix,use_nterms,nwprojpl)

        if doselfcal == True:
            try:
                assert os.path.isdir(splitavgfilename), "doselfcal = True but the splitavg file not found."
            except AssertionError:
                    logging.info("doselfcal = True but the splitavg file not found.")
                    sys.exit()
#    casalog.filter('INFO')
            logging.info("A flagging summary is provided for the MS file.")
#            ugf.flagsummary(splitavgfilename)
            casatasks.clearcal(vis = splitavgfilename)
            myfile2 = [splitavgfilename]
            if usetclean == True:
                file,gt,image=ugf.myselfcal(workdir,myfile2,ref_ant,scaloops,pcaloops,mJythreshold,imcellsize,imsize_pix,use_nterms,nwprojpl,scalsolints,clipresid,'','',False,niter_start,usetclean,uvrascal)    
    ugf.myapplycal(splitfilename,gt[len(gt)-1])            
    return file,gt,image 
   
def spectralcube(mytargets,workdir,image,spfitspw,mJythreshold,imcellsize,imsize_pix, z):
    for i in range(0,len(mytargets)):
            splitfilename = str(workdir)+mytargets[i]+'split.ms'
            model=image[len(image)-1]+'.model.tt0'
            casatasks.ft(vis=splitfilename,model=model,usescratch=True)
            casatasks.uvsub(vis=splitfilename) 
            casatasks.uvcontsub(vis=splitfilename,solint='int',fitorder=2,fitspw=spfitspw)
            casatasks.cvel(vis=splitfilename+'.contsub',outputvis=splitfilename+'.cvel.ms',veltype='optical',restfreq=str(1420.405752/(1+z))+'MHz', outframe='BARY')
            niter_cube=0
            ugf.tcleancube(splitfilename,niter_cube,mJythreshold,imcellsize,imsize_pix, z)
            niter_cube1=100
            ugf.tcleancube(splitfilename,niter_cube1,mJythreshold,imcellsize,imsize_pix, z)        
            