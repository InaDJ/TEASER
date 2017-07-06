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
import pylab as pl
import matplotlib.pyplot as plt
from cycler import cycler

def analyse_simulation_results():
    ''' This function analyses the results and exports them

    Parameters
    ----------
    prj : Project()
        Teaser instance of Project()
    outputDir : string
        complete output directory where the simulation results should be stored
    '''
    number_of_zones = 2
    remove_files = True
    outputDir = "C:\Users\ina\TEASEROutput\Aspergerijstraat_LOD1_ridge\Results/"
    buildingsmatlist = []  # list with building.mat strings
    for file in os.listdir(outputDir):
        if file.endswith(".mat"):
            buildingsmatlist.append(file)
    print buildingsmatlist

    help_file_name = "/TEASER_simulations.csv"
    help_file_simulation = open(outputDir + help_file_name, 'w')
    help_file_simulation.write(
        "Name of building;Peak power[kW];Total energy use[kWh];Specific energy use [kWh/m2];Overheating onezone[Kh];Overheating dayzone[Kh];Overheating nightzone[Kh];\n")
    help_file_simulation.close()

    df_LDC = None
    df_district = None

    # set number of plots and their colors
    colormap = plt.cm.gist_ncar
    plt.gca().set_prop_cycle(cycler('color',[colormap(i) for i in numpy.linspace(0, 0.9, len(buildingsmatlist))]))
    labels = []

    for buildingindex, building in enumerate(buildingsmatlist):
        sim = SimRes(outputDir + "/" + building)  # path to .mat file
        buildingname = building[:-4] #buildingname.mat to buildingname

        dayoverheating = 0
        nightoverheating = 0
        singleoverheating = 0

        if number_of_zones == 1:
            # First, export csv with useful information, resampled every 600 s
            aliases = {'sim.Te': "Outside temperature",
                       buildingname + '_Building.heatingSystem.QHeaSys': "Q heating system building",
                       buildingname + '_Building.heatingSystem.QHeatZone[1]': "Q heating system singlezone",
                       buildingname + '_Building.building.TSensor[1]': "TSensor of singlezone",
                       buildingname + '_Building.building.AZones[1]': "Area of singlezone"}  # name of Dymola variable : name of header of column
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
            pandas.DataFrame.to_csv(df, columns=['Outside temperature / K', 'Q heating system singlezone / W',
                                                 'TSensor of singlezone / K'],
                                    path_or_buf=outputDir + "/" + buildingname + ".csv", sep=";")

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
                df_district[buildingname + ' / W'] = df_district_new_col
                df_district = df_district.set_index('Time / s')
            else:
                df_district[buildingname + ' / W'] = df_district_new_col

            # dataframe with sorted Q of all buildings > required for LDC of all buildings
            df = df.sort_values(by=['Q heating system building / W'], ascending=False)
            df_LDC_new_col = df['Q heating system building / W'].tolist()
            if df_LDC is None:
                df_LDC = pandas.DataFrame()
                df_LDC['Time / s'] = df_LDC_index
                df_LDC[buildingname + ' / W'] = df_LDC_new_col
                df_LDC = df_LDC.set_index('Time / s')
            else:
                df_LDC[buildingname + ' / W'] = df_LDC_new_col

        elif number_of_zones == 2:
            # First, export csv with useful information, resampled every 600 s
            aliases = {'sim.Te': "Outside temperature",
                       buildingname + '_Building.heatingSystem.QHeaSys': "Q heating system building",
                       buildingname + '_Building.heatingSystem.QHeatZone[1]': "Q heating system dayzone",
                       buildingname + '_Building.heatingSystem.QHeatZone[2]': "Q heating system nightzone",
                       buildingname + '_Building.building.TSensor[1]': "TSensor of dayzone",
                       buildingname + '_Building.building.TSensor[2]': "TSensor of nightzone",
                       buildingname + '_Building.building.AZones[1]': "Area of dayzone",
                       buildingname + '_Building.building.AZones[2]': "Area of nightzone"}  # name of Dymola variable : name of header of column
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
            pandas.DataFrame.to_csv(df, columns= ['Outside temperature / K', 'Q heating system dayzone / W', 'Q heating system nightzone / W', 'TSensor of dayzone / K', 'TSensor of nightzone / K'], path_or_buf=outputDir+ "/" +buildingname+".csv", sep= ";")

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
                df_district[buildingname + ' / W'] = df_district_new_col
                df_district = df_district.set_index('Time / s')
            else:
                df_district[buildingname + ' / W'] = df_district_new_col

            # dataframe with sorted Q of all buildings > required for LDC of all buildings
            df = df.sort_values(by = ['Q heating system building / W'], ascending = False)
            df_LDC_new_col = df['Q heating system building / W'].tolist()
            if df_LDC is None:
                df_LDC = pandas.DataFrame()
                df_LDC['Time / s'] = df_LDC_index
                df_LDC[buildingname + ' / W'] = df_LDC_new_col
                df_LDC = df_LDC.set_index('Time / s')
            else:
                df_LDC[buildingname + ' / W'] = df_LDC_new_col

        # append LDC of this building to plot
        plt.plot([i/3600 for i in df_LDC_index], [i/1000 for i in df_LDC[buildingname + ' / W']])
        labels.append(buildingname.replace("_", " "))
        # print all results of this building (1- or 2-zone)
        help_file_simulation = open(outputDir + help_file_name, 'a')
        help_file_simulation.write(
            buildingname + ";" +
            str(peakpower) + ";" +
            str(energyuse) + ";" +
            str(specificenergyuse) + ";" +
            str(singleoverheating) + ";" +
            str(dayoverheating)+ ";" +
            str(nightoverheating) + ";\n")
        help_file_simulation.close()

    # create csv file with all buildings and their LDC as well as LDC of district
    df_district['District / W'] = df_district.sum(axis = 1)
    #pandas.DataFrame.to_csv(df_district, path_or_buf=outputDir + "/TEASER_simulations_district.csv", sep=";")
    df_district = df_district.sort_values(by=['District / W'], ascending=False)
    df_LDC_new_col = df_district['District / W'].tolist()
    df_LDC['District / W'] = df_LDC_new_col
    pandas.DataFrame.to_csv(df_LDC, path_or_buf=outputDir + "/TEASER_simulations_district_LDC.csv", sep=";")

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
    plt.savefig(outputDir + 'LDC.png', bbox_inches = 'tight', dpi = 1000)

    # print district peak power at the end
    districtpeakpower = df_LDC.loc[0, 'District / W']
    districtpeakpower = districtpeakpower / 1000 # W to kW
    help_file_simulation = open(outputDir + help_file_name, 'a')
    help_file_simulation.write("\n \n \n District peak power [kW];" + str(districtpeakpower))
    help_file_simulation.close()

    # remove all .mat files
    if remove_files:
        for building in buildingsmatlist:
            os.remove(outputDir+building)

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
    analyse_simulation_results()
    print("That's it! :)")
