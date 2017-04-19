import sys, string, os, datetime, shutil, getopt
import subprocess
from random import randint
import re
from optparse import OptionParser
import itertools


def combo():
    try:
        import xml.etree.cElementTree as ET
    except ImportError:
        import xml.etree.ElementTree as ET    
    xmlFile = os.path.join('C:/Users/liuxu/Documents/OneDrive/singletest/Scripts/cb.xml')
    tree = ET.ElementTree(file=xmlFile)          # Opening xml file to read command for test case 1 
    
    for elem in tree.iterfind('testsuite/testcase'):
        ead =  elem.attrib
        flag = ead.get("flag").split(',')
        roi = ead.get("roi").split(',')
        sp = ead.get("sp").split(',')
        f2p = ead.get("f2p").split(',')
        speed = ead.get("speed").split(',')
        mper = ead.get("mper").split(',')
        qthresh = ead.get("qthresh").split(',')
        
    lst = []
    subset = []
    for i in range(0, len(roi)):         
        str1 = "-roi" + " " + roi[i] + " "
        lst.append(str1)
        for j in range(0, len(sp)):
                            
                str2 = "-sp" +" " + sp[j]+ " "
                lst.append(str2)    
                for k in range(0, len(f2p)):
                     
                    str3 = "-f2p"+" " + f2p[k]+ " "
                    lst.append(str3)
                    for h in range(0, len(speed)):
                                                       
                            str4 = "-speed"+" "+ speed[h]+ " "
                            lst.append(str4)
                            for u in range(0, len(mper)):                                  
                                                                                  
                                str5 = "-mper" +" "+ mper[u]+ " "
                                lst.append(str5)
                                for l in range(0, len(qthresh)):
                                   # if len(lst) > 0:
                                    #    lst = lst[:-1]                                                                                        
                                    str6 = "-qthresh"+" "+ qthresh[l]+ " "
                                    lst.append(str6)
                                    #print(lst)
                                    subset.append(lst)  
                                    lst = lst[:-1]
                                lst = lst[:-1]
                            lst = lst[:-1]
                    lst = lst[:-1]
                lst = lst[:-1]
        lst = lst[:-1]        
    
    return subset
