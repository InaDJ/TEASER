# Created June 2017
# Ina De Jaeger

"""This module contains an example how to import TEASER projects from
*.teaserXML and pickle in order to reuse data.
"""

import teaser.logic.utilities as utilities
import os


def example_load_excel():
    """"This function demonstrates different loading options of TEASER"""
    from teaser.project import Project

    # The last option to import data into TEASER is using an Excel file. The
    # import of CityGML underlies some limitations e.g. concerning data
    # given in the file and the way the buildings are modeled. If you run this example script,
    # a Python script will be generated in the specified folder. If you run this Python script,
    # your project will be generated and exported to an IDEAS model (either One-zone or ROM (with 4 elements))

    excel_path = "C:\Users\ina\Desktop/170615Genk_LOD1_Summary.xlsx" #SPECIFY, loaded sheetname = Summary
    prj = Project(load_data=True)
    prj.name = excel_path[(excel_path.rindex("/") + len("/")):(excel_path.rindex(".xlsx",(excel_path.rindex("/") + len("/"))))] #project name = name of excel

    python_file_directory= utilities.get_full_path(("examples/GENK/")) #SPECIFY
    utilities.create_path(utilities.get_full_path(python_file_directory))

    ideas_building_model = "One-zone"
    prj.load_excel(excel_path, python_file_directory, ideas_building_model)

if __name__ == '__main__':
    example_load_excel()

    print("Example 12: That's it! :)")
