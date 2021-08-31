import os
import json
import sys,getopt
import pandas as pd
from itertools import chain
import ast
import time
import string

# Virtual Home modules
sys.path.append('../../virtualhome/simulation')
sys.path.append('../../virtualhome/dataset_utils')
import add_preconds
from unity_simulator.comm_unity import UnityCommunication
sys.path.append("../../virtualhome/demo")
from utils_demo import*

# my modules
import labelData
import activities


class Link():   
	def __init__(self, sensorsFile, activitiesFile, outputFolder, parent = None):
		"""
		Class that allows the link between the configuration files and the launch of the simulation. 
		Calling the writeJSonFile function to create the end of experiment file for the simulation.
		"""

		print("Communication")
		fileSensor = open(sensorsFile)
		dataFileSensor = json.load(fileSensor)
		dataSensor = dataFileSensor["sensors"]
		indexAppartment = dataFileSensor["indexAppartment"]

		#s = sensors.Sensors(dataSensor)
		fileSensor.close()

		fileActivities = open(activitiesFile)
		dictActivities = json.load(fileActivities)
		a = activities.TableActivities(dictActivities)
		fileActivities.close()

		Launch(dataSensor, a, indexAppartment, outputFolder)
		writing = WriteData()
		writing.writeJsonFile(dataFileSensor, dictActivities, outputFolder)


class Launch():
	def __init__(self, dataSensor, tableActivitiesClass, indexAppartment, outputFolder, parent = None):
		"""
		Launch the simulation with the different parameters : 
		- indexAppartment
		- accelerationTime
		Recovery the output of states update of the different sensors. 
		"""


		comm = UnityCommunication()
		# Reset scene with the id scene 0 (appartment 1)
		comm.reset(indexAppartment)

		success, graph_input = comm.environment_graph()

		listActivities = tableActivitiesClass.getActivities()
		dateTime = tableActivitiesClass.getConfigDate()
		initRoom = tableActivitiesClass.getInitRoom()

		tableActivitiesDurations = tableActivitiesClass.getTableActivitiesDurations()
		print(tableActivitiesDurations)

		accelerationTime = tableActivitiesClass.getConfigAcceleration()
		print("\nList activities : ", listActivities)
		print("Date time : ", dateTime)
		id_avatar = 0

		try :
			mainDoor = find_nodes(graph_input, custom_name='door')[-1]
			mainDoor['states'] = ['CLOSED']
		except IndexError :
			pass


		script = tableActivitiesClass.generateScriptActivity(tableActivitiesDurations, id_avatar, graph_input)

		print('\nExecution script :\n', script)

		success, message = comm.expand_scene(graph_input)
		if success == False : 
			print(message)

	
		comm.add_character(initial_room = initRoom)
		start_time = time.time()
		comm.set_timeScale(coefficient = accelerationTime)
		print("Acceleration Time : ", accelerationTime)


		success, time_init = comm.time_init()
		print("\nTime init : " + str(time_init))

		timeAction = {}
		times = []
		timeBefore = 0

		for index, activity in enumerate(script) :
			for script_item in activity:
				print(script_item)
				success, message = comm.render_script(script=[script_item],
				processing_time_limit=100,
				find_solution=False,
				frame_rate=30,
				image_width=512, image_height=320,
				skip_animation=False,
				recording = True,
				image_synthesis=[],
				camera_mode=['PERSON_TOP'])

				success, time_simu = comm.time_simulation()
				#print("timeBefore : ", timeBefore)
				newTime = round(time_simu-timeBefore, 2)
				print(newTime)
				timeBefore = time_simu
				times.append(newTime)

			#print("Activity : ", activity)
			success, simulation_time = comm.time_simulation()
			timeAction[simulation_time] =listActivities[index]
			#print("TimeAction : ", timeAction)
			
		#print(timeAction)
		#print(times)

		# after execution of the script
		success, outputData = comm.timestamp_sensors()
		print("--- %s seconds ---" % (time.time() - start_time))

		if outputData :

			finalData = labelData.postProcessPresenceSensor(outputData)
			#print(finalData)
			finalData = labelData.addActivityLabel(timeAction, finalData)
			#print()
			#print(finalData)
			finalData = labelData.labelTime(dateTime, finalData, tableActivitiesDurations)

			finalData = labelData.addLabelSensor(indexAppartment, finalData)
			#print()
			#print(finalData)
			finalData = labelData.compareObjSensor(dataSensor, finalData)
			print()
			print(finalData)

			#dataWithDurations = labelData.addDurationTime(durations, finalData)

			writing = WriteData()
			writing.writeCsvFile(finalData, outputFolder)


class WriteData():
	def __init__(self, parent = None):
		pass

	def createDictCsv(self, data):
		"""
		Create the dictionnary for the output csv file.
		dateTime | object | sensor_type | state | room | activity
		"""
		dictCSV = {}
		#dictCSV["id"] = []
		dictCSV["dateTime"] = []
		dictCSV["object"] = []
		dictCSV["sensor_type"] = []
		dictCSV["state"] = []
		dictCSV["room"] = []
		dictCSV["activity"] =[]

		for index in data :
			#dictCSV["id"].append(data[time]["id"])
			dictCSV["dateTime"].append(data[index]["dateTime"])
			dictCSV["object"].append(data[index]["obj"])
			try : 
				dictCSV["sensor_type"].append(data[index]["sensor"])
			except KeyError: 
				print("Problem : ", data[index])
				dictCSV["sensor_type"].append("")
			dictCSV["state"].append(data[index]["state"])
			dictCSV["room"].append(data[index]["room"])
			table = str.maketrans('', '', string.digits)
			data[index]["activity"] = data[index]["activity"].translate(table) # to remove numbers from string : example - Cook lunch 1 -> Cook lunch
			dictCSV["activity"].append(data[index]["activity"])

		return dictCSV

	def writeJsonFile(self, fileSensors, fileActivities, outputFolder):
		"""
		Create the output json file : concatenation of the 2 inputs file.
		Concatenation of the 2 inputs file
		"""
		outputFile = "log_" + outputFolder + ".json"
		with open("output/" + outputFolder + "/" + outputFile, 'w+') as f :
			json.dump(fileSensors, f, indent=4, ensure_ascii = False, sort_keys = False)
			json.dump(fileActivities, f, indent=4, ensure_ascii = False, sort_keys = False)
		print("\nFile " + outputFile + " created in /output/" + outputFolder)



	def writeCsvFile(self, finalData, outputFolder):
		"""
		Create the output csv file. 
		The different states of updates of sensors placed in the appartment scene.
		"""
		dictCSV = self.createDictCsv(finalData)

		df = pd.DataFrame.from_dict(dictCSV)

		outputFile = "log_" + outputFolder + ".csv"
		df.to_csv("output/" + outputFolder + "/" + outputFile)	
		print("\nFile " + outputFile + " created in /output/" + outputFolder)


def main(argv):
	indexAppartment = ""
	inputSensorFile = ""
	inputActivityFile = ""
	outputFolder = ""

	i = 0
	for arg in argv : 
		"""
		arguments to use to launch the simulation directly in the terminal : 
		'python simulation.py -s <inputSensorsFile> -a <inputActivitiesFile -o <outputFolder>'
		"""
		if arg == "-s" : 
			inputSensorsFile = argv[i+1]
		elif arg == "-a" :
			inputActivitiesFile = argv[i+1]
		elif arg == "-o" :
			outputFolder = argv[i+1]

			path = os.getcwd() + "/output/" + outputFolder + "/"
			if not os.path.exists(path):
				os.mkdir(os.getcwd() + "/output/" + outputFolder)

			else : # if folder exists already
				for f in os.listdir(path):
					os.remove(os.path.join(path, f))


		elif arg == "-h" :
			print('simulation.py -s <inputSensorsFile> -a <inputActivitiesFile -o <outputFolder>')
		i+=1

	print("\nInput SensorsFile is " + inputSensorsFile)
	print("Input ActivitiesFile is " + inputActivitiesFile)
	print("Output folder is " + outputFolder)

	Link(inputSensorsFile, inputActivitiesFile, outputFolder)


if __name__ == "__main__":
   main(sys.argv[1:])

