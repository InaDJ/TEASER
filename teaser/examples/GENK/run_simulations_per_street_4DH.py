# Created June 2017
# Ina De Jaeger

"""This module contains an example how to import TEASER projects from
*.teaserXML and pickle in order to reuse data.
"""

import teaser.logic.utilities as utilities
import teaser.data.output.ideas_district_simulation as simulations
import os
import time
import pandas as pd
import sys
import teaser.data.input.citygml_input as citygml_in

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
    LOD2 = False
    LOD1_ridge = False
    LOD1_halfroof = False
    LOD2_4 = True
    LOD2_8 = True
    path = "D:\Ina\GRB/"

    streetnames = ['Turfstraat', 'Strijphout', 'Zouwstraat']
    streetnamesLOD1halfroof = ['Heiweier', 'Hoevenhaag', 'Kneippstraat', 'Krommestraat', 'Middenkruis', 'Peerdsdiefweier', 'Rockxweier', 'Turfstraat', 'Westerwennel']
    streetnamesLOD1ridge = ['Kneippstraat', 'Krommestraat', 'Peerdsdiefweier', 'Zonhoverweg']
    streetnames = ['Schalmstraat', 'Sintelstraat'] #LOD2 'Hasseltweg',
    streetnames = ['DeVroente', 'Genkerhei', 'Kievitstraat', 'Kleinven', 'Middenkruis', 'Oosterwennel', 'OudeHeide', 'OudeZonhoverweg', 'Peerdsdiefweier', 'Schalmstraat', 'Sintelstraat', 'Slagmolenweg', 'Strijphout', 'Turfstraat', 'Wennel', 'Westerwennel', 'Wiekstraat', 'Zouwstraat'] # LOD2_4 'Hasseltweg',
    streetnames =['DeVroente', 'Genkerhei', 'OudeHeide', 'OudeZonhoverweg', 'Ruisstraat', 'Schalmstraat', 'Slagmolenweg'] #['Craenevenne', 'DeVroente', 'Genkerhei', 'Kleinven', 'Krommestraat', 'Middenkruis', 'Oosterwennel', 'OudeHeide', 'OudeZonhoverweg', 'Sintelstraat', 'Strijphout', 'Turfstraat', 'Westerwennel', 'Zouwstraat'] # LOD2_8 'Hasseltweg',
    streetnames = ['Hasseltweg']

    if streetnames == []:
        path_to_excel = "C:\Users\ina\Box Sync\Onderzoek\Projects\Gemeenschappelijke case Genk\Neighbourhood model 0.0.1\Number of buildings in districts\StreetsGenkPerDistrict.xlsx"
        name_of_district = "Boxbergheide"  # name of excel sheet
        streetnames = create_streetnames_from_excel(path_to_excel, name_of_district)

    for streetname in streetnames:
        print streetname
        if LOD2:
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
                prj_LOD2.export_ideas(internal_id=None, path=None, building_model="Detailed", occupant_model="ISO13790")
                prj_LOD2.save_project(file_name=None, path=None)
                simulations.ideas_district_simulation(project=prj_LOD2, simulation=True, analyseSimulation=True,
                                                      analyseGeometry=True)
            except:
                print('There has been an unknown error____________________________________________________________')
                pass
        if LOD1_ridge:
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
                prj_LOD1_ridge.export_ideas(internal_id=None, path=None, building_model="Detailed",
                                            occupant_model="ISO13790")
                prj_LOD1_ridge.save_project(file_name=None, path=None)
                simulations.ideas_district_simulation(project=prj_LOD1_ridge, simulation=True, analyseSimulation=True,
                                                      analyseGeometry=True)
            except:
                print('There has been an unknown error____________________________________________________________')
                pass
        if LOD1_halfroof:
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
                prj_LOD1_halfroof.export_ideas(internal_id=None, path=None, building_model="Detailed",
                                               occupant_model="ISO13790")
                prj_LOD1_halfroof.save_project(file_name=None, path=None)
                simulations.ideas_district_simulation(project=prj_LOD1_halfroof, simulation=True,
                                                      analyseSimulation=True, analyseGeometry=True)
            except:
                print('There has been an unknown error____________________________________________________________')
                pass
        if LOD2_4:
            try:
                prj_LOD2_4 = Project(load_data=True, used_data_country="Belgium")
                prj_LOD2_4.name = streetname + "_LOD2_4"
                print(prj_LOD2_4.name)
                prj_LOD2_4.used_library_calc = 'IDEAS'
                prj_LOD2_4.load_citygml(path=path + "Streets_LOD2/" + streetname + ".gml",
                                        checkadjacantbuildings=True,
                                        number_of_zones=2,
                                        merge_buildings=True,
                                        merge_orientations=True,
                                        number_of_orientations=4)
                prj_LOD2_4.calc_all_buildings(
                    raise_errors=True)  # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
                prj_LOD2_4.export_ideas(internal_id=None, path=None, building_model="Detailed",
                                        occupant_model="ISO13790")
                prj_LOD2_4.save_project(file_name=None, path=None)
                simulations.ideas_district_simulation(project=prj_LOD2_4, simulation=True, analyseSimulation=True,
                                                      analyseGeometry=True)
            except:
                e = sys.exc_info()[0]
                print("Error: %s" % e)
                print('There has been an unknown error____________________________________________________________')
                pass
        if LOD2_8:
            try:
                prj_LOD2_8 = Project(load_data=True, used_data_country="Belgium")
                prj_LOD2_8.name = streetname + "_LOD2_8"
                print(prj_LOD2_8.name)
                prj_LOD2_8.used_library_calc = 'IDEAS'
                prj_LOD2_8.load_citygml(path=path + "Streets_LOD2/" + streetname + ".gml",
                                        checkadjacantbuildings=True,
                                        number_of_zones=2,
                                        merge_buildings=True,
                                        merge_orientations=True,
                                        number_of_orientations=8)
                prj_LOD2_8.calc_all_buildings(
                    raise_errors=True)  # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
                prj_LOD2_8.export_ideas(internal_id=None, path=None, building_model="Detailed",
                                        occupant_model="ISO13790")
                prj_LOD2_8.save_project(file_name=None, path=None)
                simulations.ideas_district_simulation(project=prj_LOD2_8, simulation=True, analyseSimulation=True,
                                                      analyseGeometry=True)
            except:
                print('There has been an unknown error____________________________________________________________')
                pass

def create_streetnames_from_excel(path_to_excel, name_of_district):
    df_streetnames = pd.read_excel(path_to_excel, sheetname=name_of_district, squeeze=True)
    streetnames = [str(streetname) for streetname in df_streetnames.tolist()]
    return streetnames

if __name__ == '__main__':
    example_load_citygml()

    print("Example 10: That's it! :)")