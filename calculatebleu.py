__author__ = 'namithags'
import json
import time
start_time = time.time()
import codecs
import sys, math
import re
import os
import itertools
import string
import difflib

#Input candidate file
#candfilename = 'example/example1-C1.txt'
#candfilename = 'candidate-4.txt'
candfilename = sys.argv[1]

#Reference file
#reffilename = 'example/1'
#reffilename = 'e4'
reffilename  = sys.argv[2]

#output file
outputfilename = open('bleu_out.txt',"w")

def lengthoftextbestmatch(sentencelistcandidate,sentencelistreference):
    r =0.0
    for c_i in range(0,len(sentencelistcandidate)):
        cansentence_len = len(sentencelistcandidate[c_i].split(" "))
        min=1000000
        minlen=0
        for key,value in sentencelistreference.items():
            diff = abs(len(value[c_i].split(" "))- cansentence_len)
            if(diff<min):
                min=diff
                minlen=len(value[c_i].split(" "))
        r+=minlen
    return r

#get length of text (candidate translation and corpus)
def lengthoftext(list1):
    sum = 0
    if type(list1) is list:
        for eachsentece in list1:
            sum += len(eachsentece.split(" "))
    else:
        for key, value in list1.items():
            for eachsentece1 in value:
                sum += len(eachsentece1.split(" "))
    return sum


#compute brevity penality from r and c

def computebrevitypenalty(r,c):
    bp = 0.0
    if ( c > r):
        bp = 1
    else:
        bp = math.exp(float((1-float(r/c))))
    return bp

#strip punctuation
def strippunc(aa):
    exclude = set(string.punctuation)
    ss = []
    for eachtext in aa:
        ss.append( ' '.join(ch for ch in eachtext.split() if ch not in exclude))
    return ss

#get all sentences by punctuation in a list
def getsentencescand(filename):
    sentences = []
    splitregex = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
    candfp = codecs.open(filename,"r",encoding='utf-8')
    allsentences = candfp.readlines()
    for eachsentence in allsentences:
        eachsentence=eachsentence.strip()
        eachsentence = eachsentence.replace('  ',' ')
        ##eachsentence = strippunc(eachsentence.split(" "))
        eachsentence = eachsentence.split(" ")
        sentences.append(' '.join(eachsentence))
    candfp.close()
    return sentences


#get all sentences by punctuation in a list
def getsentencesref(filename):
    numberoffiles = 0
    sentences1={}
    splitregex = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s'
    if os.path.isdir(filename):
        for dirpath, dirnames, filenames in os.walk(filename):
            for eachfile in filenames:
                sentences = []
                myfile = os.path.join(dirpath, eachfile)
                candfp1 = codecs.open(myfile,"rb",encoding='utf-8')
                allsentences = candfp1.readlines()
                for eachsentence in allsentences:
                    eachsentence=eachsentence.strip()
                    eachsentence = eachsentence.replace('  ',' ')
                    ##eachsentence = strippunc(eachsentence.split(" "))
                    eachsentence = eachsentence.split(" ")
                    sentences.append(' '.join(eachsentence))
                sentences1[numberoffiles] = sentences
                numberoffiles+=1
                candfp1.close()
    else:
        sentences = []
        numberoffiles =1
        candfp = codecs.open(filename,"rb",encoding='utf-8')
        allsentences = candfp.readlines()
        for eachsentence in allsentences:
            eachsentence=eachsentence.strip()
            eachsentence = eachsentence.replace('  ',' ')
            #eachsentence = strippunc(eachsentence.split(" "))
            eachsentence = eachsentence.split(" ")
            sentences.append(' '.join(eachsentence))
            candfp.close()
            sentences1[numberoffiles] = sentences
    return sentences1,numberoffiles

#get sll n grams in a sentence
def getallngrams(eachsentence,N):
    eachsentencelist = eachsentence.split()
    if (N ==1):
        aa = eachsentencelist
    else:
        aa = zip(*[eachsentencelist[i:] for i in range(N)])
    return aa

def getallngramsref(sentencelistreference,linenumber,N):
    allngrames = []
    for key,value in sentencelistreference.items():
        eachsentence = sentencelistreference[key][linenumber]
        aa = getallngrams(eachsentence,N)
        allngrames.append(aa)
    return allngrames

#de-duplicate a list
def dedup(seq):
    seen = set()
    seen_add = seen.add
    return [x for x in seq if not (x in seen or seen_add(x))]

def countinngram(ngramsreference,eachngram):
    maxno = 0
    for eachref in ngramsreference:
        max = eachref.count(eachngram)
        if (maxno<max):
            maxno = max
    return maxno
#caluclate n gram precisions upto  length n
def ngramprecision(sentencelistcandidate, sentencelistreference , N):
    pn={}
    for i in range(0,N):
        pntotaleachcandnum =[]
        pntotaleachcandden =[]

        #reftext = " ".join(sentencelistreference)   ## considering entire text as a sentence
        linenumber = 0
        for eachcandsentence in sentencelistcandidate:
            ngramscandidate = getallngrams(eachcandsentence,(i+1))
            ngramsreference = getallngramsref(sentencelistreference,linenumber,(i+1))
            linenumber+=1
            if len(ngramscandidate)!=0 or len(ngramsreference)!=0:
                count = []
                countclip =[]
                ngramscandidate_dedup = dedup(ngramscandidate)
                for eachngram in ngramscandidate_dedup:
                    maxrefcount = countinngram(ngramsreference,eachngram)
                    count1 = ngramscandidate.count(eachngram)
                    count.append(count1)
                    countclip.append(min(count1, maxrefcount))

                pntotaleachcandnum.append(float((sum(countclip))))
                pntotaleachcandden.append(float((sum(count))))
            else:
                print "Namitha was here"

        pn[i] = sum(pntotaleachcandnum)/ sum(pntotaleachcandden)

    return pn

#################start########

if __name__ == "__main__":

    wn = []  # list of weights adding upto 1
    pn = []  # modified n gram precisions
    N = 4  # reference , change this later to good values
    for i in range (0,N):
        wn.append(1/float(N))

    sentencelistcandidate = getsentencescand(candfilename)
    sentencelistreference,numberoffiles = getsentencesref(reffilename)


    #get length of candidate translatio
    c = lengthoftext(sentencelistcandidate)

    #get length of corpus
    r = lengthoftextbestmatch(sentencelistcandidate,sentencelistreference)

    #compute brevity penalty
    bp = computebrevitypenalty(r,c)

    #compute n gram precisions upto length n
    pn1 = ngramprecision(sentencelistcandidate, sentencelistreference , N)

    
    #calculate BLEU
    sum = 0.0
    for i in range (0,N):
        #print pn1[i]
        sum += (wn[i]*(math.log(pn1[i])))
    BLEU = bp *(math.exp(sum) )

    #print BLEU

    outputfilename.write(str(BLEU))
    outputfilename.close()






