import os
import arcpy
import csv
from xml.etree.ElementTree import ElementTree  
from query_yes_no import query_yes_no

class SDEReview(object):
    
    def __init__(self, connectionString, output):
        arcpy.env.workspace = connectionString
        arcpy.env.scratchWorkspace = os.path.dirname(os.path.realpath(__file__))
        self._output = output
        
        desc = arcpy.Describe(arcpy.env.workspace)
        connectionProperties = desc.connectionProperties
        self._databaseName = connectionProperties.database
        
        dir = arcpy.GetInstallInfo("desktop")["InstallDir"]
        self._metadataTranslator = dir + "Metadata/Translator/ESRI_ISO2ISO19139.xml"
        
        self._results = []
        
        print '### Welcome to SDE Review ###'
        print 'You are about to review ' + self._databaseName
        print 'Your report will be generated at ' + self._output
        
        raw_input('Hit any key to continue.')
        
        ##self._reviewFeatureDatasets()
        self._reviewFeatureClassesWithoutFeatureDatasets()
        
        self._generateOutputCSV()
        
    def _listFeatureDatasets(self):
        
        self._datasets = arcpy.ListDatasets('*', 'FEATURES')
        
    def _featureDatasetDesc(self, featureDatasetDesc):
        
        featureDatasetDescList = featureDatasetDesc.split('.')
        self._currentFeatureDataset = featureDatasetDescList[2]
        
        print('You are about to review the ' + self._currentFeatureDataset)
        
    def _areFieldsCamelCased(self, featureClass):
        
        print("Review Fields:")
        fields = arcpy.ListFields(featureClass)
        for field in fields:
            print field.name
        
        self._isCamelCased = query_yes_no("Are you satisfied that these fields are camel cased? Y/N")
        
    def _reviewMetadata(self, featureClass):
        
        xmlOutputPath = arcpy.env.scratchWorkspace + "\\featureClass.xml"

        if os.path.isfile(xmlOutputPath): 
            os.remove(xmlOutputPath)
            
        arcpy.ExportMetadata_conversion (featureClass, self._metadataTranslator, xmlOutputPath)
        xmlFile = open(xmlOutputPath,'r')
        tree = ElementTree()
        tree.parse(xmlFile)
        root = tree.getroot()
        
        print("Reviewing Metadata")
        
        titleElement = "{http://www.isotc211.org/2005/gmd}identificationInfo/{http://www.isotc211.org/2005/gmd}MD_DataIdentification/{http://www.isotc211.org/2005/gmd}citation/{http://www.isotc211.org/2005/gmd}CI_Citation/{http://www.isotc211.org/2005/gmd}title/{http://www.isotc211.org/2005/gco}CharacterString"
        title = root.find(titleElement)
        
        summaryElement = "{http://www.isotc211.org/2005/gmd}identificationInfo/{http://www.isotc211.org/2005/gmd}MD_DataIdentification/{http://www.isotc211.org/2005/gmd}purpose/{http://www.isotc211.org/2005/gco}CharacterString"
        summary = root.find(summaryElement)
        
        constraintsElement = "{http://www.isotc211.org/2005/gmd}identificationInfo/{http://www.isotc211.org/2005/gmd}MD_DataIdentification/{http://www.isotc211.org/2005/gmd}supplementalInformation/{http://www.isotc211.org/2005/gco}CharacterString"
        constraints = root.find(constraintsElement)
        
        lateUpdatedElement = "{http://www.isotc211.org/2005/gmd}identificationInfo/{http://www.isotc211.org/2005/gmd}MD_DataIdentification/{http://www.isotc211.org/2005/gmd}citation/{http://www.isotc211.org/2005/gmd}CI_Citation/{http://www.isotc211.org/2005/gmd}date/{http://www.isotc211.org/2005/gmd}CI_Date/{http://www.isotc211.org/2005/gmd}date/{http://www.isotc211.org/2005/gco}DateTime"
        lastUpdated = root.find(lateUpdatedElement)
        
        updateFrequencyElement = "{http://www.isotc211.org/2005/gmd}identificationInfo/{http://www.isotc211.org/2005/gmd}MD_DataIdentification/{http://www.isotc211.org/2005/gmd}resourceMaintenance/{http://www.isotc211.org/2005/gmd}MD_MaintenanceInformation/{http://www.isotc211.org/2005/gmd}maintenanceAndUpdateFrequency/{http://www.isotc211.org/2005/gmd}MD_MaintenanceFrequencyCode"
        updateFrequency = root.find(updateFrequencyElement)
        
        pointOfContactElement = "{http://www.isotc211.org/2005/gmd}identificationInfo/{http://www.isotc211.org/2005/gmd}MD_DataIdentification/{http://www.isotc211.org/2005/gmd}pointOfContact/{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty/{http://www.isotc211.org/2005/gmd}individualName/{http://www.isotc211.org/2005/gco}CharacterString"
        pointOfContact = root.find(pointOfContactElement)
        
        hasMetadata = (hasattr(title, "text") AND hasattr(summary, "text") AND hasattr(constraints, "text") AND hasattr(lastUpdated, "text") AND hasattr(updateFrequency, "attrib") AND hasattr(pointOfContact, "text"))
        
        if has:
        
            self._hasMetadata = "Yes"
            
        elif hasattr(title, "text") OR hasattr(summary, "text") OR hasattr(constraints, "text") OR hasattr(lastUpdated, "text") OR hasattr(updateFrequency, "attrib") OR hasattr(pointOfContact, "text"):
            
            self._hasMetadata = "Partial"
                
        else:
            
            self._hasMetadata = "NO"
       
        print("Has Metadata: " self._hasMetadata)
        
        xmlFile.close()
        os.remove(xmlOutputPath)
            
        
    def _reviewFeatureDatasets(self):
        
        self._listFeatureDatasets()
        
        for featureDataset in self._datasets:
            
            featureClasses = arcpy.ListFeatureClasses(feature_dataset=featureDataset)
            self._featureDatasetDesc(featureDataset)
            self._reviewFeatureClasses(featureClasses)
    
    def _reviewFeatureClassesWithoutFeatureDatasets(self):
        
        self._currentFeatureDataset = "none"
        featureClasses = arcpy.ListFeatureClasses()
        
        self._reviewFeatureClasses(featureClasses)

    def _reviewFeatureClasses(self, featureClasses):
        for featureClass in featureClasses:
            print("Feature Class name: " + featureClass)

            self._areFieldsCamelCased(featureClass);
            self._reviewMetadata(featureClass);
            
            featureClassNameList = featureClass.split(".")
            self._currentSchema = featureClassNameList[1]
            tidyFeatureClassName = featureClassNameList[2]
            
            featureClassRecord = [
                self._databaseName,
                self._currentSchema,
                self._currentFeatureDataset,
                tidyFeatureClassName,
                self._isCamelCased,
                self._hasMetadata
            ]
            
            self._results.append(featureClassRecord)

    def _generateOutputCSV():
        
        outputFileCSV = open(self._output, 'wb')
        wr = csv.writer(outputFileCSV, quoting=csv.QUOTE_ALL)
        wr.writerows(self._results)
        
        
