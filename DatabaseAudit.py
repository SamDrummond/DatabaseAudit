import os
import arcpy
import query_yes_no
import csv
from xml.etree.ElementTree import ElementTree  

class SDEReview(object):
    
    def __init__(self, connectionString, output):
        arcpy.env.workspace = connectionString
        arcpy.env.scratchWorkspace = os.path.dirname(os.path.realpath(__file__))
        this._output = output
        
        desc = arcpy.describe(arcpy.env.workspace)
        connectionProperties = desc.connectionProperties
        this._databaseName = connectionProperties.database
        
        dir = arcpy.GetInstallInfo("desktop")["InstallDir"]
        this._metadataTranslator =  = dir + "Metadata/Translator/ESRI_ISO2ISO19139.xml"
        
        print '### Welcome to SDE Review ###'
        print 'You are about to review ' + this._databaseName
        print 'Your report will be generated at ' + this._output
        
        raw_input('Hit any key to continue.')
        
        this._reviewFeatureDatasets()
        this._reviewFeatureClassesWithoutFeatureDatasets()
        
        this._generateOutputCSV()
        
    def _listFeatureDatasets(self):
        
        this._datasets = arcpy.ListDatasets('*', 'FEATURES')
        
    def _featureDatasetDesc(self, featureDatasetDesc):
        
        featureDatasetDescList = featureDatasetDesc.split('.')
        
        this._currentSchema = featureDatasetDescList[1]
        this._currentFeatureDataset = featureDatasetDescList[2]
        
        print('You are about to review the ' + this._currentFeatureDataset + ' which is in the ' + this._currentSchema + 'schema.')
        
    def _areFieldsCamelCased(self, featureClass):
        
        print("Review Fields:")
        fields = arcpy.ListFields(featureClass)
        for field in fields
            print field.name
        
        this._isCamelCased = query_yes_no("Are you satisfied that these fields are camel cased? Y/N")
        
    def _reviewMetadata(self, featureClass):
        
        xmlOutputPath =a rcpy.env.scratchWorkspace + featureClass.name + ".xml"
        xmlFile = arcpy.ExportMetadata_conversion (featureClasses[0], this._metadataTranslator, xmlOutputPath)
        tree = ElementTree()
        tree.parse(xmlfile)
        root = tree.getroot()
        
        print("Review Metadata")
        
        titleElement = "{http://www.isotc211.org/2005/gmd}identificationInfo/{http://www.isotc211.org/2005/gmd}MD_DataIdentification/{http://www.isotc211.org/2005/gmd}citation/{http://www.isotc211.org/2005/gmd}CI_Citation/{http://www.isotc211.org/2005/gmd}title/{http://www.isotc211.org/2005/gco}CharacterString"
        title = root.find(titleElement)
        print("Title: " + title.text)
        
        summaryElement = "{http://www.isotc211.org/2005/gmd}identificationInfo/{http://www.isotc211.org/2005/gmd}MD_DataIdentification/{http://www.isotc211.org/2005/gmd}resourceMaintenance/{http://www.isotc211.org/2005/gmd}MD_MaintenanceInformation/{http://www.isotc211.org/2005/gmd}maintenanceAndUpdateFrequency/{http://www.isotc211.org/2005/gmd}MD_MaintenanceFrequencyCode"
        summary = root.find(summaryElement)
        print("Summary: " + summary.text)
        
        constraintsElement = "{http://www.isotc211.org/2005/gmd}identificationInfo/{http://www.isotc211.org/2005/gmd}MD_DataIdentification/{http://www.isotc211.org/2005/gmd}supplementalInformation/{http://www.isotc211.org/2005/gco}CharacterString
        constraints = root.find(constraintsElement)
        print("Constraints: " + constraints.text)
        
        lateUpdatedElement = "{http://www.isotc211.org/2005/gmd}identificationInfo/{http://www.isotc211.org/2005/gmd}MD_DataIdentification/{http://www.isotc211.org/2005/gmd}citation/{http://www.isotc211.org/2005/gmd}CI_Citation/{http://www.isotc211.org/2005/gmd}date/{http://www.isotc211.org/2005/gmd}CI_Date/{http://www.isotc211.org/2005/gmd}date/{http://www.isotc211.org/2005/gco}DateTime"
        lastUpdated = root.find(lateUpdatedElement)
        print("Last Updated: " + lastUpdated.text)
        
        updateFrequencyElement = "{http://www.isotc211.org/2005/gmd}identificationInfo/{http://www.isotc211.org/2005/gmd}MD_DataIdentification/{http://www.isotc211.org/2005/gmd}resourceMaintenance/{http://www.isotc211.org/2005/gmd}MD_MaintenanceInformation/{http://www.isotc211.org/2005/gmd}maintenanceAndUpdateFrequency/{http://www.isotc211.org/2005/gmd}MD_MaintenanceFrequencyCode"
        updateFrequency = root.find(updateFrequencyElement)
        print("Update Frequency: " + updateFrequency.attrib['codeListValue'])
        
        pointOfContactElement = "{http://www.isotc211.org/2005/gmd}identificationInfo/{http://www.isotc211.org/2005/gmd}MD_DataIdentification/{http://www.isotc211.org/2005/gmd}pointOfContact/{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty/{http://www.isotc211.org/2005/gmd}individualName/{http://www.isotc211.org/2005/gco}CharacterString"
        pointOfContact = root.find(pointOfContactElement)
        print("Point of Contact: " + pointOfContact)
        
        this._hasMetadata = query_yes_no("Are you satisfied that the feature class has metadata? Y/N")
        
        os.remove(xmlOutputPath)
        
    def _reviewFeatureDatasets(self):
        
        this._listFeatureDatasets()
        
        for(featureDataset in this._datasets):
            
            featureClasses = arcpy.ListFeatureClasses(feature_dataset=featureDataset)
            this._featureDatasetDesc(featureDataset)
            this._reviewFeatureClasses(featureClasses)
    
    def _reviewFeatureClassesWithoutFeatureDatasets(self):
        
        this._featureDataset = "none"
        featureClasses = arcpy.ListFeatureClasses()
        this._featureDatasetDesc(featureDataset)
        this._reviewFeatureClasses(featureClasses)

    def _reviewFeatureClasses(featureClasses):
        for featureClass in featureClasses:
            print("Feature Class name" = featureClass.name)
            this._areFieldsCamelCased(featureClass);
            this._reviewMetadata(featureClass);
            
            featureClassRecord = [
                this._databaseName,
                this._currentSchema,
                this._featureDataset, #need to think about this one - for feature classes that don't have one
                featureClass.name,
                this._isCamelCased,
                this._hasMetadata
            ]
            
            this._results.append(featureClassRecord)

    def _generateOutputCSV():
        
        outputFileCSV = open(this._output, 'wb')
        wr = csv.writer(outputFileCSV, quoting=csv.QUOTE_ALL)
        wr.writerows(this._results)
        
        