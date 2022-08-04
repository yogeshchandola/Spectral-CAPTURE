import casatools  
import casatasks  
import os
import logging
from datetime import datetime
#from casatools import ms
#from casatools import msmetadata as msmd
from os import sys
import casashell as csh
# FUNCTIONS
###############################################################
# A library of function that are used in the pipeline
ms=casatools.ms()
msmd=casatools.msmetadata()
        
def vislistobs(msfile):
    '''Writes the verbose output of the task listobs.'''
    ms.open(msfile)
     #outr=casatasks.listobs(vis=msfile,verbose=True,listfile=msfile+'.list')
    outr=ms.summary(verbose=True,listfile=msfile+'.list')
    print("A file containing listobs output is saved.")
    try:
        assert os.path.isfile(msfile+'.list')
        logging.info("A file containing listobs output is saved.")
    except AssertionError:
        logging.info("The listobs output as not saved in a .list file. Please check the CASA log.")
    return outr

def getpols(msfile):
        '''Get the number of polarizations in the file'''
        casatasks.vishead(msfile,mode='summary')
        msmd.open(msfile)
        polid = msmd.ncorrforpol(0)
        msmd.close()
        msmd.done()
        return polid

#casatasks.visstat()

def mypols(inpvis):
    msmd.open(inpvis)
    # get correlation types for polarization ID 3
    #corrtypes = msmd.polidfordatadesc(mypolid)
 #   corrtypes = msmd.corrprodsforpol(0)
    corrtypes = msmd.corrtypesforpol(0)
    msmd.close()
    msmd.done()
    return corrtypes

def getfields(msfile):
    '''get list of field names in the ms'''
    fieldnames=casatasks.vishead(msfile,mode='get',hdkey='field')
    #msmd.open(msfile)  
    #fieldnames = msmd.fieldnames()
    #msmd.done()
    return fieldnames[0]

def getscans(msfile, mysrc):
    '''get a list of scan numbers for the specified source'''
    msmd.open(msfile)
    myscan_numbers = msmd.scansforfield(mysrc)
    myscanlist = myscan_numbers.tolist()
    msmd.close()
    msmd.done()
    return myscanlist

def getantlist(myvis,scanno):
    msmd.open(myvis)
    antenna_name = msmd.antennasforscan(scanno)
    antlist=[]
    for i in range(0,len(antenna_name)):
        antlist.append(msmd.antennanames(antenna_name[i])[0])
    msmd.close()
    return antlist


def getnchan(msfile):
    msmd.open(msfile)
    nchan = msmd.nchan(0)
    msmd.close()
    msmd.done()
    return nchan


def freq_info(ms_file):
    sw = 0
    msmd.open(ms_file)
    freq=msmd.chanfreqs(sw)
    msmd.close()
    msmd.done()
    return freq

def makebl(ant1,ant2):
    mybl = ant1+'&'+ant2
    return mybl


def getbllists(myfile):
    myfields = getfields(myfile)
    myallscans =[]
    for i in range(0,len(myfields)):
        myallscans.extend(getscans(myfile, myfields[i]))
    myantlist = getantlist(myfile,int(myallscans[0]))
    allbl=[]
    for i in range(0,len(myantlist)):
        for j in range(0,len(myantlist)):
            if j>i:
                allbl.append(makebl(myantlist[i],myantlist[j]))
    mycc=[]
    mycaa=[]
    for i in range(0,len(allbl)):
        if allbl[i].count('C')==2:
            mycc.append(allbl[i])
        else:
            mycaa.append(allbl[i])
    myshortbl =[]
    myshortbl.append(str('; '.join(mycc)))
    mylongbl =[]
    mylongbl.append(str('; '.join(mycaa)))
    return myshortbl, mylongbl


def getbandcut(inpmsfile):
    cutoffs = {'L':0.2, 'P':0.3, '235':0.5, '610':0.2, 'b4':0.2, 'b2':0.7, '150':0.7}
    frange = freq_info(inpmsfile)
    fmin = min(frange)
    fmax = max(frange)
    if fmin > 1000E06:
        fband = 'L'
    elif fmin >500E06 and fmin < 1000E06:
        fband = 'b4'
    elif fmin >260E06 and fmin < 560E06:
        fband = 'P'
    elif fmin > 210E06 and fmin < 260E06:
        fband = '235'
    elif fmin > 80E6 and fmin < 200E6:
        fband = 'b2'
    else:
        "Frequency band does not match any of the GMRT bands."
    logging.info("The frequency band in the file is ")
    logging.info(fband)
    xcut = cutoffs.get(fband)
    logging.info("The mean cutoff used for flagging bad antennas is ")
    logging.info(xcut)
    return xcut



def myvisstatampraw1(myfile,myfield,myspw,myant,mycorr,myscan):
   # t=csh.start_casa(casatasks.visstat)
  #  default(casatasks.visstat)
    mystat = casatasks.visstat(vis=myfile,axis="amp",datacolumn="data",useflags=False,spw=myspw,
        field=myfield,selectdata=True,antenna=myant,uvrange="",timerange="",
        correlation=mycorr,scan=myscan,array="",observation="",timeaverage=False,
        timebin="0s",timespan="",maxuvwdistance=0.0,disableparallel=False,ddistart=0,
        taql='',monolithic_processing=False,intent="",reportingaxes="ddid")
    mymean1 = mystat['DATA_DESC_ID=0']['mean']
    return mymean1

def myvisstatampafcal(myfile,myfield,myspw):
   # t=csh.start_casa(casatasks.visstat)
  #  default(casatasks.visstat)
    mystat = casatasks.visstat(vis=myfile,axis="amp",datacolumn="corrected",useflags=True,spw=myspw,
        field=myfield,selectdata=True,antenna="",uvrange="",timerange="",
        correlation="",scan="",array="",observation="",timeaverage=False,
        timebin="",timespan="scan,state",maxuvwdistance=0.0,disableparallel=False,ddistart=0,
        taql='',monolithic_processing=False,intent="",reportingaxes="ddid")
    mymean1 = mystat['DATA_DESC_ID=0']['mean']
    mystd1=mystat['DATA_DESC_ID=0']['stddev']
    mymedian1 = mystat['DATA_DESC_ID=0']['median']
    mymad1=mystat['DATA_DESC_ID=0']['medabsdevmed']
    #mymean1 = mystat['field_id=0']['mean']
    #mystd1=mystat[field_id=0]'['stddev']
    #mymedian1 = mystat[field_id=0]['median']
    #mymad1=mystat[field_id=0]['medabsdevmed']
    return mymean1, mystd1, mymedian1, mymad1

def myvisstatphaseafcal(myfile,myfield,myspw):
   # t=csh.start_casa(casatasks.visstat)
  #  default(casatasks.visstat)
    mystat = casatasks.visstat(vis=myfile,axis="phase",datacolumn="corrected",useflags=True,spw=myspw,
        field=myfield,selectdata=True,antenna="",uvrange="",timerange="",
        correlation="",scan="",array="",observation="",timeaverage=False,
        timebin="",timespan="scan,state",maxuvwdistance=0.0,disableparallel=False,ddistart=0,
        taql='',monolithic_processing=False,intent="",reportingaxes="ddid")
    mymean1 = mystat['DATA_DESC_ID=0']['mean']
    mystd1=mystat['DATA_DESC_ID=0']['stddev']
    mymedian1 = mystat['DATA_DESC_ID=0']['median']
    mymad1=mystat['DATA_DESC_ID=0']['medabsdevmed']
    #mymean1 = mystat['field_id=0']['mean']
    #mystd1=mystat[field_id=0]'['stddev']
    #mymedian1 = mystat[field_id=0]['median']
    #mymad1=mystat[field_id=0]['medabsdevmed']
    return mymean1, mystd1, mymedian1, mymad1

def myvisstatampraw(myfile,myspw,myant,mycorr,myscan):
  #  default(casatasks.visstat)
    mystat = casatasks.visstat(vis=myfile,axis="amp",datacolumn="data",useflags=False,spw=myspw,
        selectdata=True,antenna=myant,uvrange="",timerange="",
        correlation=mycorr,scan=myscan,array="",observation="",timeaverage=False,
        timebin="0s",timespan="",maxuvwdistance=0.0,disableparallel=False,ddistart=0,
        taql='',monolithic_processing=False,intent="",reportingaxes="ddid")
    mymean1 = mystat['DATA_DESC_ID=0']['mean']
    mystd1=mystat['DATA_DESC_ID=0']['stddev']
    mymedian1 = mystat['DATA_DESC_ID=0']['median']
    mymad1=mystat['DATA_DESC_ID=0']['medabsdevmed']
    return mymean1,mystd1, mymedian1, mymad1



def mygaincal_ap1(myfile,mycal,myref,myflagspw,myuvracal,calsuffix):
   # default(casatasks.gaincal)
    gaintable = [str(myfile)+'.K1', str(myfile)+'.B1' ]
    casatasks.gaincal(vis=myfile, caltable=str(myfile)+'.AP.G', spw =myflagspw,uvrange=myuvracal,append=True,
        field=mycal,solint = '120s',refant = myref, minsnr = 2.0, solmode ='L1R', gaintype = 'G', calmode = 'ap',
        gaintable = [str(myfile)+'.K1', str(myfile)+'.B1' ], interp = ['nearest,nearestflag', 'nearest,nearestflag' ], 
        parang = True )
    return  gaintable


def mygaincal_ap2(myfile,mycal,myref,myflagspw,myuvracal,calsuffix):
 #   default(casatasks.gaincal)
    gaintable = [str(myfile)+'.K1'+calsuffix, str(myfile)+'.B1'+calsuffix ]
    casatasks.gaincal(vis=myfile, caltable=str(myfile)+'.AP.G'+calsuffix, spw =myflagspw,uvrange=myuvracal,append=True,
        field=mycal,solint = '120s',refant = myref, minsnr = 2.0, solmode ='L1R', gaintype = 'G', calmode = 'ap',
        gaintable = [str(myfile)+'.K1'+calsuffix, str(myfile)+'.B1'+calsuffix ], interp = ['nearest,nearestflag', 'nearest,nearestflag' ], 
        parang = True )
    return gaintable

def getfluxcal(myfile,mycalref,myscal):
    myscale = casatasks.fluxscale(vis=myfile, caltable=str(myfile)+'.AP.G', fluxtable=str(myfile)+'.fluxscale', reference=mycalref, transfer=myscal,
                    incremental=False)
    return myscale


def getfluxcal2(myfile,mycalref,myscal,calsuffix):
	myscale = casatasks.fluxscale(vis=myfile, caltable=str(myfile)+'.AP.G'+calsuffix, fluxtable=str(myfile)+'.fluxscale'+calsuffix, reference=mycalref,
       	            transfer=myscal, incremental=False)
	return myscale



def mygaincal_ap_redo(myfile,mycal,myref,myflagspw,myuvracal):
  #  default(casatasks.gaincal)
    gaintable = [str(myfile)+'.K1'+'recal', str(myfile)+'.B1'+'recal' ]
    casatasks.gaincal(vis=myfile, caltable=str(myfile)+'.AP.G.'+'recal', append=True, spw =myflagspw, uvrange=myuvracal,
        field=mycal,solint = '120s',refant = myref, minsnr = 2.0,solmode ='L1R', gaintype = 'G', calmode = 'ap',
        gaintable = [str(myfile)+'.K1'+'recal', str(myfile)+'.B1'+'recal' ], interp = ['nearest,nearestflag', 'nearest,nearestflag' ], 
        parang = True )
    return gaintable

def getfluxcal_redo(myfile,mycalref,myscal):
    myscale = casatasks.fluxscale(vis=myfile, caltable=str(myfile)+'.AP.G'+'recal', fluxtable=str(myfile)+'.fluxscale'+'recal', reference=mycalref,
                    transfer=myscal, incremental=False)
    return myscale

def mytfcrop(myfile,myfield,myants,tcut,fcut,mydatcol,myflagspw):
 #   default(casatasks.flagdata)
    casatasks.flagdata(vis=myfile, antenna = myants, field = myfield,	spw = myflagspw, mode='tfcrop', ntime='300s', combinescans=False,
        datacolumn=mydatcol, timecutoff=tcut, freqcutoff=fcut, timefit='line', freqfit='line', flagdimension='freqtime',
        usewindowstats='sum', extendflags = False, action='apply', display='none')
    return


def myrflag(myfile,myfield, myants, mytimdev, myfdev,mydatcol,myflagspw):
 #   default(casatasks.flagdata)
    casatasks.flagdata(vis=myfile, field = myfield, spw = myflagspw, antenna = myants, mode='rflag', ntime='scan', combinescans=False,
        datacolumn=mydatcol, winsize=3, timedevscale=mytimdev, freqdevscale=myfdev, spectralmax=1000000.0, spectralmin=0.0,
        extendflags=False, channelavg=False, timeavg=False, action='apply', display='none')
    return


def myrflagavg(myfile,myfield, myants, mytimdev, myfdev,mydatcol,myflagspw,cliptarget):
 #   default(casatasks.flagdata)
    casatasks.flagdata(vis=myfile,mode="clip", spw=myflagspw,field=myfield, clipminmax=cliptarget, datacolumn=mydatcol,clipoutside=True, clipzeros=True, extendpols=False, 
                        action="apply",flagbackup=True, savepars=False, overwrite=True, writeflags=True)
    casatasks.flagdata(vis=myfile, field = myfield, spw = myflagspw, antenna = myants, mode='rflag', ntime='300s', combinescans=True,
        datacolumn=mydatcol, winsize=3,	minchanfrac= 0.8, flagneartime = True, basecnt = True, fieldcnt = True,
        timedevscale=mytimdev, freqdevscale=myfdev, spectralmax=1000000.0, spectralmin=0.0, extendflags=False,
        channelavg=False, timeavg=False, action='apply', display='none') 
    
    return

def getgainspw(msfilename):
        mynchan = getnchan(msfilename)
        logging.info('The number of channels in your file %d',mynchan)
        gmrt235 = False
        gmrt610 = False
        gmrtfreq = 0.0
# check if single pol data
        mypol = getpols(msfilename)
#        logging.info('Your file contains %s polarization products.', mypol)
        if mypol == 1:
#                print("This dataset contains only single polarization data.")
                logging.info('This dataset contains only single polarization data.')
                mychnu = freq_info(msfilename)
                if 200E6< mychnu[0]<300E6:
                        poldata = 'LL'
                        gmrt235 = True
                        gmrt610 = False
                        mynchan = getnchan(msfilename)
                        if mynchan !=256:
#                                print("You have data in the 235 MHz band of dual frequency mode of the GMRT. Currently files only with 256 channels are supported in this pipeline.")
                                logging.info('You have data in the 235 MHz band of dual frequency mode of the GMRT. Currently files only with 256 channels are supported in this pipeline.')
                                sys.exit()
                elif 590E6<mychnu[0]<700E6:
                        poldata = 'RR'
                        gmrt235 = False
                        gmrt610 = True
                        mynchan = getnchan(msfilename)
                        if mynchan != 256:
#                                print("You have data in the 610 MHz band of the dual frequency mode of the legacy GMRT. Currently files only with 256 channels are supported in this pipeline.")
                                logging.info('You have data in the 610 MHz band of the dual frequency mode of the legacy GMRT. Currently files only with 256 channels are supported in this pipeline.')
                                sys.exit()
                else:
                        gmrtfreq = mychnu[0]
#                        print("You have data in a single polarization - most likely GMRT hardware correlator. This pipeline currently does not support reduction of single pol HW correlator data.")
                        logging.info('You have data in a single polarization - most likely GMRT hardware correlator. This pipeline currently does not support reduction of single pol HW correlator data.')
#                        print("The number of channels in this file are %d" %  mychnu[0])
                        logging.info('The number of channels in this file are %d', mychnu[0])
                        sys.exit()
# Now get the channel range.        
        if mynchan == 1024:
                mygoodchans = '0:250~300'   # used for visstat
                flagspw = '0:51~950'
                gainspw = '0:101~110'
                gainspw2 = ''   # central good channels after split file for self-cal
                logging.info("The following channel range will be used.")
        elif mynchan == 2048:
                mygoodchans = '0:500~600'   # used for visstat
                flagspw = '0:101~1900'
                gainspw = '0:201~210'
                gainspw2 = ''   # central good channels after split file for self-cal
                logging.info("The following channel range will be used.")
        elif mynchan == 4096:
                mygoodchans = '0:1000~1200'
                flagspw = '0:41~4050'
                gainspw = '0:201~210'
                gainspw2 = ''   # central good channels after split file for self-cal
                logging.info("The following channel range will be used.")
        elif mynchan == 8192:
                mygoodchans = '0:2000~3000'
                flagspw = '0:500~7800'
                gainspw = '0:1000~1010'
                gainspw2 = ''   # central good channels after split file for self-cal
                logging.info("The following channel range will be used.")
        elif mynchan == 16384:
                mygoodchans = '0:4000~6000'
                flagspw = '0:1000~14500'
                gainspw = '0:2000~2010'
                gainspw2 = ''   # central good channels after split file for self-cal
                logging.info("The following channel range will be used.")
        elif mynchan == 128:
                mygoodchans = '0:50~70'
                flagspw = '0:5~115'
                gainspw = '0:11~20'
                gainspw2 = ''   # central good channels after split file for self-cal
                logging.info("The following channel range will be used.")
        elif mynchan == 256:
#               if poldata == 'LL':
                if gmrt235 == True:
                        mygoodchans = '0:101~200'
                        flagspw = '0:70~220'
                        gainspw = '0:100~110'
                        gainspw2 = ''   # central good channels after split file for self-cal
                        logging.info("The following channel range will be used.")
                elif gmrt610 == True:
                        mygoodchans = '0:101~200'
                        flagspw = '0:11~240'
                        gainspw = '0:100~110'
                        gainspw2 = ''   # central good channels after split file for self-cal   
                        logging.info("The following channel range will be used.")
                else:
                        mygoodchans = '0:101~200'
                        flagspw = '0:11~240'
                        gainspw = '0:100~110'
                        gainspw2 = ''   # central good channels after split file for self-cal
                        logging.info("The following channel range will be used.")
        elif mynchan == 512:
                mygoodchans = '0:101~200'
                flagspw = '0:21~500'
                gainspw = '0:150~160'
                gainspw2 = ''   # central good channels after split file for self-cal   
                logging.info("The following channel range will be used.")
        return gainspw, gainspw2, mygoodchans, flagspw, mypol



def mysplitinit(myfile,workdir,myfield,myspw,mywidth):
    '''function to split corrected data for any field'''
 #   default(casatasks.mstransform)
    casatasks.mstransform(vis=myfile, field=myfield, spw=myspw, chanaverage=False, chanbin=mywidth, datacolumn='corrected', outputvis=str(workdir)+str(myfield)+'split.ms')
    myoutvis=str(workdir)+str(myfield)+'split.ms'
    return myoutvis


def mysplitavg(myfile,workdir,myfield,myspw,mywidth):
    '''function to split corrected data for any field'''
#    default(casatasks.mstransform) 
    myoutname= str(workdir)+str(myfield)+'splat.ms'
    casatasks.mstransform(vis=myfile, field=myfield, spw=myspw, chanaverage=True, chanbin=mywidth, datacolumn='data', outputvis=myoutname)
    return myoutname


def mytclean(myfile,myniter,mythresh,srno,cell,imsize, mynterms1,mywproj):    # you may change the multi-scale inputs as per your field
    nameprefix = getfields(myfile)[0] #myfile.split('.')[0]
    print("The image files have the following prefix =",nameprefix)
    if myniter==0:
        myoutimg = myfile+'-dirty-img'
    else:
        myoutimg = myfile+'-selfcal'+'img'+str(srno)
    myimsize=[imsize,imsize]    
 #   default(casatasks.tclean)
    if mynterms1 > 1:
        casatasks.tclean(vis=myfile,
       	        imagename=myoutimg, selectdata= True, field='0', spw='0', imsize=myimsize, cell=cell, robust=0, weighting='briggs', 
                specmode='mfs',	nterms=mynterms1, niter=myniter, #usemask='user',mask='/data/34_023/test/testsplat.ms.mask',
            usemask='auto-multithresh',minbeamfrac=0.1, sidelobethreshold = 2.0,
#           noisethreshold=5.0,
#			minpsffraction=0.05,
#			maxpsffraction=0.8,
            smallscalebias=0.6, threshold= mythresh, aterm =True, pblimit=-1,deconvolver='mtmfs', gridder='wproject', wprojplanes=mywproj, scales=[0,5,15],wbawp=False,
            restoration = True, savemodel='modelcolumn', cyclefactor = 0.5, parallel=False,interactive=False)
    else:
        casatasks.tclean(vis=myfile,
               imagename=myoutimg, selectdata= True, field='0', spw='0', imsize=myimsize, cell=cell, robust=0, weighting='briggs', 
               specmode='mfs',	nterms=mynterms1, niter=myniter, #usemask='user',mask='/data/34_023/test/testsplat.ms.mask', 
               usemask='auto-multithresh',minbeamfrac=0.1,sidelobethreshold = 2.0,
#               noisethreshold=5.0,
#			minpsffraction=0.05,
#			maxpsffraction=0.8,
                smallscalebias=0.6, threshold= mythresh, aterm =True, pblimit=-1,deconvolver='multiscale', gridder='wproject', wprojplanes=mywproj, scales=[0,5,15],wbawp=False,
                restoration = True, savemodel='modelcolumn', cyclefactor = 0.5, parallel=False,
                interactive=False)
    return myoutimg

def myonlyclean(myfile,myniter,mythresh,srno,cell,imsize,mynterms1,mywproj):
 #   default(casatasks.clean)
    myimsize=[imsize,imsize]
    casatasks.clean(vis=myfile,
    selectdata=True,
    spw='0',
    imagename='selfcal'+'img'+str(srno),
    imsize=myimsize,
    cell=cell,
    mode='mfs',
    reffreq='',
    weighting='briggs',
    niter=myniter,
    threshold=mythresh,
    nterms=mynterms1,
    gridmode='widefield',
    wprojplanes=mywproj,
    interactive=False,
    usescratch=True)
    myname = 'selfcal'+'img'+str(srno)
    return myname


def mysplit(workdir,myfile,srno):
    filname_pre = str(workdir)+getfields(myfile)[0]
 #   default(casatasks.mstransform)
    casatasks.mstransform(vis=myfile, field='0', spw='0', datacolumn='corrected', outputvis=filname_pre+'-selfcal'+str(srno)+'.ms')
    myoutvis=filname_pre+'-selfcal'+str(srno)+'.ms'
    return myoutvis


def mygaincal_ap(workdir,myfile,myref,mygtable,srno,pap,mysolint,myuvrascal,mygainspw):
    fprefix = str(workdir)+getfields(myfile)[0]
    if pap=='ap':
        mycalmode='ap'
        mysol= mysolint[srno] 
        mysolnorm = True
    else:
        mycalmode='p'
        mysol= mysolint[srno] 
        mysolnorm = False
    if os.path.isdir(fprefix+str(pap)+str(srno)+'.GT'):
        os.system('rm -rf '+fprefix+str(pap)+str(srno)+'.GT')
 #   default(casatasks.gaincal)
    casatasks.gaincal(vis=myfile, caltable=fprefix+str(pap)+str(srno)+'.GT', append=False, field='0', spw=mygainspw,
        uvrange=myuvrascal, solint = mysol, refant = myref, minsnr = 2.0,solmode='L1R', gaintype = 'G',
        solnorm= mysolnorm, calmode = mycalmode, gaintable = [], interp = ['nearest,nearestflag', 'nearest,nearestflag' ], 
        parang = True )
    mycal = fprefix+str(pap)+str(srno)+'.GT'
    return mycal


def myapplycal(myfile,mygaintables):
#    default(casatasks.applycal)
    casatasks.applycal(vis=myfile, field='0', gaintable=mygaintables, gainfield=['0'], applymode='calflag', 
             interp=['linear'], calwt=False, parang=False)
    print('Ran applycal.')




def flagresidual(myfile,myclipresid,myflagspw):
 #   default(casatasks.flagdata)
    casatasks.flagdata(vis=myfile, mode ='rflag', datacolumn="RESIDUAL_DATA", field='', timecutoff=6.0,  freqcutoff=6.0,
        timefit="line", freqfit="line",	flagdimension="freqtime", extendflags=False, timedevscale=6.0,
        freqdevscale=6.0, spectralmax=500.0, extendpols=False, growaround=False, flagneartime=False,
        flagnearfreq=False, action="apply", flagbackup=True, overwrite=True, writeflags=True)
 #   default(casatasks.flagdata)
    casatasks.flagdata(vis=myfile, mode ='clip', datacolumn="RESIDUAL_DATA", clipminmax=myclipresid,
        clipoutside=True, clipzeros=True, field='', spw=myflagspw, extendflags=False,
        extendpols=False, growaround=False, flagneartime=False,	flagnearfreq=False,
        action="apply",	flagbackup=True, overwrite=True, writeflags=True)
    casatasks.flagdata(vis=myfile,mode="summary",datacolumn="RESIDUAL_DATA", extendflags=False, 
        name=myfile+'temp.summary', action="apply", flagbackup=True,overwrite=True, writeflags=True)


def myselfcal(workdir,myfile,myref, nloops,nploops,myvalinit,mycellsize,myimagesize,mynterms2,mywproj1,mysolint1,myclipresid,myflagspw,mygainspw2,mymakedirty,niterstart,usetclean,uvrascal):
    myref = myref
    nscal = nloops # number of selfcal loops
    npal = nploops # number of phasecal loops
    # selfcal loop
    myimages=[]
    mygt=[]
    myniterstart = niterstart
    myniterend = 200000	
    if nscal == 0:
        i = nscal
        file= myfile[i]
        myniter = 0 # this is to make a dirty image
        mythresh = str(myvalinit/(i+1))+'mJy'
        print("Using "+file+" for making only an image.")
        if usetclean == False:
            myimg = myonlyclean(file,myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # clean
        else:
            myimg = mytclean(file,myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # tclean
        if mynterms2 > 1:
                casatasks.exportfits(imagename=myimg+'.image.tt0', fitsimage=myimg+'.fits')
        else:
                casatasks.exportfits(imagename=myimg+'.image', fitsimage=myimg+'.fits')

    else:
        for i in range(0,nscal+1): # plan 4 P and 4AP iterations
	    print(myfile,i)
            file= myfile[i]
            if mymakedirty == True:
                if i == 0:
                    myniter = 0 # this is to make a dirty image
                    mythresh = str(myvalinit/(i+1))+'mJy'
                    print("Using "+ file+" for making only a dirty image.")
                    if usetclean == False:
                        myimg = myonlyclean(file,myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # clean
                    else:
                        myimg = mytclean(file,myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # tclean
                    if mynterms2 > 1:
                        casatasks.exportfits(imagename=myimg+'.image.tt0', fitsimage=myimg+'.fits')
                    else:
                        casatasks.exportfits(imagename=myimg+'.image', fitsimage=myimg+'.fits')

            else:
                myniter=int(myniterstart*2**i) #myniterstart*(2**i)  # niter is doubled with every iteration int(startniter*2**count)
                if myniter > myniterend:
                    myniter = myniterend
                mythresh = str(myvalinit/(i+1))+'mJy'
                if i < npal:
                    mypap = 'p'
#print("Using "+ myfile[i]+" for imaging.")
                    try:
                        assert os.path.isdir(file)
                    except AssertionError:
                        logging.info("The MS file not found for imaging.")
                        sys.exit()
                    logging.info("Using "+file+" for imaging.")
                    if usetclean == False:
                        myimg = myonlyclean(file,myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # clean
                    else:
                        myimg = mytclean(file,myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # tclean
                    if mynterms2 > 1:
                        casatasks.exportfits(imagename=myimg+'.image.tt0', fitsimage=myimg+'.fits')
                    else:
                        casatasks.exportfits(imagename=myimg+'.image', fitsimage=myimg+'.fits')
                    myimages.append(myimg)	# list of all the images created so far
                    flagresidual(file,myclipresid,'')
                    if i>0:
                        myctables = mygaincal_ap(workdir,file,myref,mygt[i-1],i,mypap,mysolint1,uvrascal,mygainspw2)
                    else:
                        myctables = mygaincal_ap(workdir,file,myref,mygt,i,mypap,mysolint1,uvrascal,mygainspw2)
                    mygt.append(myctables)# full list of gaintables
                    if i < nscal+1:
                        if (os.path.isdir(mygt[i])):
                            myapplycal(file,mygt[i])
                            myoutfile= mysplit(workdir,file,i)
                            myfile.append(myoutfile)
                        else:
                            print(mygt[i],'file doesnt exist')
                else:
                    mypap = 'ap'
#					print("Using "+ myfile[i]+" for imaging.")
                    try:
                        assert os.path.isdir(file)
                    except AssertionError:
                        logging.info("The MS file not found for imaging.")
                        sys.exit()
                    if usetclean == False:
                        myimg = myonlyclean(file,myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # clean
                    else:
                        myimg = mytclean(file,myniter,mythresh,i,mycellsize,myimagesize,mynterms2,mywproj1)   # tclean
                    if mynterms2 > 1:
                        casatasks.exportfits(imagename=myimg+'.image.tt0', fitsimage=myimg+'.fits')
                    else:
                        casatasks.exportfits(imagename=myimg+'.image', fitsimage=myimg+'.fits')
                    myimages.append(myimg)	# list of all the images created so far
                    flagresidual(file,myclipresid,'')
                    if i!= nscal:
                        myctables = mygaincal_ap(workdir,file,myref,mygt[i-1],i,mypap,mysolint1,'',mygainspw2)
                        mygt.append(myctables) # full list of gaintables
                        if i < nscal+1:
                            if (os.path.isdir(mygt[i])):
                                print(mygt[i],'file exists')
                                myapplycal(file,mygt[i])
                                myoutfile= mysplit(workdir,file,i)
                                myfile.append(myoutfile)
                            else:
                                print(mygt[i],'file doesnt exist')
#				print("Visibilities from the previous selfcal will be deleted.")
                logging.info("Visibilities from the previous selfcal will be deleted.")
                if i < nscal:
                    fprefix = getfields(file)[0]
                    myoldvis = fprefix+'-selfcal'+str(i-1)+'.ms'
#					print("Deleting "+str(myoldvis))
                    logging.info("Deleting "+workdir+str(myoldvis))
                    os.system('rm -rf '+workdir+str(myoldvis))
#			print('Ran the selfcal loop')
    return myfile, mygt, myimages

def tcleancube(myfile,myniter,mythresh,cell,imsize, z):    # you may change the multi-scale inputs as per your field
    nameprefix = getfields(myfile)[0] #myfile.split('.')[0]
    print("The image files have the following prefix =",nameprefix)
    if myniter==0:
        myoutimg = myfile+'-dirty-cube'
    else:
        myoutimg = myfile+'-clean-cube'
    myimsize=[imsize,imsize]    
    casatasks.tclean(vis=myfile,imagename=myoutimg, datacolumn='corrected',selectdata= True, field='0', spw='0', imsize=myimsize, cell=cell,weighting='briggs', 
                specmode='cube', veltype='optical',restfreq=str(1420.405752/(1+z))+'MHz', outframe='BARY', niter=myniter, usemask='pb',deconvolver='clark', gridder='standard', restoration = True, savemodel='modelcolumn', parallel=False,interactive=False)
    return myoutimg


def flagsummary(myfile):
    try:
        assert os.path.isdir(myfile), "The MS file was not found."
    except AssertionError:
        logging.info("The MS file was not found.")
        sys.exit()
        s = casatasks.flagdata(vis=myfile, mode='summary')
        allkeys = s.keys()
    logging.info("Flagging percentage:")
    for x in allkeys:
            try:
                for y in s[x].keys():
                    flagged_percent = 100.*(s[x][y]['flagged']/s[x][y]['total'])
#                                logging.info(x, y, "%0.2f" % flagged_percent, "% flagged.")
                logstring = str(x)+' '+str(y)+' '+str(flagged_percent)
                logging.info(logstring)
            except AttributeError:
                        pass

#############End of functions##############################################################################
