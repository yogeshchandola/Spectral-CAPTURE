#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 11 20:54:35 2020

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



def spectralcube(mytargets,workdir,gt,image,flagspw,mJythreshold,imcellsize,imsize_pix, z):
    for i in range(0,len(mytargets)):
            splitfilename = str(workdir)+mytargets[i]+'split.ms'
            ugf.myapplycal(splitfilename,gt[len(gt)-1]) 
            model=image[len(image)-1]+'.model.tt0'
            casatasks.ft(vis=splitfilename,model=model,usescratch=True)
            casatasks.uvsub(vis=splitfilename) 
            casatasks.uvcontsub(vis=splitfilename,solint='int',fitorder=2,fitspw=flagspw)
            casatasks.cvel(vis=splitfilename+'.contsub',outputvis=splitfilename+'.cvel.ms',veltype='optical',restfreq=str(1420.405752/(1+z))+'MHz', outframe='BARY')
            niter_cube=0
            ugf.tcleancube(splitfilename,niter_cube,mJythreshold,imcellsize,imsize_pix, z)
            niter_cube1=100
            ugf.tcleancube(splitfilename,niter_cube1,mJythreshold,imcellsize,imsize_pix, z)
    
            
            