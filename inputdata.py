#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 12:43:39 2020

@author: yogesh
"""
import casatasks
import casatools
import os
import logging
from modules import ugfunctions
from datetime import datetime
from os import sys
import numpy as np

class inputdata:
    def __init__(self,fromlta,fromfits,ltafile,fits_file,msfilename,gvbinpath): # constructor
        self.fromlta=fromlta
        self.fromfits=fromfits
        self.ltafile=ltafile
        self.fits_file=fits_file
        self.msfilename=msfilename
        self.gvbinpath=gvbinpath

    def checkdata(self):
        testfitsfile = False
        if self.fromlta == True:
            logging.info("You have chosen to convert lta to FITS.")
            testltafile = os.path.isfile(self.ltafile)
            if testltafile == True:
                logging.info("The lta %s file exists.", self.ltafile)
                testlistscan = os.path.isfile(self.gvbinpath[0])
                testgvfits = os.path.isfile(self.gvbinpath[1])
                if testlistscan and testgvfits == True:
                    os.system(self.gvbinpath[0]+' '+self.ltafile)
                    if self.fits_file!= '' and self.fits_file != 'TEST.FITS':
                        os.system("sed -i 's/TEST.FITS/"+self.fits_file+"/"+self.ltafile.split('.')[0]+'.log')
                    try:
                        assert os.path.isfile(self.fits_file)
                        testfitsfile = True
                    except AssertionError:
                        if os.path.isfile('TEST.FITS') == True: 
#                                assert os.path.isfile('TEST.FITS'), 
                            logging.info("The file TEST.FITS file already exists. New will not be created.")
                            testfitsfile = True
                            fits_file = 'TEST.FITS'
                        else:
                            os.system(self.gvbinpath[1]+' '+self.ltafile.split('.')[0]+'.log')
                            testfitsfile = True
                else:
                    logging.info("Error: Check if listscan and gvfits are present and executable.")
        else:
            logging.info("The given lta file does not exist. Exiting the code.")
            logging.info("If you are not starting from lta file please set fromlta to False and rerun.")
 #           sys.exit()
        if self.fromfits == True:
            if self.fits_file != '':
                try:
                    assert os.path.isfile(self.fits_file)
                    testfitsfile = True
                except AssertionError:
                    try:
                        assert os.path.isfile('TEST.FITS')
                        testfitsfile = True
                    except AssertionError:
                        logging.info("Please provide the name of the FITS file.")
#                        sys.exit()
        if testfitsfile == True:
            if self.msfilename != '':
                try:
                    assert os.path.isdir(self.msfilename), "The given msfile already exists, will not create new."
                except AssertionError:
                    logging.info("The given msfile does not exist, will create new.")
        else:
                try:
                        assert os.path.isdir(self.fits_file+'.MS')
                except AssertionError:
                       msfilename = self.fits_file+'.MS'           
        if(os.path.isdir(self.msfilename)==True):
           os.system('rm'+' -rf' +" "+ self.msfilename)
           print('rm'+' -rf'+" "+ self.msfilename)
           casatasks.importgmrt(fitsfile=self.fits_file, vis = self.msfilename)
        else:
           casatasks.importgmrt(fitsfile=self.fits_file, vis = self.msfilename)
        return self.msfilename

####################################################################
class readdata:
    def __init__(self,frommultisrcms,msfilename):
        self.frommultisrcms=frommultisrcms
        self.msfilename=msfilename
    def listfile(self):
        if os.path.isfile(self.msfilename+'.list') == True:
            os.system('rm '+self.msfilename+'.list')
            ugfunctions.vislistobs(self.msfilename)
            logging.info("Please see the text file with the extension .list to find out more about your data.")
        elif os.path.isfile(self.msfilename+'.list') == False:
            #print(os.path.isfile(self.msfilename+'.list'))
            ugfunctions.vislistobs(self.msfilename)
            logging.info("Please see the text file with the extension .list to find out more about your data.")
        
    def listread(self):                       
        testms = False
        if self.frommultisrcms == True:
            if self.msfilename != '':
                print(self.msfilename)
                testms = os.path.isdir(self.msfilename)
                print(os.path.isdir(self.msfilename))
            else:
                try:
                    assert os.path.isdir('TEST.FITS.MS')
                    testms = True
            #        msfilename = 'TEST.FITS.MS'
                except AssertionError:
                    logging.info("Tried to find the MS file with default name. File not found. Please provide the name of the msfile or create the MS by setting fromfits = True.")
#                   sys.exit()
        if testms == False:
            logging.info("The MS file does not exist. Please provide msfilename. Exiting the code...")
#            sys.exit()   
        if testms == True:
            gainspw, gainspw2, mygoodchans, flagspw, mypol = ugfunctions.getgainspw(self.msfilename)
            poltypes=ugfunctions.mypols(self.msfilename)
            logging.info("Channel range for calibration:")
            logging.info(gainspw)
            logging.info("Assumed clean channel range:")
            logging.info(mygoodchans)
            logging.info("Channel range for flagging:")
            logging.info(flagspw)
            logging.info("Polarizations in the file:")
            logging.info(mypol)
            # fix target
            myfields = ugfunctions.getfields(self.msfilename)
            stdcals = ['3C48','3C147','3C286','0542+498','1331+305','0137+331','3C468.1']
            vlacals = np.loadtxt('/home/yogesh/newcasascript/vla-cals.list',dtype='str')
            myampcals =[]
            mypcals=[]
            mytargets=[]
            for i in range(0,len(myfields)):
                if myfields[i] in stdcals:
                    myampcals.append(myfields[i])
                elif myfields[i] in vlacals:
                    mypcals.append(myfields[i])
                else:
                    mytargets.append(myfields[i])
            #mybpcals = myampcals
            logging.info('Amplitude caibrators are %s', str(myampcals))
            logging.info('Phase calibrators are %s', str(mypcals))
            logging.info('Target sources are %s', str(mytargets))
        return gainspw, gainspw2, mygoodchans, flagspw, mypol, poltypes, myampcals, mypcals, mytargets


