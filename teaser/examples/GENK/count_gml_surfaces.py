# Created June 2017
# Ina De Jaeger

"""This module contains an example how to import TEASER projects from
*.teaserXML and pickle in order to reuse data.
"""
import teaser.data.output.ideas_district_simulation as simulations
import teaser.data.input.citygml_input as citygml_in
import os
import pandas as pd

def example_load_citygml():
    """"This function demonstrates different loading options of TEASER"""

    # In example e4_save we saved two TEASER projects using *.teaserXML and
    # Python package pickle. This example shows how to import these
    # information into your python environment again.

    # To load data from *.teaserXML we can use a simple API function. So
    # first we need to instantiate our API (similar to example
    # e1_generate_archetype). The XML file is called
    # `ArchetypeExample.teaserXML` and saved in the default path. You need to
    #  run e4 first before you can load this example file.

    from teaser.project import Project

    # The last option to import data into TEASER is using a CityGML file. The
    # import of CityGML underlies some limitations e.g. concerning data
    # given in the file and the way the buildings are modeled.
    path = "D:\Ina\Data\GRB\GML/" # path to folder which contains 3 folders (streets_LOD2, streets_LOD1_ridge and streets_LOD1_halfroof)
    generate_streetnames_from = "Nothing" # choose either "Excel" or "Folder"

    if generate_streetnames_from == "Folder":
        streetnames = create_streetnames_from_directory(path + "Streets_LOD2/")
    elif generate_streetnames_from == "Excel":
        path_to_excel = "C:\Users\ina\Box Sync\Onderzoek\Projects\Gemeenschappelijke case Genk\Neighbourhood model 0.0.1\Number of buildings in districts\StreetsGenkPerDistrict.xlsx"
        name_of_district = "Boxbergheide"  # name of excel sheet
        streetnames = create_streetnames_from_excel(path_to_excel, name_of_district)
    else:
        streetnames = ['Flekeleerstraat', 'Fletersdel', 'Flikbergstraat',
                   'FranklinRooseveltstraat', 'FransAllardstraat', 'Fransebosstraat', 'Fruitmarkt', 'Gaarveld',
                   'Gansenwijer', 'Gasthofstraat', 'Geenhornstraat', 'Geerstraat', 'Geitenbladstraat',
                   'Gelabbekerstraat', 'Geleenlaan', 'Genkerhei', 'GeorgesDodemontstraat', 'Geraertsstraat',
                   'Geraniumstraat', 'Gerststraat', 'Gielisdries', 'Gierenshof', 'Gierensstraat', 'Gieterijstraat',
                   'Gildelaan', 'Gilissenweier', 'Godsheidestraat', 'Gordelweg', 'Goudstraat', 'Goudvinkstraat',
                   'GouverneurAlex.Galopinstraat', 'GouverneurAlexGalopinstraat', 'Graanplein', 'Gracht', 'Grensstraat',
                   'Groenstraat', 'Groenven', 'Grotestraat', 'Grotewinkelstraat', 'Gruisweg', 'GuidoGezellelaan',
                   'GuillaumeLambertlaan', 'Guldensporenlaan', 'GustaveFrancottestraat', 'Haagbemden',
                   'Haagdoornstraat', 'Haagsteeg', 'Haardstraat', 'Haasberg', 'Halenstraat', 'Halfblookstraat',
                   'Halmstraat', 'Halveweg', 'Hamalstraat', 'Hameistraat', 'Haneveldstraat', 'Hannesstraat',
                   'Hasseltweg', 'Havenstraat', 'Haverweg', 'Hazelnootstraat', 'Hazenstraat', 'Heeldstraat',
                   'Heesterbesstraat', 'Heibergstraat', 'Heiblok', 'Heidebos', 'Heidepark', 'Heidestraat',
                   'Heidriesstraat', 'Heilapstraat', 'Heiveldstraat', 'Heiweier', 'Heizeisstraat', 'Hemelrijk',
                   'Hengelhoefstraat', 'Hengelweistraat', 'Hennepstraat', 'HenriDecleenestraat', 'HenriEsserslaan',
                   'HenriForirstraat', 'HenriLacostestraat', 'HenryFordlaan', 'Heppenzeelstraat', 'Herenstraat',
                   'Herinneringstraat', 'Herkenrodeplein', 'Herkenrodestraat', 'Hermesdijkstraat', 'Hermeslaan',
                   'Heufstraat', 'Hiemelsbergstraat', 'Hoefstadstraat', 'Hoekstraat', 'Hoevenhaag', 'Hoevenzavellaan',
                   'Hofstede', 'Hofweg', 'Holenteerstraat', 'Holeven', 'Hommelheidestraat', 'Hondeskuilstraat',
                   'Hondsbos', 'Hoogblookstraat', 'Hoogstraat', 'Hoogveldstraat', 'Hoogzij', 'Hooiopperstraat',
                   'Hooiplaats', 'Hooiweg', 'Horizonlaan', 'Hornsbergstraat', 'Hornszee', 'Horstenstraat',
                   'Hortensiastraat', 'Hospitaalstraat', 'Houtparklaan', 'Houtwal', 'Houweelstraat', 'Hovenierslaan',
                   'HubertDecreeftstraat', 'HubertGoffinstraat', 'Huisbamptstraat', 'Huisdriesstraat', 'Huiskensweier',
                   'Hulshagenstraat', 'Hulstbesstraat', 'Hulststraat', 'Iepenstraat', 'Ijzersteenweg', 'Ijzerstraat',
                   'Ijzerven', 'Inhamstraat', 'Irisstraat', 'Jaarbeurslaan', 'Jagersweg', 'JanHabexlaan',
                   'JanLatoslaan', 'JanMathijsWinterslaan', 'Jasmijnenstraat', 'JefUlburghsstraat', 'Jeneverbesstraat',
                   'Jonkersblook', 'JosDeGreevestraat', 'JulesCarlierstraat', 'Kaarbaan', 'Kamillestraat', 'Kampstraat',
                   'Kanaaloever', 'Kanaalweg', 'Kapelaansblook', 'Kapelstraat', 'Karekietstraat', 'Kastertstraat',
                   'Kattevennen', 'Keerstraat', 'Keinkesstraat', 'Keistraat', 'Kempenlaan', 'Kennipshoefstraat',
                   'Kennipstraat', 'Kensheide', 'Kerkeweg', 'Kerkstraat', 'Kielenswenbergweg', 'Kielstraat',
                   'Kievitstraat', 'Kiezelstraat', 'Klaproosstraat', 'Klaverbladstraat', 'KleineHostartstraat',
                   'KleinLangerlostraat', 'Kleinven', 'Klimoplaan', 'Klokkuil', 'Klokstraat', 'Kloosterstraat',
                   'Klotbroek', 'Klotsenhoutstraat', 'Klotstraat', 'Kneippstraat', 'Koebaan', 'Koerlostraat', 'Koerweg',
                   'Kokerstraat', 'Kolderbosstraat', 'Kolenhavenstraat', 'Kompellaan', 'KoningAlbertstraat',
                   'KoningBoudewijnlaan', 'KoninginAstridlaan', 'Koolmijnlaan', 'Koolraapstraat', 'Korenbloemstraat',
                   'Korenstraat', 'Kortestraat', 'Kouterstraat', 'Kraaistraat', 'Krekeldries', 'Krekenstraat',
                   'Krelstraat', 'Kriekboomstraat', 'Krokusstraat', 'Krommestraat', 'Kruidenlaan', 'Kruisbosstraat',
                   'Kruiseikstraat', 'Kruisstraat', 'Kuilenbroekstraat', 'Kuilenstraat', 'Kunstenaarshof', 'Kuurstraat',
                   'Kwikstaartstraat', 'Laarweg', 'Laatgoedstraat', 'Landschapshof', 'Landwaartslaan', 'Langehaag',
                   'Langerloweg', 'Langstukweg', 'Langwaterstraat', 'Lantmeetersweg', 'Lapzeisstraat', 'Lavendelstraat',
                   'Leemkuilstraat', 'Leemstraat', 'Leeuwerikstraat', 'Leliestraat', 'Lentelaan', 'LeonDereuxstraat',
                   'LeopoldIII-laan', 'Lessenberg', 'Liersstraat', 'LieveVrouwstraat', 'Lijkweg', 'Lijsterbesstraat',
                   'Lindebosstraat', 'Lindenstraat', 'Loofstraat', 'Lortblookstraat', 'Loskaaistraat',
                   'LouisChainayestraat', 'Lourdeskapelstraat', 'Lousbeekstraat', 'LucienLondotstraat', 'Luikerwijk',
                   'Lupienenstraat', 'Maaseikerbaan', 'Maastrichterweg', 'Madeliefjesstraat', 'Maisstraat',
                   'MarcelHabetslaan', 'Maretakstraat', 'Margarethalaan', 'Marjoleinstraat', 'Marktstraat',
                   'Mastboomstraat', 'Matenstraat', "MaxL'Hoeststraat", 'Mee', 'Meeuwerstraat', 'Meibloemstraat',
                   'Meidoornstraat', 'Meilweg', 'Meistraat', 'Melbergstraat', 'Mercuriuslaan', 'Meridiaanlaan',
                   'Mettenveld', 'Mezenstraat', 'Middelgracht', 'Middenkruis', 'Mie', 'Miklaan', 'Minderbroedersstraat',
                   'Mispadstraat', 'Mispelaarstraat', 'Moesstraat', 'Molenblookstraat', 'Moleneindeweg', 'Molenstraat',
                   'Mondeolaan', 'Mosselerlaan', 'Mottekruidstraat', 'Mouwstraat', 'Muggenberg', 'Mulstraat',
                   'Munsterenstraat', 'Muntstraat', 'Myosotisstraat', 'Nachtegaalstraat', 'NeelDoffstraat',
                   'Neerzijstraat', 'Negenhuizenstraat', 'Nieuwdakplein', 'Nieuwdorpstraat', 'NieuweErvenstraat',
                   'NieuweKempen', 'NieuweKuilenweg', 'Nieuwland', 'Nieuwpoortlaan', 'Nieuwstraat', 'Nijverheidslaan',
                   'Noordlaan', 'Olmenstraat', 'Omlooplaan', 'Onafhankelijkheidslaan', 'Onderwijslaan', 'Oosterring',
                   'Oostervenne', 'Oosterwennel', 'Oostlaan', 'OpdeBerk', 'OpdeMeerstraat', 'Opglabbekerzavel',
                   'Oud-Termienstraat', 'Oudasserstraat', 'OudeDriesstraat', 'OudeHeide', 'OudeHoevestraat',
                   'OudeHofstraat', 'OudeHostartstraat', 'OudeMarkt', 'OudePostweg', 'OudeZonhoverweg',
                   'Overheidestraat', 'Paardskuil', 'Pachthofstraat', 'Paesteblookstraat', 'Paneelstraat',
                   'Paniswijerstraat', 'Panoramastraat', 'Papblookstraat', 'Parallelstraat', 'Paresbemdstraat',
                   'Parklaan', 'Parochiekerkstraat', 'Passerelstraat', 'PastoorRaeymaekersstraat', 'PaulHabetslaan',
                   'PaulTrazensterstraat', 'Peerboomstraat', 'Peerdsdiefweier', 'Peerdsmeer', 'Peperhofstraat',
                   'Pepermuntstraat', 'PeterBenoitlaan', 'Peterseliestraat', 'Petuniastraat', 'Pioenstraat',
                   'Plaggenstraat', 'Planetariumweg', 'Plataanstraat', 'Plattewijerstraat', 'Ploegstraat',
                   'Populierenstraat', 'Poreistraat', 'Postbaan', 'Posteleinstraat', 'Postwinningstraat', 'Priemstraat',
                   'Priesterhaagstraat', 'Putmosstraat', 'Putstraat', 'Putwijerstraat', 'Raafstraat',
                   'RafMailleuxstraat', 'Rakestraat', 'Rechtestraat', 'Reenstraat', 'Reeweg', 'Regenbooglaan',
                   'Reinpadstraat', 'Renerkesstraat', 'Resedastraat', 'Richter', 'Rietbeemdstraat', 'Rietlaan',
                   'Rijtstraat', 'Risstraat', 'Rockxweier', 'Roedenstraat', 'Roerdompstraat', 'Roerstraat',
                   'Roggestraat', 'Romeplaats', 'Rondpuntlaan', 'Roodkruisstraat', 'Rooistraat', 'Rootenstraat',
                   'Rozemarijnstraat', 'Rozenkranslaan', 'Rozenstraat', 'Ruisstraat', 'Rustlaan', 'Salieweg',
                   'Schaapsdreef', 'Schaapsdries', 'Schabartstraat', 'Schalmstraat', 'Schansbroekstraat',
                   'Scheidingsweg', 'Schemmersberg', 'Schemmersheide', 'Schepersweg', 'SchiepseBos', 'Schietboomstraat',
                   'Schildershof', 'Schoolstraat', 'Schoorbosheide', 'Schoorbosstraat', 'Schurfstraat',
                   'Schuttenstraat', 'Seinhuisstraat', 'Singlisstraat', 'Sint-Eventiuslaan', 'Sint-Jan-Baptistplein',
                   'Sint-Janspark', 'Sint-Lodewijkstraat', 'Sint-Martensbergstraat', 'Sint-Martinusplein',
                   'Sint-Michielsstraat', 'Sintelstraat', 'Slaghoutstraat', 'Slagmolenweg', 'Sledderlo', 'Sledderloweg',
                   'Sleeuwstraat', 'Sleutelbloemstraat', 'Sliehaagstraat', 'Slingerweg', 'Sloorstraat', 'Slopstraat',
                   'Smeilstraat', 'Socialestraat', 'Sparrenlaan', 'Spechtstraat', 'Speltstraat', 'Spilstraat',
                   'Spoorstraat', 'Spoorwegstraat', 'Sportlaan', 'Springstraat', 'Spurriestraat', 'Staatstuinwijk',
                   'Stadionplein', 'Stadsplein', 'Stalenstraat', 'Stationsstraat', 'Steenakker', 'Steenbakkerijstraat',
                   'Steenbergstraat', 'Steenbeukstraat', 'Steendaalstraat', 'Steeneikstraat', 'Stegestraat',
                   'Stichelberglaan', 'Stiemerbeekstraat', 'Stoffelsbergstraat', 'Streepkenstraat', 'Strijphout',
                   'Strippestraat', 'Strooiselstraat', 'Stuifzandstraat', 'Stukstraat', 'Swennenblook',
                   'Swinnenwijerweg', 'Takkenbosstraat', 'Talingpark', 'Tarwestraat', 'Taunusweg', 'Teiserikweg',
                   'Tennislaan', 'Terboekt', 'ThorPark', 'Tiendenstraat', 'Timkensbergstraat', 'Toekomstlaan',
                   'Tolbareelstraat', 'Torenlaan', 'Transportlaan', 'Trichterweg', 'Troisdorflaan', 'Tronkstraat',
                   'Trosheidestraat', 'Truyenlandstraat', 'Tulpenstraat', 'Turfstraat', 'Uilenspiegellaan',
                   'Uitbreidingslaan', 'Vaartstraat', 'Valgaarstraat', 'Valleistraat', 'Varenlaan', 'Veenweg',
                   'VeertienSeptemberlaan', 'Vekenstraat', 'Veldstraat', 'Venkellaan', 'Vennestraat',
                   'Vierblokkenstraat', 'Vijverstraat', 'Viooltjesstraat', 'Vlakveldplein', 'Vliegplein', 'Vlierhout',
                   'Vlierstraat', 'Vlodropstraat', 'Vogelkersstraat', 'Vogelsberg', 'Vogelzangstraat', 'Volmolen',
                   'Vooruitgangstraat', 'Vooruitzichtlaan', 'Voskenslaan', 'Vredestraat', 'Vrijgeweidestraat',
                   'Waardstraat', 'Waloorstraat', 'Wandelstraat', 'Waterbleekstraat', 'Watergrasstraat',
                   'Waterscheistraat', 'Waterstraat', 'Watertorenstraat', 'WegnaarAs', 'WegnaarZwartberg', 'Weiblook',
                   'Weidestraat', 'Weienhout', 'Welzijnscampus', 'Wenbergstraat', 'Wennel', 'Westerring',
                   'Westerwennel', 'Weststraat', 'Wetzandstraat', 'Wiekstraat', 'Wielewaalstraat', 'Wiemesmeerstraat',
                   'Wijerdriesstraat', 'Wildekastanjelaan', 'Wildekerslaan', 'Wilderozentuin', 'Wildetijmstraat',
                   'Wildhoutstraat', 'Willemshofweg', 'WillyMindersstraat', 'Windekestraat', 'Windmolenstraat',
                   'Winkelstraat', 'Winterbeeklaan', 'Wintergroenstraat', 'Winterslagstraat', 'Witmeerstraat',
                   'Wolfsbergstraat', 'Woudstraat', 'Zagerijstraat', 'Zandbergstraat', 'Zandoerstraat', 'Zandstraat',
                   'Zaveldriesstraat', 'Zavelputstraat', 'ZenobeGrammestraat', 'Zevenbonderstraat', 'Zevenputtenstraat',
                   'Zinniastraat', 'Zonhoverweg', 'Zonnebloemstraat', 'Zonnedauwstraat', 'Zonneweeldelaan',
                   'Zouwstraat', 'Zuiderring', 'Zuidplaats', 'ZusterEduardalaan', 'Zwaluwstraat']
    print streetnames

    df_buildings = pd.DataFrame({'building name': ["test1"],
                                 'number of gml surfaces': [2],
                                 'number of floors': [2],
                                 'building volume': [300],
                                 'building area': [100],
                                 'groundfloor area': [50],
                                 'outerwall area': [400],
                                 'windows area': [50],
                                 'roof area': [5],
                                 'innerwall area': [500],
                                 'innerfloor area': [50]})
    for streetname in streetnames:
        print streetname
        try:
                prj_LOD2 = Project(load_data=True, used_data_country="Belgium")
                prj_LOD2.name = streetname + "_LOD2"
                prj_LOD2.used_library_calc = 'IDEAS'
                prj_LOD2.load_citygml(path=path + "Streets_LOD2/" + streetname + ".gml",
                                      checkadjacantbuildings=False,
                                      number_of_zones=1,
                                      merge_buildings=False)
                prj_LOD2.calc_all_buildings(
                    raise_errors=True)  # moet aangeroepen worden, anders wordt volume van gebouw niet goed gezet
                for bldg in prj_LOD2.buildings:
                    number_of_gmls = len(bldg.gml_surfaces)
                    building_volume = 0
                    building_area = 0
                    count_outerwalls_area = 0
                    count_windows_area = 0
                    count_rooftops_area = 0
                    count_groundfloors_area = 0
                    count_innerwalls_area = 0
                    count_floors_area = 0
                    #print bldg.name
                    for zoneindex, zone in enumerate(bldg.thermal_zones, start=1):
                        building_volume += zone.volume
                        building_area += zone.area
                        for bldg_element in zone.outer_walls:
                            count_outerwalls_area += bldg_element.area
                        for bldg_element in zone.windows:
                            count_windows_area += bldg_element.area
                        for bldg_element in zone.rooftops:
                            #print ("Roof areas: ")
                            #print bldg_element.area
                            count_rooftops_area += bldg_element.area
                        for bldg_element in zone.ground_floors:
                            count_groundfloors_area += bldg_element.area
                        for bldg_element in zone.inner_walls:
                            count_innerwalls_area += bldg_element.area
                        for bldg_element in zone.floors:
                            count_floors_area += bldg_element.area

                    df_bldg = pd.DataFrame({'building name': [bldg.name],
                                            'number of gml surfaces': [number_of_gmls],
                                            'number of floors': [bldg.number_of_floors],
                                            'building volume': [building_volume],
                                            'building area': [building_area],
                                            'groundfloor area': [count_groundfloors_area],
                                            'outerwall area': [count_outerwalls_area],
                                            'windows area': [count_windows_area],
                                            'roof area': [count_rooftops_area],
                                            'innerwall area': [count_innerwalls_area],
                                            'innerfloor area': [count_floors_area]
                                            })
                    df_buildings = pd.concat([df_buildings, df_bldg])
                df_buildings.to_excel("D:\Ina\Results\df_building_comparison.xlsx")
        except:
                print('There has been an unknown error in this street ____________________________________________________________' + streetname)
                pass
    print df_buildings

def create_streetnames_from_excel(path_to_excel, name_of_district):
    df_streetnames = pd.read_excel(path_to_excel, sheetname=name_of_district, squeeze=True)
    streetnames = [str(streetname) for streetname in df_streetnames.tolist()]
    return streetnames

def create_streetnames_from_directory(path):
    streetnames = [name[:-4] for name in os.listdir(path)
            if name.endswith(".gml")]
    return streetnames

if __name__ == '__main__':
    example_load_citygml()

    print("Example 10: That's it! :)")