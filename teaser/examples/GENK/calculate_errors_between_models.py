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
import numpy as np
from modelicares import SimRes
import matplotlib.pyplot as plt
from cycler import cycler

def calculate_errors_between_models():
    '''

    How to work with multi-index:
    #print df
    #print df['LOD2'] # returns subdataframe with all KPI's of this variant
    #print df['LOD2', 'Number of floors'] # returns subsubdataframe (= series) with the specified KPI of this variant
    #print df.loc['Dwarsstraat'] #returns subdataframe, based on row: all buildings of this street
    #print df.loc['Dwarsstraat', 'Dwarsstraat_1'] return subsubdataframe (=series) with the specified building of this street
    #print df[variant].loc[street] #returns one street in one variant
    #print df.xs('Number of floors', level='KPI', axis=1, drop_level=False) #prints the number of floors-column of all variants for all streets
    '''

    inputDir = "D:\Ina\FINAL\Results/"
    outputDir = "D:\Ina/"
    variants = ['LOD2', 'LOD1_ridge', 'LOD1_halfroof', 'LOD2_4', 'LOD2_8']
    streetnames = ['Bandstraat', 'Berm', 'Boogstraat', 'Bremstraat', 'Congostraat', 'DeBek', 'DeHeuvel', 'DeRoten', 'Drijtap', 'Gansenwijer', 'Gracht', 'Groenven', 'Gruisweg', 'Hazelnootstraat', 'Heiblok', 'Heidebos', 'Heilapstraat',
                    'Hennepstraat', 'Holeven', 'Houtwal', 'Huiskensweier', 'Ijzerven', 'Keistraat', 'Kennipstraat', 'Klotstraat', 'Leemstraat', 'Plaggenstraat', 'Ploegstraat', 'Rietbeemdstraat',
                    'Roerstraat', 'Spoorstraat', 'Vogelzangstraat', 'Zandoerstraat'] #[] #leave empty if you want to the whole directory

    if streetnames == []:
        streetnames = [name for name in os.listdir(inputDir)]
    else:
        pass

    print variants
    print streetnames

    # Create dataframe with all variants and all streets (buildings with no simulation results were already deleted)
    df = create_dataframe(variants=variants, streetnames=streetnames, inputDir=inputDir)
    df = cleanup_dataframe(df=df, outputDir=outputDir)

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

    # Analyse on street level
    df_streets = None
    for streetname in streetnames:
        df_street_pe = df_buildings.loc[streetname]
        number_of_buildings = df_street_pe.shape[0]
        df_street_mape = mean_absolute_percentage_error(df_pe=df_street_pe) #returns a Series
        df_street_mape = df_street_mape.to_frame() #converts Series to Frame, so we can transpose
        df_street_mape.columns = [streetname] # set column name to street name
        df_street_mape = df_street_mape.T # each street is a row in the bigger dataframe
        df_street_mape['General','Number of buildings'] = number_of_buildings
        if df_streets is None:
            df_streets = df_street_mape
        else:
            df_streets = pandas.concat([df_streets, df_street_mape])

    # Analyse on district level
    number_of_buildings = df_buildings.shape[0]
    df_district = mean_absolute_percentage_error(df_pe=df_buildings) #returns a Series
    df_district = df_district.to_frame() #converts Series to Frame, so we can transpose
    df_district = df_district.T
    df_district['General', 'Number of buildings'] = number_of_buildings
    df_district['District'] = 'District'
    df_district.set_index(['District'], inplace=True) #set index for this street

    # Analyse timeKPI on street level
    df_time = time_dataframe(variants=variants, streetnames=streetnames, inputDir=inputDir, outputDir=outputDir)
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
    df_time_pe['General', 'Number of buildings'] = df_streets['General','Number of buildings'] # merges on index = OK
    print ('Number of streets for timeKPI analysis: ' + str(df_time.shape[0]))
    # Analyse timeKPI on district level and add to street level
    df_time_district = df_time_pe.iloc[:, 0:-1].mul(df_time_pe.iloc[:, -1], axis=0)
    df_time_district['General', 'Number of buildings'] = df_time_pe['General', 'Number of buildings']
    df_time_district.loc['District'] = df_time_district.sum()
    df_time_district = df_time_district.div(df_time_district.iloc[-1, -1])
    df_time_pe.loc['District (weighted by number of buildings'] = df_time_district.iloc[-1].T

    # Create results excel
    variantnames = '_'.join(variants) # converts variants list to string, separated by _
    writer = pandas.ExcelWriter(outputDir+'/District_'+variantnames+".xlsx")
    df_district.to_excel(writer, 'District')
    df_streets.to_excel(writer, 'Streets')
    df_buildings.to_excel(writer, 'Buildings')
    df_time_pe.to_excel(writer, 'Time')
    writer.save()
    writer.close()

def create_dataframe(variants, streetnames, inputDir):
    """This function returns a multi-indexed dataframe for a proper analysis of the KPIs.
        DataFrame:
        Highest column label = variant, lowest column label = KPI
        Highest row index = street, lowest row index = building
    """
    df_all = None
    for streetname in streetnames:
        df_variants = None
        for variant in variants:
            # df with buildingnames as indices, geometryKPI and energyKPI as columns
            df_street_geom = pandas.read_csv(
                inputDir + streetname + "/" + streetname + "_" + variant + "_geometryKPI.csv",
                sep=";", usecols=range(0, 8) + [9, 10, 11], index_col=0, na_values=['inf'])
            df_street_geom.groupby(df_street_geom.index).last() #remove duplicative indices
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
    return df_all

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
        if kpi in ['Number of neighbours', 'Overheating onezone[Kh]', 'Overheating dayzone[Kh]',
                   'Overheating nightzone[Kh]']:
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

def time_dataframe(variants, streetnames, inputDir, outputDir):
    """ """
    # Create dataframe with timeKPIs for the streets
    df_all = None
    for streetname in streetnames:
        df_variants = None
        for variant in variants:
            # df with buildingnames as indices, geometryKPI and energyKPI as columns
            df_street_time = pandas.read_csv(
                inputDir + streetname + "/" + streetname + "_" + variant + "_timeKPI.csv",
                sep=";", index_col=0, na_values=['inf']) # this df is already "transposed" (rows are columns)
            # first set column indices right (highest level is variant, lower level is KPI)
            if 'Merging main building with extensions [s]' in df_street_time.index: #LOD1 is nog merged
                df_street_time.drop('Merging main building with extensions [s]', inplace=True)
            if 'Number of buildings after merging [-]' in df_street_time.index:
                df_street_time.drop('Number of buildings after merging [-]', inplace=True)
            df_street_time['KPI'] = df_street_time.index  # create column based on indices of transpose
            df_street_time['Variant'] = [variant] * df_street_time.shape[0]  # create column with variant name
            df_street_time.set_index(['Variant', 'KPI'], inplace=True)  # set indices to transpose
            df_street_time = df_street_time.T  # transpose to wanted format of df_street
            df_street_time['Street'] = streetname
            df_street_time.set_index(['Street'], inplace=True) # this row has its streetname as index
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
            df_all = pandas.concat([df_all, df_variants])

    # Delete streets that are incomplete
    street_na = list(df_all[df_all.isnull().any(axis=1)].index)
    print ('Streets whose timeKPIs were incomplete: ' + str(len(street_na)))
    print street_na
    df_all = df_all.dropna()

    # Print df to excel
    df_all.to_excel(outputDir + "df_time.xlsx")

    return df_all

def error(df_actual, df_forecast):
    """"This function demonstrates different loading options of TEASER"""
    df_error = df_actual.subtract(df_forecast)  # does it on index
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

def mean_percentage_error(df_actual, df_forecast):
    """"This function demonstrates different loading options of TEASER"""
    df_pe = percentage_error(df_actual=df_actual, df_forecast=df_forecast)
    df_mpe = df_pe.mean()
    return df_mpe

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

if __name__ == '__main__':
    calculate_errors_between_models()
    print("That's it! :)")
