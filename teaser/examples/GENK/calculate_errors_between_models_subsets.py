# Created June 2017
# Ina De Jaeger

"""This module contains some function to simulate projects and analyse energy results
"""

import os
import pandas
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as sm
import statsmodels as sms
from cycler import cycler
import random
from sklearn.utils import shuffle
import math

def report_errors():
    inputDir = "D:\Ina\Simulations\Models_final\Results/"
    outputDir = "D:\Ina/Results10/"
    variants = ['LOD2', 'LOD1_ridge','LOD1_halfroof','LOD1_extended', 'LOD2_4', 'LOD2_8']

    streetnames = []

    # 'Roerstraat', 'Akkerstraat', 'DeRoten', 'Gansenwijer', 'Heiblok', 'Heidebos','Keistraat', 'Klotstraat']
    # [] #leave empty if you want to the whole directory '
    #  'Blookstraat', 'Bochtlaan','Bodemstraat', 'Boekrakelaan', 'Boektveldstraat', 'Boekweitstraat',

    # 'Roerstraat', 'Akkerstraat', 'DeRoten', 'Gansenwijer', 'Heiblok', 'Heidebos','Keistraat', 'Klotstraat']
    # [] #leave empty if you want to the whole directory '

    if streetnames == []:
        streetnames = [name for name in os.listdir(inputDir)]

    analysisALL = True
    analysisPERSTREET = False

    if analysisALL:
        # calculate all errors
        outputDirdistr = outputDir + "ALL/"
        if not os.path.exists(outputDirdistr):
            os.makedirs(outputDirdistr)
        calculate_errors_between_models(inputDir=inputDir, outputDir=outputDirdistr, variants=variants, streetnames=streetnames)

    if analysisPERSTREET:
        # calculate errors per street
        for streetname in streetnames:
            outputDirstreet = outputDir + streetname + "/"
            if not os.path.exists(outputDirstreet):
                os.makedirs(outputDirstreet)
            calculate_errors_between_models(inputDir=inputDir, outputDir=outputDirstreet, variants=variants, streetnames=[streetname])

def calculate_errors_between_models(inputDir=None, outputDir=None, variants=None, streetnames=None):
    '''
    How to work with multi-index:
    #print df
    #print df['LOD2'] # returns subdataframe with all KPI's of this variant
    #print df['LOD2', 'Number of floors'] # returns subsubdataframe (= series) with the specified KPI of this variant = 1 column
    #print df.loc['Dwarsstraat'] #returns subdataframe, based on row: all buildings of this street
    #print df.loc['Dwarsstraat', 'Dwarsstraat_1'] return subsubdataframe (=series) with the specified building of this street
    #print df[variant].loc[street] #returns one street in one variant
    #print df.xs('Number of floors', level='KPI', axis=1, drop_level=False) #prints the number of floors-column of all variants for all streets
    '''

    # Options !
    analyse_streets = True
    analyse_district = True
    analyse_time = True
    compare_variants = False
    analyse_representativeness = False
    analyse_standard_err = True

    export_drawings = False
    boxplots = False
    histograms = True
    scatter = False

    key_KPIs = []

    print variants
    print streetnames
    print ('Number of streets: ' + str(len(streetnames)))

    # Excel writer
    variantnames = '_'.join(variants)  # converts variants list to string, separated by _
    writer = pandas.ExcelWriter(outputDir + '/District_' + variantnames + ".xlsx")

    # Create dataframe with all variants and all streets (buildings with no simulation results were already deleted)
    df, df_time, unsucceeded_streets = create_dataframe(variants=variants, streetnames=streetnames, inputDir=inputDir, outputDir=outputDir)
    streetnames = list(set(streetnames).difference(unsucceeded_streets))
    print streetnames
    print ('Number of streets: ' + str(len(streetnames)))
    df = cleanup_dataframe(df=df, outputDir=outputDir)

    # Analyse on building level (buildings with no valid input are deleted)
    df_buildings = analyse_building_level(variants=variants, streetnames=streetnames, df=df, writer=writer)
    df_buildings_absolute = df.loc[df_buildings.index]  # take only absolute values of valid buildings

    # Analyse on street level
    if analyse_streets:
        df_streets = analyse_street_level(streetnames=streetnames, df_buildings=df_buildings, writer=writer)

    # Analyse on district level
    if analyse_district:
        df_district, df_results = analyse_district_level(variants=variants, df_buildings=df_buildings, writer=writer)
        df_district2, df_results2 = analyse_district_level(variants=variants, df_buildings=df_buildings_absolute, writer=writer, sheetname='District_absolute')

    # Analyse time KPIs
    if analyse_time:
        df_time = analyse_time_KPI(df_time = df_time,variants=variants, writer=writer)

    if compare_variants:
        # Variations within approaches > separate function (makes figure with subplot for each KPI and all variants on each subplot)
        variations_within_approaches(df=df, df_buildings=df_buildings, outputDir=outputDir,
                                     variants = ['LOD1_ridge', 'LOD1_halfroof', 'LOD1_extended', 'LOD2'],
                                     linestyles = ['-', '-.', '--', '-'],
                                     colors = ['black', 'black', 'black', 'grey'],
                                     kpis = ['Total loss area[m2]', 'Heated volume[m3]', 'Total energy use[kWh]'],
                                     title = 'LOD1 models vs LOD2 reference model')
        variations_within_approaches(df=df, df_buildings=df_buildings, outputDir=outputDir,
                                     variants=['LOD2', 'LOD2_8', 'LOD2_4'],
                                     linestyles=['-', '-.', '--'],
                                     colors=['grey', 'grey', 'grey'],
                                     kpis=['Total energy use[kWh]', 'Overheating day zone[Kh]'],
                                     title='LOD2 models vs LOD2 reference model')

        # Variations between approaches > separate function
        variations_between_approaches(df_buildings=df_buildings, outputDir=outputDir)

    # Analyse representativeness > separate function
    if analyse_representativeness:
        is_this_dataset_representative(df_buildings=df_buildings_absolute, variant="LOD2", kpi="Total energy use[kWh]", outputDir=outputDir)

    if analyse_standard_err:
        analyse_standard_error(df_buildings_absolute=df_buildings_absolute, variant="LOD2", kpi="Total energy use[kWh]", outputDir=outputDir)

    # Export drawings
    if export_drawings:
        export_drawing(df=df, df_buildings=df_buildings, variants=variants, outputDir=outputDir, boxplots=boxplots, histograms=histograms, scatter=scatter)

    writer.save()
    writer.close()

def create_dataframe(variants, streetnames, inputDir, outputDir):
    """This function returns a multi-indexed dataframe for a proper analysis of the KPIs.
        DataFrame:
        Highest column label = variant, lowest column label = KPI
        Highest row index = street, lowest row index = building
    """
    unsucceeded_streets = []
    # /////////////// First create dataframe with buildings
    df_all = None
    for streetname in streetnames:
        try: # try per street, if not succeeded due to IO error, then report
            df_variants = None
            for variant in variants:
                # df with buildingnames as indices, geometryKPI and energyKPI as columns
                df_street_geom = pandas.read_csv(
                    inputDir + streetname + "/" + streetname + "_" + variant + "_geometryKPI.csv",
                    sep=";", usecols=range(0, 8) + [9, 10, 11], index_col=0, na_values=['inf'])
                df_street_geom.groupby(df_street_geom.index).last() #remove duplicative indices
                df_street_geom['Roof area[m2]'] = df_street_geom['Total loss area (walls+windows+roof+groundfloor)[m2]'] \
                                                        - df_street_geom['Outerwall area[m2]'] \
                                                        - df_street_geom['Window area[m2]'] \
                                                        - df_street_geom['Groundfloor area[m2]']
                                    # add roof area = total loss - window - wall - groundfloor
                df_street_ener = pandas.read_csv(
                    inputDir + streetname + "/" + streetname + "_" + variant + "_energyKPI.csv",
                    sep=";", usecols=range(0, 7), index_col=0, na_values=['inf'])
                df_street_ener = df_street_ener[:-1]  # drop last row with district peak power
                df_street_ener.groupby(df_street_ener.index).first()  # remove duplicative indices
                df_street = df_street_geom.merge(df_street_ener, how='inner', left_index=True,
                                                 right_index=True, sort=True)  # create union of keys, if one building is not in both csv, then you'll get NaNs
                # first set column indices right (highest level is variant, lower level is KPI)
                df_street_trans = df_street.T  # we need to transpose
                df_street_trans['KPI'] = df_street_trans.index  # create column based on indices of transpose
                df_street_trans['Variant'] = [variant] * df_street.shape[1]  # create column with variant name
                df_street_trans.set_index(['Variant', 'KPI'], inplace=True)  # set indices to transpose
                df_street = df_street_trans.T  # transpose back to normal df_street
                # then set row indices right (highest level is street, lower level is building name
                df_street['Street'] = [streetname] * df_street.shape[0]  # new column with streetname
                df_street.set_index(['Street', df_street.index], inplace=True)
                if df_variants is None:
                    #append to df_variants with all variants for this street
                    df_variants = df_street
                else:
                    #append to df_variants with all existing variants for this street
                    df_variants = df_variants.merge(df_street, how = 'outer', left_index=True, right_index=True)
            # All variants for this street are created, now append to df_all with all streets and all variants
            if df_all is None:
                df_all = df_variants
            else:
                df_all = pandas.concat([df_all,df_variants])
        except IOError:
            print ("Geometry and energy KPIs were incomplete for " + streetname)
            unsucceeded_streets.append(streetname)
    df_all.rename(columns={'Number of neighbours': 'Number of neighbours',
                           'Number of floors': 'Number of floors',
                           'Volume of building[m3]' : 'Heated volume[m3]',
                            '        Area of building[m2]': 'Heated floor area[m2]',
                            'Groundfloor area[m2]': 'Groundfloor area[m2]',
                            'Outerwall area[m2]': 'External wall area[m2]',
                            'Window area[m2]': 'Window area[m2]',
                            'Innerwall area[m2]': 'Internal wall area[m2]',
                            'Floor area[m2]':'Internal floor area[m2]',
                            'Total loss area (walls+windows+roof+groundfloor)[m2]': 'Total loss area[m2]',
                            'Roof area[m2]': 'Roof area[m2]',
                            'Peak power[kW]': 'Peak power[kW]',
                            'Total energy use[kWh]': 'Total energy use[kWh]',
                            'Specific energy use [kWh/m2]': 'Specific energy use[kWh/m2]',
                            'Overheating onezone[Kh]': 'Overheating one zone[Kh]',
                            'Overheating dayzone[Kh]': 'Overheating day zone[Kh]',
                            'Overheating nightzone[Kh]': 'Overheating night zone[Kh]'},
                    inplace=True)
    df_buildings = df_all

    # /////////////// Second create dataframe with timeKPI
    # Create dataframe with timeKPIs for the streets
    df_all = None
    for streetname in streetnames:
        try:
            df_variants = None
            df_street_time_ref = None
            for variant in variants:
                # df with buildingnames as indices, geometryKPI and energyKPI as columns
                df_street_time = pandas.read_csv(
                        inputDir + streetname + "/" + streetname + "_" + variant + "_timeKPI.csv",
                        sep=";", index_col=0, na_values=['inf'], header=None, usecols=[0,1]) # this df is already "transposed" (rows are columns)
                df_street_time.rename(columns={1: streetname}, inplace=True)
                # first set column indices right (highest level is variant, lower level is KPI)
                if 'Merging main building with extensions [s]' in df_street_time.index: #LOD1 is nog merged
                    df_street_time.drop('Merging main building with extensions [s]', inplace=True)
                if 'Number of buildings after merging [-]' in df_street_time.index:
                    df_street_time.drop('Number of buildings after merging [-]', inplace=True)
                if 'Number of buildings [-]' in df_street_time.index:
                    df_street_time.drop('Number of buildings [-]', inplace=True)
                if 'Analysing energy KPIs [s]' in df_street_time.index:
                    df_street_time.drop('Analysing energy KPIs [s]', inplace=True)
                if 'Analysing geometry KPIs [s]' in df_street_time.index:
                    df_street_time.drop('Analysing geometry KPIs [s]', inplace=True)

                df_street_time = df_street_time[~df_street_time.index.duplicated(keep='last')] # delete multiple records
                # Complement incomplete timeKPI for LOD2_4 and LOD2_8
                if variant == 'LOD2':
                    df_street_time_ref = df_street_time
                else:
                    pass
                if variant == 'LOD2_4' or variant == 'LOD2_8':
                    df_street_time.loc['Creating project [s]'] = df_street_time_ref.loc[('LOD2','Creating project [s]')]
                    df_street_time.loc['Searching for adjacent buildings [s]'] = df_street_time_ref.loc[('LOD2','Searching for adjacent buildings [s]')]
                df_street_time.loc['TOTAL [s]'] = df_street_time.sum(axis=0)
                df_street_time['KPI'] = df_street_time.index  # create column based on indices of transpose
                df_street_time['Variant'] = [variant] * df_street_time.shape[0]  # create column with variant name
                df_street_time.set_index(['Variant', 'KPI'], inplace=True)  # set indices to transpose
                df_street_time = df_street_time.T  # transpose to wanted format of df_street
                df_street_time.dropna(inplace=True)
                if df_variants is None:
                    # append to df_variants with all variants for this street
                    df_variants = df_street_time
                else:
                    # append to df_variants with all existing variants for this street
                    df_variants = df_variants.merge(df_street_time, how='outer', left_index=True, right_index=True)

            # All variants for this street are created, now append to df_all with all streets and all variants
            if df_all is None:
                df_all = df_variants
            else:
                df_all = df_all.append(df_variants)
        except:
            print ("TimeKPIs were incomplete for " + streetname)
    # Delete streets that are incomplete
    street_na = list(df_all[df_all.isnull().any(axis=1)].index)
    print ('Streets whose timeKPIs were complete: ' + str(len(street_na)))
    df_all.dropna(subset=[('LOD2_4','Simulating [s]')], inplace=True)

    df_time = df_all
    df_time.reindex_axis(sorted(df_time.columns), axis=1)

    # Collect number of buildings per street to calculate weighted average for timeKPI
    df_all_number = None
    for streetname in streetnames:
        try:
            variant = 'LOD1_ridge'
            # df with buildingnames as indices, geometryKPI and energyKPI as columns
            df_street_time = pandas.read_csv(
                        inputDir + streetname + "/" + streetname + "_" + variant + "_timeKPI.csv",
                        sep=";", index_col=0, na_values=['inf'], header=None, usecols=[0,1]) # this df is already "transposed" (rows are columns)
            df_street_time.rename(columns={1: streetname}, inplace=True)
            df_street_time = df_street_time.loc['Number of buildings [-]']
            df_street_time = df_street_time.T  # transpose to wanted format of df_street
            df_street_time.dropna(inplace=True)
            # All variants for this street are created, now append to df_all with all streets and all variants
            if df_all_number is None:
                df_all_number = df_street_time
            else:
                df_all_number = df_all_number.append(df_street_time)
        except:
            pass
    df_all_number = df_all_number.to_frame() # convert serties to frame, contains all streets with their number of buildings

    df_time[('General','Number of buildings')] = df_all_number
    df_time.to_excel(outputDir + "df_time.xlsx")

    return df_buildings, df_time, unsucceeded_streets

def cleanup_dataframe(df, outputDir):
    """This function cleans up the created dataframe.
        - remove duplicates
        - remove buildings with inf as input
        - remove buildings with 0 as input

    :param df:
    :param outputDir:
    :return:
    """

    df.to_excel(outputDir + "df_original.xlsx")

    # Remove duplicative buildings
    #bldg_dup = [bldg[1] for bldg in list(df[df.index.duplicated(keep='first')].index)]
    #print ('Building who were duplicates: ' + str(len(bldg_dup) + len(list(set(bldg_dup)))))  # +1 omdat er steeds 1 duplicate wegvalt
    #print list(set(bldg_dup))
    df = df[~df.index.duplicated(keep=False)]
    print ('Number of buildings in original dataframe: ' + str(df.shape[0])) # don't count duplicates in original df

    # Delete buildings with inf as input values
    bldg_inf = [bldg[1] for bldg in list(df[df.isnull().any(axis=1)].index)]
    print ('Building who had inf in their input values: ' + str(len(bldg_inf)))
    print bldg_inf
    df= df.dropna()

    # Delete building with 0 as input values for geometry
    bldg_0 = []
    for kpi in list(set(df.columns.get_level_values(1).tolist())):
        if kpi in ['Number of neighbours', 'Overheating one zone[Kh]', 'Overheating day zone[Kh]',
                   'Overheating night zone[Kh]']:
            pass  # values in these columns are allowed to be zero
        else:
            bldg_0_list = [bldg[1] for bldg in list(df[df.xs(kpi, level='KPI', axis=1, drop_level=False).isin([0]).any(
                axis=1)].index)]  # look column per column for a non-zero row and append to bldg_0 (take second value of indices)
            bldg_0 += bldg_0_list
    bldg_0 = list(set(bldg_0))  # remove duplicates in list
    print ('Buildings who had 0 in their input values: ' + str(len(bldg_0)))
    print bldg_0
    for bldg in bldg_0:
        streetname = bldg.split('_')[0]
        df.loc[streetname, bldg] = np.nan
    df = df.dropna()

    # Export modified df
    print ('Number of buildings in modified dataframe: ' + str(df.shape[0]))
    df.to_excel(outputDir + "df_modified.xlsx")

    return df

def analyse_building_level(variants, streetnames, df, writer):
    # Analyse on building level
    df_buildings = None
    bldg_nan_neigh = []
    bldg_nan_gf = []
    for streetname in streetnames:
        df_variants = None
        for variantindex, variant in enumerate(variants, start=0):
            if variantindex == 0:
                df_reference = df[variant].loc[streetname]
            else:
                df_comparison = df[variant].loc[streetname]
                df_pe = percentage_error(df_actual=df_reference, df_forecast=df_comparison, checkbuildings=True)
                bldg_nan_neigh += df_pe[1]
                bldg_nan_gf += df_pe[2]
                df_pe = df_pe[0]
                # first set column indices right (highest level is variant, lower level is KPI)
                df_pe_trans = df_pe.T  # we need to transpose
                df_pe_trans['KPI'] = df_pe_trans.index  # create column based on indices of transpose
                df_pe_trans['Variant'] = [variant] * df_pe.shape[1]  # create column with variant name
                df_pe_trans.set_index(['Variant', 'KPI'], inplace=True)  # set indices to transpose
                df_pe = df_pe_trans.T  # transpose back to normal df_pe
                # then set row indices right (highest level is street, lower level is building name
                df_pe['Street'] = [streetname] * df_pe.shape[0]  # new column with streetname
                df_pe.set_index(['Street', df_pe.index], inplace=True)
                if df_variants is None:
                    # append to df_variants with all variants for this street
                    df_variants = df_pe
                else:
                    # append to df_variants with all existing variants for this street
                    df_variants = df_variants.merge(df_pe, how='inner', left_index=True, right_index=True)
        # All variants for this street are created, now append to df_buildings with all streets and all variants
        if df_buildings is None:
            df_buildings = df_variants
        else:
            df_buildings = pandas.concat([df_buildings, df_variants])
    print ('Buildings who differed in number of neighbours: ' + str(len(list(set(bldg_nan_neigh)))))
    print list(set(bldg_nan_neigh))
    print ('Buildings who differed in groundfloor area: ' + str(len(list(set(bldg_nan_gf)))))
    print list(set(bldg_nan_gf))
    print ('Number of buildings in buildings PE dataframe: ' + str(df_buildings.shape[0]))
    df_buildings=df_buildings.iloc[list(range(700))]
    print (str(df_buildings.shape[0]))
    df_buildings.to_excel(writer, 'Buildings')
    return df_buildings

def analyse_street_level(streetnames, df_buildings, writer):
    # Analyse on street level
    df_streets = None
    for streetname in streetnames:
        df_street_pe = df_buildings.loc[streetname]
        number_of_buildings = df_street_pe.shape[0]
        # calculate mean
        df_street_mean = mean_percentage_error(df_pe=df_street_pe)  # returns a Series
        df_street_mean = df_street_mean.to_frame()  # converts Series to Frame, so we can transpose
        df_street_mean = df_street_mean.T  # each street is a row in the bigger dataframe
        df_street_mean['General', 'Number of buildings'] = number_of_buildings
        df_street_mean['Street'] = streetname
        df_street_mean['Statistic'] = 'Mean'
        # calculate stdev
        df_street_std = stdev_percentage_error(df_pe=df_street_pe)  # returns a Series
        df_street_std = df_street_std.to_frame()  # converts Series to Frame, so we can transpose
        df_street_std = df_street_std.T  # each street is a row in the bigger dataframe
        df_street_std['General', 'Number of buildings'] = " "
        df_street_std['Street'] = streetname
        df_street_std['Statistic'] = 'STD'
        # sdd mean and stdev to 1 dataframe
        df_street_mpe = pandas.concat([df_street_mean, df_street_std])
        df_street_mpe.set_index([('Street'), ('Statistic')], inplace=True)
        if df_streets is None:
            df_streets = df_street_mpe
        else:
            df_streets = pandas.concat([df_streets, df_street_mpe])

    df_streets.to_excel(writer, 'Streets')
    return df_streets

def analyse_district_level(variants, df_buildings, writer, sheetname='District'):
    # Analyse on district level
    # calculate mean
    number_of_buildings = df_buildings.shape[0]
    df_district_mean = df_buildings.mean()  # returns a Series
    df_district_mean = df_district_mean.to_frame()  # converts Series to Frame, so we can transpose
    df_district_mean = df_district_mean.T
    df_district_mean['General', 'Number of buildings'] = number_of_buildings
    df_district_mean['Statistic'] = 'Mean'
    df_district_mean.set_index(['Statistic'], inplace=True)  # set index for this street
    # calculate stdev
    df_district_std = df_buildings.std() # returns a Series
    df_district_std = df_district_std.to_frame()  # converts Series to Frame, so we can transpose
    df_district_std = df_district_std.T
    df_district_std['General', 'Number of buildings'] = number_of_buildings
    df_district_std['Statistic'] = 'STD'
    df_district_std.set_index(['Statistic'], inplace=True)  # set index for this street
    # calculate root mean square error
    df_district_rmse = df_buildings.pow(2)
    df_district_rmse = df_district_rmse.mean()
    df_district_rmse = df_district_rmse.pow(0.5)
    df_district_rmse = df_district_rmse.to_frame()  # converts Series to Frame, so we can transpose
    df_district_rmse = df_district_rmse.T
    df_district_rmse['General', 'Number of buildings'] = number_of_buildings
    df_district_rmse['Statistic'] = 'RMSE'
    df_district_rmse.set_index(['Statistic'], inplace=True)  # set index for this street
    # sdd mean and stdev to 1 dataframe
    df_district = pandas.concat([df_district_rmse, df_district_mean, df_district_std])

    # re-order df_district to df_results
    df_results = None
    if 'LOD2' in [i[0] for i in list(df_district)]:
        startindex = 1 # startindex is 1 and 0 is passed
    else:
        startindex = 0 # startindex is 0 and 0 is passed

    for variantindex, variant in enumerate(variants, start=startindex):
        if variantindex == 0: #if PE, then LOD2 not present
            pass
        else:
            df_variant = df_district[variant]
            df_variant.loc[:, 'Statistic'] = df_variant.index  # = df_variant['Statistic']
            df_variant.loc[:, 'Variant'] = [variant] * df_variant.shape[0]
            df_variant.set_index(['Variant', 'Statistic'], inplace=True)
            if df_results is None:
                df_results = df_variant
            else:
                df_results = pandas.concat([df_results, df_variant])

    df_results.to_excel(writer, sheetname)

    return df_district, df_results

def analyse_time_KPI(df_time, variants, writer):
    # Analyse timeKPI on street level
    df_variants = None
    for variantindex, variant in enumerate(variants, start=0):
        if variantindex == 0:
            df_reference = df_time[variant]
        else:
            df_comparison = df_time[variant]
            df_pe = percentage_error(df_actual=df_reference, df_forecast=df_comparison, checkbuildings=False)
            df_pe = df_pe[0]
            # first set column indices right (highest level is variant, lower level is KPI)
            df_pe_trans = df_pe.T  # we need to transpose
            df_pe_trans['KPI'] = df_pe_trans.index  # create column based on indices of transpose
            df_pe_trans['Variant'] = [variant] * df_pe.shape[1]  # create column with variant name
            df_pe_trans.set_index(['Variant', 'KPI'], inplace=True)  # set indices to transpose
            df_pe = df_pe_trans.T  # transpose back to normal df_pe
            if df_variants is None:
                # append to df_variants with all variants for this street
                df_variants = df_pe
            else:
                # append to df_variants with all existing variants for this street
                df_variants = df_variants.merge(df_pe, how='inner', left_index=True, right_index=True)
    df_time_pe = df_variants
    df_time_pe[('General', 'Number of buildings')] = df_time[('General', 'Number of buildings')]
    """df_time_pe['General', 'Number of buildings'] = df_streets['General','Number of buildings'] # merges on index = OK
    print ('Number of streets for timeKPI analysis: ' + str(df_time.shape[0]))

    # Analyse timeKPI on district level and add to street level
    df_time_district = df_time_pe.iloc[:, 0:-1].mul(df_time_pe.iloc[:, -1], axis=0)
    df_time_district['General', 'Number of buildings'] = df_time_pe['General', 'Number of buildings']
    df_time_district.loc['District'] = df_time_district.sum()
    df_time_district = df_time_district.div(df_time_district.iloc[-1, -1])
    df_time_pe.loc['District (weighted by number of buildings'] = df_time_district.iloc[-1].T"""
    df_time_pe.to_excel(writer, 'Time')
    return df_time_pe

def error(df_actual, df_forecast):
    """"This function demonstrates different loading options of TEASER"""
    df_error = df_forecast.subtract(df_actual)  # does it on index
    return df_error

def absolute_error(df_actual, df_forecast):
    """"This function demonstrates different loading options of TEASER"""
    df_error = error(df_actual=df_actual, df_forecast=df_forecast)
    df_ae = df_error.abs()
    return df_ae

def mean_absolute_error(df_actual, df_forecast):
    """"This function demonstrates different loading options of TEASER"""
    df_ae = absolute_error(df_actual=df_actual, df_forecast=df_forecast)
    df_mae = df_ae.mean()
    return df_mae

def percentage_error(df_actual, df_forecast, checkbuildings = True):
    """"This function demonstrates different loading options of TEASER"""
    df_pe = error(df_actual=df_actual, df_forecast=df_forecast).divide(df_actual)  # does it on index
    bldg_nan_neigh = []
    bldg_nan_gf = []
    if checkbuildings:
        # buildings with a different number of neighbours between variants
        df_pe = df_pe.replace([np.nan],0) # 0/0 results in nan, number/0 results in inf > so keep nan, drop inf
        df_pe = df_pe.replace([np.inf, -np.inf], np.nan)
        bldg_nan_neigh = list(df_pe[df_pe.isnull().any(axis=1)].index)
        bldg_nan_neigh += list(df_pe.loc[df_pe['Number of neighbours'] != 0].index)
        df_pe = df_pe.drop(bldg_nan_neigh)
        # buildings with a different ground floor area between variants
        bldg_nan_gf = list(df_pe.loc[df_pe['Groundfloor area[m2]'] != 0].index)
        df_pe = df_pe.drop(bldg_nan_gf)
    return [df_pe, bldg_nan_neigh, bldg_nan_gf]

def absolute_percentage_error(df_actual=None, df_forecast=None, df_pe=None):
    """"This function demonstrates different loading options of TEASER"""
    df_ape = None
    if df_actual is not None and df_forecast is not None:
        df_pe = percentage_error(df_actual=df_actual, df_forecast=df_forecast)
        df_ape = df_pe.abs()
    elif df_pe is not None:
        df_ape = df_pe.abs()
    return df_ape

def mean_percentage_error(df_actual=None, df_forecast=None, df_pe=None):
    """"This function demonstrates different loading options of TEASER"""
    df_mpe = None
    if df_actual is not None and df_forecast is not None:
        df_pe = percentage_error(df_actual=df_actual, df_forecast=df_forecast)
        df_mpe = df_pe.mean()
    elif df_pe is not None:
        df_mpe = df_pe.mean()
    return df_mpe

def stdev_percentage_error(df_actual=None, df_forecast=None, df_pe=None):
    """"This function demonstrates different loading options of TEASER"""
    df_stdev = None
    if df_actual is not None and df_forecast is not None:
        df_pe = percentage_error(df_actual=df_actual, df_forecast=df_forecast)
        df_stdev = df_pe.std()
    elif df_pe is not None:
        df_stdev = df_pe.std()
    return df_stdev

def mean_absolute_percentage_error(df_actual=None, df_forecast=None, df_pe=None):
    """"This function demonstrates different loading options of TEASER"""
    df_mape = None
    if df_actual is not None and df_forecast is not None:
        df_ape = absolute_percentage_error(df_actual=df_actual, df_forecast=df_forecast)
        df_mape = df_ape.mean()
    elif df_pe is not None:
        df_ape = absolute_percentage_error(df_pe=df_pe)
        df_mape = df_ape.mean()
    return df_mape

def root_mean_square_percentage_error(df_actual, df_forecast):
    """"This function demonstrates different loading options of TEASER"""
    df_pe = percentage_error(df_actual=df_actual, df_forecast=df_forecast)
    df_pe = df_pe.pow(2)
    df_rmspe = df_pe.mean()
    df_rmspe = df_rmspe.pow(0.5)
    return df_rmspe

def is_this_dataset_representative(df_buildings, variant, kpi, outputDir):

    #20 sets of 25 buildings
    number_of_subsets = 10
    list_of_seeds=list(range(number_of_subsets))
    sample_sizes = [5, 10, 25,50,100,200,300]

    df_samples = None
    for sample_size in sample_sizes:
        for seed in list_of_seeds:
            sample = df_buildings[variant, kpi].sample(n=sample_size, random_state=seed)
            if df_samples is None:
                df_samples = sample.reset_index()
                df_samples.drop('Street', axis=1, inplace=True)
                df_samples.drop('Name of building', axis=1, inplace=True)
                df_samples.rename(columns = {variant: 'Sample size: '+ str(sample_size), kpi: 'Sample ID: ' + str(seed)}, inplace=True)
            else:
                df_sample = sample.reset_index()
                df_sample.drop('Street', axis=1, inplace=True)
                df_sample.drop('Name of building', axis=1, inplace=True)
                df_sample.rename(columns= {variant: 'Sample size: '+ str(sample_size), kpi: 'Sample ID: ' + str(seed)}, inplace=True)
                df_samples = pandas.concat([df_samples, df_sample], axis=1)
    # final row is sample of all buildings
    df_sample = df_buildings[variant, kpi].reset_index()
    df_sample.drop('Street', axis=1, inplace=True)
    df_sample.drop('Name of building', axis=1, inplace=True)
    df_sample.rename(columns={variant: 'Sample size: ' + str(df_buildings[variant, kpi].shape[0]), kpi: 'Sample ID: 0'},
                     inplace=True)
    df_samples = pandas.concat([df_samples, df_sample], axis=1)
    sample_mean = df_sample.median()

    params = {'legend.fontsize': 18,
              'axes.labelsize': 18,
              'axes.titlesize': 18,
              'xtick.labelsize': 18,
              'ytick.labelsize': 18,
              'figure.figsize': (20, 10)}
    plt.rcParams.update(params)

    ax = df_samples.boxplot(grid=False, showfliers=False, whis=[25,75])

    # Median is line on plot
    plt.axhline(y=df_sample.median().values[0], linewidth=1, color='grey')
    # Fill area between quantile lines
    #plt.axhline(y=df_sample.quantile(q=0.25).values[0], linewidth=1, color='grey')
    #plt.axhline(y=df_sample.quantile(q=0.75).values[0], linewidth=1, color='grey')
    ax.axhspan(ymin=df_sample.quantile(q=0.25).values[0], ymax=df_sample.quantile(q=0.75).values[0], xmin=0, xmax=number_of_subsets*len(sample_sizes)+1.5, color='lightgrey')
    labels = [item.get_text().split(',')[0] for item in ax.get_xticklabels()]
    labels = [label[1:] for label in labels]
    unique_label = ''
    for labelindex, label in enumerate(labels):
        if label==unique_label:
            labels[labelindex]=''
        else:
            unique_label=label
    ax.set_xticklabels(labels)
    plt.xticks(rotation=90)
    plt.setp(ax.xaxis.get_majorticklabels(), ha='left') # sets xticks to the right column instead of the middle (which resulted in appearing in the next column)

    # Draw vertical lines between sample sizes
    for i in range(len(sample_sizes)+2):
        colors=['grey', 'lightgrey','grey', 'lightgrey','grey', 'lightgrey','grey', 'lightgrey','grey', 'lightgrey']
        #plt.axvline(x=i*number_of_subsets + 0.5, linewidth=1, color='grey')
        ax.axvspan(xmin=(i-1)*number_of_subsets + 0.5,
               xmax=(i)*number_of_subsets + 0.5, color=colors[i], alpha=0.25)

    #ax.set_ylim(-0.25,0.5)
    plt.tight_layout()
    plt.subplots_adjust(bottom=0.25, top=0.95)
    plt.title(variant + ' - ' + kpi)

    #plt.show()
    plt.savefig(outputDir + variant + kpi + "_representativeness_boxplot.png", dpi=1000)
    plt.close()

    ax = df_samples['Sample size: 200'].plot(kind='kde', linewidth=1)
    df_samples['Sample size: ' + str(df_buildings[variant, kpi].shape[0])].plot(kind='kde', linewidth=2, color='black', ax=ax)
    df_samples['Sample size: ' + str(df_buildings[variant, kpi].shape[0])].plot(kind='kde', linewidth=5, alpha = 0.3, color='black', ax=ax)
    plt.savefig(outputDir + variant + kpi + "_representativeness_KDE_200.png", dpi=1000)
    plt.close()
    ax = df_samples['Sample size: 300'].plot(kind='kde', linewidth=1)
    df_samples['Sample size: ' + str(df_buildings[variant, kpi].shape[0])].plot(kind='kde', linewidth=2, color='black', ax=ax)
    df_samples['Sample size: ' + str(df_buildings[variant, kpi].shape[0])].plot(kind='kde', linewidth=5, alpha = 0.3, color='black', ax=ax)
    plt.savefig(outputDir + variant + kpi + "_representativeness_KDE_300.png", dpi=1000)
    plt.close()

def analyse_standard_error(df_buildings_absolute,  outputDir, variant="LOD2", kpi="Total energy use[kWh]"):
    sample_sizes = range(50, 701, 25)
    print sample_sizes
    df_buildings_absolute.reset_index(level=0, drop=True, inplace=True)  # drop level
    df = shuffle(df_buildings_absolute, random_state=1)

    df_samples = None
    for sample_size in sample_sizes:

        sample = df[0:sample_size]
        sample = sample[variant, kpi]
        if df_samples is None:
            df_samples = sample.reset_index()
            df_samples.drop('Name of building', axis=1, inplace=True)
            df_samples.rename(columns = {variant: 'Sample size: '+ str(sample_size), kpi: 'Sample ID: x'}, inplace=True)
        else:
            sample = sample.reset_index()
            sample.drop('Name of building', axis=1, inplace=True)
            sample.rename(columns= {variant: 'Sample size: '+ str(sample_size), kpi: 'Sample ID: x'}, inplace=True)
            df_samples = pandas.concat([df_samples, sample], axis=1)
    df_mean = df_samples.mean()
    df_std = df_samples.std()
    df_count = df_samples.count()
    df_margin_of_error = df_std.divide(df_count**0.5)*1.96
    print df_margin_of_error

    x = sample_sizes
    y = df_mean
    e = df_margin_of_error
    params = {'legend.fontsize': 14,
              'axes.labelsize': 14,
              'figure.figsize': (15, 10),
              'axes.titlesize': 22,
              'xtick.labelsize': 14,
              'ytick.labelsize': 14}
    plt.rcParams.update(params)

    plt.errorbar(x, y, e, linestyle='None', marker='^', color='grey', linewidth=1)
    plt.grid(color='lightgrey')
    plt.xlabel('Sample size')
    plt.xticks(sample_sizes)
    plt.ylabel(variant + ' reference model - ' + kpi)
    #plt.axhspan(ymin=df_mean[-1]*0.98, ymax=df_mean[-1]*1.02, xmin=0, xmax=sample_sizes[-1], color='lightgrey', alpha = 0.5)
    plt.fill_between(x, y*0.98, y*1.02, color='lightgrey', alpha = 0.5)
    plt.tight_layout()
    plt.savefig(outputDir + variant + kpi + "_standard_error.png", dpi=300)
    plt.close()


def analyse_standard_error2(df_buildings_absolute,  outputDir, variant="LOD2", kpi="Total energy use[kWh]"):

    #20 sets of 25 buildings
    sample_sizes = [20,25,28,35,50,70,100,140,175,350] # 1, 2, 4, 5, 7, 10, 14, 20, 25, 28, 35, 50, 70, 100, 140, 175, 350, 700
    df_buildings_absolute.reset_index(level=0, drop=True, inplace=True)  # drop level
    df = shuffle(df_buildings_absolute, random_state=1)

    for sample_size in sample_sizes:
        if df_buildings_absolute.shape[0]%sample_size != 0:
            print ('Subsample size is not compatible with sample size')
        else:
            number_of_subsets = df_buildings_absolute.shape[0]/sample_size
            df_subsamples = None
            for i in list(range(number_of_subsets)):
                sample = df[sample_size*i:sample_size*(i+1)]
                sample = sample[variant, kpi]
                if df_subsamples is None:
                    df_subsamples = sample.reset_index()
                    df_subsamples.drop('Name of building', axis=1, inplace=True)
                    df_subsamples.rename(columns = {variant: 'Sample size: '+ str(sample_size), kpi: 'Sample ID: ' + str(i)}, inplace=True)
                else:
                    df_subsample = sample.reset_index()
                    df_subsample.drop('Name of building', axis=1, inplace=True)
                    df_subsample.rename(columns= {variant: 'Sample size: '+ str(sample_size), kpi: 'Sample ID: ' + str(i)}, inplace=True)
                    df_subsamples = pandas.concat([df_subsamples, df_subsample], axis=1)
            print ('Sample size: ' + str(sample_size))
            print ('Number of subsets: ' + str(number_of_subsets))
            df_mean = df_subsamples.mean()
            std_mean = df_mean.std()
            print ('STD of subsample means: ' + str(std_mean))
            mean_mean = df_mean.mean()
            print ('Mean of subsample means: ' + str(mean_mean))
            SE_mean2 = std_mean / math.sqrt(number_of_subsets)
            print ('SE on mean: ' + str(SE_mean2))
            df_std = df_subsamples.std()
            std_std = df_std.std()
            print ('STD of subsample STDs: ' + str(std_std))
            mean_std = df_std.mean()
            print ('Mean of subsample STDs: ' + str(mean_std))
            SE_STD2 = std_std / math.sqrt(number_of_subsets)
            print ('SE on STD: ' + str(SE_STD2))
            print ('_____')
    print ('Sample size: ' + str(700))
    print ('Number of subsets: ' + str(1))
    mean = df_buildings_absolute[variant,kpi].mean()
    std = df_buildings_absolute[variant,kpi].std()
    standard_error = std/math.sqrt(700)
    print ('Mean :' + str(mean))
    print ('STD: ' + str(std))
    print ('Standard error: ' + str(standard_error))
    print ('_____')

    result = sms.stats.weightstats.DescrStatsW(df_buildings_absolute['LOD2','Total energy use[kWh]']).tconfint_mean()
    print result # returns tuple of lower limit and upper limit

def variations_within_approaches(df, df_buildings, outputDir,  variants = ['LOD1_ridge', 'LOD1_halfroof', 'LOD1_extended', 'LOD2', 'LOD2_8', 'LOD2_4'],
                                 linestyles = ['-', '-.', '--', '-', '-.', '--'], colors = ['black', 'black', 'black', 'grey', 'grey', 'grey'],
                                 kpis = ['Total loss area [m2]', 'Volume of building[m3]', 'Total energy use[kWh]'],
                                 title='Variations within approaches'):
    print("Analysing variations within approaches")
    df_buildings_absolute = df.loc[df_buildings.index]  # take only absolute values of valid buildings

    params = {'legend.fontsize': 14,
              'axes.labelsize': 14,
              'axes.titlesize': 22,
              'xtick.labelsize': 14,
              'ytick.labelsize': 14}
    plt.rcParams.update(params)

    # Each KPI is subplot, all variants on the same subplot
    fig, axes = plt.subplots(nrows=len(kpis), figsize=(10,15))
    for variantindex, variant in enumerate(variants, start=0):
        for kpiindex, kpi in enumerate(kpis, start=0):
            mu = df_buildings_absolute[variant, kpi].mean()
            sigma = df_buildings_absolute[variant, kpi].std()
            cv = sigma / mu
            if kpi == 'Total energy use[kWh]' or kpi == 'Overheating day zone[Kh]':
                cv = round(cv, 4)
                mu = int(mu)
                sigma = int(sigma)
            else:
                precision = 2
                cv = round(cv, 4)
                mu = round(mu, precision)
                sigma = round(sigma, precision)

            df_buildings_absolute[variant, kpi].plot(kind='kde', linestyle=linestyles[variantindex],
                                                     color=colors[variantindex], linewidth=1, ax=axes[kpiindex],
                                                     label=variant + ' (CV = ' + str(cv) + ')' \
                                                           + '\n' + r'$\mu$ = ' + str(mu) + ', ' \
                                                           + r'$\sigma$ = ' + str(sigma))
    for axindex, ax in enumerate(axes, start=0):
        ax.grid(True)
        ax.set_xlabel(kpis[axindex])
        ax.legend(loc='upper right', fancybox=True, framealpha=0.5)
    fig.tight_layout()
    fig.suptitle(title, fontsize=24)
    fig.subplots_adjust(top=0.90, hspace=0.4)
    #plt.show()
    plt.savefig(outputDir + title + ".png", dpi=1000)
    plt.close()

def variations_between_approaches(df_buildings, outputDir):

    print("Analysing variations between approaches")

    title = 'Variations between approaches'
    variants = ['LOD1_ridge', 'LOD1_halfroof', 'LOD1_extended']
    linestyles = ['-', '-.', '--', '-.', '--']  # provide 1 style for every variant (not sufficient styles
    colors = ['black', 'black', 'black', 'grey', 'grey']  # provide 1 color for every variant
    kpis = ['Total loss area[m2]', 'Heated volume[m3]', 'Total energy use[kWh]']

    params = {'legend.fontsize': 14,
              'axes.labelsize': 14,
              'axes.titlesize': 22,
              'xtick.labelsize': 14,
              'ytick.labelsize': 14}
    plt.rcParams.update(params)

    # Each KPI is subplot, all variants on the same subplot
    fig, axes = plt.subplots(nrows=len(kpis), figsize=(10,15))
    for variantindex, variant in enumerate(variants, start=0):
        for kpiindex, kpi in enumerate(kpis, start=0):
            mu = df_buildings[variant, kpi].mean()
            sigma = df_buildings[variant, kpi].std()
            if mu != 0:
                df_buildings[variant, kpi].plot(kind='kde', linestyle=linestyles[variantindex],
                                                     color=colors[variantindex], linewidth=1, ax=axes[kpiindex],
                                                     label=variant + '\n' + r'$\mu$ = ' + str(round(mu, 4)) + ', ' + r'$\sigma$ = ' + str(round(sigma, 4)))
    for axindex, ax in enumerate(axes, start=0):
        ax.grid(True)
        ax.set_xlabel(kpis[axindex])
        ax.legend(loc='upper right', fancybox=True, framealpha=0.5)
        ax.axvline(x=0, linewidth=2, color='grey')
    fig.tight_layout()
    fig.suptitle(title, fontsize=24)
    fig.subplots_adjust(top=0.90, hspace=0.4)
    #plt.show()
    plt.savefig(outputDir + title + ".png", dpi=1000)
    plt.close()

def bootstrapplot(df_buildings, outputDir):
    from pandas.plotting import bootstrap_plot

    samplesizes = [25, 50, 100, 250, 400]
    variant = 'LOD1_ridge'
    kpi = 'Total energy use[kWh]'

    for samplesize in samplesizes:
        bootstrap_plot(df_buildings[variant, kpi], size=samplesize, samples=1000, color='grey')
        plt.tight_layout()
        plt.savefig(outputDir + 'LOD1_ridge_' + str(samplesize) + "_bootstrap.png", dpi=1000)
        plt.close()

def export_drawing(df, df_buildings, variants, outputDir, boxplots=False, histograms=False, scatter=False):
        params = {'legend.fontsize': 'small',
                  'figure.figsize': (15, 10),
                  'axes.labelsize': 'small',
                  'axes.titlesize': 'small',
                  'xtick.labelsize': 'small',
                  'ytick.labelsize': 'small'}
        plt.rcParams.update(params)

        if boxplots:
            print("Creating boxplots")
            for variantindex, variant in enumerate(variants, start = 1):
                if variantindex==1:
                    pass
                else:
                    df_buildings[variant].boxplot()
                    plt.xticks(rotation=90)
                    plt.tight_layout()
                    plt.savefig(outputDir + variant + "_boxplot.png", dpi = 1000)
                    plt.close()

        if histograms:
            print("Creating histograms")
            for variantindex, variant in enumerate(variants, start=1):
                if variantindex == 1:
                    pass
                else:
                    df_buildings.hist(column=[variant], bins = 100)
                    plt.tight_layout()
                    plt.savefig(outputDir + variant + "_graph.png", dpi=1000)
                    plt.close()

        if scatter: # not yet optimal: some combinations are calculated twice
            print("Creating scatterplots")
            correlations=[]
            df_buildings_absolute = df.loc[df_buildings.index] # only keep buildings that are in df_buildings as well
            scatter_kpis = ['Heated volume[m3]', 'Total loss area[m2]', 'Total energy use[kWh]']
            for variantindex, variant in enumerate(variants, start=1):
                if variantindex == 1:
                    referencevariant = variant

                    correlations.append(create_scatterplot(df_buildings_absolute=df_buildings_absolute,
                                       x_variant=variant,
                                       x_kpi=scatter_kpis[0],
                                       y_variant=variant,
                                       y_kpi=scatter_kpis[1],
                                       outputDir=outputDir))
                    correlations.append(create_scatterplot(df_buildings_absolute=df_buildings_absolute,
                                       x_variant=variant,
                                       x_kpi=scatter_kpis[2],
                                       y_variant=variant,
                                       y_kpi=scatter_kpis[1],
                                       outputDir=outputDir))
                    correlations.append(create_scatterplot(df_buildings_absolute=df_buildings_absolute,
                                       x_variant=variant,
                                       x_kpi=scatter_kpis[2],
                                       y_variant=variant,
                                       y_kpi=scatter_kpis[0],
                                       outputDir=outputDir))

                else:
                    # compare kpis_scatter of this variant with reference variant
                    for kpi in scatter_kpis:
                        correlations.append(create_scatterplot(df_buildings_absolute=df_buildings_absolute,
                                           x_variant=referencevariant,
                                           x_kpi=kpi,
                                           y_variant=variant,
                                           y_kpi=kpi,
                                           outputDir=outputDir))

                        correlations.append(create_scatterplot(df_buildings_absolute=df_buildings_absolute,
                                       x_variant=variant,
                                       x_kpi=scatter_kpis[0],
                                       y_variant=variant,
                                       y_kpi=scatter_kpis[1],
                                       outputDir=outputDir))
                        correlations.append(create_scatterplot(df_buildings_absolute=df_buildings_absolute,
                                       x_variant=variant,
                                       x_kpi=scatter_kpis[2],
                                       y_variant=variant,
                                       y_kpi=scatter_kpis[1],
                                       outputDir=outputDir))
                        correlations.append(create_scatterplot(df_buildings_absolute=df_buildings_absolute,
                                       x_variant=variant,
                                       x_kpi=scatter_kpis[2],
                                       y_variant=variant,
                                       y_kpi=scatter_kpis[0],
                                       outputDir=outputDir))
            for correlation in correlations:
                print correlation

def create_scatterplot(df_buildings_absolute, x_variant, x_kpi, y_variant, y_kpi, outputDir):
    # create scatterplot
    df_buildings_absolute.plot.scatter(x=(x_variant, x_kpi), y=(y_variant, y_kpi))
    # calculate regression line
    X = sm.add_constant(df_buildings_absolute[(x_variant, x_kpi)])
    result = sm.OLS(df_buildings_absolute[(y_variant, y_kpi)], X,
                    missing='drop').fit()  # ignores entires where x or y is NaN
    print result.summary()
    # plot regression line
    m = result.params[1]
    b = result.params[0]
    N = 100  # could be just 2 if you are only drawing a straight line...
    points = np.linspace(df_buildings_absolute[(x_variant, x_kpi)].min(),
                         df_buildings_absolute[(x_variant, x_kpi)].max(), N)
    plt.plot(points, m * points + b, color='k')
    plt.text(df_buildings_absolute[(x_variant, x_kpi)].min(),  # x position
             (df_buildings_absolute[(y_variant, y_kpi)].max() * 0.95),  # y position
             y_variant + '_' + y_kpi + " = " + str(round(m, 3)) + " * " + x_variant + '_' + x_kpi + " + " + str(
                 round(b, 3)),  # text
             horizontalalignment='left', verticalalignment='center', bbox=dict(facecolor='black', alpha=0.2))
    # plt.show()
    plt.savefig(outputDir + x_variant + "_" + x_kpi[:-5] + "_"+ y_variant + "_" + y_kpi[:-5] + "_scatter.png", bbox_inches='tight', dpi=1000)
    plt.close()
    return (y_variant + '_' + y_kpi + " = " + str(round(m, 3)) + " * " + x_variant + '_' + x_kpi + " + " + str(
                 round(b, 3)))

if __name__ == '__main__':
    report_errors()
    print("That's it! :)")
