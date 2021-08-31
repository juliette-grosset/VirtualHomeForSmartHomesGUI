import sys
sys.path.append("../../virtualhome/demo")
from utils_demo import*

import os


class TableActivities():
	table = {}

	def __init__(self, data, parent = None):
		TableActivities.table = data

	def getActivities(self):
		activities = []
		for activity in TableActivities.table["activities"] :
			activities.append(activity)
		return activities

	def getDurations(self):
		durations = []
		for activity in TableActivities.table["activities"] :
			for duration in TableActivities.table["activities"][activity] :
				durations.append(TableActivities.table["activities"][activity][duration])
		return durations

	def getTableActivitiesDurations(self):
		return TableActivities.table["activities"]
	
	def getConfigDate(self):
		timeDate = TableActivities.table["config"]["date"]
		timeDate += "-" + TableActivities.table["config"]["startTime"] + ":00"
		return timeDate
	
	def getConfigAcceleration(self):
		accelerationTime = TableActivities.table["config"]["accelerationTime"]
		return int(accelerationTime)

	def getInitRoom(self):
		initRoom = TableActivities.table["config"]["initRoom"]
		return initRoom

	def generateScriptActivity(self, tableActivitiesDurations, id_avatar, graph):
		script = []

		path = os.getcwd() + "/input/scripts"
		for activity in tableActivitiesDurations :
			if "Enter home" in activity :
				script_activity = path + "/EnterHome/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.readlines()
					script.append(lines)
			elif "Sleep in bed" in activity :
				script_activity = path + "/SleepInBed/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.readlines()
					script.append(lines)
			elif "Sleep" in activity :
				script_activity = path + "/Sleep/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.readlines()
					script.append(lines)
			elif "Bathe" in activity :
				script_activity = path + "/Bathe/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.readlines()
					script.append(lines)
			elif "Wash dishes" in activity :
				script_activity = path + "/WashDishes/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.readlines()
					script.append(lines)
			elif  "Cook breakfast" in activity:
				script_activity = path + "/CookBreakfast/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.read().splitlines()
					script.append(lines)
			elif "Eat breakfast" in activity :
				script_activity = path + "/EatBreakfast/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.read().splitlines()
					script.append(lines)
			elif "Cook lunch" in activity :
				script_activity = path + "/CookLunch/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.read().splitlines()
					script.append(lines)
			elif  "Eat lunch" in activity :
				script_activity = path + "/EatLunch/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.read().splitlines()
					script.append(lines)
			elif "Cook dinner" in activity :
				script_activity = path + "/CookDinner/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.read().splitlines()
					script.append(lines)
			elif  "Eat dinner" in activity :
				script_activity = path + "/EatDinner/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.read().splitlines()
					script.append(lines)
			elif "Go to toilet" in activity :
				script_activity = path + "/GoToilet/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.read().splitlines()
					script.append(lines)
			elif "Watch TV" in activity :
				script_activity = path + "/WatchTv/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.read().splitlines()
					script.append(lines)
			elif "Dress" in activity : 
				script_activity = path + "/Dress/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.read().splitlines()
					script.append(lines)
			elif "Leave home" in activity : 
				script_activity = path + "/LeaveHome/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.read().splitlines()
					script.append(lines)
			elif "Read" in activity :
				script_activity = path + "/Read/" + tableActivitiesDurations[activity]['script'] + ".txt"
				with open(script_activity) as f:
					lines = f.readlines()
					script.append(lines)
			else :
				print("Activity : " + activity + " is not unknown")
		return script