record_process/data_analyze.py                                                                      0000644 0001750 0001750 00000001050 12256452261 015601  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   import sys
import os
import numpy as np
result = [[0,0,0,0,0,0],[0,0,0,0,0,0]]
fs = open(sys.argv[1],'r')
count = [0,0]
for line in fs.readlines():
	data = line.split(' ')
	#print data
	cur = []
	for i in range(1,6):
		result[int(data[0])][i-1] = result[int(data[0])][i-1] + float(data[i][2:]) 
	result[int(data[0])][5] = result[int(data[0])][5] + float(data[6][2:-2])
	count[int(data[0])] = count[int(data[0])]+1 	
	
print 'neutral:'
for i in range(6):
	print result[0][i]*1.0/count[0]
print 'angry'
for i in range(6):
	print result[1][i]*1.0/count[1]                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        record_process/dir_process.py                                                                       0000644 0001750 0001750 00000001023 12261221332 015446  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   import os
import sys
import speech_process
def usage():
	print "Used to process wav in a labeled directory "
	print "python dir_process.py directory label"
if len(sys.argv)<4 :
	usage()
	sys.exit()
if os.path.isdir(sys.argv[1])==False:
	print "%s is not a directory"&sys.arg[1]
	sys.exit()
out = sys.argv[3]
path = sys.argv[1]
files = os.listdir(path)
label = sys.argv[2]
print label
if path.endswith('/')==False:
	path = path + '/'

for f in files:
	print f
	f = path + f
	speech_process.speech_process(f,label=label,dataFile=out)                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             record_process/log_analyze.py                                                                       0000644 0001750 0001750 00000005012 12247301142 015442  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   #coding=utf-8
import os
import sys
def evaluate(a,b,c):
	return (a+b+c)/3

def usage():
	pass

def log_analyze(log_input,log_output,sortStrategy,sortNum):
	try:
		fs = open(log_input,'r')
	except:
		print "File not Found"
		sys.exit()
	flag = False
	variance = []
	recordNum = 0
	for line in fs.readlines():
		if flag==True:
			count = count + 1
			if count==speechNum+1:
				p = line.split()
				item = [record,float(p[1]),float(p[2]),float(p[3])]
				variance.append(item)
				recordNum = recordNum + 1
				flag = False
				continue
		words = line.split()
		if len(words)<=0:
			continue
		if words[0].endswith('pcm') or words[0].endswith('wav'):
			#print words
			flag = True
			record = words[0]
			speechNum = int(words[1])
			count = 0
	if sortStrategy!=4:
		variance=sorted(variance,key=lambda v:v[sortStrategy],reverse=True)
	else:
		speedMax = max([v[1] for v in variance])
		pitchMax = max([v[2] for v in variance])
		volumeMax = max([v[3] for v in variance])
		for v in variance:
			a = v[1]/speedMax
			b = v[2]/pitchMax
			c = v[3]/volumeMax
			rank = evaluate(a,b,c)
			v.append(rank)
		variance = sorted(variance,key=lambda v:v[4],reverse=True)

	if sortNum=='INF':
		sortNum = recordNum

	variance = variance[:sortNum]

	fs = open(log_output,'w')
	if sortStrategy==1:
		strategy = '最大语速方差'
	elif sortStrategy==2:
		strategy='最大语调方差'
	elif sortStrategy==3:
		strategy='最大音量方差'
	else:
		strategy='综合'
	info = '				根据%s策略得到%d条记录\n'%(strategy,recordNum)
	fs.write(info)
	info ='%-21s%-18s%-18s%-15s\n'%('文件名','语速','语调','音量')
	fs.write(info)
	for v in variance:
		info = '%-17s%-15.2f%-15.2f%-15.2f\n'%(v[0],v[1],v[2],v[3])
		fs.write(info)
	fs.close()

if __name__=='__main__':
	if len(sys.argv)<2:
		usage()
		sys.exit()
	sortStrategy = 4
	sortNum = 'INF'
	log_input = 'NULL'
	log_output = 'NULL'

	for arg in sys.argv[1:]:
		if arg.startswith('-n'):
			sortNum = int(arg[2:])
		elif arg.startswith('-s'):
			sortStrategy = 1
		elif arg.startswith('-p'):
			sortStrategy = 2
		elif arg.startswith('-v'):
			sortStrategy = 3
		elif arg.startswith('-i'):
			log_input = arg[2:]
		elif arg.startswith('-o'):
			log_output = arg[2:]
		else:
			usage()
			sys.exit()
	if sortNum != 'INF' and sortNum < 1:
		print '排序记录数指定错误'
		usage()
		sys.exit()
	if log_input=='NULL' or log_output=='NULL':
		print '没有指定输入和输出文件'
		usage()
		sys.exit()
	#print log_input,log_output,sortStrategy,sortNum
	log_analyze(log_input,log_output,sortStrategy,sortNum)

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      record_process/mood_svm.py                                                                          0000644 0001750 0001750 00000002152 12262013346 014766  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   import sys
import os
sys.path.append('/home/will/Documents/data/lib/libsvm-3.17/python')
from svmutil import *



def train(model_file,train_data,scale_model):
	cmd = './svm-scale -s %s %s > %s'%(scale_model,train_data,'train_scaled_data')
	os.system(cmd)
	y,x = svm_read_problem('train_scaled_data')
	model = svm_train(y,x)
	svm_save_model(model_file , model)

def classify(scale_model,model_file,predict_data,evaluate=False):
	m = svm_load_model(model_file)
	cmd = './svm-scale -r %s %s > %s'%(scale_model,predict_data,'predict_scaled_data')
	os.system(cmd)

	y,x = svm_read_problem('predict_scaled_data')
	p_labels,p_acc,p_vals = svm_predict(y,x,m)
	if evaluate == True:
		(acc,mse,scc) = evaluations(y,p_labels)
		print acc,mse,scc
	else:
		return p_labels 

def train_and_classify(scale_model,model_file,train_data,predict_data):
	cmd = './svm-scale -s %s %s > %s'%(scale_model,train_data,'train_scaled_data')
	os.system(cmd)
	cmd = './svm-scale -r %s %s > %s'%(scale_model,predict_data,'predict_scaled_data')
	os.system(cmd)
	train.train('train_scaled_data',model_file)
	classify.classify(model_file,'predict_scaled_data')

                                                                                                                                                                                                                                                                                                                                                                                                                      record_process/mood_svm.pyc                                                                         0000644 0001750 0001750 00000002770 12262013355 015137  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   �
��Rc           @   sT   d  d l  Z  d  d l Z e  j j d � d  d l Td �  Z e d � Z d �  Z d S(   i����Ns0   /home/will/Documents/data/lib/libsvm-3.17/python(   t   *c         C   sR   d | | d f } t  j | � t d � \ } } t | | � } t |  | � d  S(   Ns   ./svm-scale -s %s %s > %st   train_scaled_data(   t   ost   systemt   svm_read_problemt	   svm_traint   svm_save_model(   t
   model_filet
   train_datat   scale_modelt   cmdt   yt   xt   model(    (    s   mood_svm.pyt   train   s
    c         C   s�   t  | � } d |  | d f } t j | � t d � \ } } t | | | � \ } }	 }
 | t k r� t | | � \ } } } | G| G| GHn | Sd  S(   Ns   ./svm-scale -r %s %s > %st   predict_scaled_data(   t   svm_load_modelR   R   R   t   svm_predictt   Truet   evaluations(   R	   R   t   predict_datat   evaluatet   mR
   R   R   t   p_labelst   p_acct   p_valst   acct   mset   scc(    (    s   mood_svm.pyt   classify   s    c         C   sd   d |  | d f } t  j | � d |  | d f } t  j | � t j d | � t j | d � d  S(   Ns   ./svm-scale -s %s %s > %sR   s   ./svm-scale -r %s %s > %sR   (   R   R   R   R   (   R	   R   R   R   R
   (    (    s   mood_svm.pyt   train_and_classify   s    (	   t   sysR   t   patht   appendt   svmutilR   t   FalseR   R   (    (    (    s   mood_svm.pyt   <module>   s   
	        record_process/record_analyze.py                                                                    0000666 0001750 0001750 00000002634 12247051241 016154  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   import speech_process
import numpy as np
import matplotlib.pyplot as plt
import sys
import os
import matplotlib.pyplot as plt
def usage():
	if len(sys.argv)!=2 and len(sys.argv)!=6:
		print "Usage:\n 	python record_process.py 'record_file' [-cChannelNum] [-rSampleRate] [-wSampleWidth] [-eLittleEndian] [-lLogFile]"
		print "Default Value:\n     -c1 -r8000 -w2 -e1 -llog.txt"
		print "Attention\n       Only PCM records need parameters above"
		


logFile = 'log.txt'
channelNum = 1
sampleRate = 8000
sampleWidth = 2
littleEndian = 1
for arg in sys.argv[2:]:
	if arg.startswith('-c'):
		channelNum = int(arg[2:])
	elif arg.startswith('-r'):
		sampleRate = int(arg[2:])
	elif arg.startswith('-w'):
		sampleWidth = int(arg[2:])
	elif arg.startswith('-e'):
		littleEndian = int(arg[2:])
	elif arg.startswith('-l'):
		logFile = str(arg[2:])
	else:
		print "Unrecgonize parameter :%s"%arg
		usage()
		sys.exit()
record = speech_process.speech_process(sys.argv[1],nchannels=channelNum,sampleRate=sampleRate,sampleWidth=sampleWidth,littleEndian=littleEndian,logFile=logFile)

time  = np.arange(record.frameNum)
plt.subplot(511)
plt.plot(time,record.volume)

plt.subplot(512)
plt.plot(time,record.zcr)
plt.subplot(513)
plt.plot(time,record.shortTimeEnergy)
plt.subplot(514)
plt.specgram(record.rawData,Fs=record.sampleRate,scale_by_freq = True)

time2 = np.arange(len(record.pitch))
plt.subplot(515)
#plt.plot(time2,record.pitch)
plt.show()

	
                                                                                                    record_process/record_process.py                                                                    0000644 0001750 0001750 00000002444 12256440160 016164  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   import speech_process
import numpy as np
import matplotlib.pyplot as plt
import sys
import os

def usage():
	#if len(sys.argv)!=2 and len(sys.argv)!=6:
	print "Usage:\n 	python record_process.py 'record_file' [-cChannelNum] [-rSampleRate] [-wSampleWidth] [-eLittleEndian] [-lLogFile]"
	print "Default Value:\n     -c1 -r8000 -w2 -e1 -llog.txt"
	print "Attention\n       Only PCM records need parameters above"
		
def record_process(recordFile,logFile,channelNum,sampleRate,sampleWidth,littleEndian):
	speech_process.speech_process(recordFile,nchannels=channelNum,sampleRate=sampleRate,sampleWidth=sampleWidth,littleEndian=littleEndian,logFile=logFile)

if __name__ == '__main__':
	if len(sys.argv)<2:
		usage()
		sys.exit()
	recordFile = sys.argv[1]

	logFile = 'log.txt'
	channelNum = 1
	sampleRate = 8000
	sampleWidth = 2
	littleEndian = 1
	for arg in sys.argv[2:]:
		if arg.startswith('-c'):
			channelNum = int(arg[2:])
		elif arg.startswith('-r'):
			sampleRate = int(arg[2:])
		elif arg.startswith('-w'):
			sampleWidth = int(arg[2:])
		elif arg.startswith('-e'):
			littleEndian = int(arg[2:])
		elif arg.startswith('-l'):
			logFile = str(arg[2:])
		else:
			print "Unrecgonize parameter :%s"%arg
			usage()
			sys.exit()
	record_process(recordFile,logFile,channelNum,sampleRate,sampleWidth,littleEndian)
		
                                                                                                                                                                                                                            record_process/record_process.pyc                                                                   0000644 0001750 0001750 00000003115 12253531561 016326  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   �
ف�Rc           @   s�  d  d l  Z  d  d l Z d  d l j Z d  d l Z d  d l Z d �  Z d �  Z	 e
 d k r�e e j � d k  r� e �  e j �  n  e j d Z d Z d Z d Z d Z d Z x� e j d D]� Z e j d	 � r� e e d � Z q� e j d
 � r	e e d � Z q� e j d � r+e e d � Z q� e j d � rMe e d � Z q� e j d � roe e d � Z q� d e GHe �  e j �  q� We	 e e e e e e � n  d S(   i����Nc           C   s@   t  t j � d k r< t  t j � d k r< d GHd GHd GHn  d  S(   Ni   i   sz   Usage:
 	python record_process.py 'record_file' [-cChannelNum] [-rSampleRate] [-wSampleWidth] [-eLittleEndian] [-lLogFile]s0   Default Value:
     -c1 -r8000 -w2 -e1 -llog.txts7   Attention
       Only PCM records need parameters above(   t   lent   syst   argv(    (    (    s   record_process.pyt   usage   s    *c         C   s/   t  j  |  d | d | d | d | d | �d  S(   Nt	   nchannelst
   sampleRatet   sampleWidtht   littleEndiant   logFile(   t   speech_process(   t
   recordFileR   t
   channelNumR   R   R   (    (    s   record_process.pyt   record_process   s    t   __main__i   i   s   log.txti@  s   -cs   -rs   -ws   -es   -ls   Unrecgonize parameter :%s(   R	   t   numpyt   npt   matplotlib.pyplott   pyplott   pltR   t   osR   R   t   __name__R    R   t   exitR
   R   R   R   R   R   t   argt
   startswitht   intt   str(    (    (    s   record_process.pyt   <module>   s>   			                                                                                                                                                                                                                                                                                                                                                                                                                                                   record_process/spectrogram.py                                                                       0000666 0001750 0001750 00000001355 12261152135 015500  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   """
Compute and display a spectrogram.
Give WAV file as input
"""
import matplotlib.pyplot as plt
import scipy.io.wavfile
import numpy as np
import sys


def spectrogram(m):
	sr = m.sampleRate
	x = m.rawData
	## Parameters: 10ms step, 30ms window
	#nstep = int(sr * 0.01)
	#nwin  = int(sr * 0.03)
	nstep = m.step
	nwin = m.frameSize
	nfft = nwin
	window = np.hamming(nwin)
	## will take windows x[n1:n2].  generate
	## and loop over n2 such that all frames
	## fit within the waveform
	nn = range(nwin, len(x), nstep)
	X = np.zeros( (len(nn), nfft/2) )
	for i,n in enumerate(nn):
		xseg = x[n-nwin:n]
		z = np.fft.fft(window * xseg, nfft)
		X[i,:] = np.log(np.abs(z[:nfft/2]))

	plt.imshow(X.T, interpolation='nearest',origin='lower',aspect='auto')
                                                                                                                                                                                                                                                                                   record_process/spectrogram.pyc                                                                      0000644 0001750 0001750 00000002064 12261152167 015642  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   �
]��Rc           @   sF   d  Z  d d l j Z d d l Z d d l Z d d l Z d �  Z	 d S(   s;   
Compute and display a spectrogram.
Give WAV file as input
i����Nc         C   s  |  j  } |  j } |  j } |  j } | } t j | � } t | t | � | � } t j t | � | d f � } xt t	 | � D]f \ }	 }
 | |
 | |
 !} t j
 j
 | | | � } t j t j | | d  � � | |	 d  d  � f <q} Wt j | j d d d d d d �d  S(   Ni   t   interpolationt   nearestt   origint   lowert   aspectt   auto(   t
   sampleRatet   rawDatat   stept	   frameSizet   npt   hammingt   ranget   lent   zerost	   enumeratet   fftt   logt   abst   pltt   imshowt   T(   t   mt   srt   xt   nstept   nwint   nfftt   windowt   nnt   Xt   it   nt   xsegt   z(    (    s   spectrogram.pyt   spectrogram   s    				4(
   t   __doc__t   matplotlib.pyplott   pyplotR   t   scipy.io.wavfilet   scipyt   numpyR
   t   sysR#   (    (    (    s   spectrogram.pyt   <module>   s
                                                                                                                                                                                                                                                                                                                                                                                                                                                                               record_process/speech_process.py                                                                    0000644 0001750 0001750 00000001517 12262173476 016167  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   from speech import *
frameSize = 256
overLap = 128


def speech_process(source, nchannels=1, sampleRate=8000, sampleWidth=2,littleEndian=1,minLen=0.2,minSilence=0.3,feature_file="/home/will/Documents/data.txt",label='0'):
	try:
		record = Speech(source,nchannels,sampleRate,sampleWidth,littleEndian)
	except Exception,error:
		print Exception," : ",error
		return

	record.getSpeechSegmentByAbsVolume(frameSize,overLap,minLen,minSilence)
	record.energyZeroCount()
	record.getFramePitch()
	record.getWordsPerSeg()
	record.freqAnalyze()
	record.LPC()
	record.getEnergyBelow250()
	record.getSpeechPercentage()
	record.dataProcess()
	record.writeToFile(feature_file,label)
	
	return record



def predict(record,scale_model='scale_model',model_file='train_model',label_file='records_information'):
	record.predict(scale_model,model_file,label_file)


                                                                                                                                                                                 record_process/speech_process.pyc                                                                   0000644 0001750 0001750 00000002335 12262173573 016327  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   �
>��Rc        	   @   sM   d  d l  Td Z d Z d d d d d d d	 d
 d � Z d d d d � Z d S(   i����(   t   *i   i�   i   i@  i   g�������?g333333�?s   /home/will/Documents/data.txtt   0c	         C   s�   y t  |  | | | | � }	 Wn! t k
 r? }
 t Gd G|
 GHd  SX|	 j t t | | � |	 j �  |	 j �  |	 j �  |	 j �  |	 j	 �  |	 j
 �  |	 j �  |	 j �  |	 j | | � |	 S(   Ns    : (   t   Speecht	   Exceptiont   getSpeechSegmentByAbsVolumet	   frameSizet   overLapt   energyZeroCountt   getFramePitcht   getWordsPerSegt   freqAnalyzet   LPCt   getEnergyBelow250t   getSpeechPercentaget   dataProcesst   writeToFile(   t   sourcet	   nchannelst
   sampleRatet   sampleWidtht   littleEndiant   minLent
   minSilencet   feature_filet   labelt   recordt   error(    (    s   speech_process.pyt   speech_process   s     







t   scale_modelt   train_modelt   records_informationc         C   s   |  j  | | | � d  S(   N(   t   predict(   R   R   t
   model_filet
   label_file(    (    s   speech_process.pyR      s    N(   t   speechR   R   R   R   (    (    (    s   speech_process.pyt   <module>   s   
!                                                                                                                                                                                                                                                                                                   record_process/speech.py                                                                            0000644 0001750 0001750 00000067207 12262524511 014427  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   # -*- coding: utf-8 -*-
import os
import math
import wave
import numpy as np
from math import ceil,log
import utils
import scipy.signal as signal
from scipy.signal import argrelmax
import scipy

from audiolazy import *
import pylab as pl
from scikits.talkbox import lpc as talkboxLpc
from mood_svm import classify
class Speech:
	def __init__(self,source,nchannels,sampleRate,sampleWidth,littleEndian):
		self.error = []
		self.fileName = source
		if source.find('.pcm')!=-1:
			if nchannels==0 or sampleWidth==0 or sampleRate==0 or littleEndian==-1:
				raise Exception('WrongParametersForPCM')
			try:
				fw = open(source,'r')
			except:
				print "File %s  can't be found"%(source)
				raise Exception('FileNotFound')
			self.nchannels = nchannels
			self.sampleRate = sampleRate
			self.sampleWidth = sampleWidth
			rawData = fw.read()
			if sampleWidth==1:
				dtype = np.int8
			elif sampleWidth==2:
				dtype = np.int16
			elif sampleWidth==4:
				dtype = np.int32
			self.rawData = np.fromstring(rawData,dtype=dtype)
			self.nframes = len(self.rawData)
			fw.close()
		elif source.find('.wav')!=-1:
			try:
				fw = wave.open(source,'r')
			except:
				print "File %s  can't be found"%(source)
				raise Exception('FileNotFound')
			params = fw.getparams()
			self.nchannels,self.sampleWidth,self.sampleRate,self.nframes = params[:4]
			rawData = fw.readframes(self.nframes)
			if self.sampleWidth==1:
				dtype = np.int8
			elif self.sampleWidth==2:
				dtype = np.int16
			elif self.sampleWidth==4:
				dtype = np.int32
			self.rawData = np.fromstring(rawData,dtype=dtype)
			fw.close()
		maxData = max(abs(self.rawData))
		print maxData
		if maxData<2000:
			self.isBlank = True
		else:
			self.isBlank = False
		self.maxData = maxData
		#self.rawData = self.rawData*1.0/maxData
		self.rawData = self.rawData*1.0
		self.totalLength = self.nframes*1.0/self.nchannels/self.sampleRate
		self.speechSegment = []
		self.frame = []
		self.zcr = []
		self.shortTimeEnergy = []
		self.volume = []
		self.speed = []

	def __del__(self):
		pass
	
	def getSingleWords(self):
		pass
	def getEnergyBelow250(self):
		self.energyBelow250 = []
		loc = int(250.0/4000*self.frameSize)
		for fftFrame in self.fftFrameAbs:
			totalEnergy = np.sum(fftFrame)
			below250 = np.sum(fftFrame[:loc])
			self.energyBelow250.append(below250/totalEnergy)

	# get speechSegment,volume,volumeAbs,and shortTimeEnergy 
	def getSpeechPercentage(self):
		self.speechPercentage = 0
		speechFrame = 0
		for i in self.speechSegment:
			speechFrame = speechFrame + i[1] - i[0]
		self.speechPercentage = speechFrame*1.0/self.frameNum 
		self.speechLength = self.speechPercentage*self.totalLength
	def getSpeechSegment(self,frameSize,overLap,minLen,minSilence):
		print "getSpeechSegment"
		zcrThread = 0
		if self.isBlank == True:
			return
		if frameSize<=overLap:
			raise Exception('Wrong getFrames parameters')
		self.frameSize = frameSize
		self.overLap = overLap
		self.step = self.frameSize-self.overLap
		self.frameNum = int(ceil(self.nframes/self.step))
		self.absVolume = []
		for i in range(self.frameNum):
			self.frame.append(self.rawData[i*self.step:min(i*self.step+frameSize,self.nframes)])
			#get zeroCrossingRate and energy
			#self.zcr.append(sum(self.frame[i][0:-1]*self.frame[i][1:]<=0))
			#zeroFrame = utils.isPositive(self.frame[i])
			#zcrThread = max(self.frame[i])/2
			zcrThread = 1000000
			zcr = utils.zcr(self.frame[i],zcrThread)
			self.zcr.append(zcr)
			#self.zcr.append(0.5*sum(abs(zeroFrame[0:-1]-zeroFrame[1:])))
			self.shortTimeEnergy.append(sum([k**2 for k in self.frame[i]]))
			cal = sum(self.frame[i]*self.frame[i]*1.0/self.maxData/self.maxData)
			if cal==0:
				cal = 0.001
			self.volume.append(10*np.log(cal))
			self.absVolume.append(sum(abs(self.frame[i])))
		# Two threadholds for shortTimeEnergy 
		tHoldLow = min(max(self.shortTimeEnergy)/8,1)
		tHoldHigh = min(max(self.shortTimeEnergy)/4,4)
		print '*****'
		print tHoldLow
		print tHoldHigh
		self.tHoldHigh = tHoldHigh
		self.tHoldLow = tHoldLow
		print self.tHoldHigh
		self.segmentTime = []
		# status is used to show the status of the endPointDetection machine
		# 0=>silence		1=>mayBegin		2=>speechSegment 	3=>end 
		status = 0
		count = 0
		segmentBeg = 0  
		silence = 0		#Used to indicate the length of silence frames 
		minSilence = int(minSilence*self.sampleRate/self.frameSize)  #If we meet minSilence consecutive silence than the speech is probably end
		minLen = int(minLen*self.sampleRate/self.frameSize) 	#A speech should at least longer than minLen frames
		segmentEnd = 0
		print  "minSilence",minSilence,"minLen",minLen
		for i in range(self.frameNum):
			if (status == 0) or (status == 1):
				if self.shortTimeEnergy[i]>tHoldHigh:
					segmentBeg = i-count
					status = 2
					silence = 0
					count = count + 1
					print "beg"
				elif self.shortTimeEnergy[i]>tHoldLow:
					status = 1
					count = count + 1
				else:
					status = 0
					count = 0
			elif status == 2:
				if self.shortTimeEnergy[i] > tHoldLow:
					count = count + 1
					silence = 0
				else:
					silence = silence + 1
					if silence < minSilence:	#silence is not long enough to end the speech
						count = count + 1
					elif count < minLen:		#speech is so short that it should be  noise
						status = 0
						silence = 0
						count = 0
						print "endOfNoise"
					else:
						status = 0
						segmentEnd = i - minSilence
						self.speechSegment.append((segmentBeg,segmentEnd))
						self.segmentTime.append((segmentBeg*self.totalLength/self.frameNum,segmentEnd*self.totalLength/self.frameNum))
						print "end success"
						#print "beg speech %d %f"%(segmentBeg,segmentBeg*self.totalLength/self.frameNum)
						#print "end speech %d %f"%(segmentEnd,segmentEnd*self.totalLength/self.frameNum)
						status = 0
						count = 0
						silence = 0
		if status == 2:
			self.speechSegment.append((segmentBeg,self.frameNum))
			self.segmentTime.append((segmentBeg*1.0/self.sampleRate,self.frameNum*1.0/self.sampleRate))
			#self.segmentTime.append((self.frameNum-segmentBeg)*1.0/self.sampleRate)	
		self.speechTime = sum([v[1]-v[0] for v in self.segmentTime])
		self.totalSeg = len(self.speechSegment)
	
	def energyZeroCount(self):
		self.ezr = []
		self.ezm = []
		for i in range(len(self.shortTimeEnergy)):
			if self.zcr[i]!=0:
				ezr = self.shortTimeEnergy[i]/self.zcr[i]/10000000
			else:
				ezr = self.shortTimeEnergy[i]/10000000
			ezm = self.shortTimeEnergy[i]*self.zcr[i]/10000000
			self.ezr.append(ezr)
			self.ezm.append(ezm)

	def getSpeechSegmentByAbsVolume(self,frameSize,overLap,minLen,minSilence):
		print "getSpeechSegment"
		zcrThread = 0
		if self.isBlank == True:
			return
		if frameSize<=overLap:
			raise Exception('Wrong getFrames parameters')
		self.frameSize = frameSize
		self.overLap = overLap
		self.step = self.frameSize-self.overLap
		self.frameNum = int(ceil(self.nframes/self.step))
		self.absVolume = []
		for i in range(self.frameNum):
			self.frame.append(self.rawData[i*self.step:min(i*self.step+frameSize,self.nframes)])
			zcrThread = max(self.frame[i])/8
			#get zeroCrossingRate and energy
			#self.zcr.append(sum(self.frame[i][0:-1]*self.frame[i][1:]<=0))
			#zeroFrame = utils.isPositive(self.frame[i])
			zcr = utils.zcr(self.frame[i],zcrThread)
			self.zcr.append(zcr)
			self.shortTimeEnergy.append(sum([k**2 for k in self.frame[i]]))
			cal = np.sum(self.frame[i]*self.frame[i]*1.0/self.maxData/self.maxData)
			if cal==0:
				cal = 0.001
			self.volume.append(10*np.log(cal))
			self.absVolume.append(np.sum(np.abs(self.frame[i])))
		# Two threadholds for shortTimeEnergy 
		tHoldLow = min(max(self.absVolume)/10,3*self.maxData)
		tHoldHigh = min(max(self.absVolume)/6,6*self.maxData)
		self.tHoldHigh = tHoldHigh
		self.tHoldLow = tHoldLow
		#print self.tHoldHigh
		self.segmentTime = []
		# status is used to show the status of the endPointDetection machine
		# 0=>silence		1=>mayBegin		2=>speechSegment 	3=>end 
		status = 0
		count = 0
		segmentBeg = 0  
		silence = 0		#Used to indicate the length of silence frames 
		minSilence = int(minSilence*self.sampleRate/self.frameSize)  #If we meet minSilence consecutive silence than the speech is probably end
		minLen = int(minLen*self.sampleRate/self.frameSize) 	#A speech should at least longer than minLen frames
		segmentEnd = 0
		#print  "minSilence",minSilence,"minLen",minLen
		for i in range(self.frameNum):
			if (status == 0) or (status == 1):
				if self.absVolume[i]>tHoldHigh:
					segmentBeg = i-count
					status = 2
					silence = 0
					count = count + 1
					#print "beg"
				elif self.absVolume[i]>tHoldLow:
					status = 1
					count = count + 1
				else:
					status = 0
					count = 0
			elif status == 2:
				if self.absVolume[i] > tHoldLow:
					count = count + 1
					silence = 0
				else:
					silence = silence + 1
					if silence < minSilence:	#silence is not long enough to end the speech
						count = count + 1
					elif count < minLen:		#speech is so short that it should be  noise
						status = 0
						silence = 0
						count = 0
						#print "endOfNoise"
					else:
						status = 0
						segmentEnd = i - minSilence
						self.speechSegment.append((segmentBeg,segmentEnd))
						self.segmentTime.append((segmentBeg*self.totalLength/self.frameNum,segmentEnd*self.totalLength/self.frameNum))
						#print "end success"
						#print "beg speech %d %f"%(segmentBeg,segmentBeg*self.totalLength/self.frameNum)
						#print "end speech %d %f"%(segmentEnd,segmentEnd*self.totalLength/self.frameNum)
						status = 0
						count = 0
						silence = 0
		if status == 2:
			self.speechSegment.append((segmentBeg,self.frameNum))
			self.segmentTime.append((segmentBeg*1.0/self.sampleRate,self.frameNum*1.0/self.sampleRate))
			#self.segmentTime.append((self.frameNum-segmentBeg)*1.0/self.sampleRate)	
		self.speechTime = sum([v[1]-v[0] for v in self.segmentTime])
		self.totalSeg = len(self.speechSegment)

	#50Hz ~ 450Hz
	#为了消除共振峰的影响，使用带通滤波器(60~900)或中心削波
	def getFramePitch(self):
		#放浊音基音的开始和结尾
		#pitchSeg is used to store the "ZHUOYIN" pitch seg of Each speechSeg,its length is the same as self.speechSeg
		#For example, self.pitchSeg[m][n] is the (n+1)th "ZHUOYIN" pitch seg in m+1 speechSeg 
		self.pitchSeg = []
		#self.tmp = []
		minLen = 5 # 最小浊音长度
		minSilence = 5 #浊音之间最小间隔
		if len(self.speechSegment)==0 or self.isBlank==True:
			return
		
		pitchThread = int(self.sampleRate/450)
		self.pitch = []
		self.tmp=[]
		for segTime in self.speechSegment:
			tmp = []
			pitchSum = 0
			beg = segTime[0]
			end = segTime[1]
			curFramePitch = []
			for frame in self.frame[beg:end]:
				pitch = utils.ACF(frame)
				#pl.plot(pitch)
				#pl.show()
				pitch[:pitchThread] = -abs(pitch[0])
				
				pitchMax = np.argmax(pitch)
				if pitchMax==0:
					self.error.append(('pitch error',pitch,utils.ACF(frame)))
				tmp.append((self.sampleRate/pitchMax,pitch[pitchMax]/1000000))
				curFramePitch.append(self.sampleRate/pitchMax)
			self.tmp.append(tmp)	
			pitchHigh = np.max(tmp,0)[1]/12.0
			pitchLow = np.max(tmp,0)[1]/24.0
			#pitchHigh = 0
			#pitchLow = 0
			ezrLevel = max(self.ezr[beg:end])*0.2
			volumeHigh = np.max(self.absVolume[beg:end])/4
			volumeLow = volumeHigh/2
			
			#zcrHigh = np.max(self.zcr[beg:end])/2
			#zcrLow = zcrHigh/1
			zcrHigh = 1000
			zcrLow = 1000
			#0 => 清音 1=>可能是浊音 2=>浊音 3=>浊音结束
			status = 0
			trange = []
			count = 0
			silence = 0
			self.pitch.append(curFramePitch)
			print 'ezrLevel',ezrLevel,'volumeHigh',volumeHigh,'pitchHigh',pitchHigh,'minSilence',minSilence,'minLen',minLen
			for t in range(len(tmp)):
				if tmp[t][1]>pitchHigh and self.ezr[t+beg]>ezrLevel:
					print 'beg ',t,'status',status
					if status == 0:
						start = t 
						duration = 0
						status = 1
					duration = duration+1
				else:
					if status == 1:
						trange.append((start,t))
						status = 0
						duration = 0
			if status == 1:
				trange.append((start,len(tmp)))
			self.pitchSeg.append(trange)
			self.tmp.append(tmp)




			'''
			status = 0
			for t in range(len(tmp)):
				if status==0 or status==1:
					if tmp[t][1]>pitchHigh and self.ezr[t+beg]>ezrLevel and self.absVolume[t+beg]>volumeHigh and self.zcr[t+beg]<zcrLow:
						pitchBeg = t-count 
						status = 2
						count = count+1
						print 'beg',t-count
					elif tmp[t][1]>pitchLow and self.ezr[t+beg]>ezrLevel and self.absVolume[t+beg]>volumeLow and self.zcr[t+beg]<zcrHigh:
						status = 1
						count = count+1
					else:
						status = 0
						count = 0
				elif status == 2:
					if tmp[t][1]>pitchLow and self.ezr[t+beg]>ezrLevel and self.absVolume[t+beg]>volumeLow and self.zcr[t+beg]<zcrHigh:
						count = count+1
						silence = 0
					else:
						silence = silence+1
						if silence<minSilence:
							count = count+1
						elif count < minLen:
							status = 0
							silence = 0
							count = 0
							print 'too short',pitchBeg,t			
						else:
							status = 0
							pitchEnd = t - minSilence
							trange.append((pitchBeg,pitchEnd))
							status = 0
							count = 0
							silence = 0
			if status == 2:
				if len(tmp)-pitchBeg > minLen:
					trange.append((pitchBeg,len(tmp)-1))

			self.pitchSeg.append(trange)

			#pitchSeg = []
			#for t in trange:
			#	pitchSeg.append(tmp[t[0]:t[1]])
			#self.pitchSeg.append(pitchSeg)
			
			
			#self.tmp.append(tmp)
			'''
	
	def getFramePitchAdvanced(self):
		pitchLow = 10
		self.pitchAdvanced = []
		for segTime in self.speechSegment:
			pitchAdvanced = []
			beg = segTime[0]
			end = segTime[1]
			for i in range(beg,end):
				pitch = utils.advancedACF(self.frame[i],self.frame[i+1])
				pitch[:pitchLow] = -pitch[0]
				pitchMax = np.argmax(pitch)
				pitchAdvanced.append(self.sampleRate/pitchMax)
		self.pitchAdvanced.append(pitchAdvanced)

	def LPC(self):
		print "LPC"
		if len(self.speechSegment)==0 or self.isBlank==True:
			return
		self.ar = []
		self.fmt = []
		self.bw = []
		self.frqs = []
		for frame in self.frame:
			#[ar, var, reflec] = yulewalker.aryule(frame, 8)
			[ar,var,reflec] = talkboxLpc(frame,8)
			self.ar.append(ar)
			rts = np.roots(ar)
			rts = [r for r in rts if np.imag(r)>=0]
			#angz = np.atan2(np.imag(rts),np.real(rts))
			angz = np.asarray([math.atan2(np.imag(r),np.real(r)) for r in rts])
			angz = angz*self.sampleRate/(np.pi*2)
			#print angz
			#[frqs,indices] = sort(angz)
			frqs = [(angz[i],i) for i in range(len(angz))]
			frqs.sort()
			self.frqs.append(frqs)
			fmt = []
			bandwidth = []
			for kk in range(len(frqs)):
				bw = -1.0/2*(self.sampleRate/(2*np.pi))*np.log(np.abs(rts[frqs[kk][1]]))
				#print frqs[kk][0],bw
				if ((frqs[kk][0]>90) and (bw<400) ):
					fmt.append(frqs[kk][0])
					#print frqs[kk][0]
					bandwidth.append(bw)

			fmt.sort()
			fmt = fmt[:3]
			self.fmt.append(fmt)
			self.bw.append(bandwidth)
		self.f1 = []
		for f in self.fmt:
			if len(f)==0:
				self.f1.append(0)
			else:
				self.f1.append(f[0])

	def freqAnalyze(self):
		print "freqAnalyze"
		if len(self.speechSegment)==0 or self.isBlank==True:
			return
		self.shortTimeLinjieVector = []
		self.formant = []
		self.fftFrameAbs = []
		#短时谱的临界带特征矢量
		F = [0]
		fs = self.sampleRate/self.frameSize
		for i in range(1,19):
			m = int((i+0.53)*1960/(26.81-0.53-i))
			n = m/fs
			F.append(n)
		
		
		self.formantValue = []
		self.frameSize/2+1
		self.fftFrame = []
		#h1,f1 = signal.freqz([1,-0.98],[1])
		#cc = 0
		for frame in self.frame[:-1]:
			#窗函数
			#cc = cc+1
			f = frame*signal.hamming(self.frameSize,sym=0)
			#预加重
			#f = scipy.signal.lfilter([1,-0.97],1,f)
			fftFrame = np.fft.rfft(f)/(self.frameSize/2)
			self.fftFrame.append(fftFrame)
			fftFrameAbs = [abs(fft) for fft in fftFrame]
			self.fftFrameAbs.append(fftFrameAbs)
			#短时谱临界带特征矢量
			g = np.zeros(17)
			beg = 1
		
			for i in range(1,17):
				for k in range(beg,min(len(fftFrame),F[i]+1)):
					g[i] = g[i] + abs(fftFrame[k])**2
				beg = F[i]+1
			self.shortTimeLinjieVector.append(g)
			#共振峰
			g0 = utils.argLocalMax(fftFrameAbs)
			points = [(fftFrameAbs[g],g) for g in g0]
			points.sort()
			#print g0[0]
			m = min(3,len(g0))
			formant = []
			for i in range(m):
				formant.append(points[-i-1][1]*fs)

			self.formantValue.append(points[-1][0])
			formant.sort() 
			self.formant.append(formant)
	#3,2
	def getWordsPerSeg(self,minLen=10,minSilence=5,preLen=2):
		print "getWordsPerSeg"
		if len(self.speechSegment)==0 or self.isBlank==True:
			return
		status = 0 
		self.segWord = []
		for seg in self.speechSegment:
			status = 0
			silence = 0
			segBeg = seg[0]
			segEnd = seg[1]
			volumeHigh = max(self.volume)/4
			volumeLow = max(self.volume)/8
			zcrHigh = max(self.zcr)/4
			zcrLow = max(self.zcr)/8
			#print volumeHigh,volumeLow
			word = 0
			segWord = []
			count = 0
			precount = 0
			crest = 0
			wordBeg = 0
			for frame in range(segBeg,segEnd):
				if status==0 or status==1:
					crest = max(crest,self.volume[frame])
					if self.volume[frame] >= volumeHigh:
						status = 2
						count = precount + 1
						wordBeg = frame-count
						#print "begin",frame
					elif self.volume[frame] >= volumeLow:
						status = 1
						precount = precount + 1
						if precount >= preLen:
							status = 2
							#print "begin",frame
							wordBeg = frame-precount
							count = precount
							precount = 0
					else:
						precount = 0
						status = 0
				elif status == 2:
					crest = max(crest,self.volume[frame])
					#print "crest",crest
					if self.volume[frame] >= volumeLow and self.volume[frame]>= crest/2:
						count = count + 1
						silence = 0
					else:
						silence = silence + 1
						if silence > minSilence:
							status = 0
							crest = 0
							if frame-wordBeg+1 > minLen:
								word = word + 1
								segWord.append((wordBeg,frame))
								#print "end success",frame
							else:
								pass
								#print "end of too short",frame
							precount = 0
							count = 0
			if status == 2:
				segWord.append((wordBeg,segEnd))
			self.segWord.append(segWord)
			#print segWord
			self.speed.append(len(segWord)*1.0/((segEnd-segBeg)*1.0*(self.frameSize-self.overLap)/self.sampleRate))
	

	def dataProcess(self):
		#self.maxData = 1
		#语速 基音频率 基音范围 最大基频 最小基频 基频一阶差分绝对值平均值 振幅 振幅标准差 振幅最大值 在250Hz能量以下所占百分比 第一共振峰 第一共振峰范围
		#self.speed self.pitchAverage self.pitchRange, self.volumeAverage self.volumeStd self.fmtAverage  self.fmtRange
		if len(self.speechSegment)==0 or self.isBlank==True:
			return
		self.num = len(self.speechSegment)
		
		#for i in range(self.num):
		#	pitchAverage = np.average(self.pitchSeg)
		print "We have %d speech segments in all"%self.num
		self.pitchAverage = 0
		self.pitchAveragePerSeg = []
		self.pitchRange = []
		self.volumeAverage = []
		self.volumeStd = []
		self.fmtAverage = []
		self.pitchMax = []
		self.pitchMin = []
		self.pitchStd = []
		self.volumeMax = []
		self.volumeMin = []
		self.volumeDiff = []
		self.pitchDiff = []
		self.below250 = []
		self.pitchNum = 0
		#self.fmtRange = []
		for i in range(self.num):
			pitchSum = 0
			pitchNum = 0
			pitchMax = 0
			pitchMin = 1000
			pitchDiff = 0
			for k in range(len(self.pitchSeg[i])):
				#print k
				#pitchSeg 是记录在pitch中满足50～450之间的pitch的起始点的 可以用来计算pitch的变化规律
				pitchSum = pitchSum + sum(self.pitch[i][self.pitchSeg[i][k][0]:self.pitchSeg[i][k][1]])
				pitchNum = pitchNum + self.pitchSeg[i][k][1] - self.pitchSeg[i][k][0]
				  
				if self.pitchSeg[i][k][0]==self.pitchSeg[i][k][1]:
					print self.fileName
				pitchMax = max(max(self.pitch[i][self.pitchSeg[i][k][0]:self.pitchSeg[i][k][1]]),pitchMax)
				pitchMin = min(min(self.pitch[i][self.pitchSeg[i][k][0]:self.pitchSeg[i][k][1]]),pitchMin)
				if k!=len(self.pitchSeg[i])-1:
					pitchDiff = pitchDiff + abs(self.pitch[i][k+1]-self.pitch[i][k])
				
					
				#print pitchSum
				#print pitchNum
			if pitchNum==0:
				self.pitchAveragePerSeg.append(0)
				self.pitchRange.append(0)
				self.pitchMax.append(0)
				self.pitchMin.append(0)
				self.pitchDiff.append(0)
				continue
			self.pitchAverage = self.pitchAverage + pitchSum
			self.pitchNum = self.pitchNum + pitchNum
			self.pitchAveragePerSeg.append(pitchSum*1.0/pitchNum)
			pitchDiff = pitchDiff*1.0/pitchNum
			self.pitchDiff.append(pitchDiff)
			self.pitchRange.append((pitchMax-pitchMin))
			self.pitchMax.append(pitchMax)
			self.pitchMin.append(pitchMin)

		if self.pitchNum!=0:
			self.pitchAverage = self.pitchAverage/self.pitchNum
		for i in range(self.num):
			beg = self.speechSegment[i][0]
			end = self.speechSegment[i][1]
			below250 = np.average(self.energyBelow250[beg:end])
			self.below250.append(below250)
			volume = np.average(self.absVolume[beg:end])
			volumeStd = np.std(self.absVolume[beg:end])
			fmtAverage = np.average(self.f1[beg:end])
			self.volumeAverage.append(volume)
			self.volumeStd.append(volumeStd)
			self.volumeMax.append(np.max(self.absVolume[beg:end]))
			self.volumeMin.append(np.min(self.absVolume[beg:end]))
			self.fmtAverage.append(fmtAverage)
			volumeDiff = 0
			for k in range(beg,end-1):
				volumeDiff = volumeDiff + abs(self.absVolume[k+1]-self.absVolume[k])
			self.volumeDiff.append(volumeDiff*1.0/(end-beg))
		self.features = []
		for i in range(self.num):
			features = [self.pitchMax[i],self.pitchAveragePerSeg[i],self.pitchRange[i],self.pitchMin[i],self.pitchDiff[i],self.volumeAverage[i],self.volumeStd[i],self.volumeMax[i],self.volumeDiff[i],self.below250[i]]
			self.features.append(features)
		
	
	def predict(self,scale_model,model_file,label_file):
		self.gender = 'Unknown'
		self.category = -1
		predict_data = 'predict_data'
		#全静音 单交互正常挂机 单交互异常挂机 多交互正常挂机 多交互异常挂机
		if self.isBlank==True:
			self.category = '全静音'
		else:
			if self.pitchAverage in range(100,200):
				self.gender = '男'
			elif self.pitchAverage > 200:
				self.gender = '女'
			self.writeToFile(predict_data,'0')
			self.labels = classify(scale_model,model_file,predict_data)
			cmd = 'rm %s'%predict_data
			os.system(cmd)
		fs = open(label_file,'aw')
		if len(self.labels)==1:
			if self.labels[0]==-1:
				self.category = '单交互正常挂机'
			else:
				self.category = '单交互异常挂机'
		else:
			for label in self.labels:
				if label == 1:
					self.category = '多交互异常挂机'
					break
			if self.category == -1:
				self.category = '多交互异常挂机'
		self.label = np.average(self.labels)
		
		fs.write('File:		%s\nCategory:		%s\nLabel:		%s\n'%(self.fileName,self.category,self.labels))
		#fs.write('%-20s%-20s%-20s%-20s%-20s%-20s\n'%('总时长','通话时长','通话段数','通话人音量','通话人性别','通话人语调'))
		fs.write('总时长        通话时长        通话段数        通话人音量        通话人性别        通话人语调\n')
		fs.write('%-15.2f%-15.2f%-15f%-18.2f%-16s%-20.2f\n'%(self.totalLength,self.speechLength,self.num,np.average(self.volumeAverage),self.gender,self.pitchAverage))
		fs.close()


				
				



	
	
	#用于机器学习
	def writeToFile(self,dataFile,label='0'):
	#基音频率 基音范围 振幅 振幅标准差 第一共振峰 第一共振峰范围
	#pitchAverage pitchRange pitchMax pitchMin pitchDiff volumeMax volumeAverage volumeStd volumeDiff below250 
		fs = open(dataFile,'aw')
		cnt = 1
		#fs.write(self.fileName+'\n')
		if self.isBlank==True:
			fs.write('%s %d:%f %d:%f %d:%f %d:%f %d:%f %d:%f %d:%f %d:%f %d:%f %d:%f\n'%('0',1,0,2,0,3,0,4,0,5,0,6,0,7,0,8,0,9,0,10,0))
		else:
			for i in range(self.num):
				#fs.write('Wav File Name:%s\n'%(self.fileName))
		#		fs.write('Segment Num %d:\n'%(cnt))
				cnt = cnt + 1
				fs.write('%s %d:%f %d:%f %d:%f %d:%f %d:%f %d:%f %d:%f %d:%f %d:%f %d:%f\n'%(label,1,self.pitchMax[i],2,self.pitchAveragePerSeg[i],3,self.pitchRange[i],4,self.pitchMin[i],5,self.pitchDiff[i],6,self.volumeAverage[i],7,self.volumeStd[i],8,self.volumeMax[i],9,self.volumeDiff[i],10,self.below250[i]))
		
		fs.close()
'''			
	def lpc(self):
		print "lpc"
		if len(self.speechSegment)==0 or self.isBlank==True:
			return
		self.numerator = []
		for frame in self.frame:
			acdata = acorr(frame)
			filt = levinson_durbin(acdata,8)
			self.numerator.append(filt.numerator)


'''
'''
	def pre_getWordsPerSeg(self, a=2, T=3):
		self.transitionTag = []
		for seg in self.speechSegment:
			segBeg = seg[0]
			segEnd = seg[1]
			TshortTimeEnergyBefore = sum(self.speechSegment[segBeg:segBeg+3])
			TshortTimeEnergyAfter = sum(self.speechSegment[segBeg+2:segBeg+5])
			for k in xrange(segBeg+2,segEnd-4):
				curShortEnergy = self.shortTimeEnergy[k]
				curZcr = self.zcr[k]
				flag = False
				if curShortEnergy>a*self.shortTimeEnergy[k+1] or curShortEnergy*a<self.shortTimeEnergy[k+1]:
					flag = True
				elif curZcr>a*self.zcr[k+1] or curZcr*a<self.zcr[k+1]:
					flag = True
				elif TshortTimeEnergyBefore*a < TshortTimeEnergyAfter or TshortTimeEnergyAfter*a < TshortTimeEnergyBefore:
					flag = True
				if flag == True:
					self.transitionTag.append(k)
				TshortTimeEnergyBefore = TshortTimeEnergyBefore - self.shortTimeEnergy[k-2] + self.shortTimeEnergy[k+1]
				TshortTimeEnergyAfter = TshortTimeEnergyAfter - self.shortTimeEnergy[k] + self.shortTimeEnergy[k+3]

	def dump(self,log_file):
		fs = open(log_file,'aw')
		fileName = self.fileName.split('/')[-1]
		if len(self.speechSegment)==0 or self.isBlank==True:
			fs.write('%-20s%-15s\n'%(fileName,'全静音'))
			fs.close()
			return
		fs.write('%-20s%-15d%-15.2f%-15.2f%-15.2f%-15d%-15f\n'%(fileName,self.segNum,self.averageSpeed,self.averagePitch,self.averageVolume,self.totalWord,self.speechTime))
		#totalStat = ""
		#totalStat = str(self.fileName)+"  "+str(self.totalWord)+"  "+str(self.averageVolume)+"  "+str(self.averagePitch)+"\n"
		#fs.write(totalStat)
		
		segNum = 0
		for stat in self.stat:
			segNum = segNum + 1
			fs.write('%-20s%-15d%-15.2f%-15.2f%-15.2f%-15d%-15.2f\n'%("",segNum,stat['speed'],stat['pitch'],stat['volume'],stat['words'],stat['time']))
			
		fs.write('%-20s%-15s%-15.2f%-15.2f%-15.2f\n'%("","Variance",self.speedVariance,self.pitchVariance,self.volumeVariance))
		fs.close()

	def getStat(self):
		print "getStat"
		if len(self.speechSegment)==0 or self.isBlank==True:
			return
		print len(self.speechSegment)
		self.totalWord = 0
		self.stat = []
		#otalVolume = int(sum(self.volume)/self.frameNum)
		#self.totalPitch = int(sum(self.pitch)/self.frameNum)
		self.averagePitch = 0
		self.averageVolume = 0
		speechFrameNum = 0
		
		for i in range(len(self.speechSegment)):
			self.totalWord = self.totalWord + len(self.segWord[i])
			self.averagePitch = sum(self.pitch[i]) + self.averagePitch
			segBeg = self.speechSegment[i][0]
			segEnd = self.speechSegment[i][1]
			self.averageVolume = self.averageVolume + sum(self.absVolume[segBeg:segEnd])
			speechFrameNum = speechFrameNum + segEnd - segBeg
			shortTimeEnergy = int(sum(self.shortTimeEnergy[segBeg:segEnd])/(segEnd-segBeg))
			volume = float(sum(self.absVolume[segBeg:segEnd])/(segEnd-segBeg))
			pitch = float(sum(self.pitch[i])/(segEnd-segBeg))
			speed = float(self.speed[i])
			item = {"volume":volume,"pitch":pitch,"speed":speed,"shortTimeEnergy":shortTimeEnergy,"time":self.segmentTime[i][1]-self.segmentTime[i][0],"words":len(self.segWord[i])}
			self.stat.append(item)
		self.speechFrameNum = speechFrameNum
		self.averagePitch = self.averagePitch/(self.speechFrameNum+0.01)
		self.averageVolume = self.averageVolume/(self.speechFrameNum+0.01)
		self.averageSpeed = self.totalWord*1.0/(self.speechTime+0.01)
		self.volumeVariance = sum([(v['volume']-self.averageVolume)*(v['volume']-self.averageVolume) for v in self.stat])/len(self.speechSegment)
		self.pitchVariance = sum([(v['pitch']-self.averagePitch)*(v['pitch']-self.averagePitch) for v in self.stat])/len(self.speechSegment)
		self.speedVariance = sum([(v['speed']-self.averageSpeed)*(v['speed']-self.averageSpeed) for v in self.stat])/len(self.speechSegment)
		self.segNum = len(self.speechSegment)
		self.timeLen = self.nframes/self.sampleRate/self.nchannels
		print "total words:",self.totalWord

'''                                                                                                                                                                                                                                                                                                                                                                                         record_process/speech.pyc                                                                           0000644 0001750 0001750 00000041704 12262524516 014571  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   �
I��Rc           @   s�   d  d l  Z  d  d l Z d  d l Z d  d l Z d  d l m Z m Z d  d l Z d  d l j	 Z	 d  d l m
 Z
 d  d l Z d  d l Td  d l Z d  d l m Z d  d l m Z d f  d �  �  YZ d S(	   i����N(   t   ceilt   log(   t	   argrelmax(   t   *(   t   lpc(   t   classifyt   Speechc           B   s�   e  Z d  �  Z d �  Z d �  Z d �  Z d �  Z d �  Z d �  Z d �  Z	 d �  Z
 d	 �  Z d
 �  Z d �  Z d d d d � Z d �  Z d �  Z d d � Z RS(   c         C   s�  g  |  _  | |  _ | j d � d k r>| d k sW | d k sW | d k sW | d k rf t d � � n  y t | d � } Wn d | GHt d � � n X| |  _ | |  _ | |  _ | j �  } | d k r� t	 j
 } n0 | d	 k r� t	 j } n | d
 k rt	 j } n  t	 j | d | �|  _ t |  j � |  _ | j �  n | j d � d k r>y t j | d � } Wn d | GHt d � � n X| j �  }	 |	 d
  \ |  _ |  _ |  _ |  _ | j |  j � } |  j d k r�t	 j
 } n6 |  j d	 k r�t	 j } n |  j d
 k rt	 j } n  t	 j | d | �|  _ | j �  n  t t |  j � � }
 |
 GH|
 d k  rpt |  _ n	 t |  _ |
 |  _ |  j d |  _ |  j d |  j |  j |  _ g  |  _ g  |  _ g  |  _ g  |  _ g  |  _  g  |  _! d  S(   Ns   .pcmi����i    t   WrongParametersForPCMt   rs   File %s  can't be foundt   FileNotFoundi   i   i   t   dtypes   .wavi�  g      �?("   t   errort   fileNamet   findt	   Exceptiont   opent	   nchannelst
   sampleRatet   sampleWidtht   readt   npt   int8t   int16t   int32t
   fromstringt   rawDatat   lent   nframest   closet   wavet	   getparamst
   readframest   maxt   abst   Truet   isBlankt   Falset   maxDatat   totalLengtht   speechSegmentt   framet   zcrt   shortTimeEnergyt   volumet   speed(   t   selft   sourceR   R   R   t   littleEndiant   fwR   R
   t   paramsR%   (    (    s	   speech.pyt   __init__   sl    		0					"							c         C   s   d  S(   N(    (   R-   (    (    s	   speech.pyt   __del__K   s    c         C   s   d  S(   N(    (   R-   (    (    s	   speech.pyt   getSingleWordsN   s    c         C   sn   g  |  _  t d d |  j � } xG |  j D]< } t j | � } t j | |  � } |  j  j | | � q* Wd  S(   Ng     @o@i�  (   t   energyBelow250t   intt	   frameSizet   fftFrameAbsR   t   sumt   append(   R-   t   loct   fftFramet   totalEnergyt   below250(    (    s	   speech.pyt   getEnergyBelow250P   s    	c         C   sd   d |  _  d } x' |  j D] } | | d | d } q W| d |  j |  _  |  j  |  j |  _ d  S(   Ni    i   g      �?(   t   speechPercentageR'   t   frameNumR&   t   speechLength(   R-   t   speechFramet   i(    (    s	   speech.pyt   getSpeechPercentageY   s    	c         C   s�  d GHd } |  j  t k r d  S| | k r9 t d � � n  | |  _ | |  _ |  j |  j |  _ t t |  j |  j � � |  _	 g  |  _
 x7t |  j	 � D]&} |  j j |  j | |  j t | |  j | |  j � !� d } t j |  j | | � } |  j j | � |  j j t g  |  j | D] } | d ^ q� � t |  j | |  j | d |  j |  j � }	 |	 d k r|d }	 n  |  j j d t j |	 � � |  j
 j t t |  j | � � � q� Wt t |  j � d	 d
 � }
 t t |  j � d d � } d GH|
 GH| GH| |  _ |
 |  _ |  j GHg  |  _ d } d } d } d } t | |  j |  j � } t | |  j |  j � } d } d G| Gd G| GHx�t |  j	 � D]{} | d k s�| d
 k r+|  j | | k r�| | } d } d } | d
 } d GHq|  j | |
 k rd
 } | d
 } qd } d } q�| d k r�|  j | |
 k r]| d
 } d } q| d
 } | | k  r�| d
 } q| | k  r�d } d } d } d GHqd } | | } |  j j | | f � |  j j | |  j |  j	 | |  j |  j	 f � d GHd } d } d } q�q�W| d k rs|  j j | |  j	 f � |  j j | d |  j |  j	 d |  j f � n  t g  |  j D] } | d
 | d ^ q�� |  _  t! |  j � |  _" d  S(   Nt   getSpeechSegmenti    s   Wrong getFrames parametersi@B i   g      �?g����MbP?i
   i   i   i   s   *****t
   minSilencet   minLent   begt
   endOfNoises   end success(#   R#   R"   R   R7   t   overLapt   stepR6   R    R   RA   t	   absVolumet   rangeR(   R:   R   t   mint   utilsR)   R*   R9   R%   R+   R   R   R!   R    t	   tHoldHight   tHoldLowt   segmentTimeR   R'   R&   t
   speechTimeR   t   totalSeg(   R-   R7   RK   RH   RG   t	   zcrThreadRD   R)   t   kt   calRR   RQ   t   statust   countt
   segmentBegt   silencet
   segmentEndt   v(    (    s	   speech.pyRF   `   s�    			840	'			

	
	

221c         C   s�   g  |  _  g  |  _ x� t t |  j � � D]� } |  j | d k r` |  j | |  j | d } n |  j | d } |  j | |  j | d } |  j  j | � |  j j | � q( Wd  S(   Ni    i��� (   t   ezrt   ezmRN   R   R*   R)   R:   (   R-   RD   R_   R`   (    (    s	   speech.pyt   energyZeroCount�   s    		c         C   s�  d GHd } |  j  t k r d  S| | k r9 t d � � n  | |  _ | |  _ |  j |  j |  _ t t |  j |  j � � |  _	 g  |  _
 xQt |  j	 � D]@} |  j j |  j | |  j t | |  j | |  j � !� t |  j | � d } t j |  j | | � } |  j j | � |  j j t g  |  j | D] } | d ^ q.� � t j |  j | |  j | d |  j |  j � }	 |	 d k r�d }	 n  |  j j d t j |	 � � |  j
 j t j t j |  j | � � � q� Wt t |  j
 � d d	 |  j � }
 t t |  j
 � d
 d
 |  j � } | |  _ |
 |  _ g  |  _ d } d } d } d } t | |  j |  j � } t | |  j |  j � } d } x}t |  j	 � D]l} | d k s�| d k r&|  j
 | | k r�| | } d } d } | d } q	|  j
 | |
 k rd } | d } q	d } d } q�| d k r�|  j
 | |
 k rX| d } d } q	| d } | | k  r{| d } q	| | k  r�d } d } d } q	d } | | } |  j j | | f � |  j j | |  j |  j	 | |  j |  j	 f � d } d } d } q�q�W| d k rd|  j j | |  j	 f � |  j j | d |  j |  j	 d |  j f � n  t g  |  j D] } | d | d ^ qq� |  _  t! |  j � |  _" d  S(   NRF   i    s   Wrong getFrames parametersi   i   g      �?g����MbP?i
   i   i   i   (#   R#   R"   R   R7   RK   RL   R6   R    R   RA   RM   RN   R(   R:   R   RO   R    RP   R)   R*   R9   R   R%   R+   R   R!   RQ   RR   RS   R   R'   R&   RT   R   RU   (   R-   R7   RK   RH   RG   RV   RD   R)   RW   RX   RR   RQ   RY   RZ   R[   R\   R]   R^   (    (    s	   speech.pyt   getSpeechSegmentByAbsVolume�   s�    			843	-##			
	
	
	
221c         C   s4  g  |  _  d } d } t |  j � d k s9 |  j t k r= d  St |  j d � } g  |  _ g  |  _ x�|  j D]�} g  } d } | d } | d } g  }	 x� |  j	 | | !D]� }
 t
 j |
 � } t | d � | | *t j | � } | d k r|  j j d | t
 j |
 � f � n  | j |  j | | | d f � |	 j |  j | � q� W|  j j | � t j | d � d d } t j | d � d d } t |  j | | !� d	 } t j |  j | | !� d
 } | d } d } d } d } g  } d } d } |  j j |	 � d G| Gd G| Gd G| Gd G| Gd G| GHx� t t | � � D]� } | | d | k r�|  j | | | k r�d G| Gd G| GH| d k r�| } d } d } n  | d } qB| d k rB| j | | f � d } d } qBqBW| d k r| j | t | � f � n  |  j  j | � |  j j | � ql Wd  S(   Ni   i    i�  i   s   pitch errori@B g      (@g      8@g�������?i   i   i�  t   ezrLevelt
   volumeHight	   pitchHighRG   RH   s   beg RY   (   t   pitchSegR   R'   R#   R"   R6   R   t   pitcht   tmpR(   RP   t   ACFR!   R   t   argmaxR   R:   R    R_   RM   RN   (   R-   RH   RG   t   pitchThreadt   segTimeRh   t   pitchSumRI   t   endt   curFramePitchR(   Rg   t   pitchMaxRe   t   pitchLowRc   Rd   t	   volumeLowt   zcrHight   zcrLowRY   t   trangeRZ   R\   t   tt   startt   duration(    (    s	   speech.pyt   getFramePitch#  sj    	$		

%"
)+	5c   	      C   s�   d } g  |  _  x� |  j D]� } g  } | d } | d } xm t | | � D]\ } t j |  j | |  j | d � } | d | | *t j | � } | j |  j	 | � qI Wq W|  j  j | � d  S(   Ni
   i    i   (
   t   pitchAdvancedR'   RN   RP   t   advancedACFR(   R   Rj   R:   R   (	   R-   Rq   Rl   Rz   RI   Rn   RD   Rg   Rp   (    (    s	   speech.pyt   getFramePitchAdvanced�  s    	

$c      	   C   s�  d GHt  |  j � d k s) |  j t k r- d  Sg  |  _ g  |  _ g  |  _ g  |  _ x�|  j D]�} t	 | d � \ } } } |  j j
 | � t j | � } g  | D]! } t j | � d k r� | ^ q� } t j g  | D]* } t j t j | � t j | � � ^ q� � } | |  j t j d } g  t t  | � � D] } | | | f ^ q1}	 |	 j �  |  j j
 |	 � g  }
 g  } x� t t  |	 � � D]� } d d |  j d t j t j t j | |	 | d � � } |	 | d d k r�| d k  r�|
 j
 |	 | d � | j
 | � q�q�W|
 j �  |
 d	  }
 |  j j
 |
 � |  j j
 | � q[ Wg  |  _ xJ |  j D]? } t  | � d k r�|  j j
 d � q^|  j j
 | d � q^Wd  S(
   Nt   LPCi    i   i   g      �i   iZ   i�  i   (   R   R'   R#   R"   t   art   fmtt   bwt   frqsR(   t
   talkboxLpcR:   R   t   rootst   imagt   asarrayt   matht   atan2t   realR   t   piRN   t   sortR   R!   t   f1(   R-   R(   R~   t   vart   reflect   rtsR   t   angzRD   R�   R   t	   bandwidtht   kkR�   t   f(    (    s	   speech.pyR}   �  sB    $				.@/
> 

	c      	   C   s�  d GHt  |  j � d k s) |  j t k r- d  Sg  |  _ g  |  _ g  |  _ d g } |  j |  j } xJ t	 d d � D]9 } t
 | d d d | � } | | } | j | � qq Wg  |  _ |  j d d g  |  _ x�|  j d	  D]�} | t j |  j d
 d �} t j j | � |  j d } |  j j | � g  | D] }	 t |	 � ^ q3}
 |  j j |
 � t j d � } d } xv t	 d d � D]e } xN t	 | t t  | � | | d � � D]& } | | t | | � d | | <q�W| | d } q�W|  j j | � t j |
 � } g  | D] } |
 | | f ^ q} | j �  t d t  | � � } g  } x2 t	 | � D]$ } | j | | d d | � q]W|  j j | d	 d � | j �  |  j j | � q� Wd  S(   Nt   freqAnalyzei    i   i   g�(\����?i�  g���(\�:@i   i����t   symi   i   gG�z�G:@(   R   R'   R#   R"   t   shortTimeLinjieVectort   formantR8   R   R7   RN   R6   R:   t   formantValueR<   R(   t   signalt   hammingR   t   fftt   rfftR!   t   zerosRO   RP   t   argLocalMaxR�   (   R-   t   Ft   fsRD   t   mt   nR(   R�   R<   R�   R8   t   gRI   RW   t   g0t   pointsR�   (    (    s	   speech.pyR�   �  sL    $				
		-$#
"
i
   i   i   c         C   s�  d GHt  |  j � d k s) |  j t k r- d  Sd } g  |  _ x�|  j D]�} d } d } | d } | d } t |  j � d }	 t |  j � d }
 t |  j � d } t |  j � d } d } g  } d } d } d } d } x�t | | � D]�} | d k s
| d k r�t | |  j | � } |  j | |	 k rPd } | d } | | } qw|  j | |
 k r�d } | d } | | k r�d } | | } | } d } q�qwd } d } q� | d k r� t | |  j | � } |  j | |
 k r|  j | | d k r| d } d } qw| d } | | k rwd } d } | | d | k re| d } | j	 | | f � n  d } d } qwq� q� W| d k r�| j	 | | f � n  |  j j	 | � |  j
 j	 t  | � d | | d |  j |  j |  j � qF Wd  S(   Nt   getWordsPerSegi    i   i   i   i   g      �?(   R   R'   R#   R"   t   segWordR    R+   R)   RN   R:   R,   R7   RK   R   (   R-   RH   RG   t   preLenRY   t   segR\   t   segBegt   segEndRd   Rr   Rs   Rt   t   wordR�   RZ   t   precountt   crestt   wordBegR(   (    (    s	   speech.pyR�     sn    $	




	*
	

c         C   s�  t  |  j � d k s$ |  j t k r( d  St  |  j � |  _ d |  j GHd |  _ g  |  _ g  |  _ g  |  _ g  |  _	 g  |  _
 g  |  _ g  |  _ g  |  _ g  |  _ g  |  _ g  |  _ g  |  _ g  |  _ d |  _ x�t |  j � D]�} d } d } d } d } d } x�t t  |  j | � � D]s} | t |  j | |  j | | d |  j | | d !� } | |  j | | d |  j | | d } |  j | | d |  j | | d k r�|  j GHn  t t |  j | |  j | | d |  j | | d !� | � } t t |  j | |  j | | d |  j | | d !� | � } | t  |  j | � d k r| t |  j | | d |  j | | � } qqW| d k r�|  j j d � |  j j d � |  j j d � |  j j d � |  j j d � q� n  |  j | |  _ |  j | |  _ |  j j | d | � | d | } |  j j | � |  j j | | � |  j j | � |  j j | � q� W|  j d k r�|  j |  j |  _ n  x�t |  j � D]x} |  j | d } |  j | d }	 t j |  j | |	 !� }
 |  j j |
 � t j |  j  | |	 !� } t j! |  j  | |	 !� } t j |  j" | |	 !� } |  j j | � |  j	 j | � |  j j t j |  j  | |	 !� � |  j j t j |  j  | |	 !� � |  j
 j | � d } xA t | |	 d � D], } | t |  j  | d |  j  | � } q�W|  j j | d |	 | � q�Wg  |  _# x� t |  j � D]� } |  j | |  j | |  j | |  j | |  j | |  j | |  j	 | |  j | |  j | |  j | g
 } |  j# j | � qLWd  S(   Ni    s!   We have %d speech segments in alli�  i   g      �?($   R   R'   R#   R"   t   numt   pitchAveraget   pitchAveragePerSegt
   pitchRanget   volumeAveraget	   volumeStdt
   fmtAverageRp   t   pitchMint   pitchStdt	   volumeMaxt	   volumeMint
   volumeDifft	   pitchDiffR>   t   pitchNumRN   Rf   R9   Rg   R   R    RO   R!   R:   R   t   averageR5   RM   t   stdR�   t   features(   R-   RD   Rm   R�   Rp   R�   R�   RW   RI   Rn   R>   R+   R�   R�   R�   R�   (    (    s	   speech.pyt   dataProcessQ  s�    $															 <,*AA5##* 	jc         C   s�  d |  _  d |  _ d } |  j t k r3 d |  _ n{ |  j t d d � k rW d |  _  n |  j d k rr d |  _  n  |  j | d	 � t | | | � |  _ d
 | } t	 j
 | � t | d � } t |  j � d k r� |  j d d k r� d |  _ qEd |  _ nH x* |  j D] } | d k rd |  _ PqqW|  j d k rEd |  _ n  t j |  j � |  _ | j d |  j |  j |  j f � | j d � | j d |  j |  j |  j t j |  j � |  j  |  j f � | j �  d  S(   Nt   Unknowni����t   predict_datas	   全静音id   i�   s   男s   女t   0s   rm %st   awi   i    s   单交互正常挂机s   单交互异常挂机s   多交互异常挂机s#   File:		%s
Category:		%s
Label:		%s
sw   总时长        通话时长        通话段数        通话人音量        通话人性别        通话人语调
s'   %-15.2f%-15.2f%-15f%-18.2f%-16s%-20.2f
(   t   gendert   categoryR#   R"   R�   RN   t   writeToFileR   t   labelst   ost   systemR   R   R   R�   t   labelt   writeR   R&   RB   R�   R�   R   (   R-   t   scale_modelt
   model_filet
   label_fileR�   t   cmdR�   R�   (    (    s	   speech.pyt   predict�  s:    		
	#>R�   c         C   s   t  | d � } d } |  j t k r8 | j d d � n� x� t |  j � D]� } | d } | j d | d |  j | d |  j | d |  j | d |  j	 | d	 |  j
 | d
 |  j | d |  j | d |  j | d |  j | d |  j | f � qH W| j �  d  S(   NR�   i   s?   %s %d:%f %d:%f %d:%f %d:%f %d:%f %d:%f %d:%f %d:%f %d:%f %d:%f
R�   i    i   i   i   i   i   i   i   i	   i
   (   R�   i   i    i   i    i   i    i   i    i   i    i   i    i   i    i   i    i	   i    i
   i    (   R   R#   R"   R�   RN   R�   Rp   R�   R�   R�   R�   R�   R�   R�   R�   R>   R   (   R-   t   dataFileR�   R�   t   cntRD   (    (    s	   speech.pyR�   �  s    
�(   t   __name__t
   __module__R2   R3   R4   R?   RE   RF   Ra   Rb   Ry   R|   R}   R�   R�   R�   R�   R�   (    (    (    s	   speech.pyR      s    	:						]		Z	z		+	6E	Z	.(   R�   R�   R   t   numpyR   R    R   RP   t   scipy.signalR�   R   t   scipyt	   audiolazyt   pylabt   plt   scikits.talkboxR   R�   t   mood_svmR   R   (    (    (    s	   speech.pyt   <module>   s"   
� � � 9                                                            record_process/svm-scale                                                                            0000755 0001750 0001750 00000041145 12261743211 014416  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   ELF              ��4   �1      4   	 (      4   4�4�               T  T�T�                    � ��  �           /  ���  �           /  ���   �            h  h�h�D   D         P�td�  ННL   L         Q�td                          R�td/  ���   �         /lib/ld-linux.so.2           GNU                       GNU �kze������y����ǰ(                       �K��                �              �              c              ~              O              �              G              �              :              �               '              �              �              ,              i              ?              V              ]                            2              �              p              �                 �      libc.so.6 _IO_stdin_used __printf_chk exit fopen strrchr puts putchar realloc rewind strtod fgetc fgets ungetc __fprintf_chk fclose malloc __ctype_b_loc sscanf stderr fscanf fwrite __libc_start_main free __gmon_start__ GLIBC_2.3 GLIBC_2.3.4 GLIBC_2.1 GLIBC_2.0                                        ii   �      ti	   �      ii   �      ii   �       ��  ��
  �  �  �  �  �   �  $�  (�	  ,�
  0�  4�  8�  <�  @�  D�  H�  L�  P�  T�  X�  \�  `�  S���  ��S*  ��������t�   ��[�         �5��%�    �%�h    ������%�h   ������%�h   ������%�h   �����%�h    �����% �h(   �����%$�h0   �����%(�h8   �p����%,�h@   �`����%0�hH   �P����%4�hP   �@����%8�hX   �0����%<�h`   � ����%@�hh   �����%D�hp   � ����%H�hx   ������%L�h�   ������%P�h�   ������%T�h�   ������%X�h�   �����%\�h�   �����%`�h�   ����U��WVS�����p�o  �ï(  �}�  �E�   �D$4    �D$0    �@�8-���   �D$(���   �D$,��   �}��   @��    ���V�@��l<�>  �������������D$    �T�A�D$H�$��������   �D$H��D$    �D�V�T$L�$��������   �T$L����   �    �r9u~���8-�b����D$,� �D$(� ��������  ���   � ��t���   � ���   � ��������  �|$4�D$0���D$$���D$#��  �F;Et��  �E�<�������t$��$��������D$<��  ���   � �$�g������   �|$$ ����   �     ���   �    ��  �D$4�t$�$�������D$8��  �$������y�	  �|$8��-����<$�}  �<$�u  �D$h������   �D$h9M��D$8�|$�t$�$������t֋D$8�$�������   ��D$<�$�$  ����  ���   �0�����D$D� �
��&    ����DP u�v ����DP t�D$X�D$H��9����D$L��D$H�4$�D$�D$L�D$������u����   �D$X���   �9�MЉ���   9N��>:t���>:u��T$D�N�F����Dr ��t��&    ������DJ u���u�f��DB �v u
�����u��\����D$    �D�T$L�$�$����D$,�T$L��k����D�D$0�^����D�D$4�Q����D$    �D�T$L�$������D$(�T$L��*����������T$L� �D$   �D$   �D$������$������a  �T$L��������   � ���	  �D$<�$�������   ��y��    �$�L$H�T$L������T$L�ƍ��   �0�$�������   ����B	  ���:	  �L$H1҅�x݃������݃�����Ѓ�9�u��؋D$<�$��
  ����  ���   �0�D$`�D$��a����D$�4$������x   � �D$`���������p   � ��������������D$@��	��    ����DB u�v ����DB t�D$h�   �D$D�D$X�D$H��^����D$L�t& �D$D�4$�D$�D$H�D$�D$L�D$�x�������   ���   �T$X����   9׋ }(�t& ����������������������9�u��؍<�    ���D$h����������� �D$h��������>:t	����>:u��L$@�~�F�	���Dq ��t��&    ������Dy u���u�f��DA u
�����u�z�������   �9��P������   �������   � f�����������������������9�u��؋D$<�$�	  �������D$<�$�?����|$$ tF�D$8�$�������y��  �L$8�$�L$�����D$8�$�������x�}  �D$8�$������|$# ��  ��q����D$�D$0�$�a��������I  ���   ��y������tz��[����t$�D$   �D$   �$�������   � ���   �\$� �\$�|$�D$   �4$�w�����x   � ��p   �\$� �\$�|$�D$   �4$�K�����s����t$�D$   �D$   �$�)����D$,� �D$(�\$� �\$�|$�   �D$   �4$��������   ��v�������fu+���؃�9�Y���   � �����   � ������{�������\$�|$�\$���L$�D$   �4$�L$L�������   �L$L�9�~����   �����  �4$�J�����a����D$8�D$<�$��  ���  ���   �0�D$`�D$�D$8�4$�D$�����D$`�$�  �+����D$@���v ����DB u�v ����DB t�D$h�   �D$D�D$X�D$H��^����D$L�t& �D$D�4$�D$�D$H�D$�D$L�D$��������   �D$X9�} ��&    ��<$�\$���  �D$X9���D$h�\$�$�  �>:t
f����>:u��T$@�N�F����Dr ��t��&    ������DJ u���u�f��DB �v u
�����u�D$X�x�8�����<$�\$���'  ���   98}��$
   �����D$<�$�u  ����������   ����   � 9�~*�D$�������D$�������T$�D$   � �$�������   � �$�?������   � �$�/������   � �$�����D$<�$�3����e�1�[^_]��D$8    �������   ��h����|$8�t$�D$���   �<$�D$�r�����x   �t$�<$�D$��p   �D$�R������   �    �����|$8�<$�u  �<$�m  �<$�e  ������D$0�D$   �D$��4����D$������� �$���������D$,�   �D$�D$(�D$��h����D$�D$8�$������E�M�D���D$L�D$h�D$$�D$`�D$@�D$\�D$D��e����D$H�D$$�D$�D$@�D$�D$D�D$�D$H�D$�D$8�$�j�������   ���   �4�    �L$\����   9ϋ |�pu����9�}d�2�0������{�D$4���D$�D$L� �|$���D$   �D$�������D$������� �$�������   �L$\����   9ϋ |��D$`�y���D$h���$������   �9��<����4�    �u,����9��#������   ����   �2� �0������{ҋD$4�D$�D$L� �|$�D$   �D$�������D$������� �$��������   �뒉D$�������D$�������D$   � �$������������   �   �D$4    �D$0    �D$(���   �D$,�����D$4�D$������D$�������D$   � �$�N����$   ����������� �D$   �D$   �D$��@����$�����$   �\���������� �D$'   �D$   �D$��@����$������$   �&����|$$ �A���������� �D$$   �D$   �D$��h����$�����$   �����������D$0����1�^����PTRhЙh`�QVh@�������f���$�f�f�f�f�f�f����-����wø    ��t�U����$�����Í�    ���-�����������uú    ��t�U����D$�$�����É���'    �=�� uU����|���������f�����t�    ��tU����$�����y�����s���f��S�*�����j  ���������$�����$   ������&    UWVS�������7  ���D$0�D$���   ���   ��D$��$���������   f��/�D$
   �,$�������ur��,$��D$���������)����������!� ��t������  DՍiD� ҋT$0��)��T$�)���T$�$�x�����u����[^_]�f�����[^_]Í�&    ��'    S������Z  ���D$ ���   � ��t<��p   � ����{S��x   � ����{U���   � ���   ���(��������������������\$�D$�$   �������[Í�    u����؍��   � ��u������؍��   � 빍�&    ��'    S�j����ê  ��(�D$0�D$4���   ����   ���������   �����t& ����{b�����    ������   ��   �����؍��   ���������{J�D$�� ����\$�D$�$   �
������   � ��([Ít& u������؍��   ���������z�u��؃�([Ð�t& �j��������؃�([Í�&    ���   ����   ���*���������������f�f�f�UW1�VS�U����Õ  ���l$0������!��������)�����t'��    �D$8�,$�D$�D$4�D$��������9�u߃�[^_]�����������������  S���������#  ��[�     Usage: svm-scale [options] data_filename
options:
-l lower : x scaling lower limit (default -1)
-u upper : x scaling upper limit (default +1)
-y y_lower y_upper : y scaling limits (default: no y scaling)
-s save_filename : save scaling parameters to save_filename
-r restore_filename : restore scaling parameters from restore_filename  inconsistent lower/upper specification
 cannot use -r and -s simultaneously
    WARNING: minimal feature index is %d, but indices should start from 1
  WARNING: feature index %d appeared in file %s was not seen in the scaling factor file %s.
  WARNING: scaling factors with indices smaller than 1 are not stored to the file %s.
    WARNING: original #nonzeros %ld
         new      #nonzeros %ld
Use -l 0 if many original feature values are zeros
 %d:%g  unknown option
 r can't open file %s
 %d %*f %*f
 %d:%*f can't allocate enough memory
 %d:%lf %d %lf %lf
 w x
 %d %.16g %.16g
   �����������������������������������������������������������������������;H       ���d   p���T  �����   �����   �����   ����  �����   ����         zR |�         ����p   FJtx ?;*2$"   @   0���)    A�N    P   \   D����    A�A�A�A�N0�
A�A�A�A�CCC�A�A�A�      �   �����    A�N i
A�G4   �   \���
   A�N0�
A�Ea
A�FO
A�H,     ���[   A�BI����

�A�A�A�A8   <  ���a    A�A�C�A�N0HA�A�A�A�   x  8���                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       `�@�             ��   ԙ   �         �      ���o��   \�   ́
                      �   �            �   �            ���o�����o   ���ob�                                                        �        �����&�6�F�V�f�v���������Ɔֆ�����&�6�            ���������������      �?      �   GCC: (Ubuntu/Linaro 4.8.1-10ubuntu8) 4.8.1 GCC: (Ubuntu/Linaro 4.7.3-7ubuntu3) 4.7.3  .symtab .strtab .shstrtab .interp .note.ABI-tag .note.gnu.build-id .gnu.hash .dynsym .dynstr .gnu.version .gnu.version_r .rel.dyn .rel.plt .init .text .fini .rodata .eh_frame_hdr .eh_frame .init_array .fini_array .jcr .dynamic .got .got.plt .data .bss .comment                                                   T�T                    #         h�h                     1         ���  $                  D   ���o   ���                   N         ́�  �              V         \�\                   ^   ���o   b�b  2                k   ���o   ���  P                z   	      ��                  �   	      ��  �               �         ���  #                  �         Ѕ�  p                �         @�@  �                 �         ԙ�                    �         ��  �                 �         Н�  L                  �         �  �                 �         �/                    �         �/                    �         �/                    �         �/  �                �         ���/                   �          � 0  d                 �         h�h0  ,                  �         ���0  <                  �      0       �0  U                               �0                                 �6        3         	              �=  �                                     T�          h�          ��          ��          ́          \�          b�          ��          �     	     �     
     ��          Ѕ          @�          ԙ          �          Н          �          �          �          �          �          ��           �          h�          ��                                ��   ��          Պ          Ȋ          ��       !   ��       &   ̇       +            ��6   �      C   Е      X    �      k   @�      �   ��     �   �      �   `�      �   �      +            ���   ��      �   �                   ���   �         �        �       )   �      ?  Й     O              k  ��    �  h�       �             �             �  p�     �             �  ��      �             �  ���     �  ��     �  ԙ        x�     	               ��)     /  ��     <             N  P�
    Z             m               h�      �  ��     �             �  Ȱ     �              �             �  l�     �  �     �             �               ��     ,  `�a     <  ��     F             W             i             |  ԰      �  ��      �  �     �             �             �  ��      �  @�[    �  ��     �             �             �                             а     !  ��     +  ��     7  ��     C             ^  ���     t              �  ��     �  ��     �  ��     �  ��      �              svm-scale.c .L53 .L54 .L56 .L57 .L58 .L59 crtstuff.c __JCR_LIST__ deregister_tm_clones register_tm_clones __do_global_dtors_aux completed.6608 __do_global_dtors_aux_fini_array_entry frame_dummy __frame_dummy_init_array_entry __FRAME_END__ __JCR_END__ __init_array_end _DYNAMIC __init_array_start _GLOBAL_OFFSET_TABLE_ __libc_csu_fini _ITM_deregisterTMCloneTable __x86.get_pc_thunk.bx data_start stderr@@GLIBC_2.0 free@@GLIBC_2.0 y_min fgets@@GLIBC_2.0 _edata fclose@@GLIBC_2.1 _Z13output_targetd feature_min _fini y_max rewind@@GLIBC_2.0 _Z14exit_with_helpv num_nonzeros fwrite@@GLIBC_2.0 _Z6outputid realloc@@GLIBC_2.0 malloc@@GLIBC_2.0 __data_start max_line_len puts@@GLIBC_2.0 y_lower __gmon_start__ exit@@GLIBC_2.0 __dso_handle _IO_stdin_used fscanf@@GLIBC_2.0 __libc_start_main@@GLIBC_2.0 new_num_nonzeros __libc_csu_init y_scaling fopen@@GLIBC_2.1 ungetc@@GLIBC_2.0 putchar@@GLIBC_2.0 _end _start _fp_hw strtod@@GLIBC_2.0 fgetc@@GLIBC_2.0 __bss_start main upper __printf_chk@@GLIBC_2.3.4 strrchr@@GLIBC_2.0 sscanf@@GLIBC_2.0 _Jv_RegisterClasses line max_index feature_max __TMC_END__ __fprintf_chk@@GLIBC_2.3.4 _Z8readlineP8_IO_FILE _ITM_registerTMCloneTable min_index y_upper lower _init __ctype_b_loc@@GLIBC_2.3                                                                                                                                                                                                                                                                                                                                                                                                                            record_process/utils.py                                                                             0000644 0001750 0001750 00000013633 12261500557 014315  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   import math
import numpy as np
import pylab as pl 
from spectrogram import spectrogram
def plotVolume(m):
    pl.subplot([m.volume,m.absVolume,m.shortTimeEnergy])
def plotPitch(m):
    pitch = []
    pitchValue = []
    end = 0
    for index,r in enumerate(m.speechSegment):
        pitch = pitch + [0]*(r[0]-end) + m.pitch[index]
        pitchValue = pitchValue + [0]*(r[0]-end) + [t[1] for t in m.tmp[index]]
        end = r[1]
    pitch = pitch + [0]*(m.frameNum-m.speechSegment[-1][1])
    pitchValue = pitchValue + [0]*(m.frameNum-m.speechSegment[-1][1])
    pl.subplot(511)
    pl.ylabel('pitch')
    pl.plot(pitch)
    for index,s in enumerate(m.pitchSeg):
        for p in s:
            pl.plot([p[0]+m.speechSegment[index][0],p[0]+m.speechSegment[index][0]],[0,500],color='red')
            pl.plot([p[1]+m.speechSegment[index][0],p[1]+m.speechSegment[index][0]],[0,500],color='green')
    pl.subplot(512)
    for index,s in enumerate(m.pitchSeg):
        for p in s:
            pl.plot([p[0]+m.speechSegment[index][0],p[0]+m.speechSegment[index][0]],[0,max(pitchValue)],color='red')
            pl.plot([p[1]+m.speechSegment[index][0],p[1]+m.speechSegment[index][0]],[0,max(pitchValue)],color='green')
    pl.ylabel('value')
    pl.plot(pitchValue)
    pl.subplot(513)
    for index,s in enumerate(m.pitchSeg):
        for p in s:
            pl.plot([p[0]+m.speechSegment[index][0],p[0]+m.speechSegment[index][0]],[0,max(m.zcr)],color='red')
            pl.plot([p[1]+m.speechSegment[index][0],p[1]+m.speechSegment[index][0]],[0,max(m.zcr)],color='green')
    pl.ylabel('zcr')
    pl.plot(m.zcr)
    pl.subplot(514)
    for index,s in enumerate(m.pitchSeg):
        for p in s:
            pl.plot([p[0]+m.speechSegment[index][0],p[0]+m.speechSegment[index][0]],[0,1],color='red')
            pl.plot([p[1]+m.speechSegment[index][0],p[1]+m.speechSegment[index][0]],[0,1],color='green')
    pl.ylabel('volume')
    pl.plot(m.absVolume/max(m.absVolume))
    pl.subplot(515)
    for index,s in enumerate(m.pitchSeg):
        for p in s:
            pl.plot([p[0]+m.speechSegment[index][0],p[0]+m.speechSegment[index][0]],[0,max(m.ezr)],color='red')
            pl.plot([p[1]+m.speechSegment[index][0],p[1]+m.speechSegment[index][0]],[0,max(m.ezr)],color='green')
    pl.ylabel('ezr')
    pl.plot(m.ezr)
    pl.show()

def plot(m):
    pl.plot(m)
    pl.show()
def subplot(m):
    n = len(m)
    n = n*100+10+1
    for k in m:
        pl.subplot(n)
        pl.plot(k)
        n = n+1
    pl.show()
def plotAll(m):
    pitch = []
    end = 0
    for index,r in enumerate(m.speechSegment):
        pitch = pitch + [0]*(r[0]-end) + m.pitch[index]
        end = r[1]
    pitch = pitch + [0]*(m.frameNum-m.speechSegment[-1][1])
    pl.subplot(611)
    pl.plot(m.absVolume)
    #pl.xlabel('Frame Num')
    pl.ylabel('Volume')
    #pl.grid(True)
    for s in m.speechSegment:
        pl.plot([s[0],s[0]],[0,max(m.absVolume)],color='red')
        pl.plot([s[1],s[1]],[0,max(m.absVolume)],color='green')
        
    pl.subplot(612)
    pl.plot(m.zcr)
    pl.ylabel('Zero Cross Rate')
    #pl.xlabel('Frame Num')
    pl.subplot(613)
    pl.plot(pitch)
    #pl.xlabel('Frame Num')
    pl.ylabel('Pitch')
    for index,s in enumerate(m.pitchSeg):
        for p in s:
            pl.plot([p[0]+m.speechSegment[index][0],p[0]+m.speechSegment[index][0]],[0,500],color='red')
            pl.plot([p[1]+m.speechSegment[index][0],p[1]+m.speechSegment[index][0]],[0,500],color='green')
    pl.subplot(614)
    
    
    pl.plot(m.f1)
    pl.ylabel('Formant 1')
    pl.subplot(615)
    spectrogram(m)
    pl.ylabel("spectrogram")
    pl.xlabel('Frame Num')
    pl.subplot(616)
    pl.ylabel("Energy Below 250Hz")
    pl.plot(m.energyBelow250)
    pl.show()

# method 1: absSum
def calVolume(waveData, frameSize, overLap):
    wlen = len(waveData)
    step = frameSize - overLap
    frameNum = int(math.ceil(wlen*1.0/step))
    volume = np.zeros((frameNum,1))
    for i in range(frameNum):
        curFrame = waveData[np.arange(i*step,min(i*step+frameSize,wlen))]
        curFrame = curFrame - np.median(curFrame) # zero-justified
        volume[i] = np.sum(np.abs(curFrame))
    return volume

# method 2: 10 times log10 of square sum
def calVolumeDB(waveData, frameSize, overLap):
    wlen = len(waveData)
    step = frameSize - overLap
    frameNum = int(math.ceil(wlen*1.0/step))
    volume = np.zeros((frameNum,1))
    for i in range(frameNum):
        curFrame = waveData[np.arange(i*step,min(i*step+frameSize,wlen))]
        curFrame = curFrame - np.mean(curFrame) # zero-justified
        volume[i] = 10*np.log10(np.sum(curFrame*curFrame))
    return volume

def argLocalMax(R):
    result = []
    for r in range(1,len(R)-1):
        if(R[r-1]<R[r] and R[r]>R[r+1]):
            result.append(r)
    return result

# Auto-Correlation Function
def ACF(frame):
    flen = len(frame)
    acf = np.zeros(flen)
    for i in range(flen):
    	try:
        	acf[i] = np.dot(frame[i:flen],frame[0:flen-i])
        except:
        	print frame[i:flen]
        	print i,flen
        	raise Exception('Error')

    return acf

def zcr(frame,zcrThread):
    n = len(frame)
    cnt = 0
    for i in range(n-1):
        if ((np.sign(frame[i])*np.sign(frame[i+1])<0) and (abs(frame[i]-frame[i+1])>zcrThread)):
            cnt = cnt+1
    return cnt

def advancedACF(frame1,frame2):
    if len(frame1)!=len(frame2):
        return
    frame = frame1+frame2
    flen = len(frame1)
    acf = np.zeros(flen)
    if len(frame1)!=len(frame2):
        return -1
    for k in range(flen/2):
        acf[k] = np.dot(frame[:flen],frame[k:flen+k])
    return acf

# average magnitude difference function
def AMDF(frame):
	flen = len(frame)
	amdf = np.zeros(flen)
	for i in range(flen):
		amdf[i] = np.sum(abs(frame[i:flen]-frame[0:flen-i]))

def complexGreater(a,b):
    return abs(a)**2>abs(b)**2

def isPositive(frame):
    trans = []
    for i in frame:
        if i>=0:
            trans.append(1)
        else:
            trans.append(-1)
    return np.array(trans)                                                                                                     record_process/utils.pyc                                                                            0000644 0001750 0001750 00000015371 12261500562 014455  0                                                                                                    ustar   will                            will                                                                                                                                                                                                                   �
o��Rc           @   s�   d  d l  Z  d  d l Z d  d l Z d  d l m Z d �  Z d �  Z d �  Z d �  Z	 d �  Z
 d �  Z d	 �  Z d
 �  Z d �  Z d �  Z d �  Z d �  Z d �  Z d �  Z d S(   i����N(   t   spectrogramc         C   s#   t  j |  j |  j |  j g � d  S(   N(   t   plt   subplott   volumet	   absVolumet   shortTimeEnergy(   t   m(    (    s   utils.pyt
   plotVolume   s    c   	      C   s�  g  } g  } d } x� t  |  j � D]u \ } } | d g | d | |  j | } | d g | d | g  |  j | D] } | d ^ qv } | d } q" W| d g |  j |  j d d } | d g |  j |  j d d } t j d � t j d � t j | � x� t  |  j	 � D]� \ } } x� | D]� } t j | d |  j | d | d |  j | d g d d g d d �t j | d |  j | d | d |  j | d g d d g d d	 �q+WqWt j d
 � x� t  |  j	 � D]� \ } } x� | D]� } t j | d |  j | d | d |  j | d g d t
 | � g d d �t j | d |  j | d | d |  j | d g d t
 | � g d d	 �q�Wq�Wt j d � t j | � t j d � x� t  |  j	 � D]� \ } } x� | D]� } t j | d |  j | d | d |  j | d g d t
 |  j � g d d �t j | d |  j | d | d |  j | d g d t
 |  j � g d d	 �q�Wq�Wt j d � t j |  j � t j d � x� t  |  j	 � D]� \ } } x� | D]� } t j | d |  j | d | d |  j | d g d d g d d �t j | d |  j | d | d |  j | d g d d g d d	 �q�Wq�Wt j d � t j |  j t
 |  j � � t j d � x� t  |  j	 � D]� \ } } x� | D]� } t j | d |  j | d | d |  j | d g d t
 |  j � g d d �t j | d |  j | d | d |  j | d g d t
 |  j � g d d	 �q�Wq�Wt j d � t j |  j � t j �  d  S(   Ni    i   i����i�  t   pitchi�  t   colort   redt   greeni   t   valuei  t   zcri  R   i  t   ezr(   t	   enumeratet   speechSegmentR   t   tmpt   frameNumR   R   t   ylabelt   plott   pitchSegt   maxR   R   R   t   show(	   R   R   t
   pitchValuet   endt   indext   rt   tt   st   p(    (    s   utils.pyt	   plotPitch   sZ    $;##HPNVQYHPQYc         C   s   t  j |  � t  j �  d  S(   N(   R   R   R   (   R   (    (    s   utils.pyR   6   s    c         C   sa   t  |  � } | d d d } x2 |  D]* } t j | � t j | � | d } q% Wt j �  d  S(   Nid   i
   i   (   t   lenR   R   R   R   (   R   t   nt   k(    (    s   utils.pyR   9   s    c         C   s�  g  } d } xK t  |  j � D]: \ } } | d g | d | |  j | } | d } q W| d g |  j |  j d d } t j d � t j |  j � t j d � xw |  j D]l } t j | d | d g d t	 |  j � g d d �t j | d | d g d t	 |  j � g d d �q� Wt j d	 � t j |  j
 � t j d
 � t j d � t j | � t j d � x� t  |  j � D]� \ } } x� | D]� } t j | d |  j | d | d |  j | d g d d g d d �t j | d |  j | d | d |  j | d g d d g d d �q�Wq�Wt j d � t j |  j � t j d � t j d � t |  � t j d � t j d � t j d � t j d � t j |  j � t j �  d  S(   Ni    i   i����ic  t   VolumeR	   R
   R   id  s   Zero Cross Rateie  t   Pitchi�  if  s	   Formant 1ig  R    s	   Frame Numih  s   Energy Below 250Hz(   R   R   R   R   R   R   R   R   R   R   R   R   t   f1R    t   xlabelt   energyBelow250R   (   R   R   R   R   R   R   R   (    (    s   utils.pyt   plotAllA   sB    $#37HP
c   	      C   s�   t  |  � } | | } t t j | d | � � } t j | d f � } xn t | � D]` } |  t j | | t | | | | � � } | t j	 | � } t j
 t j | � � | | <qU W| S(   Ng      �?i   (   R    t   intt   matht   ceilt   npt   zerost   ranget   aranget   mint   mediant   sumt   abs(	   t   waveDatat	   frameSizet   overLapt   wlent   stepR   R   t   it   curFrame(    (    s   utils.pyt	   calVolumel   s    
+ c   	      C   s�   t  |  � } | | } t t j | d | � � } t j | d f � } xv t | � D]h } |  t j | | t | | | | � � } | t j	 | � } d t j
 t j | | � � | | <qU W| S(   Ng      �?i   i
   (   R    R)   R*   R+   R,   R-   R.   R/   R0   t   meant   log10R2   (	   R4   R5   R6   R7   R8   R   R   R9   R:   (    (    s   utils.pyt   calVolumeDBx   s    
+(c         C   sn   g  } xa t  d t |  � d � D]F } |  | d |  | k  r  |  | |  | d k r  | j | � q  q  W| S(   Ni   (   R.   R    t   append(   t   Rt   resultR   (    (    s   utils.pyt   argLocalMax�   s
     0c         C   s�   t  |  � } t j | � } xk t | � D]] } y, t j |  | | !|  d | | !� | | <Wq( |  | | !GH| G| GHt d � � q( Xq( W| S(   Ni    t   Error(   R    R,   R-   R.   t   dott	   Exception(   t   framet   flent   acfR9   (    (    s   utils.pyt   ACF�   s    ,	c         C   s�   t  |  � } d } xu t | d � D]c } t j |  | � t j |  | d � d k  r# t |  | |  | d � | k r# | d } q# q# W| S(   Ni    i   (   R    R.   R,   t   signR3   (   RF   t	   zcrThreadR!   t   cntR9   (    (    s   utils.pyR   �   s    Pc         C   s�   t  |  � t  | � k r d  S|  | } t  |  � } t j | � } t  |  � t  | � k r] d Sx= t | d � D]+ } t j | |  | | | | !� | | <qn W| S(   Ni����i   (   R    R,   R-   R.   RD   (   t   frame1t   frame2RF   RG   RH   R"   (    (    s   utils.pyt   advancedACF�   s    
)c         C   se   t  |  � } t j | � } xC t | � D]5 } t j t |  | | !|  d | | !� � | | <q( Wd  S(   Ni    (   R    R,   R-   R.   R2   R3   (   RF   RG   t   amdfR9   (    (    s   utils.pyt   AMDF�   s    c         C   s   t  |  � d t  | � d k S(   Ni   (   R3   (   t   at   b(    (    s   utils.pyt   complexGreater�   s    c         C   sM   g  } x7 |  D]/ } | d k r/ | j  d � q | j  d � q Wt j | � S(   Ni    i   i����(   R?   R,   t   array(   RF   t   transR9   (    (    s   utils.pyt
   isPositive�   s    (   R*   t   numpyR,   t   pylabR   R    R   R   R   R   R(   R;   R>   RB   RI   R   RO   RQ   RT   RW   (    (    (    s   utils.pyt   <module>   s"   		/			+								                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       