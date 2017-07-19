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

    starttime = time.time()

    prj_gml = Project(load_data=True, used_data_country="Belgium")
    prj_gml.name = "Berm_merge"
    prj_gml.used_library_calc = 'IDEAS'

    prj_gml.load_citygml(path= "C:\Users\ina\Box Sync\Onderzoek\GRB\Streets_LOD1_Ridge_based\Berm.gml",
                         checkadjacantbuildings=True,
                         number_of_zones=2,
                         merge_buildings=True,
                         merge_orientations=True,
                         number_of_orientations=8)

    # "C:\Users\ina\Box Sync\Onderzoek\UNDER CONSTRUCTION/4DH2017\FME\Real model build up\Waterschei_works_better.gml",
    prj_gml.number_of_elements_calc = 4
    prj_gml.merge_windows_calc = False
    prj_gml.weather_file_path = utilities.get_full_path(
        os.path.join(
            "data",
            "input",
            "inputdata",
            "weatherdata",
            "DEU_BW_Mannheim_107290_TRY2010_12_Jahr_BBSR.mos"))

    # To make sure the parameters are calculated correctly we recommend to
    # run calc_all_buildings() function
    #prj_gml.calc_all_buildings(raise_errors=True) # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
    # To export the ready-to-run models simply call Project.export_ibpsa().
    # First specify the IBPSA related library you want to export the models
    # for. The models are identical in each library, but IBPSA Modelica
    # library is  just a core set of models and should not be used
    # standalone. Valid values are 'AixLib' (default), 'Buildings',
    # 'BuildingSystems' and 'IDEAS'. We chose AixLib
    # You can specify the path, where the model files should be saved.
    # None means, that the default path in your home directory
    # will be used. If you only want to export one specific building, you can
    # pass over the internal_id of that building and only this model will be
    # exported. In this case we want to export all buildings to our home
    # directory, thus we are passing over None for both parameters.
    prj_gml.save_project(file_name=None, path=None)

    prj_gml.export_ideas(
        internal_id=None,
        path=None,
        building_model="Detailed")

    endtime = time.time()
    print("Pre-processing lasted: " + str((endtime - starttime) / 60) + " minutes.")

    """
    Now we define the output directory where the simulation results should be
    stored, in addition we need to define the path where the exported models
    are
    """
    #simulations.ideas_district_simulation(project=prj_gml, simulation=True, analyseGeometry=True)

    for bldgindex, bldg in enumerate(prj_gml.buildings):
        print("Building name: " + bldg.name)
        for zoneindex, zone in enumerate(bldg.thermal_zones, start=1):
            print("Zone name: " + str(zone.name) + " " + str(zone.internal_id))
            print("Zone floor number: " + str(zone.floor_number))
            print ("Zone area: " + str(zone.area))
            print("Building number of floors: " + str(bldg.number_of_floors))
            print(zone.parent.parent.used_library_calc)
            # loop all building elements of this zone
            buildingelements = zone.outer_walls + zone.inner_walls + zone.windows + zone.rooftops + zone.ground_floors + zone.ceilings + zone.floors
            count_outerwalls_area = 0
            count_rooftops_area = 0
            count_groundfloors_area = 0
            count_innerwalls_area = 0
            count_ceilings_area = 0
            count_floors_area = 0
            count_windows_area = 0
            for elementindex, buildingelement in enumerate(buildingelements, start=1):
                print(buildingelement.name + " has a tilt of " + str(buildingelement.tilt) + " and an orient of " + str(
                    buildingelement.orientation) + " and an area of " + str(buildingelement.area))

    """
        print("Printing gml_surfaces for building " + str(bldg.name))
        for gml_surface in bldg.gml_surfaces:
            print("Area: " + str(gml_surface.surface_area))
            print("Orientation: " + str(gml_surface.surface_orientation))
            print("Tilt: " + str(gml_surface.surface_tilt))
            print("/")
            """

if __name__ == '__main__':
    example_load_citygml()

    print("Example 10: That's it! :)")
