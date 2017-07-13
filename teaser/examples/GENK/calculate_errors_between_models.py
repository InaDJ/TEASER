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
    resultsDir = "C:\Users\ina\Desktop\Results/"
    variants = ['LOD2', 'LOD1_ridge', 'LOD1_halfroof']
    streetnames = [] #leave empty if you want to the whole directory
    if streetnames == []:
        streetnames = [name for name in os.listdir(resultsDir)]
    else:
        pass
    print variants
    print streetnames

    df = create_dataframe(variants=variants, streetnames=streetnames, resultsDir=resultsDir)
    df.to_excel("C:\Users\ina\Desktop/df.xlsx")

    #print df
    #print df['LOD2'] # returns subdataframe with all KPI's of this variant
    #print df['LOD2', 'Number of floors'] # returns subsubdataframe (= series) with the specified KPI of this variant
    #print df.loc['Dwarsstraat'] #returns subdataframe, based on row: all buildings of this street
    #print df.loc['Dwarsstraat', 'Dwarsstraat_1'] return subsubdataframe (=series) with the specified building of this street
    #print df[variant].loc[street] #returns one street in one variant

    # Analyse on building level
    df_buildings = None
    for streetname in streetnames:
        df_variants = None
        for variantindex, variant in enumerate(variants, start=0):
            if variantindex == 0:
                df_reference = df[variant].loc[streetname]
            else:
                df_comparison = df[variant].loc[streetname]
                df_pe = percentage_error(df_actual=df_reference, df_forecast=df_comparison)
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
                    df_variants = df_variants.merge(df_pe, how='outer', left_index=True, right_index=True)
        # All variants for this street are created, now append to df_buildings with all streets and all variants
        if df_buildings is None:
            df_buildings = df_variants
        else:
            df_buildings = pandas.concat([df_buildings, df_variants])

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

    # Create results excel
    variantnames = '_'.join(variants) # converts variants list to string, separated by _
    writer = pandas.ExcelWriter("C:\Users\ina\Desktop"+'/District_'+variantnames+".xlsx")
    df_district.to_excel(writer, 'District')
    df_streets.to_excel(writer, 'Streets')
    df_buildings.to_excel(writer, 'Buildings')
    writer.save()
    writer.close()

def create_dataframe(variants, streetnames, resultsDir):
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
                resultsDir + streetname + "/" + streetname + "_" + variant + "_geometryKPI.csv",
                sep=";", usecols=range(0, 8) + [9, 10, 11], index_col=0, na_values=['inf'])
            df_street_geom.groupby(df_street_geom.index).first() #remove duplicative indices
            df_street_ener = pandas.read_csv(
                resultsDir + streetname + "/" + streetname + "_" + variant + "_energyKPI.csv",
                sep=";", usecols=range(0, 7), index_col=0, na_values=['inf'])
            df_street_ener = df_street_ener[:-1]  # drop last row with district peak power
            df_street_ener.groupby(df_street_ener.index).first()  # remove duplicative indices
            df_street = df_street_geom.merge(df_street_ener, how='left', left_index=True,
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

def percentage_error(df_actual, df_forecast):
    """"This function demonstrates different loading options of TEASER"""
    df_pe = error(df_actual=df_actual, df_forecast=df_forecast).divide(df_actual)  # does it on index
    return df_pe

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
