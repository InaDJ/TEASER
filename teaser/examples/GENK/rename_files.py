# Created July 2017
# Ina De Jaeger

"""This module contains some functions to check which files are in multiple folders, and to merge these file.
For CityGML: the last line of the first file needs to be deleted
and the first two lines of the second file need to be deleted
After you merged the files, you should also rename the ID's and names of the buildings/buildingparts.
DON'T FORGET THIS!

Two different modes:
1. compare between folders and merge between folders (for now implemented for 4 folders = 6 combinations)
2. merge specified files within 1 folders (enter the names of the existing files and the name of the new file)

"""

import os

def rename_files():
    """
    Parameters
    ----------

    """
    path = "C:\Users\ina\Desktop\GRB/"
    variant1 = "Streets_LOD2"
    variant2 = "Streets_LOD1_Ridge_based"
    variant3 = "Streets_LOD1_Half_roof_based"
    variants = [variant1, variant2, variant3]

    for variant in variants:
        variant_path = path + variant + "/"
        for filename in os.listdir(variant_path):
            if (" " in filename) == True:
                # rename file
                old_filename = filename
                new_filename = filename.replace(" ", "")
                os.rename(variant_path+old_filename, variant_path+new_filename)
                # replace all occurances in gml file
                with open(variant_path+new_filename, 'r') as file:
                    filedata = file.read()
                filedata = filedata.replace(old_filename[:-4], new_filename[:-4]) # delete the .gml at the end
                with open(variant_path+new_filename, 'w') as file:
                    file.write(filedata)
                print (old_filename + " has been changed to " + new_filename)

def check_files_in_folder():
    """
    Parameters
    ----------

    """
    compare_between_folders = True
    merge_specified_files = False
    rename_files = False

    path = "D:\Ina\Data\GRB\GML/"
    gml_1 = "Genk_Streets_1_2/"
    gml_3 = "Genk_Streets_3_4_5/"
    gml_6 = "Genk_Streets_6_7_8/"
    gml_9 = "Genk_Streets_9_10_11/"
    variant1 = "Streets_LOD2"
    variant2 = "Streets_LOD1_Ridge_based"
    variant3 = "Streets_LOD1_Half_roof_based"
    variants = [variant1, variant2, variant3]
    "D:\Ina\Data\GRB\GML\Genk_Streets_3_4_5\Streets_LOD2\Akkerstraat.gml"
    if compare_between_folders: #run multiple times in case streets are in more than 2 folders
        list_1 = [file for file in os.listdir(path+gml_1+variant1+"/") if file.endswith(".gml")]
        list_3 = [file for file in os.listdir(path+gml_3+variant1+"/") if file.endswith(".gml")]
        list_6 = [file for file in os.listdir(path+gml_6+variant1+"/") if file.endswith(".gml")]
        list_9 = [file for file in os.listdir(path+gml_9+variant1+"/") if file.endswith(".gml")]
        lists = [list_1, list_3, list_6, list_9]

        print list_1
        print list_3
        print list_6
        print list_9

        seen = []
        repeated = []
        repeated_1_3 = []
        repeated_1_6 = []
        repeated_1_9 = []
        repeated_3_6 = []
        repeated_3_9 = []
        repeated_6_9 = []
        for lindex, l in enumerate(lists, start = 0):
            for i in l:
                if i in seen:
                    repeated.append(i)
                    if i in list_1 and lindex == 1:
                        repeated_1_3.append(i)
                    elif i in list_1 and lindex == 2:
                        repeated_1_6.append(i)
                    elif i in list_1 and lindex == 3:
                        repeated_1_9.append(i)
                    elif i in list_3 and lindex == 2:
                        repeated_3_6.append(i)
                    elif i in list_3 and lindex == 3:
                        repeated_3_9.append(i)
                    elif i in list_6 and lindex == 3:
                        repeated_6_9.append(i)
                else:
                    seen.append(i)
        print repeated
        print len(repeated)
        print repeated_1_3 # 4 streets: ['Hooiweg.gml', 'Kastertstraat.gml', 'Lousbeekstraat.gml', 'Maastrichterweg.gml', 'Swinnenwijerweg.gml']
        print len(repeated_1_3)
        print repeated_1_6
        print len(repeated_1_6) # 1 street: ['Bloemenstraat.gml']
        print repeated_1_9
        print len(repeated_1_9) # 0 streets
        print repeated_3_6
        print len(repeated_3_6) # 3 streets: ['Europalaan.gml', 'Peerdsdiefweier.gml', 'Slagmolenweg.gml']
        print repeated_3_9
        print len(repeated_3_9) # 5 streets: ['Europalaan.gml', 'Neerzijstraat.gml', 'Richter.gml', 'Wiemesmeerstraat.gml', 'Winterslagstraat.gml']
        print repeated_6_9
        print len(repeated_6_9) # 10 streets: ['Driehoevenstraat.gml', 'EvenceCoppeelaan.gml', 'Gieterijstraat.gml', 'Hoefstadstraat.gml', 'Korenbloemstraat.gml', 'Kuilenstraat.gml', 'Nieuwe Kuilenweg.gml', 'Paresbemdstraat.gml', 'Peperhofstraat.gml', 'Streepkenstraat.gml']

        for streetname in repeated_1_3:
            for variant in variants:
                filepath1 = path+gml_1+variant+"/"+streetname
                filepath2 = path+gml_3+variant+"/"+streetname
                file1 = open(filepath1,'r')
                lines1 = file1.readlines()
                file1.close()
                file2 = open(filepath2,'r')
                lines2 = file2.readlines()
                file2.close()

                os.remove(filepath1)
                os.remove(filepath2)

                file3 = open(filepath1, 'w')
                file3.writelines([line for line in lines1[:-1]])
                file3.writelines([line for line in lines2[2:]])
                file3.close()
        for streetname in repeated_1_6:
            for variant in variants:
                filepath1 = path+gml_1+variant+"/"+streetname
                filepath2 = path+gml_6+variant+"/"+streetname
                file1 = open(filepath1,'r')
                lines1 = file1.readlines()
                file1.close()
                file2 = open(filepath2,'r')
                lines2 = file2.readlines()
                file2.close()

                os.remove(filepath1)
                os.remove(filepath2)

                file3 = open(filepath1, 'w')
                file3.writelines([line for line in lines1[:-1]])
                file3.writelines([line for line in lines2[2:]])
                file3.close()
        for streetname in repeated_1_9:
            for variant in variants:
                filepath1 = path+gml_1+variant+"/"+streetname
                filepath2 = path+gml_9+variant+"/"+streetname
                file1 = open(filepath1,'r')
                lines1 = file1.readlines()
                file1.close()
                file2 = open(filepath2,'r')
                lines2 = file2.readlines()
                file2.close()

                os.remove(filepath1)
                os.remove(filepath2)

                file3 = open(filepath1, 'w')
                file3.writelines([line for line in lines1[:-1]])
                file3.writelines([line for line in lines2[2:]])
                file3.close()
        for streetname in repeated_3_6:
            for variant in variants:
                filepath1 = path+gml_3+variant+"/"+streetname
                filepath2 = path+gml_6+variant+"/"+streetname
                file1 = open(filepath1,'r')
                lines1 = file1.readlines()
                file1.close()
                file2 = open(filepath2,'r')
                lines2 = file2.readlines()
                file2.close()

                os.remove(filepath1)
                os.remove(filepath2)

                file3 = open(filepath1, 'w')
                file3.writelines([line for line in lines1[:-1]])
                file3.writelines([line for line in lines2[2:]])
                file3.close()
        for streetname in repeated_3_9:
            for variant in variants:
                filepath1 = path+gml_3+variant+"/"+streetname
                filepath2 = path+gml_9+variant+"/"+streetname
                file1 = open(filepath1,'r')
                lines1 = file1.readlines()
                file1.close()
                file2 = open(filepath2,'r')
                lines2 = file2.readlines()
                file2.close()

                os.remove(filepath1)
                os.remove(filepath2)

                file3 = open(filepath1, 'w')
                file3.writelines([line for line in lines1[:-1]])
                file3.writelines([line for line in lines2[2:]])
                file3.close()
        for streetname in repeated_6_9:
            for variant in variants:
                filepath1 = path+gml_6+variant+"/"+streetname
                filepath2 = path+gml_9+variant+"/"+streetname
                file1 = open(filepath1,'r')
                lines1 = file1.readlines()
                file1.close()
                file2 = open(filepath2,'r')
                lines2 = file2.readlines()
                file2.close()

                os.remove(filepath1)
                os.remove(filepath2)

                file3 = open(filepath1, 'w')
                file3.writelines([line for line in lines1[:-1]])
                file3.writelines([line for line in lines2[2:]])
                file3.close()

    if merge_specified_files: #merges the specified gml's into 1 gml, CAUTION: does not change names within file
        current_area = gml_9
        current_folder = path + current_area

        current_names = ["Bethaniastraat.gml", "Bethanidstraat.gml", "Bethaninstraat.gml", "Bethaniostraat.gml", "Bethanirstraat.gml", "Bethanitstraat.gml"]
        correct_name = 'Bethaniestraat.gml'
        current_names = ['EvenceCoppaeplaats.gml', 'EvenceCoppteplaats.gml']
        correct_name = 'EvenceCoppeeplaats.gml'
        current_names = ['EvenceCoppeelaan.gml', 'EvenceCopprelaan.gml', 'EvenceCoppselaan.gml']
        correct_name = 'EvenceCoppeelaan.gml'
        current_names = ['AndreDumontlaan.gml', 'Andr1Dumontlaan.gml', 'Andr2Dumontlaan.gml', 'Andr3Dumontlaan.gml', 'Andr4Dumontlaan.gml', 'Andr5Dumontlaan.gml', 'Andr6Dumontlaan.gml', 'Andr8Dumontlaan.gml', 'AndrdDumontlaan.gml']
        correct_name = 'AndreDumontlaan.gml'
        current_names = ['EvenceCoppeelaan.gml', 'EvenceCopp.gml', 'EvenceCoppaelaan.gml', 'EvenceCopprelaan.gml', 'EvenceCoppselaan.gml', 'EvenceCopptelaan.gml']
        correct_name = 'EvenceCoppeelaan.gml'

        for streetindex, streetname in enumerate(current_names, start=0):
            if streetindex==0:
                for variant in variants:
                    filepath1 = path + current_area + variant + "/" + correct_name
                    filepath2 = path + current_area + variant + "/" + streetname

                    file2 = open(filepath2, 'r')
                    lines2 = file2.readlines()
                    file2.close()

                    os.remove(filepath2)

                    file3 = open(filepath1, 'w')
                    file3.writelines([line for line in lines2])
                    file3.close()
            else:
                for variant in variants:
                    filepath1 = path+current_area+variant+"/"+correct_name
                    filepath2 = path+current_area+variant+"/"+streetname
                    file1 = open(filepath1,'r')
                    lines1 = file1.readlines()
                    file1.close()
                    file2 = open(filepath2,'r')
                    lines2 = file2.readlines()
                    file2.close()

                    os.remove(filepath1)
                    os.remove(filepath2)

                    file3 = open(filepath1, 'w')
                    file3.writelines([line for line in lines1[:-1]])
                    file3.writelines([line for line in lines2[2:]])
                    file3.close()

    if rename_files: # replaces within 1 file all old filenames by their new names
        current_area = gml_9
        file_needs_to_renamed = False

        current_names = ["Bethaniastraat.gml", "Bethanidstraat.gml", "Bethaninstraat.gml", "Bethaniostraat.gml", "Bethanirstraat.gml", "Bethanitstraat.gml"]
        correct_name = 'Bethaniestraat.gml'
        current_names = ['EvenceCopp.gml', 'EvenceCoppaelaan.gml', 'EvenceCoppkelaan.gml', 'EvenceCopptelaan.gml', 'EvenceCoppwelaan.gml']
        correct_name = 'EvenceCoppeelaan.gml'
        current_names = ['EvenceCoppaeplaats.gml', 'EvenceCoppteplaats.gml']
        correct_name = 'EvenceCoppeeplaats.gml'
        current_names = ['AndreDumontlaan.gml', 'Andr1Dumontlaan.gml', 'Andr2Dumontlaan.gml', 'Andr3Dumontlaan.gml', 'Andr4Dumontlaan.gml', 'Andr5Dumontlaan.gml', 'Andr6Dumontlaan.gml', 'Andr8Dumontlaan.gml', 'AndrdDumontlaan.gml']
        correct_name = 'AndreDumontlaan.gml'
        current_names = ['EvenceCoppeelaan.gml', 'EvenceCopp.gml', 'EvenceCoppaelaan.gml', 'EvenceCopprelaan.gml', 'EvenceCoppselaan.gml', 'EvenceCopptelaan.gml']
        correct_name = 'EvenceCoppeelaan.gml'

        for old_name in current_names:
            for variant in variants:
                variant_path = path + current_area + variant + "/"
                if file_needs_to_renamed:
                    os.rename(variant_path+old_name, variant_path+correct_name)
                # replace all occurances in gml file
                with open(variant_path+correct_name, 'r') as file:
                    filedata = file.read()
                filedata = filedata.replace(old_name[:-4], correct_name[:-4]) # delete the .gml at the end
                with open(variant_path+correct_name, 'w') as file:
                    file.write(filedata)
                print (old_name + " has been changed to " + correct_name)
                # code for erasing spaces in filenames
                #for filename in os.listdir(variant_path):
                    #if (" " in filename) == True:
                        # rename file
                        #old_filename = filename
                        #new_filename = filename.replace(" ", "")
                        #os.rename(variant_path+old_filename, variant_path+new_filename)
                        # replace all occurances in gml file
                        #with open(variant_path+new_filename, 'r') as file:
                            #filedata = file.read()
                        #filedata = filedata.replace(old_filename[:-4], new_filename[:-4]) # delete the .gml at the end
                        #with open(variant_path+new_filename, 'w') as file:
                            #file.write(filedata)
                        #print (old_filename + " has been changed to " + new_filename)

if __name__ == '__main__':
    check_files_in_folder()
    print("That's it! :)")
