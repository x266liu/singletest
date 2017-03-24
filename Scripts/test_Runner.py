import sys, string, os, datetime, shutil, getopt
import subprocess
from random import randint
import re
from optparse import OptionParser
#import commands
import glob
import generateTestResultFile, fp

# import every test case .py file in the TestModules folder
for file in glob.glob(os.path.join('./TestModules', "*.*")):
    fileName = os.path.basename(file)
    if fileName[:2] == 'TC' and fileName[-3:] == '.py':
        tcName = fileName[:-3]
        tcRegex = re.compile("(TC\_([0-9]+\_)+)")
        tcNumChars = tcRegex.search(tcName)
        if tcNumChars:
            tcNumChars = tcNumChars.group(1)
        else:
            raise Exception('TC regex string malformed: ' + tcName)

        tcObjName = tcNumChars + 'ClassObject'
        
        #try:
        # eg format: from TestModules.TC_1_test_Command_Saving_Log_File_In_Working_Directory import TC_1_ClassObject 
        exec("from TestModules.%s import %s" % (tcName,tcObjName))
        #except ImportError:
        #    print("failed on import from " + fileName)            

#sys.path.append("E:/SSIMWavePlusPlayerTestingRelated/TestAutomationWorkspace/SSIMWaveInc/SSIMWaveAutomationFramework/TestModules")
#from SSIMWaveAutomationFramework.TestModules.TC_1_Test_Command_Saving_Log_File_Showing_Frame_Numbers_Performance_Values_On_Console import testFun

try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

class SSIMWaveCommandBasedVersionTesting:
    
    def __init__(self, starting_Index_Of_TC, ending_Index_Of_TC):
    
        # Make sure script is running in new enough version of python
        if sys.version_info[0] < 3:
            print("these test were written for python 3.3 and above")
            print("try the command \"python test_Runner.py\" on Windows or \"python3 test_Runner.py\" on Linux")
            exit()
        
        # WRITE ALL COMMOM VARIABLES OVER HERE
        # These are only default values, they may be changed by the command line arguments
        self.starting_Index_Of_TC = [1]     
        self.ending_Index_Of_TC = [11]
        fp.produceGolden = 0 ;
        fp.screenshot =0 ;
        self.testModeF2P = 1000000; # used by some test cases to speed up testing by only processing the first n frames in each video. Use a large number (1000000) to process all frames
        self.tcDevMode = False # prints better exceptions when a test case fails instead of moving on to the next test case
        self.noRunList = [[3,3]]
        self.elementAttributeDictionary = {}
        self.timeout = 1500;

    # Pass in a list of ints eg. for test case 1.2.3 use [1 2 3], and the elementAttributeDictionary from testSuit.xml
    def run_Test_Case(self, subTestNumList, elementAttributeDictionary):
        # Build string eg. TC_1_2_3
        tcNumChar = 'TC'
        for val in subTestNumList:
            
            tcNumChar += '_' + str(val)
        # Run command eg. TC_1_2_3_ClassObject.run_TC_1_2_3(elementAttributeDictionary)
       
        try:
            exec("%s_ClassObject.run_%s(elementAttributeDictionary)" % (tcNumChar, tcNumChar))
        except ImportError:
            print("failed to find or start test case " + tcNumChar)    
            raise
        except:
            if(self.tcDevMode):
                raise # in dev mode we want all the detail for the error instead of catching it
            tcName = self.tc_num_to_string(subTestNumList)
            description = elementAttributeDictionary.get("description")
            print("\nUnexpected error with " + tcName + ": ", sys.exc_info())
            generateTestResultFile.testResultObject.writeInTestFile(tcName + ",FAIL," + description + ",Unknown exception" + str(sys.exc_info()))
            generateTestResultFile.testResultObject.writeInTestFile("\n")
            generateTestResultFile.testResultObject.TotalNumberOfFailTC += 1
            generateTestResultFile.testResultObject.totalNumberOfTC += 1 # TC count            
    
    def tc_num_getstartandend(self, start,end, ref ):
        size_start = len(start)
        
        size_end = len(end)
        size_testcase = len(ref)

        fp.num3start_end_Index_Of_TC[0] = 0 ;
        fp.num3start_end_Index_Of_TC[1] = 100 ;

        if(size_start == 2 ):
            if start[0]==ref[0] :
               #and start[1]== ref[1]):
                fp.num3start_end_Index_Of_TC[0] = start[1]
                if(size_end == 2 ):
                    if start[0]==end[0] : 
                       #and start[1]==end[1]):
                        fp.num3start_end_Index_Of_TC[1] = end[1]
                    return ;

        if( size_end ==2):
            if end[0]==ref[0] :
               #and end[1]== ref[1]):
                fp.num3start_end_Index_Of_TC[1] = end[1] ;
        return ;     


    # true if isGreater is larger than ref
    def tc_num_gte(self, isGreater, ref,mode):
        size1 = len(ref)
        size2 = len(isGreater)
        
        if size1 == 2 and size2 == 1 and mode ==1:
            if  isGreater[0] == ref[0] : 
            #and isGreater[1] == ref[1] :
                return 1  ;
        
        # checks if isGreater is sorted to the end of the list
        return self.tc_sort_list([isGreater, ref])[1] == isGreater
    
    
    # returns a sorted list of test cases eg. [[1,1],[2,6,7],[2,6,7,3]]
    def tc_sort_list(self, tcList):
        return sorted(tcList, key=lambda v: [int(i) for i in v])
        
        
    # returns the test case num as a string eg. [2,6,7] becomes 2.6.7
    def tc_num_to_string(self, subTestNumList):
        return ".".join(str(x) for x in subTestNumList)
        
        
    # returns the test case num as a string eg. [2,6,7] becomes 2.6.7
    def tc_get_next_test(self, subTestNumList):
        return ".".join(str(x) for x in subTestNumList)
           
           
# WRITE ONE FUNCTION OF ONLY FILE CREATGING AND CLOSSING ETC
                                                                
    def test_Runner(self):
             
        #self.testResults = open(self.Test_Result_File_Name, 'a')        # Opening Test Result file to write result of test case 1 
        generateTestResultFile.testResultObject.timeoutflag = self.timeout
        # FOLLOWING COMMAND RAN
        # E:\V1>E:\\V1\\QA_V2.exe -dev iphone5 -d E:\\V1\\Reference.mp4 -r E:\\V1\\Reference.avi -m ssimp -lt stdout    
        xmlFile = os.path.join('testSuit.xml')
        tree = ET.ElementTree(file=xmlFile)          # Opening xml file to read command for test case 1 
        IsTestCasePassed = False
        fountTCinXMLfile = False

        # Delete test result file if it already exists in path. 
        for file in os.listdir(os.path.join('..','TestReport','')):
            if file.endswith(".csv"):
                os.remove(os.path.join('..','TestReport','test_Results.csv'))
        
        generateTestResultFile.testResultObject.openTestFile()
        generateTestResultFile.testResultObject.writeInTestFile("Test Case Number,Expected(Pass or Fail), Result, Equal, Description,Command, Conditions Checked")
        generateTestResultFile.testResultObject.writeInTestFile("\n")

        
        #os.chdir("E:\SSIMWavePlusPlayerTestingRelated\TestAutomationWorkspace\SSIMWaveInc\SSIMWaveAutomationFramework")   # Delete existing test result file
        #for file in glob.glob("*.csv"):
            #if file == "test_Results.csv":
          
          
        #make new test results log folder named using the current date
        currentTime = datetime.datetime.now()
        newLogFolderName = currentTime.strftime("%Y-%m-%d %Hh%Mm%Ss")
        os.mkdir(os.path.join(fp.paths.logDir, newLogFolderName))
        fp.paths.testRunLogFolder = os.path.join(fp.paths.logDir, newLogFolderName)

        

        # loop through each test in tst in testSuit.xml
        for elem in tree.iterfind('testsuite/testcase'):     # search elements from XML file to find command
            #print "\nelement tag: ", elem.tag               # Keep prints for debugging later to find bugs
            #print "element attribute: ", elem.attrib
            self.elemTag = elem.tag
            self.elementAttributeDictionary =  elem.attrib
            self.elementAttributeDictionary.update({"f2p":str(self.testModeF2P)})
            
            tcNum =  [int(n) for n in self.elementAttributeDictionary.get("number").split('.')]

            #print ("green add "+ self.tc_num_to_string(tcNum)+"  "+self.tc_num_to_string(self.starting_Index_Of_TC)+"   "+ self.tc_num_to_string(self.ending_Index_Of_TC))
          
            #skip some test cases
            if tcNum in self.noRunList:
                pass

            elif (self.tc_num_gte(tcNum, self.starting_Index_Of_TC,1)) and (self.tc_num_gte(self.ending_Index_Of_TC, tcNum,0)):      # condition to run test cases from starting index till end, user can chose start TC and finish TC. 
                # run the test case, this function throws an exception if the test case number doesn't exist
                print("\n")
               
                #get the fp.num3start_end_Index_Of_TC[0]  and fp.num3start_end_Index_Of_TC[1] 
                self.tc_num_getstartandend(self.starting_Index_Of_TC,self.ending_Index_Of_TC,tcNum )    

                #all testcase add screenshot.    
                fp.screenshot =1

                self.run_Test_Case(tcNum, self.elementAttributeDictionary)  
            
                #self.starting_Index_Of_TC += 1          # after executing go to next index for next TC. 
                if self.tc_num_gte(tcNum, self.ending_Index_Of_TC,2):
                    print("Finished testing from starting index to end index")
                    break
                    
        print("\nDone running any tests\n")    

            
        #  Write Test Summary Report 
        generateTestResultFile.testResultObject.OpenFileAndSetFilePointerAtBeginning()
        
        # Record the test settings
        generateTestResultFile.testResultObject.writeInTestFile("\n")
        generateTestResultFile.testResultObject.writeInTestFile("Test Run Settings")
        generateTestResultFile.testResultObject.writeInTestFile("\n")

        
        # self.tcDevMode = False # prints better exceptions when a test case fails instead of moving on to the next test case
        generateTestResultFile.testResultObject.writeInTestFile("Starting TC Number: " + self.tc_num_to_string(self.starting_Index_Of_TC))
        generateTestResultFile.testResultObject.writeInTestFile("\n")
        generateTestResultFile.testResultObject.writeInTestFile("Ending TC Number: " + self.tc_num_to_string(self.ending_Index_Of_TC))
        generateTestResultFile.testResultObject.writeInTestFile("\n")
        generateTestResultFile.testResultObject.writeInTestFile("Frames to process setting: " + str(self.testModeF2P))

        #self.testResults = open(self.Test_Result_File_Name, 'a')        # Opening Test Result file to write result of test case 1 
        generateTestResultFile.testResultObject.writeInTestFile("\n")
        generateTestResultFile.testResultObject.writeInTestFile("\n")
        generateTestResultFile.testResultObject.writeInTestFile("Test Summary Report")
        generateTestResultFile.testResultObject.writeInTestFile("\n")
        generateTestResultFile.testResultObject.writeInTestFile("\n")
        generateTestResultFile.testResultObject.writeInTestFile("Total Number of Test Cases: " + str(int(generateTestResultFile.testResultObject.totalNumberOfTC)))
        generateTestResultFile.testResultObject.writeInTestFile("\n")
        generateTestResultFile.testResultObject.writeInTestFile("Total Number of Pass Test Cases: " + str(int(generateTestResultFile.testResultObject.TotalNumberOfPassTC)))
        generateTestResultFile.testResultObject.writeInTestFile("\n")
        generateTestResultFile.testResultObject.writeInTestFile("Total Number of Fail Test Cases: " + str(int(generateTestResultFile.testResultObject.TotalNumberOfFailTC)))        
        generateTestResultFile.testResultObject.closeTestFile()
        
        #copy the completed test file to the log archive folder
        print("Moving test result report to the test run log folder \"" + fp.paths.testRunLogFolder[1:] + "\"")
        shutil.copy(generateTestResultFile.testResultObject.Test_Result_File_Name, fp.paths.testRunLogFolder)

def usage():
  tab = "    "
  print("\n==============================================================")
  print(tab + "SSIMWave Automated Test Runner")
  print(tab + "Version 0.5")
  print("==============================================================\n")

  print('Usage:')
  print(tab + sys.argv[0] + ' [options]')
  print(tab + sys.argv[0] + ' -dev')
  print(tab + sys.argv[0] + ' -start 1.1.3 -end 4.1.2 -dev -f2p 100 -norun 2.1:3.1')
  
  print("\nSingle-Flag Options:")  
  print(tab + "-dev \t Use this, the SPL developer test suit. Functional tests that take about 1 minute.")  
  print(tab + "-full \t Run all tests for the full length. Takes about 60 minutes.")  
  #print(tab + "-default \t Use the hard coded values in test_Runner.py.") 
  print(tab + "-h \t\t Print this program usage help message.")
  print(tab + "-timeout \t reset timeout time.")
 
  print("\nMulti-Flag Options:")
  print(tab + "-exceptions <1 or 0>\t1 to halt and print on any exceptions. 0 by default.")
  print(tab + "-f2p <int>\t\t\tSome cases will only process the specified number of frames. All frames by default.")
  print(tab + "-start <tc_num>\t\tRun test sequentially starting with this test case. eg. 1.1")
  print(tab + "-end <tc>\t\t\tStop running test cases after running this test. eg 7.1")
  print(tab + "-norun <tc:tc>\t\tDon't run these specific test cases. eg 2.1:2.2")
  #util1();

def util1():
    path = 'F:\\TestData\\TestData\\2-FrameRate'
    files = os.listdir(path)
    print (path+"---------------------------------------")
    for i in files:
        print (i)

    return ;

# Processes command line arguments then starts the test cases
if __name__ == '__main__':

    argv = sys.argv
    emp1 = SSIMWaveCommandBasedVersionTesting(1, 2)
    
    if len(argv) == 1:
        usage()                     
        sys.exit() 
    
    # Single-Flag modes, don't allow using these with other flags
    if len(argv) == 2:
        # -dev is for SPL library developers, it runs a bunch of tests quickly
        if argv[1] == '-dev':
            fp.screenshot =1 ;
            emp1.testModeF2P = 10
            emp1.starting_Index_Of_TC = [0]
            emp1.ending_Index_Of_TC = [999]
            emp1.tcDevMode = False          #only True when develping test cases
            
            #4.1 is unsuported
            #12.1.X are long video files
            #13.2.X are very high resolution and run slowly
            emp1.noRunList = [[3,3]]
        elif argv[1] == '-dev2':
            emp1.testModeF2P = 10
            emp1.starting_Index_Of_TC = [0]
            emp1.ending_Index_Of_TC = [999]
            emp1.tcDevMode = False          #only True when develping test cases
            
            #4.1 is unsuported
            #12.1.X are long video files
            #13.2.X are very high resolution and run slowly
            emp1.noRunList = [[3,3]]
                
        elif argv[1] == '-full':
            fp.screenshot =1 ;
            emp1.testModeF2P = 1000000
            emp1.starting_Index_Of_TC = [0]
            emp1.ending_Index_Of_TC = [999]  
            emp1.tcDevMode = False 
        elif argv[1] == '-golden':
            fp.produceGolden = 1
            emp1.testModeF2P = 1000000
            emp1.starting_Index_Of_TC = [0]
            emp1.ending_Index_Of_TC = [999]  
            emp1.tcDevMode = False 
        elif argv[1] == '-default':
            pass    
        elif argv[1] == '-h':
            usage()
            sys.exit()
        else:
            print("\nERROR \nOption " + argv[1] + " is not supported.")
            usage()
            sys.exit(2) 
            
    #Multi-Flag modes
    else:            
        i = 0
        while i < len(argv[1:]):       
            i = i + 1
            #print("Enter loop with value: ", i)
            if argv[i] in ["-h", "-help"]:      
                usage()                     
                sys.exit()                  
            elif argv[i] in ['-debug']: 
                global _debug    
                if argv[i+1] == '1':                              
                    _debug = 1 
                elif argv[i+1] == '0':            
                    _debug = 0 
                else:
                    print("\nERROR \nOption " + argv[i] + " " + argv[i+1] + " is not supported.")
                    usage()
                    sys.exit(2)               
                i = i + 1            
            elif argv[i] in ["-f2p"]: 
                emp1.testModeF2P = argv[i+1]
                i = i + 1
            elif argv[i] in ["-dev"]:
                emp1.testModeF2P = 10
                emp1.tcDevMode = False          #only True when develping test cases
                i = i + 1 
            elif argv[i] in '-timeout':
                emp1.timeout = argv[i+1]       
            elif argv[i] in ["-start"]: 
                emp1.starting_Index_Of_TC = [int(n) for n in argv[i+1].split('.')] # string to list of ints
                i = i + 1
            elif argv[i] in ["-end"]: 
                emp1.ending_Index_Of_TC = [int(n) for n in argv[i+1].split('.')]
                i = i + 1
            elif argv[i] in ["-norun"]: 
                emp1.noRunList = [[int(p) for p in n.split('.')] for n in argv[i+1].split(':')]
                i = i + 1
            elif argv[i] in ["-exceptions"]: 
                if argv[i+1] == '1':
                    emp1.tcDevMode = True
                elif argv[i+1] == '0':
                    emp1.tcDevMode = False
                else:
                    print("\nERROR \nOption " + argv[i] + " " + argv[i+1] + " is not supported.")
                    usage()
                    sys.exit(2)                      
                i = i + 1
            else:
                print("\nERROR \nOption " + argv[i] + " is not supported or has too many other arguments.")
                usage()
                sys.exit(2)              
           

    emp1.test_Runner()
    
pass
