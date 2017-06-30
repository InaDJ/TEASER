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

def ideas_district_simulation(project, simulation=True, analyseSimulation=False, analyseGeometry=False, outputDir=None, packageDir=None):
    """
    This function simulates a project with buildings.

    Parameters
    ----------
    prj : Project()
        Teaser instance of Project()
    outputDir : string
        complete output directory where the simulation results should be stored
    packageDir : string
        complete output directory where the exported models are (top level package.mo and package.order files)
    """
    prj = project

    if packageDir is None:
        packagepath = utilities.get_default_path() + "/" + prj.name
    else:
        packagepath = packageDir
    utilities.create_path(packagepath)

    if outputDir is None:
        outputpath = packagepath + "/Results"
    else:
        outputpath = outputDir
    utilities.create_path(outputpath)

    if simulation:
        starttime = time.time()

        """
        Now we need to create a simulation list for buildingspy
        """

        li = []
        for bld in prj.buildings:
            # this is necessary for the correct names in the simulation script
            name = prj.name + "." + bld.name + "." + bld.name  # path to runable building.mo files
            s = Si.Simulator(name, "dymola", outputpath, packagepath)
            li.append(s)

        po = Pool(processes=3)
        po.map(simulate_case, li)

        endtime = time.time()
        print('Simulation lasts: ', endtime - starttime, ' seconds or ', (endtime - starttime) / 60, ' minutes! or',
              (endtime - starttime) / (60 * 60), 'hours.')

        if analyseSimulation:
            analyse_simulation_results(outputDir=outputpath)

    if analyseGeometry:
        analyse_geometry_results(outputDir=outputpath, project=prj)

def simulate_case(s):
    """ Set common parameters and run a simulation.

    :param s: A simulator object.

    """
    s.showGUI(show=False)
    s.setStartTime(-2592000)    # simulate one month before the actual simulations
    s.setStopTime(3.1536e7)     # simulate one year
    s.setNumberOfIntervals(56880)  # per 10 min: 56880, per hour: 9480 (there are 34,128,000 s in 13 months)
    s.setSolver("Dassl")
    s.showProgressBar(show=True)
    s.printModelAndTime()
    s.simulate()


def analyse_simulation_results(outputDir):
    ''' This function analyses the results and exports them

    Parameters
    ----------
    prj : Project()
        Teaser instance of Project()
    outputDir : string
        complete output directory where the simulation results should be stored
    '''

    buildingsmatlist = []  # list with building.mat strings
    for file in os.listdir(outputDir):
        if file.endswith(".mat"):
            buildingsmatlist.append(file)

    help_file_name = "/TEASER_simulations.csv"
    help_file_simulation = open(outputDir + help_file_name, 'w')
    help_file_simulation.write(
        "Name of building;Peak power[W];Total energy use[J];Overheating[Ks];\n")
    help_file_simulation.close()

    districtpeakpower = list() #list that sums the peak power of the individual buildings

    for buildingindex, building in enumerate(buildingsmatlist):
        sim = SimRes(outputDir + "/" + building)  # path to .mat file
        buildingname = building[:-4] #buildingname.mat to buildingname
        aliases = {'sim.Te': "Outside temperature",
                   buildingname + '_Building.heatingSystem.QHeaSys': "Q heating system",
                   buildingname + '_Building.building.TSensor[1]': "TSensor of zone"}  # name of Dymola variable : name of header of column
        dfwithalltimes = sim.to_pandas(list(aliases), aliases)
        df = dfwithalltimes.loc[lambda df: df.index > 0, :]  # dataframe, starting with time = 0 (more or less)
        pandas.DataFrame.to_csv(df, path_or_buf=outputDir+ "/" +buildingname+".csv", sep= ";")

        # calculate peak power of all buildings to csv file
        maxvariables = pandas.DataFrame.max(df)  # method for peak power, return a pandas series

        # calculate energy use for space heating
        timearray = df.index.values
        qarray = df['Q heating system / W'].values
        energyuse = numpy.trapz(y=qarray, x=timearray)

        # calculate overheating = K.h (over 25degC = 298.15 K)
        temparray = df["TSensor of zone / K"].values
        overheatingarray = [(temp - 298.15) for temp in temparray]  # this array contains all temp - 25degC, if negative, set to 0, then integrate
        for index, temp in enumerate(overheatingarray):
            if temp < 0.0:
                overheatingarray[index] = 0.0
        overheating = numpy.trapz(y=overheatingarray, x=timearray)

        # add all powers of all buildings, in order to get the peak power of the district
        # assumes that all timesteps of all buildings are equal (!!! not true if different user behaviour)
        # TODO: create a dataframe with timesteps of 10 minutes (not 10 min AND each event)
        if buildingindex == 0:
            # create list for the first time
            for element in qarray:
                districtpeakpower.append(element)
        else:
            # list exists, make the sum of each element respectively
            for index, element in enumerate(qarray):
                districtpeakpower[index] += element

        # print all results of this building
        help_file_simulation = open(outputDir + help_file_name, 'a')
        help_file_simulation.write(
            buildingname + ";" + str(maxvariables.loc['Q heating system / W']) + ";" + str(energyuse) + ";" + str(
                overheating) + ";\n")
        help_file_simulation.close()

    #print district peak power at the end
    help_file_simulation = open(outputDir + help_file_name, 'a')
    help_file_simulation.write("\n \n \n District peak power;" + str(max(districtpeakpower)))
    help_file_simulation.close()

def analyse_geometry_results(outputDir, project):
    """             prj,
                   building_model="Detailed",
                   merge_windows=False,
                   internal_id=None,
                   exportpath=None):
    Exports values to a record file for IDEAS simulation

    The Export function for creating a IDEAS example model

    Parameters
    ----------
    building_model : str
        setter of the used IDEAS building model
        (Currently only detailed is supported)
    merge_windows : bool
            True for merging the windows into the outer walls, False for
            separate resistance for window, default is False
    internal_id : float
        setter of the used building which will be exported, if None then
        all buildings will be exported
    exportpath : string
        if the Files should not be stored in OutputData, an alternative
        path can be specified as a full and absolute path

    """
    starttime = time.time()

    help_file_name = "/TEASER_geometry.csv"
    help_file_geometry = open(outputDir + help_file_name, 'w')
    help_file_geometry.write(
        "Name of building;Number of neighbours;Number of floors;Volume of building;\
        Area of building;Groundfloor area;Outerwall area;Window area;\
        Deleted wall area;Innerwall area;Floor area;Total loss area (walls+windows+roof+groundfloor);Total loss area (every house is detached);\n")
    help_file_geometry.close()

    for bldgindex, bldg in enumerate(project.buildings):
        building_volume = 0
        building_area = 0

        count_outerwalls_area = 0
        count_windows_area = 0
        count_rooftops_area = 0
        count_groundfloors_area = 0
        count_innerwalls_area = 0
        count_floors_area = 0

        for zoneindex, zone in enumerate(bldg.thermal_zones, start = 1):
            building_volume += zone.volume
            building_area += zone.area

            for bldg_element in zone.outer_walls:
                count_outerwalls_area += bldg_element.area

            for bldg_element in zone.windows:
                count_windows_area += bldg_element.area

            for bldg_element in zone.rooftops:
                count_rooftops_area += bldg_element.area

            for bldg_element in zone.ground_floors:
                count_groundfloors_area += bldg_element.area

            for bldg_element in zone.inner_walls:
                count_innerwalls_area += bldg_element.area

            for bldg_element in zone.floors:
                count_floors_area += bldg_element.area

        help_file_geometry = open(outputDir + help_file_name, 'a')
        help_file_geometry.write(str(bldg.name) + ";" + str(len(bldg.list_of_neighbours)) + ";" +
                                str(bldg.number_of_floors) +";" + str(building_volume) + ";" +
                                str(building_area) +";" + str(count_groundfloors_area) + ";" +
                                str(count_outerwalls_area) + ";" + str(count_windows_area) + ";" +
                                str(bldg.deleted_surfaces_area) + ";" + str(count_innerwalls_area) + ";" +
                                str(count_floors_area) + ";" +
                                str(count_outerwalls_area+count_windows_area+count_groundfloors_area+count_rooftops_area) + ";" +
                                str(count_outerwalls_area+count_windows_area+count_groundfloors_area+count_rooftops_area+bldg.deleted_surfaces_area) +
                                "\n")
        help_file_geometry.close()

    endtime = time.time()
    print("Geometrical analysis lasted: " + str((endtime - starttime) / 60) + " minutes. Exports can be found here:")
    print(outputDir + help_file_name)



if __name__ == '__main__':
    ideas_district_simulation()
    print("That's it! :)")
