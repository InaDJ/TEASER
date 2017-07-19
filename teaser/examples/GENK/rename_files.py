# Created July 2017
# Ina De Jaeger

"""This module contains some functions to check which files are in multiple folders, and to merge these file.
For CityGML: the last line of the first file needs to be deleted
and the first two lines of the second file need to be deleted
After you merged the files, you should also rename the ID's and names of the buildings/buildingparts.
DON'T FORGET THIS!

Two different modes:
1. compare between folders and merge between folders (for now implemented for 4 folders = 6 combinations)
2. merge specified files within 1 folders (enter the names of the existing files and the name of the new file)

"""

import buildingspy.simulate.Simulator as Si
import time
from multiprocessing import Pool
import teaser.logic.utilities as utilities
import os
import pandas
import numpy
from modelicares import SimRes
import matplotlib.pyplot as plt
from cycler import cycler

def rename_files():
    """
    Parameters
    ----------

    """
    path = "C:\Users\ina\Desktop\GRB/"
    variant1 = "Streets_LOD2"
    variant2 = "Streets_LOD1_Ridge_based"
    variant3 = "Streets_LOD1_Half_roof_based"
    variants = [variant1, variant2, variant3]

    for variant in variants:
        variant_path = path + variant + "/"
        for filename in os.listdir(variant_path):
            if (" " in filename) == True:
                # rename file
                old_filename = filename
                new_filename = filename.replace(" ", "")
                os.rename(variant_path+old_filename, variant_path+new_filename)
                # replace all occurances in gml file
                with open(variant_path+new_filename, 'r') as file:
                    filedata = file.read()
                filedata = filedata.replace(old_filename[:-4], new_filename[:-4]) # delete the .gml at the end
                with open(variant_path+new_filename, 'w') as file:
                    file.write(filedata)
                print (old_filename + " has been changed to " + new_filename)

if __name__ == '__main__':
    rename_files()
    print("That's it! :)")
