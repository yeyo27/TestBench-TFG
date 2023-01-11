#!/usr/bin/python3
from shared_resource import Shared_Resource
from tkinter import Tk
from tkinter import messagebox
from interface import test_bench_gui
from robot_controller import Robot_Controller
from server_aleman import Server_Aleman
import json
import sys
import os

#methods
def read_json(filename:str):
        js = None
        def __check_format(dic):
            error = 0
            try:
                ##Points verification##
                for x in dic["Points"]: 
                    if isinstance(dic["Points"][x],list):#For home positions (lists)
                        if len(dic["Points"][x])!= 6:
                            error = 1
                            break
                        for i in dic["Points"][x]: #Joints values
                            if not isinstance(i,(int,float)):
                                error = 1
                                break
                    else: #For stations (dictionaries)
                        for i in dic["Points"][x]: #Steps of stations
                            if len(dic["Points"][x][i])!= 6:
                                error = 1
                                break
                            for j in dic["Points"][x][i]: #Joint values of every step
                                if not isinstance(j,(int,float)):
                                    error = 1
                                    break
                            
                ##For robot controller variables##
                for x in dic["Robot_controller"]: 
                    if not isinstance(dic["Robot_controller"][x],(int,float)):
                        error = 1
                        break
                if not isinstance(dic["Robot_arm"]["Robot_ip"],str):
                    error = 1
                if not isinstance(dic["Robot_arm"]["Angle_speed"],(int,float)):
                    error = 1
                
                if len(dic["Robot_arm"]["Empty_payload"]) != 4:
                    error = 1
                else:
                    for x in dic["Robot_arm"]["Empty_payload"]:
                        if not isinstance(x,(int,float)):
                            error = 1
                            break
                
                if len(dic["Robot_arm"]["Full_payload"]) != 4:
                    error = 1
                else:
                    for x in dic["Robot_arm"]["Full_payload"]:
                        if not isinstance(x,(int,float)):
                            error = 1
                            break
                
                if not isinstance(dic["Robot_arm"]["Gripper_timeout"],(int,float)):
                    error = 1
                ##For raspberry variables##
                if not isinstance(dic["Raspberry"]["HOST"],str):
                    error = 1
                if not isinstance(dic["Raspberry"]["MSPM PORT"],int):
                    error = 1
                if not isinstance(dic["Raspberry"]["Laser PORT"],int):
                    error = 1
                
            except:
                messagebox.showerror("Fatal Error","There are fields missing!")
                error = 1
            return error
        if os.path.exists(filename):
            # reading the data from the file
            with open(filename) as f:
                    data = f.read()
            
            # reconstructing the data as a dictionary
            try:
                js = json.loads(data)
                error = __check_format(js)
                print(error)
                if error:
                    raise Exception("Wrong format or values in config file")
            except:
                messagebox.showerror("Fatal Error","Config file has incorrect values!")

        else:
            messagebox.showerror("Fatal Error","Config file is missing!")

        return js

#Config File reading
config = read_json("sc/conf/last_config.txt")

SIMULATION = False #Simulation is set to false

HOST = config["Raspberry"]["HOST"]      #Raspberry IPv4 in system local network 
PORT = config["Raspberry"]["MSPM PORT"] #Port to connect Raspberry and MSPM machine

# Test connection with MSPM tower:
# CMD: ping 192.168.100.25

#Share resource initialize
shared_resource = Shared_Resource(config)

#Status register initialization
for i in range(16):
    shared_resource.get_SR().change_bit_from_int(i, 0)

#Root definition
root=Tk()
#Root configuration
root.title("Test Bench GUI") #Set window title
root.resizable(True,True) #Make the window resizable (width, heigth)
root.config(bg="light gray")

#Creation of robot controller and server_aleman instances
robot_controller = Robot_Controller(config, shared_resource, simulation=SIMULATION)
server_aleman = Server_Aleman(shared_resource, (HOST, PORT))

interface = test_bench_gui(shared_resource,root) #Interface initialization
interface.params_upd()


#Threads run with start method
robot_controller.start()
server_aleman.start()


root.mainloop() #Interface thread starts using mainloop method
shared_resource.Quit = True #Once interface is closed, global Quit is set to True

#Wait for the threads to stop
robot_controller.join()
server_aleman.end_connection()
server_aleman.join()
server_aleman.end_connection()

sys.exit(0)



