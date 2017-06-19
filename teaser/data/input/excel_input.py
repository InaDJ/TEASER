# Created June 2017
# Ina De Jaeger (KU Leuven, EnergyVille)

"""ideas_output

This module contains function to call Templates for IDEAS model generation
"""
import os
import teaser.logic.utilities as utilities
import pandas as pd
import numpy as np
from mako.template import Template

def import_from_excel(path=None,
                 building_model="One-zone"):
    """ Imports buildings from excel

        This function uses Mako Templates specified in
        data.output.modelicatemplates.ideas

        Parameters
        ----------
        buildings : list of instances of Building
            list of TEASER instances of a Building that is exported to IDEAS
             models. If you want to export a single building,
            please pass it over as a list containing only that building.
        prj : instance of Project
            Instance of TEASER Project object to access Project related
            information, e.g. name or version of used libraries
        path : string
            if the Files should not be stored in default output path of TEASER,
            an alternative path can be specified as a full path
        building_model : string
            Currently, only export to one-zone models is supported. Two-zone models
            will be added soon

        LOOK FOR #SPECIFY AND ADD CORRECT DATA
        """
    #READ EXCEL
    excel_path = "C:\Users\ina\Desktop/170615Genk_LOD1_Summary.xlsx" #SPECIFY
    df = pd.read_excel(excel_path,
                       sheetname= "Summary",
                       header=0,
                       index_col=None)
    print("This project contains " + str(len(df.index)) + " buildings. Now creating python script to generate these buildings in TEASER.") #each line is one building

    #CREATE FIRST PART OF PYTHON SCRIPT
    project_name = excel_path[(excel_path.rindex("/") + len("/")):(excel_path.rindex(".xlsx",(excel_path.rindex("/") + len("/"))))] #project name = name of excel
    used_data_country = "Belgium"
    python_file_directory= utilities.get_full_path(("examples/GENK/")) #SPECIFY
    utilities.create_path(utilities.get_full_path(python_file_directory))
    python_file_path = python_file_directory + project_name + ".py"
    teaser_project_start_template = Template(filename=utilities.get_full_path
    ("data/input/inputtemplates/teaser_project_start_from_excel"))  # do not include template .txt
    out_file = open(python_file_path, 'w')
    out_file.write(teaser_project_start_template.render_unicode(
        project_name=project_name,
        used_data_country=used_data_country))
    out_file.close()

    #CREATE ALL BUILDINGS WITHIN PROJECT
    for index, row in df.iterrows():    #to iterate rows and get their values based on column-names
        name_of_building = row["name_of_building"]
        street_of_building = str(row["Street"]) + " " + str(row["Number"])
        city_of_building = row["City"]
        year_of_construction = row["year_of_construction"]
        number_of_floors = row["number_of_floors"]
        height_of_floors = row["height_of_floors"]
        total_floor_area = row["total_floor_area"]
        volume_of_zone = row["volume_of_zone"]
        infiltration_rate = 5/20            #n50-value divided by 20
        wall_north_area = row["wall_N"]
        wall_east_area = row["wall_E"]
        wall_south_area = row["wall_S"]
        wall_west_area = row["wall_W"]
        window_north_area = row["window_N"]
        window_east_area = row["window_E"]
        window_south_area = row["window_S"]
        window_west_area = row["window_W"]
        roof_tilt = row["roof_tilt"]
        roof_north_area = row["roof_north_area"]
        roof_east_area = row["roof_east_area"]
        roof_south_area = row["roof_south_area"]
        roof_west_area = row["roof_west_area"]
        inner_wall_area = row["internal_wall_area"]
        ground_floor_area = row["ground_floor_area"]
        inner_floor_area = row["internal_floor_area"]
        ceiling_area = row["internal_floor_area"]

        teaser_building_template = Template(filename=utilities.get_full_path
        ("data/input/inputtemplates/teaser_building_from_excel"))  # do not include template .txt
        out_file = open(python_file_path, 'a')
        out_file.write(teaser_building_template.render_unicode(
                name_of_building=name_of_building,
                street_of_building=street_of_building,
                city_of_building=city_of_building,
                year_of_construction=year_of_construction,
                number_of_floors=number_of_floors,
                height_of_floors=height_of_floors,
                total_floor_area=total_floor_area,
                volume_of_zone=volume_of_zone,
                infiltration_rate=infiltration_rate,
                wall_north_area=wall_north_area,
                wall_east_area=wall_east_area,
                wall_south_area=wall_south_area,
                wall_west_area=wall_west_area,
                window_north_area=window_north_area,
                window_east_area=window_east_area,
                window_south_area=window_south_area,
                window_west_area=window_west_area,
                roof_tilt=roof_tilt,
                roof_north_area=roof_north_area,
                roof_east_area=roof_east_area,
                roof_south_area=roof_south_area,
                roof_west_area=roof_west_area,
                inner_wall_area=inner_wall_area,
                ground_floor_area=ground_floor_area,
                inner_floor_area=inner_floor_area,
                ceiling_area=ceiling_area))
        out_file.close()

    #CREATE FINAL PART OF PYTHON SCRIPT
    number_of_elements_in_ROM = 4
    ideas_building_model = "One-zone"
    assert ideas_building_model in ["One-zone", "ROM"]
    teaser_project_end_template = Template(filename=utilities.get_full_path
    ("data/input/inputtemplates/teaser_project_end_from_excel"))  # do not include template .txt
    out_file = open(python_file_path, 'a')
    out_file.write(teaser_project_end_template.render_unicode(
        number_of_elements_in_ROM=number_of_elements_in_ROM,
        ideas_building_model=ideas_building_model))
    out_file.close()

    #RUN PYTHON SCRIPT > manually !

if __name__ == '__main__':
    import_from_excel()
    print("That's it! :)")