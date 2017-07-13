from setuptools import setup
from sys import platform

setup(name='teaser',
      version='0.5.2',
      description='Tool for Energy Analysis and Simulation for '
                  'Efficient Retrofit ',
      url='https://github.com/RWTH-EBC/TEASER',
      author='RWTH Aachen University, E.ON Energy Research Center, '
             'Institute of Energy Efficient Buildings and Indoor Climate',
      author_email='ebc-teaser@eonerc.rwth-aachen.de',
      license='MIT',
      packages=[
          'teaser',
          'teaser.logic',
          'teaser.logic.archetypebuildings',
          'teaser.logic.archetypebuildings.bmvbs',
          'teaser.logic.archetypebuildings.bmvbs.custom',
          'teaser.logic.archetypebuildings.urbanrenet',
          'teaser.logic.buildingobjects',
          'teaser.logic.buildingobjects.boundaryconditions',
          'teaser.logic.buildingobjects.buildingphysics',
          'teaser.logic.buildingobjects.buildingsystems',
          'teaser.logic.buildingobjects.calculation',
          'teaser.logic.simulation',
          'teaser.data',
          'teaser.data.bindings',
          'teaser.data.bindings.opengis',
          'teaser.data.bindings.opengis.citygml',
          'teaser.data.bindings.opengis.citygml.raw',
          'teaser.data.bindings.opengis.misc',
          'teaser.data.bindings.opengis.misc.raw',
          'teaser.data.bindings.opengis.raw',
          'teaser.data.bindings.schemas',
          'teaser.data.bindings.v_0_3_9',
          'teaser.data.bindings.v_0_4',
          'teaser.data.bindings.v_0_5',
          'teaser.data.input',
          'teaser.data.input.inputdata',
          'teaser.data.input.inputdata.weatherdata',
          'teaser.data.inputtemplates',
          'teaser.data.output',
          'teaser.data.output.texttemplate',
          'teaser.data.output.modelicatemplate',
          'teaser.data.output.modelicatemplate.AixLib',
          'teaser.data.output.modelicatemplate.IBPSA',
          'teaser.data.output.modelicatemplate.IDEAS',
          'teaser.examples',
          'teaser.examples.simulation',
          'teaser.examples.verification',
          'teaser.examples.examplefiles',
          'teaser.examples.examplefiles.MelatenXML',
          'teaser.examples.GENK',
          'teaser.gui',
          'teaser.gui.controller',
          'teaser.gui.guihelp',
          'teaser.gui.guiimages',
          'teaser.gui.guiimages.OfficeBuildings',
          'teaser.gui.guiimages.Residentials'],
      package_data={
          'teaser.data.input.inputdata': ['*.xml'],
          'teaser.data.input.inputdata.weatherdata': [
              'DEU_BW_Mannheim_107290_TRY2010_12_Jahr_BBSR.mos'],
          'teaser.data.input.inputtemplates': [
              'teaser_building_from_excel',
              'teaser_project_end_from_excel',
              'teaser_project_start_from_excel'],
          'teaser.data.output.modelicatemplate': [
              'package',
              'package_order',
              'conversion',
              'modelica_language'],
          'teaser.data.output.modelicatemplate.AixLib': [
              'AixLib_Multizone',
              'AixLib_ThermalZoneRecord_OneElement',
              'AixLib_ThermalZoneRecord_TwoElement',
              'AixLib_ThermalZoneRecord_ThreeElement',
              'AixLib_ThermalZoneRecord_FourElement'],
          'teaser.data.output.modelicatemplate.IBPSA': [
              'IBPSA_OneElement',
              'IBPSA_TwoElements',
              'IBPSA_ThreeElements',
              'IBPSA_FourElements'],
          'teaser.data.output.modelicatemplate.IDEAS': [
              'ideas_BoundaryWall',
              'ideas_Building',
              'ideas_Building_inner_sim',
              'ideas_ConnectComponents',
              'ideas_ConnectZones',
              'ideas_ConstructionRecord',
              'ideas_ElectricalSystem',
              'ideas_FrameRecord',
              'ideas_FourElements_Building'
              'ideas_FourElements_structure'
              'ideas_GlazingRecord',
              'ideas_HeatingSystem',
              'ideas_InnerWall',
              'ideas_MaterialRecord',
              'ideas_Occupant',
              'ideas_Occupant_ProjectLevel'
              'ideas_OuterWall',
              'ideas_Project',
              'ideas_SlabOnGround',
              'ideas_Structure',
              'ideas_VentilationSystem',
              'ideas_Window',
              'ideas_Zone',
              'package',
              'package_order'],
          'teaser.data.output.texttemplate': [
              'ReadableBuilding_OneElement',
              'ReadableBuilding_TwoElement',
              'ReadableBuilding_ThreeElement',
              'ReadableBuilding_FourElement'],
          'teaser.data.bindings.schemas': ['*.xsd'],
          'teaser.gui.guiimages': ['*.png'],
          'teaser.gui.guiimages.OfficeBuildings': ['*.png'],
          'teaser.gui.guiimages.Residentials': ['*.png'],
          'teaser.examples.examplefiles': ['*.teaserXML', '*.gml'],
          'teaser.examples.examplefiles.MelatenXML': ['*.xml']},
      classifiers=[
          'License :: OSI Approved :: MIT License',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Intended Audience :: Science/Research',
          'Topic :: Software Development :: Code Generators',
          'Topic :: Scientific/Engineering',
          'Topic :: Utilities'],
      install_requires=['mako', 'pyxb', 'pytest', 'scipy'])