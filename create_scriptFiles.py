import os
import sys

import json

def main(argv) :
    with open(argv[0], newline='') as jsonFile:
        data = json.load(jsonFile)
        for activity in data['activities'] :
            path = os.getcwd() + "/input/scripts"
            nameFile = data['activities'][activity]['script'] + '.txt'
            path_activity = ""
            if "Enter home" in activity :
                path_activity = path + "/EnterHome/" + nameFile   
            elif "Sleep in bed" in activity :
                path_activity = path + "/SleepInBed/" + nameFile
            elif "Sleep" in activity :
                path_activity = path + "/Sleep/" + nameFile
            elif "Bathe" in activity :
                path_activity = path + "/Bathe/" + nameFile
            elif "Wash dishes" in activity :
                path_activity = path + "/WashDishes/" + nameFile
            elif  "Cook breakfast" in activity :
                path_activity = path + "/CookBreakfast/" + nameFile
            elif "Eat breakfast" in activity :
                path_activity = path + "/EatBreakfast/" + nameFile
            elif "Cook lunch" in activity :
                path_activity = path + "/CookLunch/" + nameFile
            elif  "Eat lunch" in activity :
                path_activity = path + "/EatLunch/" + nameFile
            elif "Cook dinner" in activity :
                path_activity = path + "/CookDinner/" + nameFile
            elif  "Eat dinner" in activity :
                path_activity = path + "/EatDinner/" + nameFile
            elif "Go to toilet" in activity :
                path_activity = path + "/GoToilet/" + nameFile
            elif "Watch TV" in activity :
                path_activity = path + "/WatchTv/" + nameFile
            elif "Dress" in activity : 
                path_activity = path + "/Dress/" + nameFile
            elif "Leave home" in activity : 
                path_activity = path + "/LeaveHome/" + nameFile
            elif "Read" in activity : 
                path_activity = path + "/Read/" + nameFile
            else : 
                print("Activity" + activity + " not unknown.")
            
            with open(path_activity, "w") as file:
                file.write("")
                print("File " + path_activity + " created.")

if __name__ == "__main__":
   main(sys.argv[1:])