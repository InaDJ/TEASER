# Created June 2017
# Ina De Jaeger

"""This module contains an example how to import TEASER projects from
*.teaserXML and pickle in order to reuse data.
"""
import teaser.data.output.ideas_district_simulation as simulations
import teaser.data.input.citygml_input as citygml_in
import os
import pandas as pd

def example_load_citygml():
    """"This function demonstrates different loading options of TEASER"""

    # In example e4_save we saved two TEASER projects using *.teaserXML and
    # Python package pickle. This example shows how to import these
    # information into your python environment again.

    # To load data from *.teaserXML we can use a simple API function. So
    # first we need to instantiate our API (similar to example
    # e1_generate_archetype). The XML file is called
    # `ArchetypeExample.teaserXML` and saved in the default path. You need to
    #  run e4 first before you can load this example file.

    from teaser.project import Project

    # The last option to import data into TEASER is using a CityGML file. The
    # import of CityGML underlies some limitations e.g. concerning data
    # given in the file and the way the buildings are modeled.
    LOD2 = True
    LOD2_4 = False
    LOD2_8 = False
    LOD1_ridge = False
    LOD1_halfroof = False
    LOD1_extended = False

    path = "D:\Ina\Data\GRB\GML/" # path to folder which contains 3 folders (streets_LOD2, streets_LOD1_ridge and streets_LOD1_halfroof)
    generate_streetnames_from = "Nothing" # choose either "Excel" or "Folder"

    if generate_streetnames_from == "Folder":
        streetnames = create_streetnames_from_directory(path + "Streets_LOD2/")
    elif generate_streetnames_from == "Excel":
        path_to_excel = "C:\Users\ina\Box Sync\Onderzoek\Projects\Gemeenschappelijke case Genk\Neighbourhood model 0.0.1\Number of buildings in districts\StreetsGenkPerDistrict.xlsx"
        name_of_district = "Boxbergheide"  # name of excel sheet
        streetnames = create_streetnames_from_excel(path_to_excel, name_of_district)
    else:
        streetnames = ['Blookstraat', 'Beukenveld', 'Basculestraat', 'Gruisweg', 'AlbertForgeurstraat', 'Achterstraat',
                       'AugustCollonstraat', 'Alsemstraat', 'Holeven', 'AlfredWautersstraat', 'Boektveldstraat',
                       'Bijenstraat', 'Boekweitstraat', 'Vogelzangstraat', 'Binnendelweg', 'Acacialaan', 'DeVroente',
                       'Groenven', 'Houtwal', 'Biezenstraat', 'Heilapstraat', 'Bandstraat', 'Berglaan',
                       'Rietbeemdstraat', 'AdolfGreinerstraat', 'Zandoerstraat', 'Hazelnootstraat', 'Bergbeemdstraat',
                       'Kennipstraat', 'Blookbergstraat', 'DeBek', 'Ploegstraat', 'Bemdekensstraat', 'Drijtap',
                       'Bleuskenstraat', 'Genkerhei', 'Aldebiezenstraat', 'Gracht', 'Bodemstraat', 'Bijlkestraat',
                       'Berm', 'Arbeidsstraat', 'Boxbergstraat','Biegrachtstraat', 'DeHeuvel', 'Ijzerven',
                       'Boogstraat', 'Hennepstraat', 'Berghausstraat',
                       'Bevrijdingslaan', 'Beverststraat',
                       'Congostraat', 'OudeHeide', 'Anijsstraat', 'Berenbroekstraat', 'Bremstraat', 'Beemdenstraat']

    print streetnames

    streetnames_succeeded = []
    for streetname in streetnames:
        print streetname
        LOD2_succeeded = not LOD2 #set to True if this case should not be simulated
        LOD1_ridge_succeeded = not LOD1_ridge
        LOD1_halfroof_succeeded = not LOD1_halfroof
        LOD2_4_succeeded = not LOD2_4
        LOD2_8_succeeded = not LOD2_8
        LOD1_extended_succeeded = not LOD1_extended

        if LOD2 == True:
            try:
                prj_LOD2 = Project(load_data=True, used_data_country="Belgium")
                prj_LOD2.name = streetname + "_LOD2"
                print(prj_LOD2.name)
                prj_LOD2.used_library_calc = 'IDEAS'
                prj_LOD2.load_citygml(path=path + "Streets_LOD2/" + streetname + ".gml",
                                      checkadjacantbuildings=True,
                                      number_of_zones=2,
                                      merge_buildings=True)
                prj_LOD2.calc_all_buildings(
                    raise_errors=True)  # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
                prj_LOD2.export_ideas(internal_id=None, path=None, building_model="Detailed", occupant_model= "ISO13790")
                prj_LOD2.save_project(file_name=None, path=None)
                simulations.ideas_district_simulation(project=prj_LOD2, simulation=True, analyseSimulation=True,
                                                      analyseGeometry=True)
                LOD2_succeeded = True
            except:
                print('There has been an unknown error in ' + streetname + '____________________________________________________________')
                pass
        if LOD2_4 == True and LOD2_succeeded == True:
            try:
                prj_LOD2_4 = prj_LOD2
                prj_LOD2_4.name = streetname + "_LOD2_4"
                print(prj_LOD2_4.name)
                prj_LOD2_4.used_library_calc = 'IDEAS'
                orientation_dict_4 = {
                    'East': [45.0, 135.0, 90.0],
                    'South': [135.0, 225.0, 180.0],
                    'West': [225.0, 315.0, 270.0]}
                citygml_in._merge_orientations(prj=prj_LOD2_4, orientation_dict=orientation_dict_4)
                prj_LOD2_4.calc_all_buildings(
                    raise_errors=True)  # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
                prj_LOD2_4.export_ideas(internal_id=None, path=None, building_model="Detailed", occupant_model= "ISO13790")
                prj_LOD2_4.save_project(file_name=None, path=None)
                simulations.ideas_district_simulation(project=prj_LOD2_4, simulation=True, analyseSimulation=True,
                                                      analyseGeometry=True)
                LOD2_4_succeeded = True
            except:
                print('There has been an unknown error in ' + streetname + '____________________________________________________________')
                pass
        if LOD2_8 == True and LOD2_4_succeeded == True:
            try:
                prj_LOD2_8 = prj_LOD2
                prj_LOD2_8.name = streetname + "_LOD2_8"
                print(prj_LOD2_8.name)
                prj_LOD2_8.used_library_calc = 'IDEAS'
                orientation_dict_8 = {
                    'North east': [22.5, 67.5, 45.0],
                    'East': [67.5, 110.5, 90.0],
                    'South east': [110.5, 157.5, 135.0],
                    'South': [157.5, 202.5, 180.0],
                    'South west': [202.5, 247.5, 225.0],
                    'West': [247.5, 292.5, 270.0],
                    'North west': [292.5, 337.5, 315.0]}
                citygml_in._merge_orientations(prj=prj_LOD2_8, orientation_dict=orientation_dict_8)
                prj_LOD2_8.calc_all_buildings(
                    raise_errors=True)  # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
                prj_LOD2_8.export_ideas(internal_id=None, path=None, building_model="Detailed", occupant_model= "ISO13790")
                prj_LOD2_8.save_project(file_name=None, path=None)
                simulations.ideas_district_simulation(project=prj_LOD2_8, simulation=True, analyseSimulation=True,
                                                      analyseGeometry=True)
                LOD2_8_succeeded = True
            except:
                print('There has been an unknown error in ' + streetname + '____________________________________________________________')
                pass
        if LOD1_ridge == True and LOD2_8_succeeded == True:
            try:
                prj_LOD1_ridge = Project(load_data=True, used_data_country="Belgium")
                prj_LOD1_ridge.name = streetname + "_LOD1_ridge"
                print(prj_LOD1_ridge.name)
                prj_LOD1_ridge.used_library_calc = 'IDEAS'
                prj_LOD1_ridge.load_citygml(path=path + "Streets_LOD1_Ridge_based/" + streetname + ".gml",
                                            checkadjacantbuildings=True,
                                            number_of_zones=2,
                                            merge_buildings=False)  # no need to merge buildings, 1 building model per building (in fact better: because does not end on _1, sometimes also on _2 or _3)
                prj_LOD1_ridge.calc_all_buildings(
                    raise_errors=True)  # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
                prj_LOD1_ridge.export_ideas(internal_id=None, path=None, building_model="Detailed", occupant_model= "ISO13790")
                prj_LOD1_ridge.save_project(file_name=None, path=None)
                simulations.ideas_district_simulation(project=prj_LOD1_ridge, simulation=True, analyseSimulation=True,
                                                      analyseGeometry=True)
                LOD1_ridge_succeeded = True
            except:
                print('There has been an unknown error in ' + streetname + '____________________________________________________________')
                pass
        if LOD1_halfroof == True and LOD1_ridge_succeeded == True:
            try:
                prj_LOD1_halfroof = Project(load_data=True, used_data_country="Belgium")
                prj_LOD1_halfroof.name = streetname + "_LOD1_halfroof"
                print(prj_LOD1_halfroof.name)
                prj_LOD1_halfroof.used_library_calc = 'IDEAS'
                prj_LOD1_halfroof.load_citygml(path=path + "Streets_LOD1_Half_roof_based/" + streetname + ".gml",
                                               checkadjacantbuildings=True,
                                               number_of_zones=2,
                                               merge_buildings=False)
                prj_LOD1_halfroof.calc_all_buildings(
                    raise_errors=True)  # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
                prj_LOD1_halfroof.save_project(file_name=None, path=None)
                prj_LOD1_halfroof.export_ideas(internal_id=None, path=None, building_model="Detailed", occupant_model= "ISO13790")
                prj_LOD1_halfroof.save_project(file_name=None, path=None)
                simulations.ideas_district_simulation(project=prj_LOD1_halfroof, simulation=True,
                                                      analyseSimulation=True, analyseGeometry=True)
                LOD1_halfroof_succeeded = True
            except:
                print('There has been an unknown error in ' + streetname + '____________________________________________________________')
                pass

        if LOD1_extended == True and LOD1_halfroof_succeeded == True:
            try:
                prj_LOD1_extended = Project(load_data=True, used_data_country="Belgium")
                prj_LOD1_extended.name = streetname + "_LOD1_extended"
                print(prj_LOD1_extended.name)
                prj_LOD1_extended.used_library_calc = 'IDEAS'
                prj_LOD1_extended.load_citygml(path=path + "Streets_LOD1_extended/" + streetname + ".gml",
                                      checkadjacantbuildings=True,
                                      number_of_zones=2,
                                      merge_buildings=True)
                prj_LOD1_extended.calc_all_buildings(
                    raise_errors=True)  # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
                prj_LOD1_extended.export_ideas(internal_id=None, path=None, building_model="Detailed", occupant_model= "ISO13790")
                prj_LOD1_extended.save_project(file_name=None, path=None)
                simulations.ideas_district_simulation(project=prj_LOD1_extended, simulation=True, analyseSimulation=True,
                                                      analyseGeometry=True)
                LOD1_extended_succeeded = True
            except:
                print('There has been an unknown error in ' + streetname + '____________________________________________________________')
                pass
        if LOD2_succeeded == True and LOD1_ridge_succeeded == True and LOD1_halfroof_succeeded == True and LOD2_4_succeeded == True and LOD2_8_succeeded == True and LOD1_extended_succeeded == True:
            streetnames_succeeded.append(streetname)
            print (streetname + " SUCCEEDED COMPLETELY______________________________________________________________________________________________________________________________________________________________________________")
    print ("Original number of streets " + str(len(streetnames)) + ", number of succeeded streets " + str(len(streetnames_succeeded)))

def create_streetnames_from_excel(path_to_excel, name_of_district):
    df_streetnames = pd.read_excel(path_to_excel, sheetname=name_of_district, squeeze=True)
    streetnames = [str(streetname) for streetname in df_streetnames.tolist()]
    return streetnames

def create_streetnames_from_directory(path):
    streetnames = [name[:-4] for name in os.listdir(path)
            if name.endswith(".gml")]
    return streetnames

if __name__ == '__main__':
    example_load_citygml()

    print("Example 10: That's it! :)")