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
    LOD1_ridge = False
    LOD1_halfroof = False
    path = "C:\Users\ina\Box Sync\Onderzoek\GRB/"

    streetnames = ["Bandstraat"] #, "Bremstraat", "Brikkenovenstraat", "Broeder Juulstraat", "Broedersstraat", "Buitenlaan", "Clematitenstraat", "C-Mine", "Coghenstraat", "Congostraat", "Craenevenne"]
    #['Ankerstraat', 'Bandstraat', 'Berm', 'Boekrakelaan', 'Boogstraat', 'Boxbergstraat', 'Bremstraat', 'Congostraat', 'Craenevenne', 'De Bek', 'De Heuvel', 'De Mierlik', 'De Roten', 'De Vroente', 'Drijtap', 'Gansenwijer', 'Genkerhei', 'Gilissenweier', 'Gracht', 'Groenven', 'Gruisweg', 'Hasseltweg', 'Hazelnootstraat', 'Heiblok', 'Heidebos', 'Heilapstraat', 'Heiweier', 'Hennepstraat', 'Hoevenhaag', 'Holeven', 'Houtwal', 'Huiskensweier', 'Ijzerven', 'Keistraat', 'Kennipstraat', 'Kievitstraat', 'Kleinven', 'Klotstraat', 'Kneippstraat', 'Krommestraat', 'Landwaartslaan', 'Leemstraat', 'Middenkruis', 'Oosterwennel', 'Oude Heide', 'Oude Zonhoverweg', 'Peerdsdiefweier', 'Plaggenstraat', 'Ploegstraat', 'Rietbeemdstraat', 'Rockxweier', 'Roerstraat', 'Ruisstraat', 'Schalmstraat', 'Sintelstraat', 'Slagmolenweg', 'Spoorstraat', 'Strijphout', 'Turfstraat', 'Vogelzangstraat', 'Wennel', 'Westerwennel', 'Wiekstraat', 'Zandoerstraat', 'Zijgracht', 'Zodenstraat', 'Zonhoverweg', 'Zouwstraat']
    if streetnames == []:
        path_to_excel = "C:\Users\ina\Box Sync\Onderzoek\Projects\Gemeenschappelijke case Genk\Neighbourhood model 0.0.1\Number of buildings in districts\StreetsGenkPerDistrict.xlsx"
        name_of_district = "Boxbergheide"  # name of excel sheet
        streetnames = create_streetnames_from_excel(path_to_excel, name_of_district)

    for streetname in streetnames:
        if LOD2:
            try:
                prj_LOD2 = Project(load_data=True, used_data_country="Belgium")
                prj_LOD2.name = streetname + "_LOD2"
                prj_LOD2.used_library_calc = 'IDEAS'
                prj_LOD2.load_citygml(path=path + "Streets_LOD2/"  +streetname + ".gml",
                                     checkadjacantbuildings=True,
                                     number_of_zones=2,
                                     merge_buildings=True)
                prj_LOD2.calc_all_buildings(raise_errors=True) # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
                for bldg in prj_LOD2.buildings:
                    for zone in bldg.thermal_zones:
                        for wall in zone.outer_walls:
                            print ("Outer wall orientation: " + str(wall.orientation))
                            print ("Outer wall tilt: " + str(wall.tilt))
                        for roof in zone.rooftops:
                            print ("Roof orientation: " + str(roof.orientation))
                            print ("Roof tilt: " + str(roof.tilt))

                #prj_LOD2.export_ideas(internal_id=None,path=None,building_model="Detailed")
                #prj_LOD2.save_project(file_name=None, path=None)
                #simulations.ideas_district_simulation(project=prj_LOD2, simulation=False, analyseSimulation=True, analyseGeometry=True)
            except:
                pass
        if LOD1_ridge:
            try:
                prj_LOD1_ridge = Project(load_data=True, used_data_country="Belgium")
                prj_LOD1_ridge.name = streetname + "_LOD1_ridge"
                prj_LOD1_ridge.used_library_calc = 'IDEAS'
                prj_LOD1_ridge.load_citygml(path=path + "Streets_LOD1_Ridge_based/" +streetname + ".gml",
                                     checkadjacantbuildings=True,
                                     number_of_zones=2,
                                     merge_buildings=False) # no need to merge buildings, 1 building model per building (in fact better: because does not end on _1, sometimes also on _2 or _3)
                prj_LOD1_ridge.calc_all_buildings(raise_errors=True) # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
                prj_LOD1_ridge.export_ideas(internal_id=None,path=None,building_model="Detailed")
                prj_LOD1_ridge.save_project(file_name=None, path=None)
                simulations.ideas_district_simulation(project=prj_LOD1_ridge, simulation=True, analyseSimulation=True, analyseGeometry=True)
            except:
                pass
        if LOD1_halfroof:
            try:
                prj_LOD1_halfroof = Project(load_data=True, used_data_country="Belgium")
                prj_LOD1_halfroof.name = streetname + "_LOD1_halfroof"
                prj_LOD1_halfroof.used_library_calc = 'IDEAS'
                prj_LOD1_halfroof.load_citygml(path=path + "Streets_LOD1_Half_roof_based/" +streetname + ".gml",
                                     checkadjacantbuildings=True,
                                     number_of_zones=2,
                                     merge_buildings=False)
                prj_LOD1_halfroof.calc_all_buildings(raise_errors=True) # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
                prj_LOD1_halfroof.save_project(file_name=None, path=None)
                prj_LOD1_halfroof.export_ideas(internal_id=None,path=None,building_model="Detailed")
                prj_LOD1_halfroof.save_project(file_name=None, path=None)
                simulations.ideas_district_simulation(project=prj_LOD1_halfroof, simulation=True, analyseSimulation=True, analyseGeometry=True)
            except:
                pass

def create_streetnames_from_excel(path_to_excel, name_of_district):
    df_streetnames = pd.read_excel(path_to_excel, sheetname=name_of_district, squeeze=True)
    streetnames = [str(streetname) for streetname in df_streetnames.tolist()]
    return streetnames

if __name__ == '__main__':
    example_load_citygml()

    print("Example 10: That's it! :)")
