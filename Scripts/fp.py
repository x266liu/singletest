'''
Created on Oct 30, 2014

@author: Aaron Zink
'''
from __future__ import print_function
import csv, glob, sys, string, os
import generateTestResultFile

num3start_end_Index_Of_TC=[0,100]


# shared by all test cases to prevent hard coding paths and have different paths between Windows and Linux
class globalTCPaths(object):
    '''
    classdocs
    '''
    
    testRoot = os.path.join('..')
    testReportDir = os.path.join(testRoot, 'TestReport')
    scriptDir = os.path.join(testRoot, 'Scripts')
    logDir = os.path.join(testRoot, 'Logs')
    splTestApplication = os.path.join(testRoot, 'Bin', 'SSIMplusYUV', 'Linux', 'SSIMplusYUV')
    sqmLibApplication = os.path.join(testRoot, 'Bin', 'SQMLib', 'Linux', 'SSQM')
    testResultFileName = os.path.join(testReportDir, 'test_Results.csv')

    testDataDir = os.path.join(testRoot, "TestData")
    if ((sys.platform == 'win32') or (sys.platform == 'win64')):
	    testDataDir = os.path.join("C:\\Users\\liuxu\\Documents\\OneDrive\\SingleSourceTesting\\TestData")
            
    goldFileFolder = os.path.join(testRoot, "ReferenceResults")
    
    produceGolden = 0
    screenshot = 0 
    #get most recently created folder in the Logs dir
    for name in glob.iglob(os.path.join(logDir, '*')):
        if(name == ''):
            testRunLogFolder = os.path.join(os.path.getctime)
        else:
            testRunLogFolder = os.path.join(max(glob.iglob((os.path.join(logDir, '*'))), key=os.path.getctime))
    
    
    
    def __init__(self):
        '''
        Constructor
        '''

        #add .exe to the name if on Windows
        if ((sys.platform == 'win32') or (sys.platform == 'win64')):
            self.splTestApplication = os.path.join(self.testRoot, 'Bin', 'SSIMplusYUV', 'Windows', 'SSIMplus.exe')
            self.sqmLibApplication = os.path.join(self.testRoot, 'Bin', 'SQMLib', 'Windows', 'SSQM.exe')
         

paths = globalTCPaths()

# shared by all test cases to reduce duplicate code for common tasks
class globalTCFunctions(object):

    # passed is true or false that the first condition in the eAD passed
    def conditionResult(self, passed, elemetnAttributeDictionary):
        conditionResult(self, 0, passed, elemetnAttributeDictionary)
    
    # conditionNum is a list of conditions eg [0, 1] that correspond to conditions in the eAD conditions list
    # passed is true or false that the listed conditions passed
    def conditionResult(self, conditionNum, passed, elemetnAttributeDictionary):
        tcNumber = elemetnAttributeDictionary.get('number')
        conditionString = elemetnAttributeDictionary.get('conditions')
        conditions = conditionString.split(";")
        description = elemetnAttributeDictionary.get('description')
       
        passDescription = ""
        for val in conditionNum:
            passDescription += "   " + conditions[val] + " as expected. "
        
        failDescription = ""
        for val in conditionNum:
            failDescription += "   Failing condition: " + conditions[val] + " "
        
        subTest = ""
        
        if(passed):
            print("Test Case " + tcNumber + " PASSED: " + passDescription)
            generateTestResultFile.testResultObject.writeInTestFile(tcNumber + ",PASS," + description + ","+ passDescription)
            generateTestResultFile.testResultObject.writeInTestFile("\n")
            generateTestResultFile.testResultObject.TotalNumberOfPassTC += 1
            generateTestResultFile.testResultObject.totalNumberOfTC += 1 # TC count
            return passDescription
            
        else:
            print( "Test Case " + tcNumber + " FAILED: " + failDescription)
            generateTestResultFile.testResultObject.writeInTestFile(tcNumber + ",FAIL," + description + "," + failDescription)
            generateTestResultFile.testResultObject.writeInTestFile("\n")
            generateTestResultFile.testResultObject.TotalNumberOfFailTC += 1
            generateTestResultFile.testResultObject.totalNumberOfTC += 1 # TC count
            return failDescription
    
    def printCommandList(self, commandList):
        print( "Command Executing: ", " ".join(commandList))
    
    def verifyReportCsvPair(self, testReportPath, goldReportPath):
        #print("1.1")
        result = True
        validDelta = 0.1
        numFrames = -1
            
        testFile = open(testReportPath, 'rt', encoding="utf8")
        #print("1.2")
        try:
            test = csv.reader(testFile, delimiter=',', quoting=csv.QUOTE_NONE)
            #goldFile = open(goldReportPath, 'rt', encoding="utf8")
            #gold = csv.reader(goldFile, delimiter=',', quoting=csv.QUOTE_NONE)
            
            # Find the number of frames in the test
            for row in test:
                if row and "Number of frames processed" in row[0]:
                    numFrames = int(row[1])
            testFile.seek(0) #reset the csv position
            
            #print("1.3")
            # Check average score for standard SSIMplus
            deviceName = ["default", "Default", "SSIMplusCore", "SSIMplus Core", "SSIMplus", " Source_Quality"]
            result = (abs(self.csvCalculateDeviceMean(testReportPath, deviceName, numFrames) - self.csvCalculateDeviceMean(goldReportPath, deviceName, numFrames)) < validDelta)
            
            #print("1.4")
            # Check the frame scores match for standard SSIMplus
            goldScores = self.csvGetDeviceFrameScores(goldReportPath, deviceName)
            #print("1.5")
            testScores = self.csvGetDeviceFrameScores(testReportPath, deviceName)
            #print("1.6")
            #print("length(goldScores) = ",len(goldScores),"length(testScores) = ",len(testScores))
            for idx,score in enumerate(testScores): 
                if idx < len(goldScores):
                    result = result and (abs(score - goldScores[idx]) < validDelta)
            
            #print("1.7")
            return result    
        except FileNotFoundError:
            print( "\nFile was not created or could not be found. ", sys.exc_info()[1])        
        except TypeError:
            print("\nCouldn't read the CSV file, it is empty or malformed. ", sys.exc_info()[0], sys.exc_info()[1])
        finally:
            testFile.close()
            
        return False
    
    def csvGetDeviceFrameScores(self, csvPath, deviceName):
        devColNum = -1
        scoreList = []
       
        
        csvFile = open(csvPath, 'rt', encoding="utf8")
        try:           
            csvReader = csv.reader(csvFile, delimiter=',', quoting=csv.QUOTE_NONE)
            
            # Find the column number by checking the column headers  
            for row in csvReader:
              
                if row and "Scores" in row[0]:               # They come after "SSIMplus Scores"
                   
                    scoreColumnHeaders = next(csvReader)               
                    if "Reference" in scoreColumnHeaders[0]: # The row starts with "Reference"
                      
                        for header in scoreColumnHeaders:
                           
                            if (header in deviceName):
                              
                                devColNum = scoreColumnHeaders.index(header)
                                break 

                if row and (len(row) > 1) and (devColNum != -1):  
                    scoreList.append(float(row[devColNum]))  

        finally:
            csvFile.close()
                                      
        if (devColNum != -1):
            return scoreList
        else:
            print("couldn't find the frame scores for" + str(csvPath))
            return("couldn't find the frame scores for" + str(csvPath))
    
    def csvCalculateDeviceMean(self, csvPath, deviceName, numFrames):
        devColNum = -1
        calculatedMean = -1
               
        frameScores = self.csvGetDeviceFrameScores(csvPath, deviceName)
        del frameScores[numFrames:] #get rid of extra frames
        calculatedMean = sum(frameScores)/len(frameScores) if len(frameScores) > 0 else float('nan')   
        
        return calculatedMean

        
    def csvGetDeviceMean(self, csvPath, deviceName):
        devColNum = -1
        fileMean = -1
        
        csvFile = open(csvPath, 'rt', encoding="utf8")
        try:            
            csvReader = csv.reader(csvFile, delimiter=',', quoting=csv.QUOTE_NONE)

            # Find the column number by checking the column headers  
            for row in csvReader:
                if row and "Summary" in row[0]:              # They come after "Summary"
                    scoreColumnHeaders = next(csvReader)               
                    if "Statistic" in scoreColumnHeaders[0]: # The row is named "Statistic"
                        for header in scoreColumnHeaders:  
                            if (header in deviceName):
                                devColNum = scoreColumnHeaders.index(header)
                                break 

                if row and (devColNum != -1) and "Mean" in row[0]:                  
                    fileMean = float(row[devColNum])                                 
            
            return fileMean
                
        finally:
            csvFile.close()
         
        print("couldn't find the mean for" + str(csvPath))
        return("couldn't find the mean for" + str(csvPath))
        
    def csvGetWarningString(self, csvPath):
        warning = ""
        
        csvFile = open(csvPath, 'rt', encoding="utf8")
        try:            
            csvReader = csv.reader(csvFile, delimiter=',', quoting=csv.QUOTE_NONE)

            for row in csvReader:
                if row and "Warning" in row[0]:              # They come after "Summary"
                    warning = row[0]                             
            
            return warning
                
        finally:
            csvFile.close()
         
        print("couldn't read CSV " + str(csvPath))
        return("couldn't read CSV " + str(csvPath))
        
    # check for a warning in the test CSV and compare it to the gold file
    def verifyReportCsv(self, elementAttributeDictionary):
        reportName = elementAttributeDictionary.get('string') + '_Report.csv'
        testReportPath = os.path.join(paths.testRunLogFolder, reportName)
        goldReportPath = os.path.join(paths.goldFileFolder, reportName)
        
        if('warning' in open(testReportPath).read().lower()):      
            if (self.csvGetWarningString(testReportPath) != self.csvGetWarningString(goldReportPath)):
                return False  
       
        return self.verifyReportCsvPair(testReportPath, goldReportPath)
                
    def verifyPerfLog(self, elementAttributeDictionary):       
        return True

util = globalTCFunctions()