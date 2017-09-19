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

def ideas_district_simulation(project, simulation=True, analyseSimulation=True, analyseGeometry=True, outputDir=None, packageDir=None, resultsDir = None):
    """
    This function simulates a project with buildings.
    First, the buildings are simulated.
    Then, the energy KPIs are analysed.
    Finally, the geometry KPIs are analysed.

    Parameters
    ----------
    prj : Project()
        Teaser instance of Project()
    simulation : bool
        Do the buildings need to be simulated?
    analyseSimulation : bool
        Do the energy KPIs need to be analysed?
    analyseGeometry : bool
        Do the geometry KPIs need to be analysed?
    outputDir : string
        complete output directory where the simulation results should be stored
    packageDir : string
        complete output directory where the exported models are (top level package.mo and package.order files)
    resultsDir : string
        complete outputdirectory where the analysis results should be stored
    """
    prj = project

    if packageDir is None: # where modelica files are
        packagepath = utilities.get_default_path() + "/" + prj.name
    else:
        packagepath = packageDir
    utilities.create_path(packagepath)

    if outputDir is None: # where .mat files should come
        outputpath = packagepath + "/Results"
    else:
        outputpath = outputDir
    utilities.create_path(outputpath)

    if resultsDir is None: # where analysis .csv files should come
        resultspath = utilities.get_default_path() + "/Results/" + prj.name.split('_')[0] # folder with streetname
    else:
        resultspath = resultsDir
    utilities.create_path(resultspath)

    if simulation:
        starttime = time.time()
        print ("Starting simulations")

        """
        Now we need to create a simulation list for buildingspy
        """

        li = []
        for bld in prj.buildings:
            # this is necessary for the correct names in the simulation script
            name = prj.name + "." + bld.name + "." + bld.name  # path to runable building.mo files
            s = Si.Simulator(name, "dymola", outputpath, packagepath)
            li.append(s)

        po = Pool(15)
        po.map(simulate_case, li)

        endtime = time.time()
        help_file_name = "/" + prj.name + "_timeKPI.csv"
        help_file_simulation = open(resultspath + help_file_name, 'a')
        help_file_simulation.write("Simulating [s];" + str(endtime - starttime) + ";\n")
        help_file_simulation.close()

    if analyseSimulation:
        analyse_simulation_results(project = prj, outputDir=outputpath, resultsDir = resultspath)

    if analyseGeometry:
        analyse_geometry_results(project=prj, outputDir=outputpath, resultsDir = resultspath)

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

def analyse_simulation_results(project, outputDir, resultsDir, remove_files = True):
    ''' This function analyses the results and exports them

    Parameters
    ----------
    prj : Project()
        Teaser instance of Project()
    outputDir : string
        complete output directory where the simulation results should be stored e.g. "C:\Users\ina\TEASEROutput\Aspergerijstraat_LOD1_ridge\Results/"
    '''
    starttime = time.time()
    print ("Starting analysis of energy KPIs")

    buildingsmatlist = [file for file in os.listdir(outputDir) if
                        file.endswith(".mat")]  # list with building.mat strings
    print buildingsmatlist

    help_file_name = "/" + project.name + "_energyKPI.csv"
    help_file_simulation = open(resultsDir + help_file_name, 'w')
    help_file_simulation.write(
        "Name of building;Peak power[kW];Total energy use[kWh];Specific energy use [kWh/m2];Overheating onezone[Kh];Overheating dayzone[Kh];Overheating nightzone[Kh];\n")
    help_file_simulation.close()

    df_LDC = None
    df_district = None

    # set number of plots and their colors
    colormap = plt.cm.gist_ncar
    plt.gca().set_prop_cycle(cycler('color',[colormap(i) for i in numpy.linspace(0, 0.6, len(buildingsmatlist))]))
    labels = []

    for buildingindex, building in enumerate(project.buildings):
        if building.name+'.mat' in buildingsmatlist:
            sim = SimRes(outputDir + "/" + building.name + ".mat")  # path to .mat file

            dayoverheating = 0
            nightoverheating = 0
            singleoverheating = 0

            if project.number_of_zones == 2 and building.number_of_floors != 1:
                # First, export csv with useful information, resampled every 600 s
                aliases = {'QHeaSys': "Q heating system building",
                           'QHeatZone[1]': "Q heating system dayzone",
                           'QHeatZone[2]': "Q heating system nightzone",
                           'TSensor[1]': "TSensor of dayzone",
                           'TSensor[2]': "TSensor of nightzone",
                           'AZones[1]': "Area of dayzone",
                           'AZones[2]': "Area of nightzone"}  # name of Dymola variable : name of header of column
                df = sim.to_pandas(list(aliases), aliases)
                df = df.loc[lambda df: df.index > 0, :]  # dataframe, starting with time = 0 (more or less)
                # create column with datetime based on the index (which is in seconds)
                df['Datetime'] = pandas.to_datetime(df.index, unit='s')
                # set this new column as index
                df = df.set_index('Datetime')
                # resample in 600s (= 10 min) and take the mean value (resample method is only valid with datetime)
                df = df.resample('600s').mean()
                # convert the index back to seconds (unix time is in nanoseconds, so divide by 10^9) (required for trapzintegration)
                df.index = df.index.astype(numpy.int64)
                df.index = df.index/10**9
                df_LDC_index = df.index
                pandas.DataFrame.to_csv(df, columns= ['Q heating system dayzone / W',
                                                      'Q heating system nightzone / W',
                                                      'TSensor of dayzone / K',
                                                      'TSensor of nightzone / K'],
                                        path_or_buf=resultsDir+ "/" + project.name + "_" + building.name + ".csv",
                                        sep= ";")

                # Second, calculate KPIs to add to TEASER_simulations.csv
                # calculate energy use for space heating [J = Ws]
                timearray = df.index.values
                qarray = df['Q heating system building / W'].values
                energyuse = numpy.trapz(y=qarray, x=timearray)
                # calculate energy use for space heating [kWh]
                energyuse = energyuse/1000/3600
                # calculate energy use for space heating per floor area [kWh/m2]
                area = df.loc[0, 'Area of dayzone / m2'] + df.loc[0, 'Area of nightzone / m2']
                specificenergyuse = energyuse/area
                # calculate overheating of dayzone [Ks] (over 25degC = 298.15 K)
                daytemparray = df["TSensor of dayzone / K"].values
                dayoverheatingarray = [(temp - 298.15) for temp in
                                       daytemparray]  # this array contains all temp - 25degC, if negative, set to 0, then integrate
                for index, temp in enumerate(dayoverheatingarray):
                    if temp < 0.0:
                        dayoverheatingarray[index] = 0.0
                dayoverheating = numpy.trapz(y=dayoverheatingarray, x=timearray)
                # calculate overheating of dayzone [Kh]
                dayoverheating = dayoverheating/3600
                # calculate overheating of nightzone [Ks] (over 25degC = 298.15 K)
                nighttemparray = df["TSensor of nightzone / K"].values
                nightoverheatingarray = [(temp - 298.15) for temp in
                                         nighttemparray]
                for index, temp in enumerate(nightoverheatingarray):
                    if temp < 0.0:
                        nightoverheatingarray[index] = 0.0
                nightoverheating = numpy.trapz(y=nightoverheatingarray, x=timearray)
                # calculate overheating of nightzone [Kh]
                nightoverheating = nightoverheating / 3600
                # calculate peak power building [W]
                maxvariables = pandas.DataFrame.max(df) # returns pandas series with max values for all columns
                peakpower = maxvariables.loc['Q heating system building / W']
                # calculate peak power building [kW]
                peakpower = peakpower/1000

                # Third, create dataframe for all Q heating system of the district > Load Duration Curve
                # dataframe with unsorted Q of all buildings > required to determine Q district
                df_district_new_col = df['Q heating system building / W'].tolist()
                if df_district is None:
                    df_district = pandas.DataFrame()
                    df_district['Time / s'] = df_LDC_index
                    df_district[building.name + ' / W'] = df_district_new_col
                    df_district = df_district.set_index('Time / s')
                else:
                    df_district[building.name + ' / W'] = df_district_new_col

                # dataframe with sorted Q of all buildings > required for LDC of all buildings
                df = df.sort_values(by = ['Q heating system building / W'], ascending = False)
                df_LDC_new_col = df['Q heating system building / W'].tolist()
                if df_LDC is None:
                    df_LDC = pandas.DataFrame()
                    df_LDC['Time / s'] = df_LDC_index
                    df_LDC[building.name + ' / W'] = df_LDC_new_col
                    df_LDC = df_LDC.set_index('Time / s')
                else:
                    df_LDC[building.name + ' / W'] = df_LDC_new_col

            elif project.number_of_zones == 1 or building.number_of_floors == 1:
                # First, export csv with useful information, resampled every 600 s
                aliases = {'QHeaSys': "Q heating system building",
                           'QHeatZone[1]': "Q heating system singlezone",
                           'TSensor[1]': "TSensor of singlezone",
                           'AZones[1]': "Area of singlezone"}  # name of Dymola variable : name of header of column
                df = sim.to_pandas(list(aliases), aliases)
                df = df.loc[lambda df: df.index > 0, :]  # dataframe, starting with time = 0 (more or less)
                # create column with datetime based on the index (which is in seconds)
                df['Datetime'] = pandas.to_datetime(df.index, unit='s')
                # set this new column as index
                df = df.set_index('Datetime')
                # resample in 600s (= 10 min) and take the mean value (resample method is only valid with datetime)
                df = df.resample('600s').mean()
                # convert the index back to seconds (unix time is in nanoseconds, so divide by 10^9) (required for trapzintegration)
                df.index = df.index.astype(numpy.int64)
                df.index = df.index / 10 ** 9
                df_LDC_index = df.index
                pandas.DataFrame.to_csv(df, columns=['Q heating system singlezone / W',
                                                     'TSensor of singlezone / K'],
                                        path_or_buf=resultsDir + "/" + project.name + "_" + building.name + ".csv",
                                        sep=";")

                # Second, calculate KPIs to add to TEASER_simulations.csv
                # calculate energy use for space heating [J = Ws]
                timearray = df.index.values
                qarray = df['Q heating system building / W'].values
                energyuse = numpy.trapz(y=qarray, x=timearray)
                # calculate energy use for space heating [kWh]
                energyuse = energyuse / 1000 / 3600
                # calculate energy use for space heating per floor area [kWh/m2]
                area = df.loc[0, 'Area of singlezone / m2']
                specificenergyuse = energyuse / area
                # calculate overheating of singlezone [Ks] (over 25degC = 298.15 K)
                singletemparray = df["TSensor of singlezone / K"].values
                singleoverheatingarray = [(temp - 298.15) for temp in
                                       singletemparray]  # this array contains all temp - 25degC, if negative, set to 0, then integrate
                for index, temp in enumerate(singleoverheatingarray):
                    if temp < 0.0:
                        singleoverheatingarray[index] = 0.0
                singleoverheating = numpy.trapz(y=singleoverheatingarray, x=timearray)
                # calculate overheating of singlezone [Kh]
                singleoverheating = singleoverheating / 3600
                # calculate peak power building [W]
                maxvariables = pandas.DataFrame.max(df)  # returns pandas series with max values for all columns
                peakpower = maxvariables.loc['Q heating system building / W']
                # calculate peak power building [kW]
                peakpower = peakpower / 1000

                # Third, create dataframe for all Q heating system of the district > Load Duration Curve
                # dataframe with unsorted Q of all buildings > required to determine Q district
                df_district_new_col = df['Q heating system building / W'].tolist()
                if df_district is None:
                    df_district = pandas.DataFrame()
                    df_district['Time / s'] = df_LDC_index
                    df_district[building.name + ' / W'] = df_district_new_col
                    df_district = df_district.set_index('Time / s')
                else:
                    df_district[building.name + ' / W'] = df_district_new_col

                # dataframe with sorted Q of all buildings > required for LDC of all buildings
                df = df.sort_values(by=['Q heating system building / W'], ascending=False)
                df_LDC_new_col = df['Q heating system building / W'].tolist()
                if df_LDC is None:
                    df_LDC = pandas.DataFrame()
                    df_LDC['Time / s'] = df_LDC_index
                    df_LDC[building.name + ' / W'] = df_LDC_new_col
                    df_LDC = df_LDC.set_index('Time / s')
                else:
                    df_LDC[building.name + ' / W'] = df_LDC_new_col

            # append LDC of this building to plot
            plt.plot([i/3600 for i in df_LDC_index], [i/1000 for i in df_LDC[building.name + ' / W']])
            labels.append(building.name.replace("_", " "))
            # print all results of this building (1- or 2-zone)
            help_file_simulation = open(resultsDir + help_file_name, 'a')
            help_file_simulation.write(
                building.name + ";" +
                str(peakpower) + ";" +
                str(energyuse) + ";" +
                str(specificenergyuse) + ";" +
                str(singleoverheating) + ";" +
                str(dayoverheating)+ ";" +
                str(nightoverheating) + ";\n")
            help_file_simulation.close()

    # create csv file with all buildings and their LDC as well as LDC of district
    df_district['District / W'] = df_district.sum(axis = 1)
    #pandas.DataFrame.to_csv(df_district, path_or_buf=resultsDir + "/TEASER_simulations_district.csv", sep=";")
    df_district = df_district.sort_values(by=['District / W'], ascending=False)
    df_LDC_new_col = df_district['District / W'].tolist()
    df_LDC['District / W'] = df_LDC_new_col
    pandas.DataFrame.to_csv(df_LDC,
                            path_or_buf=resultsDir + "/" + project.name + "_LDC.csv",
                            sep=";")

    # save plot
    plt.legend(labels, loc='upper right',
               bbox_to_anchor=[1.05, 1],
               columnspacing=1.0, labelspacing=0.0,
               handletextpad=0.0, handlelength=1.5,
               fancybox=True, shadow=True)
    plt.grid()
    plt.ylim(ymin=-0.25)
    plt.xlim(xmin=-50,xmax=8760)
    plt.xlabel('Time [h]')
    plt.ylabel('Power [kW]')
    plt.title('Load duration curves for space heating')
    plt.savefig(resultsDir + "/" + project.name + '_LDC.png', bbox_inches = 'tight', dpi = 1000)
    plt.close()

    # print district peak power at the end
    districtpeakpower = df_LDC.loc[0, 'District / W']
    districtpeakpower = districtpeakpower / 1000 # W to kW
    help_file_simulation = open(resultsDir + help_file_name, 'a')
    help_file_simulation.write("\n\n\nDistrict peak power [kW];" + str(districtpeakpower))
    help_file_simulation.close()

    # remove all .mat files
    if remove_files:
        for building in buildingsmatlist:
            os.remove(outputDir+"/"+building)
    endtime = time.time()
    help_file_name = "/" + project.name + "_timeKPI.csv"
    help_file_simulation = open(resultsDir + help_file_name, 'a')
    help_file_simulation.write("Analysing energy KPIs [s];" + str(endtime - starttime) + ";\n")
    help_file_simulation.close()

def analyse_geometry_results(project, outputDir, resultsDir):
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
    print ("Starting analysis of geometry KPIs")

    help_file_name =  "/" + project.name + "_geometryKPI.csv"
    help_file_geometry = open(resultsDir + help_file_name, 'w')
    help_file_geometry.write(
        "Name of building;Number of neighbours;Number of floors;Volume of building[m3];\
        Area of building[m2];Groundfloor area[m2];Outerwall area[m2];Window area[m2];\
        Deleted wall area[m2];Innerwall area[m2];Floor area[m2];Total loss area (walls+windows+roof+groundfloor)[m2];Total loss area (every house is detached)[m2];\n")
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

        help_file_geometry = open(resultsDir + help_file_name, 'a')
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
    help_file_name = "/" + project.name + "_timeKPI.csv"
    help_file_simulation = open(resultsDir + help_file_name, 'a')
    help_file_simulation.write("Analysing geometry KPIs [s];" + str(endtime - starttime) + ";\n")
    help_file_simulation.close()

if __name__ == '__main__':
    ideas_district_simulation()
    print("That's it! :)")
