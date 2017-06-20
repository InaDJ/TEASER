# Created November 2016
# Ina De Jaeger (KU Leuven, EnergyVille)

"""ideas_output

This module contains function to call Templates for IDEAS model generation
"""
import os
import teaser.logic.utilities as utilities
from mako.template import Template
from mako.lookup import TemplateLookup

def export_ideas(buildings,
                 prj,
                 path=None,
                 building_model="One-zone"):
    """Exports models for IDEAS library

        Exports a building for detailed IDEAS Building model (currently
        only one-zone models are supported, two-zone models will be added).
        Building model is described in conference paper: De Jaeger I, Reynders G,
        Saelens D. Impact of spatial accuracy on district energy simulations.
        Energy Procedia 2017:?:? (paper accepted for NSB 2017)
        This function uses Mako Templates specified in
        data.output.modelicatemplates.ideas

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
            Currently, only export to one-zone models is supported. Two-zone models
            will be added soon
        """
    assert building_model in ["One-zone","ROM"]
    uses = ['Modelica(version="' + prj.modelica_info.version + '")',
        'IBPSA(version="' + prj.buildings[-1].library_attr.version + '")']

    #create project.mo, package.mo and package.order on project level
    _help_project(path=path, prj=prj, buildings=buildings, uses=uses)

    if building_model == "One-zone":
        print("Exporting to one-zone IDEAS building models")
        for bldg in buildings:
            #path variables
            bldg_path = os.path.join(path,bldg.name) + "/"
            occupant_path = bldg_path + "Occupant/"
            structure_path = bldg_path + "Structure/"
            structure_filepath = utilities.get_full_path(structure_path + bldg.name
                +"_Structure.mo")
            data_path = structure_path + "Data/"
            materials_path = data_path + "Materials/"
            constructions_path = data_path + "Constructions/"
            #folder creation
            _help_foldercreation(bldg_path=bldg_path, structure_path=structure_path,
                                 materials_path=materials_path, constructions_path=constructions_path)

            #create building.mo, package.mo and package.order on building level
            _help_building(bldg_path=bldg_path, prj=prj, bldg=bldg)
            #create occupant.mo, package.mo and package.order on occupant level
            _help_occupant(occupant_path=occupant_path, prj=prj, bldg=bldg)
            #create structure.mo, package.mo and package.order on structure level
                #(here initialisation, later addition of zones and components)
            _help_structure(structure_path=structure_path,
                            structure_filepath=structure_filepath,
                            data_path=data_path,
                            prj=prj, bldg=bldg)
            #create help file for connections to add to structure.mo
            help_connections = open(utilities.get_full_path(structure_path +
                                                    "help_connections.txt"), 'w')
            help_connections.close()

            bldg_materials = [] #required for package.order on materials level
            bldg_constructions = [] #required for package.order on constructions level

            for zoneindex, zone in enumerate(bldg.thermal_zones, start = 1):
                buildingelements = zone.outer_walls + zone.rooftops + zone.ground_floors \
                        + zone.inner_walls + zone.ceilings + zone.floors + zone.windows
                count_windows = 0
                count_outerwalls = 0
                count_rooftops = 0
                count_groundfloors = 0
                count_innerwalls = 0
                count_ceilings = 0
                count_floors = 0
                count_elementsinzone = 0
                for elementindex, buildingelement in enumerate(buildingelements, start = 1): #index required for annotation placement
                    construction_mats = ""
                    #create material.mo
                    for layerelement in buildingelement.layer:
                        material = layerelement.material
                        #add the material to the construction outputstring
                        modelicapathtomaterial = "Data.Materials." + \
                                            material.name.replace(" ", "")
                        construction_mats = construction_mats + \
                                            modelicapathtomaterial + \
                                            "(d=" + \
                                            str(layerelement.thickness) + "),"
                        if material.name.replace(" ", "") in bldg_materials:
                            pass #material is already created for this building
                        else:
                            #create material.mo
                            _help_records(recordTemplate="Material",
                                          recordPath=materials_path,
                                          prj=prj, bldg=bldg,
                                          material=material)
                            #add material name to the bldg_materials list
                            bldg_materials.append(material.name.replace(" ", ""))

                    #check which type of building element and add it to structure.mo
                    if type(buildingelement).__name__ == "Window":
                        count_windows += 1
                        count_elementsinzone += 1
                        #rename element, required when citygml import
                        if buildingelement.name == "None":
                            buildingelement.name = "Window_" + str(zone.floor_number) + "_" + str(count_windows)
                        else:
                            buildingelement.name = buildingelement.name + "_" + str(zone.floor_number) + "_" + str(count_windows)
                        #add to structure.mo + create glazing.mo and frame.mo
                        _help_window(structure_path=structure_path,
                                     prj=prj, bldg=bldg, zone=zone, zoneindex=zoneindex,
                                     buildingelement=buildingelement, elementindex=elementindex,
                                     count_elementsinzone=count_elementsinzone,
                                     constructions_path=constructions_path)
                        #add construction name to the bldg_constructions list (both glazing and frame)
                        bldg_constructions.append(buildingelement.name.replace(" ", "")
                                                  + "_Glazing")
                        bldg_constructions.append(buildingelement.name.replace(" ", "")
                                                  + "_Frame")
                    else: #if no window, then opaque for sure
                        if type(buildingelement).__name__ == "OuterWall":
                            count_outerwalls += 1
                            count_elementsinzone +=1
                            #rename element
                            if buildingelement.name == "None":
                                buildingelement.name = "OuterWall_" + str(zone.floor_number) + "_" + str(count_outerwalls)
                            else:
                                buildingelement.name = buildingelement.name + "_" + str(zone.floor_number) + "_" + str(count_outerwalls)
                            #add to structure.mo
                            _help_buildingelement(ideasTemplate="OuterWall",
                                                  structure_path=structure_path,
                                                  structurefile_path=structure_filepath,
                                                  constructions_path=constructions_path,
                                                  prj=prj, bldg=bldg, zone=zone, zoneindex=zoneindex,
                                                  buildingelement=buildingelement, elementindex=elementindex,
                                                  count_elementsinzone=count_elementsinzone,
                                                  construction_mats=construction_mats,
                                                  inc="incWall",
                                                  azi=(buildingelement.orientation-180)/180)
                                                    # TEASER orientation vs IDEAS orientation
                        elif type(buildingelement).__name__ == "Rooftop":
                            count_rooftops += 1
                            count_elementsinzone +=1
                            #rename element
                            if buildingelement.name == "None":
                                buildingelement.name = "Rooftop_" + str(zone.floor_number) + "_" + str(count_rooftops)
                            else:
                                buildingelement.name = buildingelement.name + "_" + str(zone.floor_number) + "_" + str(count_rooftops)
                            if buildingelement.orientation == -1:
                                inc = "incCeil"
                            else:
                                inc = buildingelement.tilt
                            #add to structure.mo
                            _help_buildingelement(ideasTemplate="OuterWall",
                                                  structure_path=structure_path,
                                                  structurefile_path=structure_filepath,
                                                  constructions_path=constructions_path,
                                                  prj=prj, bldg=bldg, zone=zone, zoneindex=zoneindex,
                                                  buildingelement=buildingelement, elementindex=elementindex,
                                                  count_elementsinzone=count_elementsinzone,
                                                  construction_mats=construction_mats,
                                                  inc=inc)
                        elif type(buildingelement).__name__ == "GroundFloor":
                            count_groundfloors += 1
                            count_elementsinzone += 1
                            #rename element
                            if buildingelement.name == "None":
                                buildingelement.name = "Groundfloor_" + str(zone.floor_number) + "_" + str(count_groundfloors)
                            else:
                                buildingelement.name = buildingelement.name + "_" + str(zone.floor_number) + "_" + str(count_groundfloors)
                            #add to structure.mo
                            _help_buildingelement(ideasTemplate="SlabOnGround",
                                                  structure_path=structure_path,
                                                  structurefile_path=structure_filepath,
                                                  constructions_path=constructions_path,
                                                  prj=prj, bldg=bldg, zone=zone, zoneindex=zoneindex,
                                                  buildingelement=buildingelement, elementindex=elementindex,
                                                  count_elementsinzone=count_elementsinzone,
                                                  construction_mats=construction_mats,
                                                  inc="incFloor")
                        elif type(buildingelement).__name__ == "InnerWall":
                            count_innerwalls +=1
                            count_elementsinzone +=2 #element is in IDEAS InternalWall, dus 2 connectionpoints to zone
                            #rename element
                            if buildingelement.name == "None":
                                buildingelement.name = "InnerWall_" + str(zone.floor_number) + "_" + str(count_innerwalls)
                            else:
                                buildingelement.name = buildingelement.name + "_" + str(zone.floor_number) + "_" + str(count_innerwalls)
                            # add to structure.mo
                            _help_buildingelement(ideasTemplate="InnerWall",
                                                  structure_path=structure_path,
                                                  structurefile_path=structure_filepath,
                                                  constructions_path=constructions_path,
                                                  prj=prj, bldg=bldg, zone=zone, zoneindex=zoneindex,
                                                  buildingelement=buildingelement, elementindex=elementindex,
                                                  count_elementsinzone=count_elementsinzone,
                                                  construction_mats=construction_mats,
                                                  inc="incWall",
                                                  azi=(buildingelement.orientation-180)/180)
                                                        #TEASER orientation vs IDEAS orientation
                        elif type(buildingelement).__name__ == "Ceiling":
                            count_ceilings += 1
                            count_elementsinzone += 2 #element is in IDEAS InternalWall, dus 2 connectionpoints to zone
                            #rename element
                            if buildingelement.name == "None":
                                buildingelement.name = "Ceiling_" + str(zone.floor_number) + "_" + str(count_ceilings)
                            else:
                                buildingelement.name = buildingelement.name + "_" + str(zone.floor_number) + "_" + str(count_ceilings)
                            #add to structure.mo
                            _help_buildingelement(ideasTemplate="InnerWall",
                                                  structure_path=structure_path,
                                                  structurefile_path=structure_filepath,
                                                  constructions_path=constructions_path,
                                                  prj=prj, bldg=bldg, zone=zone, zoneindex=zoneindex,
                                                  buildingelement=buildingelement, elementindex=elementindex,
                                                  count_elementsinzone=count_elementsinzone,
                                                  construction_mats=construction_mats,
                                                  inc="incCeil")
                        elif type(buildingelement).__name__ == "Floor":
                            count_floors += 1
                            count_elementsinzone += 2 #element is in IDEAS InternalWall, dus 2 connectionpoints to zone
                            #rename element
                            if buildingelement.name == "None":
                                buildingelement.name = "Floor_" + str(zone.floor_number) + "_" + str(count_floors)
                            else:
                                buildingelement.name = buildingelement.name + "_" + str(zone.floor_number) + "_" + str(count_floors)
                            #add to structure.mo
                            _help_buildingelement(ideasTemplate="InnerWall",
                                                  structure_path=structure_path,
                                                  structurefile_path=structure_filepath,
                                                  construction_mats=construction_mats,
                                                  constructions_path=constructions_path,
                                                  prj=prj, bldg=bldg, zone= zone, zoneindex=zoneindex,
                                                  buildingelement=buildingelement, elementindex=elementindex,
                                                  count_elementsinzone=count_elementsinzone,
                                                  inc="incFloor")
                        else:
                            print("This building element, named " + buildingelement.name +
                                  " \n is neither a Window(), nor an OuterWall(), nor a Rooftop(), " +
                                  " \n nor a Groundfloor(), nor an InnerWall(), nor a Ceiling(), " +
                                  " \n nor a Floor() and was therefore not exported")
                        #add construction name to the bldg_constructions list
                        bldg_constructions.append(buildingelement.name.replace(" ", ""))
                #add this zone to the structure.mo file + add connections to help_connections
                _help_zone(structure_path=structure_path,
                           prj=prj, bldg=bldg, zone=zone, zoneindex=zoneindex,
                           count_elementsinzone=count_elementsinzone)

            #add connections from help_connections to the structure.mo file
            structure_file = open(utilities.get_full_path(structure_path +
                                         bldg.name + "_Structure.mo"), 'a')
            structure_file.write("equation\n")
            help_connections = open(utilities.get_full_path(structure_path +
                                                    "help_connections.txt"), 'r')
            structure_file.write(help_connections.read())
            help_connections.close()
            #add last sentence to the structure.mo file
            structure_file.write("end "+ bldg.name + "_Structure;")
            structure_file.close()
            #delete the help_connections.txt
            os.remove(structure_path + "help_connections.txt")

            #create package.mo and package.order on constructions level
            _help_package(constructions_path, "Constructions",
                          within=prj.name + "." + bldg.name + \
                                 ".Structure.Data",
                          kindofpackage="MaterialProperties",
                          packagedescription="Library of building envelope constructions")
            _help_package_order(constructions_path, [], None, bldg_constructions, [])
            #create package.mo and package.order on materials level
            _help_package(materials_path, "Materials",
                          within=prj.name + "." + bldg.name + \
                                 ".Structure.Data",
                          kindofpackage="MaterialProperties",
                          packagedescription="Library of construction materials")
            _help_package_order(materials_path, [], None, bldg_materials, [])
        print("Exports can be found here:")
        print(path)
    elif building_model == "ROM":
        #_help_project was reeds aangeroepen onafhankelijk vh export model, echter in .order zit occupant niet, dus we overschrijven nu de file
        _help_package_order(path, buildings, extra_list=[prj.name + "_Project", "Occupant"])

        occupant_path = path + "/Occupant/"
        utilities.create_path(utilities.get_full_path(occupant_path))
        #create occupant.mo, package.mo and package.order on occupant level
        filepath = utilities.get_full_path("data/output/modelicatemplate/ideas/")
        occupant_template = Template(filename=filepath + "ideas_Occupant_ProjectLevel")
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
            _help_package_order(path=bldg_path,package_list_with_addition=[],addition=None,extra_list=[bldg.name + "_Building","Structure"])

            for zone in bldg.thermal_zones:
                out_file = open(utilities.get_full_path(os.path.join(
                    structure_path, bldg.name + '_Structure' + '.mo')), 'w')
                out_file.write(structure_template.render_unicode(zone=zone))
                out_file.close()

                _help_package(path=structure_path,name="Structure",within=prj.name + '.' + bldg.name)
                _help_package_order( path=structure_path,package_list_with_addition=[],addition=None,extra_list=[bldg.name + "_Structure"])
        print("Exports can be found here:")
        print(path)

    else:
        print("Please indicate a supported mode for export \
        (for now only: One-zone, ROM), for this reason nothing has been exported")

def _help_foldercreation (bldg_path, structure_path, materials_path, constructions_path):
    # we create a folder for each building
    utilities.create_path(utilities.get_full_path(bldg_path))
    # folder for the heating system
    utilities.create_path(utilities.get_full_path(bldg_path
                                                + "HeatingSystem"))
    # folder for the ventilation system
    utilities.create_path(utilities.get_full_path(bldg_path
                                                + "VentilationSystem"))
    # folder for the electrical system
    utilities.create_path(utilities.get_full_path(bldg_path
                                                + "ElectricalSystem"))
    # folder for the occupant
    utilities.create_path(utilities.get_full_path(bldg_path
                                                + "Occupant"))
    # folder for the structure, materials and constructions
    utilities.create_path(utilities.get_full_path(structure_path))
    utilities.create_path(utilities.get_full_path(materials_path))
    utilities.create_path(utilities.get_full_path(constructions_path))

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

def _help_package_order(path, package_list_with_addition, addition=None, extra_list=[], package_list_without=[]):
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

def _help_records(recordTemplate, recordPath, prj, bldg, buildingelement=None, material=None, construction_mats="", nameofglazinginIDEAS="", frame_uvalue=0):
     #make sure that path = constructions_path when recordTemplate = Construction, Glazing or Frame"
     #make sure that path = materials_path when recordTemplate = Material

    assert recordTemplate in ["Construction", "Glazing", "Frame", "Material"]
    filepath = utilities.get_full_path("data/output/modelicatemplate/ideas/")

    if recordTemplate == "Construction":
        template = Template(filename=filepath + "ideas_ConstructionRecord")
        recordname = recordPath + buildingelement.name.replace(" ", "") + ".mo"
        assert buildingelement is not None
        assert construction_mats is not ""
    elif recordTemplate == "Glazing":
        template = Template(filename=filepath + "ideas_GlazingRecord")
        recordname = recordPath + buildingelement.name.replace(" ", "")\
                                + "_Glazing.mo"
        assert buildingelement is not None
        assert nameofglazinginIDEAS is not ""
    elif recordTemplate == "Frame": #not yet in use
        template = Template(filename=filepath + "ideas_FrameRecord")
        recordname = recordPath + buildingelement.name.replace(" ", "")\
                                + "_Frame.mo"
        assert buildingelement is not None
        assert frame_uvalue is not 0
    elif recordTemplate == "Material":
        template = Template(filename=filepath+"ideas_MaterialRecord")
        recordname = recordPath + material.name.replace(" ", "") + ".mo"
        assert material is not None
    else:
        print("I'm sorry, I cannot find an IDEAS recordtemplate for this record")

    #create record.mo
    out_file = open(utilities.get_full_path(recordname), 'w')
    out_file.write(template.render_unicode(
        mod_prj=prj.name,
        bldg=bldg,
        #required for construction, glazing and frame
        buildingelement=buildingelement,
        #only required for construction
        construction_mats=construction_mats[:-1],  # delete last comma
        #only required for glazing
        nameofglazinginIDEAS = nameofglazinginIDEAS,
        #only required for frame
        frame_uvalue = frame_uvalue,
        #only required for materials
        mat=material))
    out_file.close()

def _help_buildingelement(ideasTemplate, structure_path, structurefile_path, constructions_path,
                          prj, bldg, zone, zoneindex,
                          buildingelement, elementindex, count_elementsinzone,
                          construction_mats, inc, azi = "aziSouth"):

    assert ideasTemplate in ["OuterWall", "SlabOnGround", "InnerWall", "Window", "BoundaryWall"]
    filepath = utilities.get_full_path(
        "data/output/modelicatemplate/ideas/")
    if ideasTemplate == "OuterWall":
        template = Template(filename=filepath + "ideas_OuterWall")
    elif ideasTemplate == "SlabOnGround":
        template = Template(filename=filepath + "ideas_SlabOnGround")
    elif ideasTemplate == "InnerWall":
        template = Template(filename=filepath + "ideas_InnerWall")
    elif ideasTemplate == "Window":
        template = Template(filename=filepath + "ideas_Window")
    elif ideasTemplate == "BoundaryWall": #currently not in use
        template = Template(filename=filepath + "ideas_BoundaryWall")
    else:
        print("I'm sorry, I cannot find an IDEAS template for this BuildingElement()")
    #add component to structure.mo
    out_file = open(structurefile_path, 'a')
    out_file.write(
        template.render_unicode(
            bldg=bldg,
            mod_prj=prj.name,
            buildingelement=buildingelement,
            zoneindex=zoneindex,
            elementindex=elementindex,
            inc=inc,
            azi=azi))
    out_file.close()
    #create construction.mo
    _help_records(recordTemplate="Construction", recordPath=constructions_path, prj=prj, bldg=bldg,
                  buildingelement=buildingelement, construction_mats=construction_mats)
    #add component-connection statements to help_connections
    _help_connectcomponents(structure_path=structure_path, buildingelement=buildingelement, zone=zone, count_elementsinzone=count_elementsinzone, ideasTemplate = ideasTemplate)

def _help_window (structure_path, constructions_path, prj, bldg, zone, zoneindex, buildingelement, elementindex, count_elementsinzone):
    #this should be enhanced, for now: allocate window type based on construction year (based on TABULA Belgium)
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
        frame_uvalue = 3 #self defined, for this moment, same as 2006-2011 > Change this

    #add window to structure.mo
    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    window_template = Template(
        filename=filepath + "ideas_Window")
    out_file = open(utilities.get_full_path(
        structure_path + bldg.name
        + "_Structure.mo"), 'a')
    out_file.write(window_template.render_unicode(
        bldg=bldg,
        mod_prj=prj.name,
        buildingelement=buildingelement,
        zoneindex=zoneindex,
        elementindex = elementindex,
        count_elementsinzone= count_elementsinzone))
    out_file.close()
    #create glazing.mo
    _help_records(recordTemplate="Glazing", recordPath=constructions_path, prj = prj, bldg = bldg, buildingelement=buildingelement,
                  nameofglazinginIDEAS= nameofglazinginIDEAS)
    #create frame.mo (not yet in use)
    _help_records(recordTemplate="Frame", recordPath=constructions_path, prj= prj, bldg = bldg, buildingelement=buildingelement,
                  frame_uvalue= frame_uvalue)
    #add component-connection statements
    _help_connectcomponents(structure_path=structure_path, buildingelement=buildingelement, zone=zone, count_elementsinzone=count_elementsinzone)

def _help_zone (structure_path, prj, bldg, zone, zoneindex, count_elementsinzone):
    #add zone to structure.mo file
    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    zone_template = Template(
        filename=filepath + "ideas_Zone")
    out_file = open(utilities.get_full_path(structure_path +
                                           bldg.name + "_Structure.mo"), 'a')
    out_file.write(zone_template.render_unicode(bldg=bldg,
                                                mod_prj=prj.name,
                                                zone=zone,
                                                zoneindex=zoneindex,
                                                count_elementsinzone = count_elementsinzone))
    out_file.close()

    #add zone-connection statements
    _help_connectzones(structure_path, zone, zoneindex)

def _help_connectcomponents (structure_path, zone, buildingelement, count_elementsinzone, ideasTemplate= ""):
    #add component-connection statements to help_connections
    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    connectcomponents_template = Template(
        filename=filepath + "ideas_ConnectComponents")
    help_connections = open(utilities.get_full_path(structure_path +
                                            "help_connections.txt"), 'a')
    help_connections.write(connectcomponents_template.render_unicode(
        buildingelement=buildingelement,
        zone=zone,
        index=count_elementsinzone,
        ideasTemplate = ideasTemplate))
    help_connections.close()

def _help_connectzones (structure_path, zone, zoneindex):
    #add zone-connection statements to help_connections
    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    connectzones_templates = Template(
        filename=filepath + "ideas_ConnectZones")
    help_connections = open(utilities.get_full_path(structure_path +
                                            "help_connections.txt"), 'a')
    help_connections.write(connectzones_templates.render_unicode(
                                        zone=zone,
                                        index=zoneindex))
    help_connections.close()

def _help_structure (structure_path, structure_filepath, data_path, prj, bldg):
    #create structure.mo
    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    structure_template = Template(
        filename=filepath + "ideas_Structure")
    out_file = open(structure_filepath, 'w')
    out_file.write(structure_template.render_unicode(bldg=bldg,
                                                     mod_prj=prj.name))
    out_file.close()
    #create package.mo and package.order on structure level
    _help_package(structure_path, "Structure",
                  within=prj.name + "." + bldg.name,
                  packagedescription=
                  "Package of the particular building structure")
    _help_package_order(structure_path, [bldg], "_Structure", ["Data"], [])
    #create package.mo and package.order on data level
    _help_package(data_path, "Data",
                  within=prj.name + "." + bldg.name + ".Structure",
                  kindofpackage="MaterialProperties",
                  packagedescription=
                  "Data for transient thermal building simulation")
    _help_package_order(data_path, [], None, ["Materials", "Constructions"], [])

def _help_heatingsystem ():

    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    heatingsystem_template = Template(
        filename=filepath + "ideas_HeatingSystem")

def _help_ventilationsystem ():

    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    ventilationsystem_template = Template(
        filename=filepath + "ideas_VentilationSystem")

def _help_electricalsystem ():

    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    electricalsystem_template = Template(
        filename=filepath + "ideas_ElectricalSystem")

def _help_occupant (occupant_path, prj, bldg):
    #create occupant.mo
    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    occupant_template = Template(
        filename=filepath + "ideas_Occupant")
    out_file = open(utilities.get_full_path(occupant_path + "ISO13790.mo"), 'w')
    out_file.write(occupant_template.render_unicode(bldg=bldg,
                                                    mod_prj=prj.name))
    out_file.close()

    #create package.mo and package.order on occupant level
    _help_package(occupant_path, "Occupant",
                  within=prj.name + "." + bldg.name,
                  packagedescription=
                  "Package of the particular building occupant")
    _help_package_order(occupant_path, [], "", ["ISO13790"], [])

def _help_building (bldg_path, prj, bldg):
    #building.mo model
    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    building_template = Template(
        filename=filepath + "ideas_Building")
    out_file = open(utilities.get_full_path(bldg_path +
                                           bldg.name + "_Building.mo"), 'w')
    out_file.write(building_template.render_unicode(bldg=bldg,
                                                    mod_prj=prj.name))
    out_file.close()

    #this building with an inner sim > runable file on building level
    building_runable_template = Template(
        filename = filepath + "ideas_Building_runable")
    out_file = open(utilities.get_full_path(bldg_path +
                                           bldg.name + ".mo"), 'w')
    out_file.write(building_runable_template.render_unicode(bldg=bldg,
                                                    mod_prj=prj.name))
    out_file.close()

    _help_package(bldg_path, bldg.name, within=prj.name)
    _help_package_order(bldg_path, [bldg], "_Building",
                        ["Structure", "HeatingSystem", \
                         "VentilationSystem", "ElectricalSystem", \
                         "Occupant"], [bldg])

def _help_project(path, prj, buildings, uses):

    filepath = utilities.get_full_path(
            "data/output/modelicatemplate/ideas/")
    template = Template(
        filename=filepath + "ideas_Project")
    out_file = open(utilities.get_full_path(path +"/" +
                                           prj.name + "_Project.mo"), 'w')
    out_file.write(template.render_unicode(prj_name=prj.name,
                    buildings = buildings))
    out_file.close()

    _help_package(path, prj.name, uses, within=None)
    _help_package_order(path, buildings, extra_list=[prj.name + "_Project"])