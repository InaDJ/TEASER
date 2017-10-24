# Created June 2017
# Ina De Jaeger

"""This module contains some function to simulate projects and analyse energy results
"""

import buildingspy.simulate.Simulator as Si
import time
from multiprocessing import Pool
import teaser.logic.utilities as utilities
import os
import pandas as pd
import numpy as np
from modelicares import SimRes
import matplotlib.pyplot as plt
import statsmodels.api as sm
from cycler import cycler
from shutil import copyfile

def extract_unmerged_streets_blacklist():
    xls = pd.ExcelFile("D:\Ina\Data\Generate blacklist for teaser\TEASER_buildings_blacklist.xlsx")
    df = xls.parse('TEASER_unmerged', parse_cols='C')
    buildings_unmerged = df.as_matrix()
    buildings_unmerged =[i.split('_')[0] for [i] in buildings_unmerged]
    streets_unmerged = list(set(buildings_unmerged))
    streets_unmerged = ['Oude Hofstraat', 'Dr. Loriersstraat', 'Gouverneur Alex. Galopinstraat']
    print streets_unmerged
    for street in streets_unmerged:
        for dirpath, dirnames, filenames in os.walk("D:\Ina\Data\GRB\Genk_LOD2_VITO"):
            for filename in [f for f in filenames if f.endswith(street+"_WallSurface.shp")]:
                print os.path.join(dirpath, filename)
                copyfile(os.path.join(dirpath, filename), os.path.join("D:\Ina\Data\GRB2\Extra streets to do blacklist", filename))
            for filename in [f for f in filenames if f.endswith(street + "_RoofSurface.shp")]:
                print os.path.join(dirpath, filename)
                copyfile(os.path.join(dirpath, filename),os.path.join("D:\Ina\Data\GRB2\Extra streets to do blacklist", filename))
            for filename in [f for f in filenames if f.endswith(street+"_WallSurface.dbf")]:
                print os.path.join(dirpath, filename)
                copyfile(os.path.join(dirpath, filename), os.path.join("D:\Ina\Data\GRB2\Extra streets to do blacklist", filename))
            for filename in [f for f in filenames if f.endswith(street + "_RoofSurface.dbf")]:
                print os.path.join(dirpath, filename)
                copyfile(os.path.join(dirpath, filename),os.path.join("D:\Ina\Data\GRB2\Extra streets to do blacklist", filename))
    # then the files are in 1 folder, then use automater in FME on this folder!
if __name__ == '__main__':
    extract_unmerged_streets_blacklist()
    print("That's it! :)")
