# Created June 2017
# Ina De Jaeger

"""This module contains an example how to import TEASER projects from
*.teaserXML and pickle in order to reuse data.
"""

import teaser.logic.utilities as utilities
import teaser.data.output.ideas_district_simulation as simulations
import os
import time


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
    streetname = "Talingpark"

    starttime = time.time()

    prj_LOD2 = Project(load_data=True, used_data_country="Belgium")
    prj_LOD2.name = streetname + "_LOD2"
    prj_LOD2.used_library_calc = 'IDEAS'
    prj_LOD2.load_citygml(path="C:\Users\ina\Box Sync\Onderzoek\GML\Streets_LOD2/"+streetname+".gml",
                         checkadjacantbuildings=True,
                         number_of_zones=2,
                         merge_buildings=True)
    prj_LOD2.calc_all_buildings(raise_errors=True) # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
    prj_LOD2.export_ideas(internal_id=None,path=None,building_model="Detailed")

    prj_LOD1_ridge = Project(load_data=True, used_data_country="Belgium")
    prj_LOD1_ridge.name = streetname + "_LOD1_ridge"
    prj_LOD1_ridge.used_library_calc = 'IDEAS'
    prj_LOD1_ridge.load_citygml(path="C:\Users\ina\Box Sync\Onderzoek\GML\Streets_LOD1_Ridge_based/"+streetname+".gml",
                         checkadjacantbuildings=True,
                         number_of_zones=2,
                         merge_buildings=True)
    prj_LOD1_ridge.calc_all_buildings(raise_errors=True) # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
    prj_LOD1_ridge.export_ideas(internal_id=None,path=None,building_model="Detailed")

    prj_LOD1_halfroof = Project(load_data=True, used_data_country="Belgium")
    prj_LOD1_halfroof.name = streetname + "_LOD1_halfroof"
    prj_LOD1_halfroof.used_library_calc = 'IDEAS'
    prj_LOD1_halfroof.load_citygml(path="C:\Users\ina\Box Sync\Onderzoek\GML\Streets_LOD1_Half_roof_based/"+streetname+".gml",
                         checkadjacantbuildings=True,
                         number_of_zones=2,
                         merge_buildings=True)
    prj_LOD1_halfroof.calc_all_buildings(raise_errors=True) # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
    prj_LOD1_halfroof.save_project(file_name=None, path=None)
    prj_LOD1_halfroof.export_ideas(internal_id=None,path=None,building_model="Detailed")

    endtime = time.time()
    print("Pre-processing lasted: " + str((endtime - starttime) / 60) + " minutes.")

    #simulations.ideas_district_simulation(project=prj_LOD2, simulation=False, analyseGeometry=True)
    #simulations.ideas_district_simulation(project=prj_LOD1_ridge, simulation=False, analyseGeometry=True)
    #simulations.ideas_district_simulation(project=prj_LOD1_halfroof, simulation=False, analyseGeometry=True)

if __name__ == '__main__':
    example_load_citygml()

    print("Example 10: That's it! :)")
