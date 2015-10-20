import os
import arcpy
import csv
import FieldCheck

from xml.etree.ElementTree import ElementTree  


class SDEReview(object):

    def __init__(self, connection_string, output, is_metadata_check=False):

        arcpy.env.workspace = connection_string
        arcpy.env.scratchWorkspace = os.path.dirname(os.path.realpath(__file__)) + "\\scratch"
        self._output = output
        
        desc = arcpy.Describe(arcpy.env.workspace)
        connection_properties = desc.connectionProperties
        self._database_name = connection_properties.database

        self._is_metadata_check = is_metadata_check

        if self._is_metadata_check:
            install_dir = arcpy.GetInstallInfo("desktop")["InstallDir"]
            self._metadata_translator = install_dir + "Metadata/Translator/ESRI_ISO2ISO19139.xml"
            print(self._metadata_translator)

        self._results = []
        
        print('### Welcome to SDE Review ###')
        print('You are about to review ' + self._database_name)
        print('Your report will be generated at ' + self._output)

        raw_input('Hit any key to continue.')
        
        self._review_feature_data_sets()
        self._review_feature_classes_without_feature_data_sets()
        
        self._generate_output_csv()
        
    def _list_feature_data_sets(self):

        self._data_sets = arcpy.ListDatasets('*', 'FEATURES')

    def _feature_data_set_desc(self, feature_data_set_desc):

        feature_data_set_desc_list = feature_data_set_desc.split('.')
        self._current_feature_data_set = feature_data_set_desc_list[2]
        
        print('You are about to review the ' + self._current_feature_data_set)
        
    def _are_fields_camel_cased(self, feature_class):
        
        print("Review Fields:")
        fields = arcpy.ListFields(feature_class)
        
        self._is_camel_cased = "Yes"
        
        for field in fields:

            if not (field.name.lower() == "OBJECTID".lower() or field.name.lower() == "SHAPE.STArea()".lower() or
                    field.name.lower() == "SHAPE.STLength()".lower() or field.name.lower() == "SHAPE".lower()):
            
                verify_camel_case = FieldCheck.VerifyCamelCase(field.name)
                camel_case_results = verify_camel_case.is_camel_cased()
                print(field.name + ": " + str(camel_case_results))

                if not camel_case_results:
                    self._is_camel_cased = "No"

    def _review_metadata(self, feature_class):
        
        xml_output_path = arcpy.env.scratchWorkspace + "\\featureClass.xml"

        if os.path.isfile(xml_output_path):
            os.remove(xml_output_path)
            
        arcpy.ExportMetadata_conversion(feature_class, self._metadata_translator, xml_output_path)
        xml_file = open(xml_output_path, 'r')
        tree = ElementTree()
        tree.parse(xml_file)
        root = tree.getroot()
        
        print("Reviewing Metadata")
        
        title_element = "{http://www.isotc211.org/2005/gmd}identificationInfo/" \
                        "{http://www.isotc211.org/2005/gmd}MD_DataIdentification/" \
                        "{http://www.isotc211.org/2005/gmd}citation/" \
                        "{http://www.isotc211.org/2005/gmd}CI_Citation/{http://www.isotc211.org/2005/gmd}title/" \
                        "{http://www.isotc211.org/2005/gco}CharacterString"
        title = root.find(title_element)
        
        summary_element = "{http://www.isotc211.org/2005/gmd}identificationInfo/" \
                          "{http://www.isotc211.org/2005/gmd}MD_DataIdentification/" \
                          "{http://www.isotc211.org/2005/gmd}purpose/" \
                          "{http://www.isotc211.org/2005/gco}CharacterString"
        summary = root.find(summary_element)
        
        constraints_element = "{http://www.isotc211.org/2005/gmd}identificationInfo/" \
                              "{http://www.isotc211.org/2005/gmd}MD_DataIdentification/" \
                              "{http://www.isotc211.org/2005/gmd}supplementalInformation/" \
                              "{http://www.isotc211.org/2005/gco}CharacterString"

        constraints = root.find(constraints_element)
        
        last_updated_element = "{http://www.isotc211.org/2005/gmd}identificationInfo/" \
                               "{http://www.isotc211.org/2005/gmd}MD_DataIdentification/" \
                               "{http://www.isotc211.org/2005/gmd}citation/" \
                               "{http://www.isotc211.org/2005/gmd}CI_Citation/" \
                               "{http://www.isotc211.org/2005/gmd}date/" \
                               "{http://www.isotc211.org/2005/gmd}CI_Date/{http://www.isotc211.org/2005/gmd}date/" \
                               "{http://www.isotc211.org/2005/gco}DateTime"

        last_updated = root.find(last_updated_element)
        
        update_frequency_element = "{http://www.isotc211.org/2005/gmd}identificationInfo/" \
                                   "{http://www.isotc211.org/2005/gmd}MD_DataIdentification/" \
                                   "{http://www.isotc211.org/2005/gmd}resourceMaintenance/" \
                                   "{http://www.isotc211.org/2005/gmd}MD_MaintenanceInformation/" \
                                   "{http://www.isotc211.org/2005/gmd}maintenanceAndUpdateFrequency/" \
                                   "{http://www.isotc211.org/2005/gmd}MD_MaintenanceFrequencyCode"
        update_frequency = root.find(update_frequency_element)
        
        point_of_contact_element = "{http://www.isotc211.org/2005/gmd}identificationInfo/" \
                                   "{http://www.isotc211.org/2005/gmd}MD_DataIdentification/" \
                                   "{http://www.isotc211.org/2005/gmd}pointOfContact/" \
                                   "{http://www.isotc211.org/2005/gmd}CI_ResponsibleParty/" \
                                   "{http://www.isotc211.org/2005/gmd}individualName/" \
                                   "{http://www.isotc211.org/2005/gco}CharacterString"
        point_of_contact = root.find(point_of_contact_element)

        if hasattr(title, "text") \
                and hasattr(summary, "text") \
                and + hasattr(constraints, "text") \
                and hasattr(last_updated, "text") \
                and + hasattr(update_frequency, "attrib") \
                and + hasattr(point_of_contact, "text"):

            self._hasMetadata = "Yes"
        
        elif hasattr(title, "text") \
                or + hasattr(summary, "text") \
                or + hasattr(constraints, "text") \
                or + hasattr(last_updated, "text") \
                or + hasattr(update_frequency, "attrib") \
                or + hasattr(point_of_contact, "text"):

            self._hasMetadata = "Partial"
            
        else:
            self._hasMetadata = "No"
        
        xml_file.close()
        os.remove(xml_output_path)

    def _review_feature_data_sets(self):
        
        self._list_feature_data_sets()
        
        for feature_data_set in self._data_sets:
            
            feature_classes = arcpy.ListFeatureClasses(feature_dataset=feature_data_set)
            self._feature_data_set_desc(feature_data_set)
            self._review_feature_classes(feature_classes)
    
    def _review_feature_classes_without_feature_data_sets(self):
        
        self._current_feature_data_set = "none"
        feature_classes = arcpy.ListFeatureClasses()
        
        self._review_feature_classes(feature_classes)

    def _review_feature_classes(self, feature_classes):
        for feature_class in feature_classes:
            print("Feature Class name: " + feature_class)

            self._is_camel_cased = "Unknown"
            self._has_metadata = "Unknown"

            if arcpy.Exists(feature_class):
                self._are_fields_camel_cased(feature_class)

                if self._is_metadata_check:
                    self._review_metadata(feature_class)

            feature_class_name_list = feature_class.split(".")
            self._current_schema = feature_class_name_list[1]
            tidy_feature_class_name = feature_class_name_list[2]
        
            feature_class_record = [
                self._database_name,
                self._current_schema,
                self._current_feature_data_set,
                tidy_feature_class_name,
                self._is_camel_cased,
                self._has_metadata
            ]

            self._results.append(feature_class_record)

    def _generate_output_csv(self):
        
        output_file_csv = open(self._output, 'wb')
        wr = csv.writer(output_file_csv, quoting=csv.QUOTE_ALL)
        wr.writerows(self._results)
