import sys
sys.path.append("../../virtualhome/demo")
from utils_demo import*

import datetime
import json

def compareObjSensor(dataSensor, finalData):
	"""
	Compare the output dictionnary of the file, and the dataSensor dictionnary.
	Remove the lines corresponding to the different sensors not present in the appartment
	according to the user (configuration file)
	"""
	obj_track = []
	for room in dataSensor : 
		for obj in dataSensor[room]:
			if dataSensor[room][obj] == "yes":
				obj_track.append(obj)

	log = {}
	for line in finalData :
		track = False
		for obj in obj_track :
			if finalData[line]["obj"] == obj or finalData[line]["obj"] == "character" :
				track = True
				log[line] = {}
				log[line] = finalData[line]

		if not track : 
			#print("line deleted -> obj not track")
			pass
			
	return log


def addLabelSensor(indexAppartment, dataLabelTime):
	"""
	Add an entry sensor to the dictionnary. 
	- power sensor: ON/OFF
	- door sensor (opening/closing) : OPEN/CLOSED
	- pressure sensor : LIYING/SITTING
	- touch sensor : TOUCH/NOT TOUCH
	- presence sensor : ON/OFF - its type of sensor doesn't have id (not in the environment graph of virtualHome) 
	"""
	listIdObj = getListIdObj(indexAppartment, dataLabelTime) # recover mapping id : custom_name

	for time in dataLabelTime :
		idObj = dataLabelTime[time]["id"]

		if idObj != "" : # because if it is a presence_sensor they don't have an id
			if idObj in listIdObj : # if idObj exists in the list of config sensors oh the experience
				dataLabelTime[time]["obj"] = listIdObj[idObj] # object = custom_name 
			else : # object is not track
				print("\nobject " + dataLabelTime[time]["obj"] + " with id " + idObj + " is not track")
				

		state = dataLabelTime[time]["state"]
		if (state == "ON" or state == "OFF") and idObj != "" :
			dataLabelTime[time]["sensor"] = "power"
		elif state == "OPEN" or state == "CLOSED" :
			dataLabelTime[time]["sensor"] = "door"
		elif state == "SITTING" or state == "LYING" :
			dataLabelTime[time]["sensor"] = "pressure"
			"""
			if state == "SITTING" :
				dataLabelTime[time]["state"] = "ON : SITTING"
			else : 
				dataLabelTime[time]["state"] = "ON : LYING"
			"""
			dataLabelTime[time]["state"] = "ON"
			
		elif state == "STAND UP" :
			dataLabelTime[time]["sensor"] = "pressure"
			dataLabelTime[time]["state"] = "OFF"

		elif state == "TOUCH" or state == "NOT TOUCH" :
			dataLabelTime[time]["sensor"] = "touch"

		elif (state == "ON" or state == "OFF") and idObj == "" :
			dataLabelTime[time]["sensor"] = "presence"
		else : # presence sensor : state = ON or OFF but no id
			pass
	return dataLabelTime


def getListIdObj(indexAppartment, dataLabelTime):
	"""
	Read the configuration file of the appartment.
	This files contains the mapping : id / different custom_name.
	"""

	fileConfig=open('config/configAppartment' + str(indexAppartment) + '.json', 'r')
	dataFileConfig = json.load(fileConfig)
	
	listIdObj = {}
	for obj in dataFileConfig['objects'] :
		id_obj = dataFileConfig['objects'][obj]['id']
		sensor_equiped = dataFileConfig['objects'][obj]['sensorEquiped']
		if id_obj != "" and sensor_equiped != []:
			listIdObj[id_obj] = obj

	#print(listIdObj)
	
	return listIdObj


def addActivityLabel(timeAction, finalData):
	"""
	Add an entry activity in the dictionary to all the updates of sensors.
	Compare the time of the end of the different actions with the timestamp linked to the update of the sensor.
	If the update is lower, it means that it took place during the action's activity. 
	"""
	print("TimeAction : ", timeAction)
	for index in finalData :
		time_simulation = finalData[index]["timestamp"]
		for time in timeAction :
			if float(time_simulation) <= time :
				activity = timeAction[time]
				finalData[index]["activity"] = activity
				break
	return finalData	


def labelTime(dateTime, finalData, tableActivitiesDurations):
	"""
	Modify the different timestamp to add the date and the startTime of the simulation.
	Modify the different timestamp in function of the duration of activities.
	"""

	lastActivity = finalData['1']['activity']
	currentActivity = ""
	lastTimestamp = 0


	lastDateTime = datetime.datetime.strptime("{}".format(dateTime), "%d-%m-%Y-%H:%M:%S")

	for index in finalData :
		currentActivity = finalData[index]['activity']
		print('activity : ' + finalData[index]['activity'])

		currentTimestamp = finalData[index]['timestamp']
		print('currentTimestamp : ' + currentTimestamp)

		if currentActivity == lastActivity :

			timestamp = finalData[index]["timestamp"]
			newTime = datetime.timedelta(seconds = float(timestamp)-float(lastTimestamp))
			newDateTime = lastDateTime + newTime
			
			#print("newTime : " + str(newTime))
			lastTime = str(newTime)
			finalData[index]['dateTime'] = str(newDateTime)
			lastDateTime = newDateTime
			print(newDateTime)


		else : 
			durationLastActivity = tableActivitiesDurations[lastActivity]["duration"]
			print("durationLastActivity : ", durationLastActivity)
			nbHoursLastActivity = durationLastActivity.split(":")[0]
			nbMinutesLastActivity = durationLastActivity.split(":")[1]

			timestamp = finalData[index]["timestamp"]
			newTime = datetime.timedelta(hours = int(nbHoursLastActivity), minutes = int(nbMinutesLastActivity), seconds = float(timestamp) - float(lastTimestamp))
			newDateTime = lastDateTime + newTime
			
			#print("newTime : " + str(newTime))
			lastTime = str(newTime)
			finalData[index]['dateTime'] = str(newDateTime)
			lastDateTime = newDateTime
			print(newDateTime)


		lastActivity = currentActivity
		lastTimestamp = float(currentTimestamp)

	return finalData


def addDurationTime(durations, finalData):
	"""
	Add the duration of the last activity to the time of the new activity 
	"""
	activity = ""
	indexActivity = -1
	for line in finalData :
		new_activity = finalData[line]["activity"]
		if activity != new_activity : 
			indexActivity += 1
			timeActivity = durations[indexActivity]
			print(timeActivity)

			print(line)
	return finalData


def postProcessPresenceSensor(outputData):
	"""
	Add a line of update if the avatar is in an area of presenceSensor at the beginnning of the simulation
	"""
	finalData = {}
	for index in outputData : 
		if "presence"  in outputData[index]["obj"] and outputData[index]["state"] == "OFF":
			finalData["0"] = {}
			finalData["0"]["timestamp"] = "0.0"
			finalData["0"]["id"] =outputData[index]["id"]
			finalData["0"]["obj"] = outputData[index]["obj"]
			finalData["0"]["state"] = "ON"
			finalData["0"]["room"] = outputData[index]["room"]
			break
	for index in outputData : 
		finalData[index] = {}
		finalData[index] = outputData[index]

	#print(finalData)
	return finalData
