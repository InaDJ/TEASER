# -*- coding: utf-8 -*-
"""
Created on Fri Nov 27 14:04:09 2015

@author: pre
"""

from teaser.Logic.BuildingObjects.TypeBuildings.UseConditions18599 import UseConditions18599
from teaser.Logic.BuildingObjects.Building import Building
from teaser.Logic.BuildingObjects.ThermalZone import ThermalZone
from teaser.Project import Project


thermal_zone_types = []
import teaser.Logic.Utilis as ut  
prj = Project(True)
for usage in prj.data.conditions_bind.UseConditions18599:
    thermal_zone_types.append(usage.usage)
bldg = Building(prj)
tz = ThermalZone(bldg)
uc = UseConditions18599(tz) 
use_list = []                         
for value in thermal_zone_types:
    uc = UseConditions18599(tz) 
    uc.load_use_conditions(value)
    uc.parent=None
    uc.profile_lighting = 6*[0.0]+12*[1.0]+6*[0.0]
    use_list.append(uc)
for i, value in enumerate(use_list):
    value.save_use_conditions(ut.get_default_path(),"UseConditions")

