import json
import random
import sys
import os
from typing_extensions import final
import cv2
import numpy as np
import matplotlib.pyplot as plt

sys.path.append('../../virtualhome/simulation')
sys.path.append('../../virtualhome/dataset_utils')

import add_preconds
import augmentation_utils

from tqdm import tqdm
from unity_simulator.comm_unity import UnityCommunication
from unity_simulator import utils_viz

sys.path.append("../../virtualhome/demo")
from utils_demo import*


class CreateFileConfiguration():
    def __init__(self, indexAppartment, outputFile, parent = None):
        comm = UnityCommunication()

        # Reset scene with the id scene 0 (appartment 1)
        comm.reset(indexAppartment)

        # Returns environment graph
        s, graph_input = comm.environment_graph()

        success, presenceSensors = comm.get_presence_sensors()

        success, faucetSensors = comm.get_faucet_sensors() 

        rooms = self.idRoom(graph_input)

        dictConfig = {}
        dictConfig['objects'] = {}
        dictConfig['presenceSensors'] = {}
        for node in graph_input['nodes'] : 
            if node["custom_name"] != '' and node["custom_name"] != None :
                for edge in graph_input['edges'] :
                    if edge['from_id'] == node['id'] :
                        for room in rooms :
                            if rooms[room] == edge['to_id'] :
                                dictConfig['objects'][node['custom_name']] = {}
                                dictConfig['objects'][node['custom_name']]['id'] = str(node['id'])
                                dictConfig['objects'][node['custom_name']]['room'] = room
                                dictConfig['objects'][node['custom_name']]['sensorEquiped'] = []
                                dictConfig['objects'][node['custom_name']]['sensorEquiped'] = node['sensor_equiped']

        
        for sensor in presenceSensors :
            dictConfig['presenceSensors'][sensor] = {}
            dictConfig['presenceSensors'][sensor]['room'] = presenceSensors[sensor]['room']
            dictConfig['presenceSensors'][sensor]['floor'] = presenceSensors[sensor]['floor']
            dictConfig['presenceSensors'][sensor]['sensorEquiped'] = presenceSensors[sensor]['sensorEquiped'] 
        

        for sensor in faucetSensors : # binary sensors (ON/OFF : water stream)
            dictConfig['objects'][sensor] = {}
            dictConfig['objects'][sensor]['id'] = faucetSensors[sensor]['id']
            dictConfig['objects'][sensor]['room'] = faucetSensors[sensor]['room']
            dictConfig['objects'][sensor]['sensorEquiped'] = faucetSensors[sensor]['sensorEquiped']


        #print(dictConfig)
        final_path = "config/" + outputFile +".json"
        if 	os.path.exists(final_path):
            mapId = self.getMapId(dictConfig, final_path)
            #print(mapId)
            self.updateScriptsData(mapId)

        self.writeData(dictConfig, final_path)

    def getMapId(self, dictConfig, final_path):
        olderFileConfig = open(final_path)
        previousData = json.load(olderFileConfig)
        mapId = {}
        for obj in previousData['objects'] :
            if "id" in previousData['objects'][obj] :
                mapId[obj] = {}
                mapId[obj]['previous'] = previousData['objects'][obj]['id']
            
            try : 
                mapId[obj]['actual'] = dictConfig['objects'][obj]['id']
            except KeyError : 
                print("The object " + obj + " is not track anymore, all script line in scripts with this object will not be updated.")
        print("mapId :", mapId)
        return mapId

    def updateScriptsData(self, mapId):
        """
        Enable to update scripts files with the good id of objets corresponding to the new configuration of the appartment scene.
        If an object is not in the previousConfig -> its id will not be updated 
        If an object is not in the actualConfig -> print a message
        """

        path_dir = os.getcwd() + "/input/scripts/"
        #os.chdir(path_dir)
        folders = os.listdir(path_dir)
        if ".DS_Store" in folders : # MacOs users
            folders.remove(".DS_Store")

        for scripts_folder in folders :
            path_folder_script = path_dir + "/" + scripts_folder
            files = os.listdir(path_folder_script)
            if ".DS_Store" in files : # MacOs users
                files.remove(".DS_Store")
            for file in files : 
                path_file = path_dir + "/" + scripts_folder + "/" + file
                with open(path_file) as f:
                    lines = f.readlines()
                    for i, line in enumerate(lines) : 
                        #print(line)

                        for obj in mapId :
                            previousId = mapId[obj]['previous']
                            actualId = mapId[obj]['actual']
                            if previousId in line : 
                                
                                newLine = line.replace(previousId, actualId)
                                lines[i] = newLine
                                #print(line)
                                print(line  + "  --> previous Id : " + previousId + " and actual Id : " + actualId)
                                print(obj)
                                print(newLine)
                                print("\n\n\n")
                with open(path_file, 'w') as file:
                    file.writelines(lines)


    def writeData(self, dictConfig, final_path):
        with open(final_path, 'w+') as f :
            json.dump(dictConfig, f, indent=4, ensure_ascii = False, sort_keys = False)
        print("\nFile " + final_path + ".json created.")

    def idRoom(self, graph):
        idRoom = {}
        for node in graph['nodes']:
            if node['class_name'] == 'kitchen' :
                idRoom['kitchen'] = node['id']
            elif node['class_name'] == 'bathroom' :
                idRoom['bathroom'] = node['id']
            elif node['class_name'] == 'bedroom' :
                idRoom['bedroom'] = node['id']
            elif node['class_name'] == "livingroom" :
                idRoom['livingroom'] = node['id']
            elif node['class_name'] == "entrance" :
                idRoom['entrance'] = node['id']
            elif node['class_name'] == "outside" :
                idRoom['outside'] = node['id']
            else : 
                pass
        return idRoom


def main(argv):
    indexAppartment = ""

    i=0
    for arg in argv : 
        if arg == '-i' :
            indexAppartment = argv[i+1]
        elif arg == '-h' :
            print('sceneConfig.py -i <indexAppartment>')
        i+=1
    outputFile = "configAppartment" + str(indexAppartment)

    print("\nIndex appartment is " + indexAppartment)
    print("OutputFile is " + outputFile)

    CreateFileConfiguration(indexAppartment, outputFile)


if __name__ == "__main__" :
    main(sys.argv[1:])