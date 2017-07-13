# Created November 2016
# Ina De Jaeger (KU Leuven, EnergyVille)

"""ideas_output

This module contains function to call Templates for IDEAS model generation
"""
import os
import re
import teaser.logic.utilities as utilities
from mako.template import Template
from mako.lookup import TemplateLookup

def export_ideas(buildings,
                 prj,
                 path=None,
                 building_model="Detailed"):
    """Exports models for IDEAS library

        Exports a building for detailed IDEAS Building model.
        Building model is described in conference paper: De Jaeger I, Reynders G,
        Saelens D. Impact of spatial accuracy on district energy simulations.
        Energy Procedia 2017:?:? (paper accepted for NSB 2017)
        This function uses Mako Templates specified in data.output.modelicatemplates.ideas

        Parameters
        ----------
        buildings : list of instances of Building
            list of TEASER instances of a Building that is exported to IDEAS
             models. If you want to export a single building,
            please pass it over as a list containing only that building.
        prj : instance of Project
            Instance of TEASER Project object to access Project related
            information, e.g. name or version of used libraries
        path : string
            if the Files should not be stored in default output path of TEASER,
            an alternative path can be specified as a full path
        building_model : string
            Currently, only "Detailed", "ROM", or "GenkNET"
        """

    assert building_model in ["Detailed","ROM", "GenkNET"]
    uses = ['Modelica(version="' + prj.modelica_info.version + '")',
            'IDEAS(version="1.0.0")']

    template_path = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    lookup = TemplateLookup(directories=[utilities.get_full_path(
        os.path.join('data', 'output', 'modelicatemplate'))])

    # Then, create building level
    for bldg in buildings:
        # Rename building if not already correct
        if len(bldg.name.split('_')) == 3:
            bldg.name = bldg.name.split('_')[0]+"_"+bldg.name.split('_')[1]
        # Re-order thermal zones, first dayzone, then nightzone (required for two-zone)
        if bldg.thermal_zones[0].name == "DayZone":
            pass
        else:
            for zoneindex, zone in enumerate(bldg.thermal_zones):
                if zone.name == "DayZone":
                    old_index = zoneindex
                    new_index = 0
                    bldg.thermal_zones[old_index], bldg.thermal_zones[new_index] = \
                        bldg.thermal_zones[new_index], bldg.thermal_zones[old_index]

        # Create folders (building, structure)
        bldg_path = utilities.get_full_path(path + "/" + bldg.name + "/")
        utilities.create_path(bldg_path)
        structure_path = bldg_path + "Structure/"
        utilities.create_path(structure_path)

        # Create building level (building.mo, package.mo and package.order)
        building_template = Template(filename=template_path + "ideas_Building")
        out_file = open((bldg_path + bldg.name + "_Building.mo"), 'w')
        out_file.write(building_template.render_unicode(
            bldg=bldg))
        out_file.close()

        building_innersim_template = Template(filename=template_path + "ideas_Building_inner_sim")
        out_file = open((bldg_path + bldg.name + ".mo"), 'w')
        out_file.write(building_innersim_template.render_unicode(
            bldg=bldg))
        out_file.close()

        _help_package(bldg_path, bldg.name, within=prj.name)
        _help_package_order(path=bldg_path,
                            package_list_with_addition=[bldg],
                            addition="_Building",
                            extra_list= ["Structure","Occupant"],
                            # not yet "HeatingSystem","VentilationSystem","ElectricalSystem"
                            package_list_without=[bldg])

        if building_model == "Detailed" or building_model == "ROM":
            # Create folder (vent., heat., electr. system and occupant)
            ventilation_path = bldg_path + "VentilationSystem"
            utilities.create_path(ventilation_path)
            heating_path = bldg_path + "Heatingsystem"
            utilities.create_path(heating_path)
            electrical_path = bldg_path + "ElectricalSystem"
            utilities.create_path(electrical_path)
            occupant_path = bldg_path + "Occupant/"
            utilities.create_path(occupant_path)

            # Create occupant level (occupant.mo, package.mo and package.order)
            occupant_template = Template(filename=template_path + "ideas_Occupant")
            out_file = open((occupant_path + "ISO13790.mo"), 'w')
            out_file.write(occupant_template.render_unicode(
                bldg=bldg))
            out_file.close()

            _help_package(occupant_path, "Occupant",
                          within=prj.name + "." + bldg.name,
                          packagedescription=
                          "Package of the particular building occupant")
            _help_package_order(occupant_path, [], "", ["ISO13790"], [])

            if building_model == "Detailed":
                # Create structure level (structure.mo, package.mo and package.order)
                #       (here initialisation, later addition of zones and components)
                structure_filepath = structure_path + bldg.name + "_Structure.mo"
                template = Template(filename=template_path + "ideas_Structure")
                out_file = open(structure_filepath, 'w')
                out_file.write(template.render_unicode(bldg=bldg))
                out_file.close()
                #       create help file for connections to add to structure.mo
                help_connections = open((structure_path + "help_connections.txt"), 'w')
                help_connections.close()

                _help_package(structure_path, "Structure",
                              within=prj.name + "." + bldg.name,
                              packagedescription=
                              "Package of the particular building structure")
                _help_package_order(structure_path, [bldg], "_Structure", ["Data"], [])
                count_zonesinbldg = 0
                elements_from_previous_zone = []
                for zoneindex, zone in enumerate(bldg.thermal_zones, start=1):
                    count_zonesinbldg +=1

                    count_outerwalls = 0
                    count_windows = 0
                    count_rooftops = 0
                    count_groundfloors = 0
                    count_innerwalls = 0
                    count_ceilings = 0
                    count_floors = 0
                    count_elementsinzone = 0

                    if elements_from_previous_zone != []:
                        for bldg_element in elements_from_previous_zone:
                            # bldg_element was created in previous zone, just needs to be connected
                            count_elementsinzone +=1
                            # Add bldg_element to help_connections
                            template = Template(filename=template_path + "ideas_ConnectComponents")
                            help_connections = open((structure_path + "help_connections.txt"), 'a')
                            help_connections.write(template.render_unicode(
                                zone=zone,
                                buildingelement=bldg_element,
                                index=count_elementsinzone+1,
                                connect_to_a=False,
                                connect_to_b=True))
                            help_connections.close()
                        elements_from_previous_zone = []

                    for bldg_element in zone.outer_walls:
                        count_outerwalls +=1
                        count_elementsinzone += 1
                        bldg_element.name = type(bldg_element).__name__ + "_" + str(count_zonesinbldg) + "_" + str(count_outerwalls)
                        # Add outerwall to structure.mo
                        template = Template(filename=template_path + "ideas_OuterWall", lookup=lookup)
                        out_file = open(structure_filepath, 'a')
                        out_file.write(
                            template.render_unicode(
                                buildingelement=bldg_element,
                                zoneindex=count_zonesinbldg,
                                elementindex=count_elementsinzone))
                        out_file.close()
                        # Add outerwall to help_connections
                        template = Template(filename=template_path + "ideas_ConnectComponents")
                        help_connections = open((structure_path +"help_connections.txt"), 'a')
                        help_connections.write(template.render_unicode(
                            zone=zone,
                            buildingelement=bldg_element,
                            index=count_elementsinzone,
                            connect_to_a=True,
                            connect_to_b=False))
                        help_connections.close()

                    for bldg_element in zone.windows:
                        count_windows +=1
                        count_elementsinzone += 1
                        bldg_element.name = type(bldg_element).__name__ + "_" + str(count_zonesinbldg) + "_" + str(count_windows)
                        # Add window to structure.mo
                        template = Template(filename=template_path + "ideas_Window", lookup=lookup)
                        out_file = open(structure_filepath, 'a')
                        out_file.write(
                            template.render_unicode(
                                buildingelement=bldg_element,
                                zoneindex=count_zonesinbldg,
                                elementindex=count_elementsinzone))
                        out_file.close()
                        # Add window to help_connections
                        template = Template(filename=template_path + "ideas_ConnectComponents")
                        help_connections = open((structure_path +"help_connections.txt"), 'a')
                        help_connections.write(template.render_unicode(
                            zone=zone,
                            buildingelement=bldg_element,
                            index=count_elementsinzone,
                            connect_to_a=True,
                            connect_to_b=False))
                        help_connections.close()

                    for bldg_element in zone.rooftops:
                        count_rooftops +=1
                        count_elementsinzone += 1
                        bldg_element.name = type(bldg_element).__name__ + "_" + str(count_zonesinbldg) + "_" + str(count_rooftops)
                        # Add rooftop to structure.mo
                        template = Template(filename=template_path + "ideas_OuterWall", lookup=lookup)
                        out_file = open(structure_filepath, 'a')
                        out_file.write(
                            template.render_unicode(
                                buildingelement=bldg_element,
                                zoneindex=count_zonesinbldg,
                                elementindex=count_elementsinzone))
                        out_file.close()
                        # Add rooftop to help_connections
                        template = Template(filename=template_path + "ideas_ConnectComponents")
                        help_connections = open((structure_path + "help_connections.txt"), 'a')
                        help_connections.write(template.render_unicode(
                            zone=zone,
                            buildingelement=bldg_element,
                            index=count_elementsinzone,
                            connect_to_a=True,
                            connect_to_b=False))
                        help_connections.close()

                    for bldg_element in zone.ground_floors:
                        count_groundfloors +=1
                        count_elementsinzone +=1
                        bldg_element.name = type(bldg_element).__name__ + "_" + str(count_zonesinbldg) + "_" + str(count_groundfloors)
                        # Add groundfloor to structure.mo
                        template = Template(filename=template_path + "ideas_SlabOnGround", lookup=lookup)
                        out_file = open(structure_filepath, 'a')
                        out_file.write(
                            template.render_unicode(
                                buildingelement=bldg_element,
                                zoneindex=count_zonesinbldg,
                                elementindex=count_elementsinzone))
                        out_file.close()
                        # Add groundfloor to help_connections
                        template = Template(filename=template_path + "ideas_ConnectComponents")
                        help_connections = open((structure_path + "help_connections.txt"), 'a')
                        help_connections.write(template.render_unicode(
                            zone=zone,
                            buildingelement=bldg_element,
                            index=count_elementsinzone,
                            connect_to_a=True,
                            connect_to_b=False))
                        help_connections.close()

                    for bldg_element in zone.inner_walls: #always internal in one-zone
                        count_innerwalls +=1
                        count_elementsinzone +=2
                        bldg_element.name = type(bldg_element).__name__ + "_" + str(count_zonesinbldg) + "_" + str(count_innerwalls)
                        # Add innerwall to structure.mo
                        template = Template(filename=template_path + "ideas_InnerWall", lookup=lookup)
                        out_file = open(structure_filepath, 'a')
                        out_file.write(
                            template.render_unicode(
                                buildingelement=bldg_element,
                                zoneindex=count_zonesinbldg,
                                elementindex=count_elementsinzone))
                        out_file.close()
                        # Add innerwall to help_connections
                        template = Template(filename=template_path + "ideas_ConnectComponents")
                        help_connections = open((structure_path + "help_connections.txt"), 'a')
                        help_connections.write(template.render_unicode(
                            zone=zone,
                            buildingelement=bldg_element,
                            index=count_elementsinzone,
                            connect_to_a=True,
                            connect_to_b=True))
                        help_connections.close()

                    for bldg_element in zone.floors: #ceilings are not created as they are included in the construction record of the floor
                        if zone.floor_number == 0:
                            error = "This ground floor zone has more than 1 floor/ceiling, which is unexpected"
                            assert len(zone.floors) < 2, error

                            # floor is between two zones (this one and next one)
                            count_floors +=1
                            count_elementsinzone += 1
                            bldg_element.name = type(bldg_element).__name__ + "_" + str(count_zonesinbldg) + "_" + str(
                                count_floors)
                            elements_from_previous_zone.append(bldg_element)

                            # Add floor to structure.mo
                            template = Template(filename=template_path + "ideas_InnerWall", lookup=lookup)
                            out_file = open(structure_filepath, 'a')
                            out_file.write(
                                template.render_unicode(
                                    buildingelement=bldg_element,
                                    zoneindex=count_zonesinbldg,
                                    elementindex=count_elementsinzone))
                            out_file.close()
                            # Add floor to help_connections of this zone
                            template = Template(filename=template_path + "ideas_ConnectComponents")
                            help_connections = open((structure_path + "help_connections.txt"), 'a')
                            help_connections.write(template.render_unicode(
                                zone=zone,
                                buildingelement=bldg_element,
                                index=count_elementsinzone,
                                connect_to_a=True,
                                connect_to_b=False))
                            help_connections.close()

                        else:
                            # floor is internal in zone
                            count_floors +=1
                            count_elementsinzone +=2
                            bldg_element.name = type(bldg_element).__name__ + "_" + str(count_zonesinbldg) + "_" + str(count_floors)
                            # Add floor to structure.mo
                            template = Template(filename=template_path + "ideas_InnerWall", lookup=lookup)
                            out_file = open(structure_filepath, 'a')
                            out_file.write(
                                template.render_unicode(
                                    buildingelement=bldg_element,
                                    zoneindex=count_zonesinbldg,
                                    elementindex=count_elementsinzone))
                            out_file.close()
                            # Add floor to help_connections
                            template = Template(filename=template_path + "ideas_ConnectComponents")
                            help_connections = open((structure_path +"help_connections.txt"), 'a')
                            help_connections.write(template.render_unicode(
                                zone=zone,
                                buildingelement=bldg_element,
                                index=count_elementsinzone,
                                connect_to_a=True,
                                connect_to_b=True))
                            help_connections.close()

                    # Add zone to structure.mo and to help_connections
                    template = Template(filename=template_path + "ideas_Zone")
                    out_file = open(structure_filepath, 'a')
                    out_file.write(
                        template.render_unicode(
                            zone=zone,
                            zoneindex=zoneindex,
                            count_elementsinzone=count_elementsinzone))
                    out_file.close()

                    template = Template(filename=template_path + "ideas_ConnectZones")
                    help_connections = open(structure_path +"help_connections.txt", 'a')
                    help_connections.write(template.render_unicode(
                        zone=zone,
                        index=zoneindex))
                    help_connections.close()


                # End of structure.mo
                structure_file = open(utilities.get_full_path(structure_path +
                                                              bldg.name + "_Structure.mo"), 'a')
                structure_file.write("equation\n")
                help_connections = open(utilities.get_full_path(structure_path +
                                                                "help_connections.txt"), 'r')
                structure_file.write(help_connections.read())
                help_connections.close()
                structure_file.write("end " + bldg.name + "_Structure;")
                structure_file.close()
                os.remove(structure_path + "help_connections.txt")

                # Create folder (data, mat. and constr.)
                data_path = structure_path + "Data/"
                utilities.create_path(data_path)
                materials_path = data_path + "Materials/"
                utilities.create_path(materials_path)
                constructions_path = data_path + "Constructions/"
                utilities.create_path(constructions_path)

                # Create data level (package.mo and package.order)
                _help_package(data_path, "Data",
                              within=prj.name + "." + bldg.name + ".Structure",
                              kindofpackage="MaterialProperties",
                              packagedescription=
                              "Data for transient thermal building simulation")
                _help_package_order(data_path, [], None, ["Materials", "Constructions"], [])

                # Create material and construction level
                #   Per building: 1 construction year > All building elements are of same kind, so we take one of each type and create it on building level
                outer_walls = []
                rooftops = []
                ground_floors = []
                inner_walls = []
                ceilings = []
                floors = []
                windows = []
                for zone in bldg.thermal_zones:
                    if zone.outer_walls != [] and outer_walls == []:
                        outer_walls.append(zone.outer_walls[0])
                    if zone.rooftops != [] and rooftops == []:
                        rooftops.append(zone.rooftops[0])
                    if zone.ground_floors != [] and ground_floors == []:
                        ground_floors.append(zone.ground_floors[0])
                    if zone.inner_walls != [] and inner_walls == []:
                        inner_walls.append(zone.inner_walls[0])
                    if zone.ceilings != [] and ceilings == []:
                        ceilings.append(zone.ceilings[0])
                    if zone.floors != [] and floors == []:
                        floors.append(zone.floors[0])
                    if zone.windows != [] and windows == []:
                        windows.append(zone.windows[0])

                bldg_materials = [] # required for package.order on materials level
                bldg_constructions = [] # required for package.order on constructions level

                bldg_elements = outer_walls + rooftops + ground_floors + inner_walls
                for bldg_element in bldg_elements:
                    construction_name = type(bldg_element).__name__
                    construction_mats = "" # construction outputstring

                    for layer_element in bldg_element.layer:
                        # Create material
                        material = layer_element.material
                        if material.name.replace(" ", "") in bldg_materials:
                            pass
                        else:
                            template = Template(filename=template_path + "ideas_MaterialRecord")
                            out_file = open(materials_path + material.name.replace(" ", "") + ".mo", 'w')
                            out_file.write(template.render_unicode(
                                bldg=bldg,
                                mat=material))
                            out_file.close()
                            bldg_materials.append(material.name.replace(" ", ""))
                        # Create construction (construction outputstring)
                        construction_mats = construction_mats + \
                                            "Data.Materials." + \
                                            material.name.replace(" ", "") + \
                                            "(d=" + \
                                            str(layer_element.thickness) + "),"

                    template = Template(filename=template_path + "ideas_ConstructionRecord")
                    out_file = open(constructions_path + construction_name+ ".mo", 'w')
                    out_file.write(template.render_unicode(
                        bldg=bldg,
                        construction_name=construction_name,
                        construction_mats=construction_mats[:-1]))  # delete last comma
                    out_file.close()
                    bldg_constructions.append(construction_name)

                if floors != []:
                    floor = floors[0]
                    ceiling = ceilings[0]
                    construction_name = type(floor).__name__
                    construction_mats = "" # construction outputstring

                    for layer_element in floor.layer:
                        # Create material
                        material = layer_element.material
                        if material.name.replace(" ", "") in bldg_materials:
                            pass
                        else:
                            template = Template(filename=template_path + "ideas_MaterialRecord")
                            out_file = open(materials_path + material.name.replace(" ", "") + ".mo", 'w')
                            out_file.write(template.render_unicode(
                                bldg=bldg,
                                mat=material))
                            out_file.close()
                            bldg_materials.append(material.name.replace(" ", ""))
                        # Create construction (construction outputstring)
                        construction_mats = construction_mats + \
                                            "Data.Materials." + \
                                            material.name.replace(" ", "") + \
                                            "(d=" + \
                                            str(layer_element.thickness) + "),"
                    for layer_element in ceiling.layer:
                        # Create material
                        material = layer_element.material
                        if material.name.replace(" ", "") in bldg_materials:
                            pass
                        else:
                            template = Template(filename=template_path + "ideas_MaterialRecord")
                            out_file = open(materials_path + material.name.replace(" ", "") + ".mo", 'w')
                            out_file.write(template.render_unicode(
                                bldg=bldg,
                                mat=material))
                            out_file.close()
                            bldg_materials.append(material.name.replace(" ", ""))
                        # Create construction (construction outputstring)
                        construction_mats = construction_mats + \
                                            "Data.Materials." + \
                                            material.name.replace(" ", "") + \
                                            "(d=" + \
                                            str(layer_element.thickness) + "),"

                    template = Template(filename=template_path + "ideas_ConstructionRecord")
                    out_file = open(constructions_path + construction_name+ ".mo", 'w')
                    out_file.write(template.render_unicode(
                        bldg=bldg,
                        construction_name=construction_name,
                        construction_mats=construction_mats[:-1]))  # delete last comma
                    out_file.close()
                    bldg_constructions.append(construction_name)

                for window in windows:
                    construction_name = type(window).__name__
                    if bldg.year_of_construction <= 1945:
                        nameofglazinginIDEAS = "EpcSingle"
                        frame_uvalue = 2.6
                    elif bldg.year_of_construction >= 1946 and bldg.year_of_construction <= 1970:
                        nameofglazinginIDEAS = "EpcSingle"
                        frame_uvalue = 2.6
                    elif bldg.year_of_construction >= 1971 and bldg.year_of_construction <= 1990:
                        nameofglazinginIDEAS = "EpcDouble"
                        frame_uvalue = 4.55
                    elif bldg.year_of_construction >= 1991 and bldg.year_of_construction <= 2005:
                        nameofglazinginIDEAS = "EpcDouble"
                        frame_uvalue = 4.6
                    elif bldg.year_of_construction >= 2006 and bldg.year_of_construction <= 2011:
                        nameofglazinginIDEAS = "Ins2Ar"
                        frame_uvalue = 3
                    elif bldg.year_of_construction >= 2012 and bldg.year_of_construction <= 2016:
                        nameofglazinginIDEAS = "Ins2Ar"
                        frame_uvalue = 3  # self defined, for this moment, same as 2006-2011 > Change this

                    template = Template(filename=template_path + "ideas_GlazingRecord")
                    out_file = open(constructions_path + construction_name + "_Glazing.mo", 'w')
                    out_file.write(template.render_unicode(
                        bldg=bldg,
                        construction_name=construction_name,
                        nameofglazinginIDEAS=nameofglazinginIDEAS))
                    out_file.close()
                    bldg_constructions.append(construction_name + "_Glazing")

                    template = Template(filename=template_path + "ideas_FrameRecord")
                    out_file = open(constructions_path + construction_name + "_Frame.mo", 'w')
                    out_file.write(template.render_unicode(
                        bldg=bldg,
                        construction_name=construction_name,
                        frame_uvalue=frame_uvalue))
                    out_file.close()
                    bldg_constructions.append(construction_name + "_Frame")

                # create package.mo and package.order on materials level
                _help_package(materials_path, "Materials",
                                within=prj.name + "." + bldg.name + \
                                        ".Structure.Data",
                                kindofpackage="MaterialProperties",
                                packagedescription="Library of construction materials")
                _help_package_order(materials_path, [], None, bldg_materials, [])

                # create package.mo and package.order on constructions level
                _help_package(constructions_path, "Constructions",
                              within=prj.name + "." + bldg.name + \
                                     ".Structure.Data",
                              kindofpackage="MaterialProperties",
                              packagedescription="Library of building envelope constructions")
                _help_package_order(constructions_path, [], None, bldg_constructions, [])
    # Now, create project level (project.mo, package.mo and package.order) (after buildings are renamed)
    template = Template(
        filename=template_path + "ideas_Project")
    out_file = open(utilities.get_full_path(path +"/" +
                                           prj.name + "_Project.mo"), 'w')
    out_file.write(template.render_unicode(prj_name=prj.name,
                    buildings = buildings))
    out_file.close()

    _help_package(path, prj.name, uses, within=None)
    _help_package_order(path,
                        package_list_without=buildings,
                        extra_list=[prj.name + "_Project"])

    print("IDEAS building model export is finished. Exports can be found here:")
    print(path)

    if building_model == "ROM":
        #_help_project was reeds aangeroepen onafhankelijk vh export model, echter in .order zit occupant niet, dus we overschrijven nu de file
        _help_package_order(path, buildings, extra_list=[prj.name + "_Project", "Occupant"])

        occupant_path = path + "/Occupant/"
        utilities.create_path(utilities.get_full_path(occupant_path))
        #create occupant.mo, package.mo and package.order on occupant level
        template_path = utilities.get_full_path("data/output/modelicatemplate/ideas/")
        occupant_template = Template(filename=template_path + "ideas_Occupant_ProjectLevel")
        out_file = open(utilities.get_full_path(occupant_path + "ISO13790.mo"), 'w')
        out_file.write(occupant_template.render_unicode(project=prj))
        out_file.close()
        _help_package(occupant_path, "Occupant",within=prj.name,
                      packagedescription="Package of the particular building occupant")
        _help_package_order(occupant_path, [], "", ["ISO13790"], [])


        lookup = TemplateLookup(directories=[utilities.get_full_path(
            os.path.join('data', 'output', 'modelicatemplate'))])
        building_template = Template(
            filename=utilities.get_full_path(
                "data/output/modelicatemplate/IDEAS/ideas_FourElements_Building"), lookup=lookup)
        structure_template = Template(
            filename=utilities.get_full_path(
                "data/output/modelicatemplate/IDEAS/ideas_FourElements_Structure"), lookup=lookup)

        for i, bldg in enumerate(buildings):
            bldg_path = os.path.join(path, bldg.name) + "/"
            utilities.create_path(utilities.get_full_path(bldg_path))
            structure_path = bldg_path + "Structure"
            utilities.create_path(utilities.get_full_path(structure_path))

            out_file = open(utilities.get_full_path(os.path.join(bldg_path +
                                           bldg.name + "_Building.mo")), 'w')
            out_file.write(building_template.render_unicode(bldg=bldg))
            out_file.close()

            _help_package(path=bldg_path,name=bldg.name,within=bldg.parent.name)
            _help_package_order(path=bldg_path,package_list_with_addition=[],addition=None,extra_list=[bldg.name + "_Building","Structure", bldg.name])

            for zone in bldg.thermal_zones:
                out_file = open(utilities.get_full_path(os.path.join(
                    structure_path, bldg.name + '_Structure' + '.mo')), 'w')
                out_file.write(structure_template.render_unicode(zone=zone))
                out_file.close()

                _help_package(path=structure_path,name="Structure",within=prj.name + '.' + bldg.name)
                _help_package_order( path=structure_path,package_list_with_addition=[],addition=None,extra_list=[bldg.name + "_Structure"])

def _help_package(path, name, uses=None, within=None,
                  kindofpackage=None, packagedescription=None):
    '''creates a package.mo file
    Parameters
    ----------
    path : string
        path of where the package.mo should be placed
    name : string
        name of the Modelica package
    uses : [string]
       array containing strings with which Modelica version and which IDEAS version was used
    within : string
        path of Modelica package containing this package
    '''
    package_template = Template(filename=utilities.get_full_path
    ("data/output/modelicatemplate/ideas/package"))
    out_file = open(
        utilities.get_full_path(path + "/" + "package" + ".mo"), 'w')
    out_file.write(package_template.render_unicode(
                                name=name,
                                within=within,
                                uses=uses,
                                kindofpackage = kindofpackage,
                                packagedescription=packagedescription))
    out_file.close()

def _help_package_order(path, package_list_with_addition=None, addition=None, extra_list=[], package_list_without=[]):
    '''creates a package.order file
    Parameters
    ----------
    path : string
        path of where the package.order should be placed
    package_list_with_addition : [string]
        name of all models or packages contained in the package
    addition : string
        if there should be a suffix in front of package_list.string it can
        be specified
    extra_list : [string]
        an extra package or model not contained in package_list can be
        specified, necessary in IDEAS for the folders Structure,
        HeatingSystem, ...
    package_list_without : [string]
        name of all models or packages containd in the package, that don't require the addition
    '''
    if package_list_with_addition is None:
        package_list_with_addition = []
    order_template = Template(filename=utilities.get_full_path
    ("data/output/modelicatemplate/ideas/package_order"))

    out_file = open(
        utilities.get_full_path(path + "/" + "package" + ".order"), 'w')
    out_file.write(order_template.render_unicode
                   (list_with_add=package_list_with_addition,
                    addition=addition,
                    list_without_add=package_list_without,
                    extra=extra_list))
    out_file.close()