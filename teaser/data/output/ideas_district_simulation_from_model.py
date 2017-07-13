# Created June 2017
# Ina De Jaeger

"""This module contains some function to simulate projects and analyse energy results
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

def ideas_district_simulation_from_model(prj_name = "Berenbroekstraat_LOD2", matDir = "C:\Users\ina\Desktop\Results2/", simulation=True, outputDir=None, packageDir=None, resultsDir=None):
    """
    This function simulates the building model of an exported project which has not yet been simulated.
    This script only simulates them, does not perform any analysis (this needs to be done through the regular way (run_simulations_per_street.py)
    How to use?
        Fill in the prj_name above
        Fill in the directory where the .mat files can be found
        Check in the model directory if it are the last 4 files from the list that need to be deleted, if not: change below

    Parameters
    ----------
    prj : Project()
        Teaser instance of Project()
    outputDir : string
        complete output directory where the simulation results should be stored
    packageDir : string
        complete output directory where the exported models are (top level package.mo and package.order files)
    """
    prj_name = prj_name
    if packageDir is None: # where modelica files are
        packagepath = utilities.get_default_path() + "/" + prj_name
    else:
        packagepath = packageDir
    utilities.create_path(packagepath)

    if outputDir is None: # where .mat files should come
        outputpath = packagepath + "/Results"
    else:
        outputpath = outputDir
    utilities.create_path(outputpath)

    if resultsDir is None: # where analysis .csv files should come
        resultspath = "C:\Users\ina\Box Sync\Onderzoek\Results/" + prj_name.split('_')[0] # folder with streetname
    else:
        resultspath = resultsDir
    utilities.create_path(resultspath)

    if simulation:
        starttime = time.time()
        print ("Starting simulations")

        """
        Now we need to create a simulation list for buildingspy
        """

        buildingsmatlist = [file for file in os.listdir(matDir) if
                            file.endswith(".mat")]  # list with building.mat strings
        buildingsmatlist = [bldg[:-4] for bldg in buildingsmatlist]
        print ("List with building.mat files (" + str(len(buildingsmatlist)) + ")")
        print buildingsmatlist

        buildingmodellist = [name for name in os.listdir(packagepath)] # list with building.mo strings
        buildingmodellist = buildingmodellist[:-4] # last 4 files are not building maps (check for this case, may also be first 4)
        print ("List with building.mo files (" + str(len(buildingmodellist)) + ")")
        print buildingmodellist

        buildingsimlist = [bldg for bldg in buildingmodellist if
                           bldg not in buildingsmatlist] # list with models that need to be simulated
        print ("List with buildings to be simulated (" + str(len(buildingsimlist)) + ")")
        print buildingsimlist

        li = []
        for bld in buildingsimlist:
            # this is necessary for the correct names in the simulation script
            name = prj_name + "." + bld + "." + bld  # path to runable building.mo files
            s = Si.Simulator(name, "dymola", outputpath, packagepath)
            li.append(s)

        po = Pool(3)
        po.map(simulate_case, li)

        endtime = time.time()
        help_file_name = "/" + prj_name + "_timeKPI.csv"
        help_file_simulation = open(resultspath + help_file_name, 'a')
        help_file_simulation.write("Simulating [s];" + str(endtime - starttime) + ";\n")
        help_file_simulation.close()

    print("Simulation and KPI analysis are finished. Exports can be found here:")
    print(resultspath)

def simulate_case(s):
    """ Set common parameters and run a simulation.

    :param s: A simulator object.

    """
    s.showGUI(show=False)
    s.setStartTime(-2592000)    # simulate one month before the actual simulations
    s.setStopTime(3.1536e7)     # simulate one year
    s.setNumberOfIntervals(56880)  # per 10 min: 56880, per hour: 9480 (there are 34,128,000 s in 13 months)
    s.setSolver("Lsodar")
    s.showProgressBar(show=True)
    s.printModelAndTime()
    s.simulate()

if __name__ == '__main__':
    ideas_district_simulation_from_model()
    print("That's it! :)")
