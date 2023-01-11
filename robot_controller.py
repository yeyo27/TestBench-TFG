# Consumer
from threading import Thread
from robot import Robot
from time import sleep
from time import time
from shared_resource import Shared_Resource
from typing import Union
from datetime import datetime
from functools import partial

class Jig():
    in_port_c     : int #Centering cylinders control signal
    in_port_p     : int #Probes cylinders control signal
    out_port_ic_c : int #Blind end stroke sensor signal of centering cylinders
    out_port_ic_p : int #Blind end stroke sensor signal of probes cylinders
    out_port_fc   : int #Cylinders rod end stroke sensor
    open_value    = 0   #Depends on used logic
    close_value   = open_value
    n_closed      = 0   #--SOLENOID VALVES STATE-- If 1, normally closed. If 0, normally open
    n_open        = int(not(n_closed))

    def __init__(self,in_port_c:int, in_port_p:int, out_port_ic_c:int, out_port_ic_p:int, out_port_fc:int):
        #These in/out ports are in/out ports of the jig, not robot controller (Regarding the robot controller, they are the opposite)
        self.in_port_c     = in_port_c
        self.in_port_p     = in_port_p
        self.out_port_ic_c = out_port_ic_c
        self.out_port_ic_p = out_port_ic_p
        self.out_port_fc   = out_port_fc

class Robot_Controller(Thread):

    __robot            : Robot
    __slow_speed       : Union[int, None]
    __fast_speed       : Union[int, None]
    __shared_resource  : Shared_Resource
    __jig1             : Jig #HP station jig
    __jig2             : Jig #LCR station jig
    __jig3             : Jig #PT station jig
    __jig_in           : int #In station jig
    __jig_ng           : int #NoGood station jig
    __jig_ok           : int #OkParts station jig
    __gripper_pin      : int #Digital pin of the gripper
    __n_open_gripper   = 1
    __n_closed_gripper = not(__n_open_gripper)
    __simulation       : bool

    def __init__(self, config:dict, shared_resource: Shared_Resource, simulation: bool = True):
        
        Thread.__init__(self)
        
        self.config                = config #Loaded config file is stored

        self.__points              = config["Points"] #Points dictionary, received through config

        self.__shared_resource     = shared_resource #This is the same resource for every module

        #Robot parameters
        self.__robot               = Robot(shared_resource) #Robot arm instance
        self.__slow_speed          = config["Robot_controller"]["Slow_linear_speed"] #Speeds initialization
        self.__fast_speed          = config["Robot_controller"]["Fast_linear_speed"]
        self.__jig1                = Jig(0,1,  0,1,2) #(in_port_c, in_port_p,   out_port_ic_c,out_port_ic_p, out_port_fc)
        self.__jig2                = Jig(2,3,  3,4,5) #same config as jig1
        self.__jig3                = Jig(4,5,  6,7,8) #same config as jig1 #Port 8 is digital input 0
        self.__jig_in              = 9   #Sensor pin of the in station (robot controller DI1)
        self.__jig_ok              = 10  #Sensor pin of Okparts station (DI2)
        self.__jig_ng              = 11  #Sensor pin of NoGood statiom (DI3)
        self.__gripper_pin         = 6   #Gripper valve pin (CO6)
        self.__laser_trigger       = 7   #Laser trigger pin (CO7)
        self.__simulation          = simulation
        
        #Speed weights
        self.__pt_full = False
        self.__speed_weight_fast = {
            "Empty"  : 1.7,
            "Full"   : 0.8,
            "fast_ok": 0.6,
            "Outputs": 0.3
        }
        self.__speed_weight_slow = {
            "Empty"  : 1.7,
            "Full"   : 0.6,
            "fast_ok": 0.5,
            "Outputs": 0.32
        }

        #Interface functions
        self.__shared_resource.openlcr = partial(self.__Open_LCR_Jig)
        self.__shared_resource.closelcr = partial(self.__Close_LCR_Jig)
        self.__shared_resource.verify   = partial(self.autoverification)
        self.__shared_resource.robotini = partial(self.__robot.ini)
        
        
        self.__ordenes = {
            "MoveFromInpToHiPot\n"      : self.__Mv_In_to_HP,
            "MoveFromHiPotToLCR\n"      : self.__Mv_HP_to_LCR,
            "MoveFromHiPotToNoGood\n"   : self.__Mv_HP_to_NG,
            "MoveFromLCRToPowTow\n"     : self.__Mv_LCR_to_PT,
            "MoveFromLCRToNoGood\n"     : self.__Mv_LCR_to_NG,
            "MoveFromPowTowToOKparts\n" : self.__Mv_PT_to_OK,
            "MoveFromPowTowToNoGood\n"  : self.__Mv_PT_to_NG,
            "OpenHiPotJig\n"            : self.__Open_HiPot_Jig,
            "OpenLCRJig\n"              : self.__Open_LCR_Jig,
            "OpenPowTowJig\n"           : self.__Open_PowTow_Jig,
            "OpenAllJigs\n"             : self.__Open_All_Jigs
        }

    def run(self):
        now = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        filename = "sc/logs/error/Error_" +now +".txt"
        self.f = open(filename,"a")
        if not self.__simulation: #If this is not a simulation, initialize robot controller
            self.logprint("\nConnecting to Robot... (Make sure Controller is On)")
            time0 = time()
            while not self.__shared_resource.Quit:
                try:
                    self.initialize()
                    break
                except:
                    if (time() - time0)>=2:
                        #self.__shared_resource.Quit = True
                        #print("\nRobot controller is off. Please turn it on and restart the program")
                        self.logprint("\nRobot controller is not ready yet")
                        time0 = time()
        while not self.__shared_resource.Quit: #If interface is not closed, we run the thread
            action = self.__shared_resource.consume_order() #This is constantly trying to consume orders.
            if action != None: #Once we receive an order, we execute it
                print("SR: ", self.__shared_resource.get_SR().get_value()) #Screen printing of Status Register
                self.logprint("\nSR: "+str(self.__shared_resource.get_SR().get_value())) #Interface printing of Status  Register
                
                if action[:11] == "LaserPrint ": #
                    self.__Laser_Print(action)
                else:
                    try:
                        self.__ordenes[action]()
                    except:
                        print("ORDEN NO PROGRAMADA: " + action)
                        self.logprint("ORDER IS NOT PROGRAMMED: "+action)
                
                print("SR: ", bin(self.__shared_resource.get_SR().get_value())[2:].zfill(16))
                self.logprint("SR: "+str(bin(self.__shared_resource.get_SR().get_value())[2:].zfill(16)))
        try:
            self.release()
        except:
            pass
        self.f.close()

    def initialize(self):
        self.__points=self.__shared_resource.config["Points"]
        self.__robot.ini() #Robot initialize
        self.logprint("\nRobot Connected")
        self.__robot.change_payload("empty")
        self.thread_init() #Button pad and read in thread initialization
        self.move_home(self.__points["Home"])
        if not self.__robot.es_is_pressed: #Only verify at the beginning if emergency stop is not pressed
            self.autoverification()
        
        #Jigs initialization
        self.open_jig(self.__jig1)
        self.open_jig(self.__jig2)
        self.open_jig(self.__jig3)
           
    def release(self):
        self.read_in.join() #Waits for threads execution to end
        self.__robot.fin() #Releases robot arm

    def logprint(self,text):
        self.__shared_resource.logger.write(text) #Prints into the interface scrollbar

    def __move_steps(self, arm_status_Home:list, arm_status_Pi:dict, arm_status_PL:dict, pick:str, place:str, jig_pick:Union[Jig, int], jig_place:Union[Jig, int]):
        
        ###################Initialization###################
        error_detected=0
        error_robot = 0
        error_jig = 0
        err_reg = [0, 0,0,0, 0,0,0,0] #Error register initialize
        
        if self.__pt_full:
            speedweight = self.__speed_weight_slow #Slow speed weights, this is PowTow full
        else:
            speedweight = self.__speed_weight_fast
        
        self.__fast_speed = self.__shared_resource.config["Robot_controller"]["Fast_linear_speed"]
          
        self.__slow_speed = self.__shared_resource.config["Robot_controller"]["Slow_linear_speed"]

        self.__robot.gripper_action(self.__gripper_pin,self.__n_closed_gripper) #Open gripper every move_steps call (may arise problems)
        
        fast_speed = speedweight["Empty"]*self.__fast_speed
        
        self.__robot.speed_set(fast_speed) #Speed setting
        
        self.__robot.move_upwards()

        self.__robot.change_payload("empty") #maybe not needed because of initialize
        
        #If the stations we are working with have a jig, we open them
        if isinstance(jig_pick,Jig):
            self.open_jig(jig_pick)
        if isinstance(jig_place,Jig):
            self.open_jig(jig_place)
        ##################################################

        if ((error_detected==0)): #Check jig_pick status if necessary
            if isinstance(jig_pick,Jig):
                print("Checking if pick jig is open")
                self.logprint("\nChecking if pick jig is open")
                error_jig = self.jig_status("open",jig_pick)
            elif isinstance(jig_pick,int):
                error_jig = self.jig_status("station_occupied",jig_pick)
            if error_jig != 0: #if error, update err_reg and error_detected==1
                err_reg = [0,0,0, 0,0,0,0,1]
                error_detected=1

        if error_detected == 0: #Checks if jig from place station is open (if necessary)
            if isinstance(jig_place,Jig):
                error_jig = self.jig_status("open",jig_place)
            elif isinstance(jig_place,int):
                error_jig = self.jig_status("station_empty",jig_place)
            if error_jig != 0: #if error, update err_reg and error_detected==1
                err_reg = [0,0,0, 0,1,0,1,1]
                error_detected = 1

        if (error_detected==0): #From home to pick up
            error_robot = self.__robot.move_arms_list(arm_status_Pi["PiU"])
            if error_robot != 0: #if error, update err_reg and error_detected==1
                err_reg = [0,0,0, 0,0,0,0,0] #No need to change bits from 3 to 0 (index from 4 to 7 in the list) because they are already 0
                error_detected=1

        if error_detected == 0: #From preprepick to prepick
            error_robot = self.__robot.move_arms_list(arm_status_Pi["PrePi"])
            if error_robot != 0: #if error, update err_reg and error_detected==1
                err_reg = [0,0,0, 0,0,0,1,1]
                error_detected = 1

        if error_detected == 0: #From prepick to pick
            self.__robot.speed_set(self.__slow_speed)
            error_robot = self.__robot.move_arms_list(arm_status_Pi["Pi"])
            if error_robot != 0: #if error, update err_reg and error_detected==1
                err_reg = [0,0,0, 0,0,1,0,0]
                error_detected = 1

        if error_detected == 0: #End effector off -> on
            error_robot = self.__robot.gripper_action(self.__gripper_pin,self.__n_open_gripper)
            if error_robot != 0:
                err_reg = [0,0,0, 0,0,1,0,1]
                error_detected = 1
        
        if error_detected == 0: #From pick to prepick
            self.__robot.change_payload("full") #Payload changes while carrying a jig
            fast_speed = speedweight["Full"]*self.__fast_speed
            if isinstance(jig_pick,Jig):
                error_robot = self.__robot.move_arms_list(arm_status_Pi["PrePi"])
            if error_robot != 0: #if error, update err_reg and error_detected==1
                err_reg = [0,0,0, 0,0,1,1,0]
                error_detected = 1
        
        if error_detected == 0 and isinstance(jig_pick,Jig): #From prepick to preprepick
            error_robot = self.__robot.move_arms_list(arm_status_Pi["PrePrePi"])
            if error_robot != 0: #if error, update err_reg and error_detected==1
                err_reg = [0,0,0, 0,0,1,1,1]
                error_detected = 1

        if error_detected == 0: #From prepick to pick up
            self.__robot.speed_set(fast_speed)
            error_robot = self.__robot.move_arms_list(arm_status_Pi["PiU"])
            if error_robot != 0: #if error, update err_reg and error_detected==1
                err_reg = [0,0,0, 0,1,0,0,0]
                error_detected = 1        

        if error_detected == 0: #From Home to place up
            error_robot = self.__robot.move_arms_list(arm_status_PL["PiU"]) 
            if error_robot != 0: #if error, update err_reg and error_detected==1
                err_reg = [0,0,0, 0,1,0,1,0]
                error_detected = 1

        if error_detected == 0 and isinstance(jig_place,Jig): #From place up to prepreplace
            error_robot = self.__robot.move_arms_list(arm_status_PL["PrePrePi"])
            self.__robot.speed_set(self.__slow_speed)
            if error_robot != 0: #if error, update err_reg and error_detected==1
                err_reg = [0,0,0, 0,1,1,0,0]
                error_detected = 1

        if error_detected == 0: #From prepreplace to preplace
            if place == "OKparts":
                ok_speed = speedweight["fast_ok"]*self.__fast_speed
                self.__robot.speed_set(ok_speed)
            error_robot = self.__robot.move_arms_list(arm_status_PL["PrePi"])
            if error_robot != 0: #if error, update err_reg and error_detected==1
                err_reg = [0,0,0, 0,1,1,0,1]
                error_detected = 1

        if error_detected == 0: #From preplace to place
            if place == "NoGood" or place == "OKparts":
                self.__slow_speed = speedweight["Outputs"]*self.__slow_speed #Speed is slower in outputs stations
            self.__robot.speed_set(self.__slow_speed)
            error_robot = self.__robot.move_arms_list(arm_status_PL["Pl"])
            if error_robot != 0: #if error, update err_reg and error_detected==1
                err_reg = [0,0,0, 0,1,1,1,0]
                error_detected = 1

        if error_detected == 0: #End effector on -> off
            error_robot = self.__robot.gripper_action(self.__gripper_pin,self.__n_closed_gripper)
            self.__robot.change_payload("empty")
            fast_speed = speedweight["Empty"]*self.__fast_speed
            if error_robot != 0: #if error, update err_reg and error_detected==1
                err_reg = [0,0,0, 0,1,1,1,1]
                error_detected = 1
          
        if error_detected == 0: #From prepreplace to place up
            self.__robot.speed_set(fast_speed)
            error_robot = self.__robot.move_arms_list(arm_status_PL["PiU"])
            if error_robot != 0: #if error, update err_reg and error_detected==1
                err_reg = [0,0,0, 1,0,0,1,0]
                error_detected = 1                                      
        
        if error_detected == 0: #Closes jig from the place station or checks proximity sensors
            if isinstance(jig_place,Jig):
                error_jig = self.close_jig(jig_place,self.__shared_resource.config["Robot_controller"]["Close_timeout"])
            elif isinstance(jig_place,int):
                error_jig = self.jig_status("station_occupied",jig_place)
            if error_jig != 0: #if error, update err_reg and error_detected==1
                err_reg = [0,0,0, 0,1,0,1,1]
                error_detected = 1
           
        if error_detected == 0: #If no errors arise, corresponding registers bits are set to 0   
            self.__shared_resource.get_SR().change_bit_from_int(8, 0)
            for i in range (8):
                self.__shared_resource.get_ER().change_bit_from_int(i, 0)
                                                                    

        if error_detected == 1: #If errors arise, registers are updated
            
            self.__shared_resource.consume_order() #Clears orders list if error
            
            self.__pt_full = False
            
            if pick=="In": #Error register bits 6 to 4 update according to the defined codification
                err_reg[0:3] = [0,0,0]
            elif pick == "HiPot":
                if place =="LCR":
                    err_reg[0:3] = [0,0,1]
                elif place == "NoGood":
                    err_reg[0:3] = [0,1,0]
            elif pick == "LCR":
                if place == "PowTow":
                    err_reg[0:3] = [0,1,1]
                elif place == "NoGood":
                    err_reg[0:3] = [1,0,0]
            elif pick == "PowTow":
                if place == "OKparts":
                    err_reg[0:3] = [1,0,1]
                elif place == "NoGood":
                    err_reg[0:3] = [1,1,0]

            

            self.__shared_resource.get_SR().change_bit_from_int(8, 1) #SR bit 8 set to 1
            for i in range (8):
                self.__shared_resource.get_ER().change_bit_from_int(i, err_reg[len(err_reg)-1-i]) #Error register is updated

            logline="" #Line of log file initialize

            now = datetime.now().strftime("[%H:%M:%S:%f]")  #Store the current time in a variable 

            error_reg = str(bin(self.__shared_resource.get_ER().get_value())[2:].zfill(8))

            #Give format to the line ([Time] Move Code: 010 Step Code: 01010) *This is just a example
            logline= "\n" + now + "\t" + "Move Code: " + error_reg[0:3] + "\t" + "Step Code: " + error_reg[3:len(error_reg)-1] +"\n"
            self.f.write(logline) #Write in the file
            self.f.flush() #Avoid blank files when writing


        
        #In the end we print error value and registers value
        print("Error Code: --> " + str(error_detected) + " <--   if Error Code = 0, robot moves are ok")
        self.logprint("\nError Code: --> " + str(error_detected) + " <--   if Error Code = 0, robot moves are ok")
        print("Error Register: " + str(bin(self.__shared_resource.get_ER().get_value())[2:].zfill(8)))
        self.logprint("\nError Register: " + str(bin(self.__shared_resource.get_ER().get_value())[2:].zfill(8)))

        return error_detected

    def move(self,home, pick, place,jig_pick, jig_place): #Calls the move_steps method
        self.__points=self.__shared_resource.config["Points"] #Points are load in every time to allow modification through interface
        return self.__move_steps(self.__points[home], self.__points[pick], self.__points[place], pick, place, jig_pick,jig_place)

    def move_home(self, home): #Moves to main home coordinates and releases the robot
        speed = self.__shared_resource.config["Robot_controller"]["Home_linear_speed"] #Reads the current speed of home move
        self.__robot.speed_set(speed) #Changes speed
        self.__robot.move_upwards() #Linear motion in Z coordinate
        return self.__robot.move_arms_list(home) #Joint motion

    def autoverification(self):
        self.__shared_resource.get_SR().change_bit_from_int(11, 1) #This bit means verification is in process
        time0 = time()
        alarm_length = float(self.__shared_resource.config["Robot_controller"]["Alarm_length"]) #Read alarm length
            
        #Alarm setting and length PENDING CHANGE
        #self.__robot.digital_write(self.__alarm_port,1)
        while time() - time0 >= alarm_length:
            pass  
        #self.__robot.digital_write(self.__alarm_port,0)
            
        #Here we check jigs status. If there are piece or problems, we get 1 as output
        in_state            = self.jig_status("station_empty", self.__jig_in)
        hipot_state         = self.check(self.__jig1)
        lcr_state           = self.check(self.__jig2)
        powtow_state        = self.check(self.__jig3)
        ng_state            = self.jig_status("station_empty", self.__jig_ng)
        ok_state            = self.jig_status("station_empty", self.__jig_ok)
        codet, valuet = self.__robot.digital_read_tool(0) #Read tool input 0 (close gripper sensor)
        self.__Open_All_Jigs()
        
        #Cration of states list
        states = [in_state, hipot_state, lcr_state, powtow_state, ng_state,ok_state]
        
        #Bits 6 to 15 of SR set to 0
        for i in range(6,16):
                self.__shared_resource.get_SR().change_bit_from_int(i, 0)
                
        #SR is updated according to the stations state
        for i in range(1,4):
            self.__shared_resource.get_SR().change_bit_from_int(i, states[i])
            if states[i] == 1:
                #If a station is not empty, error
                self.__shared_resource.get_SR().change_bit_from_int(8, 1)
        
        if valuet == 1: #if gripper is closed
            self.__shared_resource.get_SR().change_bit_from_int(8, 1) #Error
            self.logprint("\nERROR: Gripper must be open to avoid possible problems")

        status_register = self.__shared_resource.get_SR().get_value()
        print(bin(status_register)[2:].zfill(16)) #Print SR value
        self.logprint("\n\n"+"SR: "+str(bin(status_register)[2:].zfill(16)))
        
        
        sleep(2) #Wait for 2 seconds to resume

    def thread_init(self):
        #Read in thread is defined and started when this function is called
        self.read_in = Thread(target= self.read_in_thread)
        self.read_in.start()
        
    def read_in_thread(self):
        #According to the value of read_in_interval, it reads several controller inputs and calculates arms parameters
        time0 = time()
        #Flags for emergency stop edges are set to False, initially
        is_open = False #Falling edge flag
        sr_reset = False #Rising edge flag
        interval = self.__shared_resource.config["Robot_controller"]["Read_in_interval"]
        #Reading of arm connection status
        try:
            self.__shared_resource.params["Arm Connected"] =self.__robot.robot_conn_status() #Must be in real time
        except:
            self.__shared_resource.params["Arm Connected"] = False
        while not self.__shared_resource.Quit:
            if (time() - time0) >= interval: #Only execute the following commands if fixed time elapses
                try:
                    #Reading of in, nogood and okparts sensors
                    code_in, value_in = self.__robot.digital_read(self.__jig_in)
                    code_ng, value_ng = self.__robot.digital_read(self.__jig_ng)
                    code_ok, value_ok = self.__robot.digital_read(self.__jig_ok)

                    #SR is updated according to sensors value
                    self.__shared_resource.get_SR().change_bit_from_int(0, int(value_in))
                    self.__shared_resource.get_SR().change_bit_from_int(5, int(value_ng))
                    self.__shared_resource.get_SR().change_bit_from_int(4,int(value_ok))

                    #Current positions values are stored in shared resource to be displayed on the interface
                    code, self.__shared_resource.params["Cartesian Position"] = self.__robot.get_xyz_pos()
                    code, self.__shared_resource.params["Joint Position"] = self.__robot.get_joint_pos()

                    if self.__robot.read_controller_error() != 0:
                        #If there is controller error, we update that error and enable the robot (this is to avoid fake values on the interface)
                        self.__shared_resource.params["Robot Error"] = self.__robot.read_controller_error()
                        self.__robot.enable_robot()
                    self.__shared_resource.params["Arm Mode"] = self.__robot.read_state() #Reads arm state and stores in shared resource
                except:
                    pass
                time0=time() #Update time to reset the count
            
            if self.__robot.es_is_pressed: #Checks if emergency stop is pressed
                if is_open: #If falling edge
                    is_open = False #set to False again
                    try:
                        self.__Open_All_Jigs() #We open all stations
                    except:
                        pass
                    self.__shared_resource.consume_order() #If order list was not empty, it is cleared.
                    self.__pt_full = False #Then PowTow station will be empty
                self.__shared_resource.get_SR().change_bit_from_int(8, 1) #Error is set to 1
                self.__shared_resource.inmotion = False #Arm is no longer in motion
                sr_reset = True #Rising edge flag is set to true
            else:
                is_open = True #If emergency stop is not pressed, falling edge flag is set to true
                if sr_reset: #If rising edge
                    sr_reset = False #Set to false again
                    try:
                        self.__robot.enable_robot() #Robot is enabled to continue the main functionality
                        self.move_home(self.__points["Home"]) #Move to a known position to restart process
                        self.__shared_resource.params["Robot Error"] = self.__robot.read_controller_error() #Update error register once ES is no longer pressed
                        self.autoverification() #Verification process
                    except:
                        pass
            
    def open_jig(self, jig_n:Jig): #Opens the specified jig

        error_code = self.__robot.digital_write(jig_n.in_port_p,jig_n.n_closed) #We send the n_closed value to specific digital input
        #If it is normally closed, it is open with 1. Otherwise, it is open with 0
        if error_code == 0:
            sleep(0.5) #To avoid needless damage
            error_code = self.__robot.digital_write(jig_n.in_port_c,jig_n.n_closed) #If no errors, we open probes
        return error_code
     
    def close_jig(self, jig_n:Jig, timeout = 5): #Closes the specified jig

        error_code = self.__robot.digital_write(jig_n.in_port_c,jig_n.n_open) #We send th n_open value to specific digital input
        #If normally closed, it is closed with 0. Otherwise, it is open with 1
        if error_code == 0:
            time0 = time()
            while time() - time0 <= timeout:
                #This function locks the process until centering cyllinder is closed or error arises
                error_code, value_c = self.__robot.digital_read(jig_n.out_port_ic_c)
                
                if (value_c == jig_n.close_value or error_code != 0) and (time()-time0>=0.7): #If it is closed or error arise, loop breaks
                    break;
                
            if error_code == 0 and value_c == jig_n.close_value: #If no errors arise, we close probes cyllinder
                error_code = self.__robot.digital_write(jig_n.in_port_p,jig_n.n_open) #We send the n_open value to specific digital input
                if error_code == 0:#If no error, we enter the timed loop
                    time0 = time()
                    while time() - time0 <= timeout:
                        error_code, value_p = self.__robot.digital_read(jig_n.out_port_ic_p) #Read sensors
                        if value_p == jig_n.close_value or error_code != 0: #If closed or error, break the loop
                            break;
                    if error_code == 0 and value_p == jig_n.close_value: #If error or not closed, error is 
                        pass
                    else:
                        error_code = 1
            else:
                error_code = 1

        return error_code

    def jig_status(self, check, jig_n:Union[Jig, int]): #Checks te specified status of a jig
        if check == "open" and isinstance(jig_n,Jig):
            #For check status, we must ensure that the reading from the specificied port is correct
            timeout = float(self.__shared_resource.config["Robot_controller"]["Status_open_to"])
            time0 = time()
            #Same functionality as close_jig. Reads port within timeout. If values are not correct, error
            #Read port after loop, otherwise timeout elapses when wait=False in maiin move function
            err_code, value = self.__robot.digital_read(jig_n.out_port_fc) 
            while time() - time0 <= timeout:
                err_code, value = self.__robot.digital_read(jig_n.out_port_fc)
                if value == jig_n.open_value or err_code != 0:
                    break;
            if err_code != 0 or int(value) == int(not(jig_n.open_value)):
                error = 1
            elif err_code == 0 and int(value) == jig_n.open_value:
                error = 0

        elif check == "station_occupied" and isinstance(jig_n,int):
            #Checks in, nogood or okparts sensors. If there is piece, no error.
            error_code,value = self.__robot.digital_read(jig_n)
            if error_code != 0 or value == 0:
                error = 1
            else:
                error = 0

        elif check == "station_empty" and isinstance(jig_n,int):
            #Checks in, nogood or okparts sensors. If it is empty, no error.
            error_code, value = self.__robot.digital_read(jig_n)
            if error_code != 0 or value == 1:
                error = 1
            else:
                error = 0

        elif check == "close" and isinstance(jig_n,Jig):
            #For close status, we must ensure both centering and puntas cyllinders are closed
            err_code_c, value_c = self.__robot.digital_read(jig_n.out_port_ic_c)
            err_code_p, value_p = self.__robot.digital_read(jig_n.out_port_ic_p)
            if err_code_c != 0 or err_code_p != 0 or int(value_c) == int(not(jig_n.close_value)) or int(value_p) == int(not(jig_n.close_value)):
                error = 1
            else:
                error = 0

        return error

    def check(self, jig_n : Jig):
        error = 0
        error_code = self.open_jig(jig_n) #force open at the beggining
        if error_code != 0:
            error =1   # there is a communication error, finish
        else:
            error_code = self.jig_status("open",jig_n) #Check if open
            if (error_code==1):  #if jig is not open, error
                error =1
            else:
                error_code= self.close_jig(jig_n,self.__shared_resource.config["Robot_controller"]["Close_timeout_check"]) #close the jig
                error_code = self.jig_status("open",jig_n) #Check if open
                if error_code==0:  #if jig is open after send a close command, error
                    error=1
                else:
                    error_code = self.jig_status("close",jig_n) #asking if jigs is close as usual (that means that a part is in the jig)
                    if error_code==0:  #there is a part in the jig, the jig is not empty
                        error=1
        return error

    def interface_bt_fcn(self):
        #This function calls the methods of the interface if their buttons were previously pressed. Once they are executed,
        #their flags are set to false until buttons are pressed again
        if self.__shared_resource.wantupdate:
            self.__shared_resource.updateparams()
            self.__shared_resource.wantupdate = False
            self.logprint("params updated")
        
        if self.__shared_resource.wantsave:
            self.__shared_resource.saveparams()
            self.__shared_resource.wantsave = False
            self.logprint("params saved")
        
        if self.__shared_resource.wantload:
            self.__shared_resource.loadparams()
            self.__shared_resource.wantload = False
            self.logprint("params loaded")
        
        if self.__shared_resource.wantreset:
            self.__shared_resource.resetparams()
            self.__shared_resource.wantreset = False
            self.logprint("params reset")

    def __Mv_In_to_HP(self):

        self.__shared_resource.params["Current Step"] = "In to HiPot" #Update current step for the interface

        self.interface_bt_fcn() #Calls parameters buttons functions

        self.__shared_resource.inmotion = True #Arm motion is set to true to avoid parameters change during process

        if self.__simulation: #If simulation, we just print
            for i in range(5):
                print("     Realizando robot: Move In to HP: " + str(i) + "/5 \n")
                sleep(1)
        else: #If no simulation
            print("     Executing robot: Move In to HP\n") #Print process name
            self.logprint("\n     Executing robot: Move In to HP\n")
            if (self.move("HomeInHiPot","In", "HiPot",self.__jig_in,self.__jig1)!=0): #Call move funtion and read error output
                #If error
                print("\n     ERROR EXECUTING : Move In to HP\n")
                self.logprint("\n     ERROR EXECUTING : Move In to HP\n")
            else:
                #If no error, SR is updated
                print("\n     Succesfully executed: Move In to HP\n")
                self.logprint("\n     Succesfully executed: Move In to HP\n")
                self.__shared_resource.get_SR().change_bit_from_int(0, 0)
                self.__shared_resource.get_SR().change_bit_from_int(1, 1)

            self.__shared_resource.inmotion = False #Once motion ends, robot is no longer in motion

    def __Mv_HP_to_LCR(self):
        self.__shared_resource.params["Current Step"] = "HiPot to LCR" #Update current step for the interface

        self.interface_bt_fcn() #Calls parameters buttons functions

        self.__shared_resource.inmotion = True #Arm motion is set to true to avoid parameters change during process

        if self.__simulation: #If simulation, we just print
            for i in range(4):
                print("     Realizando robot: Move HP to LCR: " + str(i) + "/4 \n")
                sleep(1)
        else: #If no simulation
            print("     Executing robot: Move HP to LCR\n") #Print process name
            self.logprint("     Executing robot: Move HP to LCR\n")

            if(self.move("HomeHiPotLCR", "HiPot", "LCR", self.__jig1, self.__jig2)): #Call move funtion and read error output
                #If error
                print("\n     ERROR EXECUTING : Move HP to LCR\n")
                self.logprint("\n     ERROR EXECUTING : Move HP to LCR\n")
            else:
                #If no error, SR is updated
                print("\n     Succesfully executed: Move HP to LCR\n")
                self.logprint("\n     Succesfully executed: Move HP to LCR\n")
                self.__shared_resource.get_SR().change_bit_from_int(1, 0)
                self.__shared_resource.get_SR().change_bit_from_int(2, 1)

            self.__shared_resource.inmotion = False #Once motion ends, robot is no longer in motion

    def __Mv_HP_to_NG(self):
        self.__shared_resource.params["Current Step"] = "HiPot to NoGood" #Update current step for the interface

        self.interface_bt_fcn() #Calls parameters buttons functions

        self.__shared_resource.inmotion = True #Arm motion is set to true to avoid parameters change during process

        if self.__simulation: #If simulation, we just print
            for i in range(6):
                print("     Realizando robot: Move HP to NoGood: " + str(i) + "/6 \n")
                sleep(1)
        else: #If no simulation
            print("     Executing robot: Move HP to NoGood\n") #Print process name
            self.logprint("     Executing robot: Move HP to NoGood\n")

            if(self.move("HomeHiPotNoGood","HiPot", "NoGood", self.__jig1, self.__jig_ng)): #Call move funtion and read error output
                #If error
                print("\n     ERROR EXECUTING : Move HP to NoGood\n")
                self.logprint("\n     ERROR EXECUTING : Move HP to NoGood\n")
            else:
                #If no error, SR is updated
                print("\n     Succesfully executed: Move HP to NoGood\n")
                self.logprint("\n     Succesfully executed: Move HP to NoGood\n")
                self.__shared_resource.get_SR().change_bit_from_int(1, 0)
                self.__shared_resource.get_SR().change_bit_from_int(5, 1)
            
            self.__shared_resource.inmotion = False #Once motion ends, robot is no longer in motion

    def __Mv_LCR_to_PT(self):

        self.__shared_resource.params["Current Step"] = "LCR to PowTow" #Update current step for the interface

        self.interface_bt_fcn() #Calls parameters buttons functions

        self.__shared_resource.inmotion = True #Arm motion is set to true to avoid parameters change during process

        if self.__simulation: #If simulation, we just print
            for i in range(6):
                print("     Realizando robot: Move LCR to PT: " + str(i) + "/6 \n")
                sleep(1)
        else: #If no simulation
            print("     Executing robot: Move LCR to PT\n") #Print process name
            self.logprint("     Executing robot: Move LCR to PT\n")

            if(self.move("HomeLCRPowTow","LCR", "PowTow",self.__jig2,self.__jig3)): #Call move funtion and read error output
                #If error
                print("\n     ERROR EXECUTING : Move LCR to PT\n")
                self.logprint("\n     ERROR EXECUTING : Move LCR to PT\n")
            else:
                #If no error, SR is updated
                print("\n     Succesfully executed: Move LCR to PT\n")
                self.logprint("\n     Succesfully executed: Move LCR to PT\n")

                self.__shared_resource.get_SR().change_bit_from_int(2, 0)
                self.__shared_resource.get_SR().change_bit_from_int(3, 1)
                self.__pt_full = True #Station is now full
                    
            self.__shared_resource.inmotion = False #Once motion ends, robot is no longer in motion

    def __Mv_LCR_to_NG(self):

        self.__shared_resource.params["Current Step"] = "LCR to NoGood" #Update current step for the interface

        self.interface_bt_fcn() #Calls parameters buttons functions

        self.__shared_resource.inmotion = True #Arm motion is set to true to avoid parameters change during process

        if self.__simulation: #If simulation, we just print
            for i in range(5):
                print("     Realizando robot: Move LCR to NoGood: " + str(i) + "/5 \n")
                sleep(1)
        else: #If no simulation
            print("     Executing robot: Move LCR to NoGood\n") #Print process name
            self.logprint("     Executing robot: Move LCR to NoGood\n")

            if(self.move("HomeLCRNoGood","LCR", "NoGood",self.__jig2,self.__jig_ng)): #Call move funtion and read error output
                #If error
                print("\n     ERROR EXECUTING : Move LCR to NoGood\n")
                self.logprint("\n     ERROR EXECUTING : Move LCR to NoGood\n")
            else:
                #If no error, SR is updated
                print("     Succesfully executed: Move LCR to NoGood\n")
                self.logprint("\n     Succesfully executed: Move LCR to NoGood\n")
                self.__shared_resource.get_SR().change_bit_from_int(2, 0)
                self.__shared_resource.get_SR().change_bit_from_int(5, 1)
            
            self.__shared_resource.inmotion = False #Once motion ends, robot is no longer in motion

    def __Mv_PT_to_OK(self):

        self.__shared_resource.params["Current Step"] = "PowTow to OKparts" #Update current step for the interface

        self.interface_bt_fcn() #Calls parameters buttons functions

        self.__shared_resource.inmotion = True #Arm motion is set to true to avoid parameters change during process

        self.__pt_full = False #Station gets empty with this motion, so this variable is set to true

        self.__shared_resource.get_SR().change_bit_from_int(6, 0) #Laser process bit

        if self.__simulation: #If simulation, we just print
            for i in range(5):
                print("     Realizando robot: Move PT to OK_Parts: " + str(i) + "/5 \n") 
                sleep(1)
        else: #If no simulation
            print("     Executing robot: Move PT to OKparts\n") #Print process name
            self.logprint("     Executing robot: Move PT to OKparts\n")

            if(self.move("HomePowTowOKparts","PowTow", "OKparts",self.__jig3,self.__jig_ok)): #Call move funtion and read error output
                #If error
                print("\n     ERROR EXECUTING : Move PT to Okparts\n")
                self.logprint("\n     ERROR EXECUTING : Move PT to Okparts\n")

            else:
                #If no error, SR is updated
                print("     Succesfulyl executed: Move PT to OKparts\n")
                self.logprint("\n     Succesfully executed: Move PT to OKparts\n")
                self.__shared_resource.get_SR().change_bit_from_int(3, 0)
                self.__shared_resource.get_SR().change_bit_from_int(4, 1)

            self.__shared_resource.inmotion = False #Once motion ends, robot is no longer in motion

    def __Mv_PT_to_NG(self):

        self.__shared_resource.params["Current Step"] = "PowTow to NoGood" #Update current step for the interface

        self.__shared_resource.get_SR().change_bit_from_int(6, 0)  #Laser process bit

        self.interface_bt_fcn() #Calls parameters buttons functions

        self.__shared_resource.inmotion = True #Arm motion is set to true to avoid parameters change during process

        self.__pt_full = False #Station gets empty with this motion, so this variable is set to true

        if self.__simulation: #If simulation, we just print
            for i in range(5):
                print("     Realizando robot: Move PT to NoGood: " + str(i) + "/5 \n")
                sleep(1)
        else: #If no simulation
            print("     Executing robot: Move PT to NoGood\n") #Print process name
            self.logprint("     Executing robot: Move PT to NoGood\n")

            if(self.move("HomePowTowNoGood","PowTow", "NoGood",self.__jig3,self.__jig_ng)): #Call move funtion and read error output
                #If error
                print("\n     ERROR EXECUTING : Move PT to NoGood\n")
                self.logprint("\n     ERROR EXECUTING : Move PT to NoGood\n")
            else:
                #If no error, SR is updated
                print("\n     Succesfully executed: Move PT to NoGood\n")
                self.logprint("\n     Succesfully executed: Move PT to NoGood\n")
                self.__shared_resource.get_SR().change_bit_from_int(3, 0)
                self.__shared_resource.get_SR().change_bit_from_int(5, 1)

            self.__shared_resource.inmotion = False #Once motion ends, robot is no longer in motion

    def __Laser_Print(self, data_received: str):

        data_print = data_received[11:].strip("\n") #We get the data to be printed from the input string. we use last characters and delete \n
        date = datetime.today().strftime("%y/%m/%d") #Get current time
        data_print = date + data_print #Add current time to data_print
        print("Text to print:  -->" + data_print + "<--") #Print text on terminal and interface
        self.logprint("Text to print:  -->"+data_print+"<--\n")

        self.__robot.digital_write(self.__laser_trigger,0) #Laser trigger is set to 0 to avoid errors
        self.__shared_resource.get_SR().change_bit_from_int(6, 1) #Laser process bit is set to 1

        with open("/home/pi/share/print.txt", "w")as file: #Open shared file to write on its first line
            file.write(data_print) #Write data
            file.close() #Close file to avoid problems
        print("Triggering laser") #Print proces info
        self.logprint("Triggering laser\n")
        self.__robot.digital_write(self.__laser_trigger,1) #Laser trigger output is activated

        sleep(self.__shared_resource.config["Robot_controller"]["Laser_time"]) #Wait for 2 seconds to avoid problems

        self.__robot.digital_write(self.__laser_trigger,0) #Output deactivated

        self.__shared_resource.get_SR().change_bit_from_int(6, 0) #Laser process bit is set to 0
        
    #Functions to control jigs. They may be used by the interface
    def __Open_HiPot_Jig(self):
        self.open_jig(self.__jig1)
    
    def __Open_LCR_Jig(self):
        self.open_jig(self.__jig2)
    
    def __Close_LCR_Jig(self):
        self.close_jig(self.__jig2)

    def __Open_PowTow_Jig(self):
        self.open_jig(self.__jig3)
    
    def __Open_All_Jigs(self):
        self.open_jig(self.__jig1)
        self.open_jig(self.__jig2)
        self.open_jig(self.__jig3)

    ##Test functions##
    def jig_test_sensor(self): #Function to test the magnetic sensors and open/close functions
        while True:
            print("Cerrando")
            print("Error en close: " + str(self.close_jig(self.__jig1)))
            sleep(3)
            print("Abriendo")
            print("Error en open: " + str(self.open_jig(self.__jig1)))
            sleep(3)

    def jig_test(self): #Same as jig_test_sensor, but this one is a non sensors version
        code = self.__robot.digital_write(self.__jig1.in_port_p,1)
        print(str(code) + "1 a las puntas")
        sleep(2)
        code = self.__robot.digital_write(self.__jig1.in_port_c,1)
        print(str(code) + "1 al centrador")
        sleep(2)
        code = self.__robot.digital_write(self.__jig1.in_port_c,0)
        print(str(code) +"0 al centrador")
        sleep(2)
        code = self.__robot.digital_write(self.__jig1.in_port_p,0)
        print(str(code) + "0 a las puntas")
        sleep(2)

    def sensor_test(self): #Function to only check sensor reading
        while True:
            print("Inicio de carrera:")
            print(self.__robot.digital_read(self.__jig1.out_port_ic_p))
            sleep(1)
            print("Final de carrera:")
            print(self.__robot.digital_read(self.__jig1.out_port_fc))

    def move_test(self): #Method to move the robot arm (no sensors)
        self.__shared_resource.get_SR().change_bit_from_int(1, 0)
        err_reg = [0,0,0,1,0,0,0,0]
        error_code = self.__robot.digital_write(self.__jig1.in_port_p,1)
        sleep(1)
        if error_code == 0:
            error_code = self.__robot.digital_write(self.__jig1.in_port_c,1)
        if error_code != 0:
            self.__shared_resource.get_SR().change_bit_from_int(8,1)
            err_reg[4] = 0
            err_reg[5] = 0
            err_reg[6] = 0
            err_reg[7] = 1
            for i in range (8):
                self.__shared_resource.get_ER().change_bit_from_int(i, err_reg[len(err_reg)-1-i])
        else:
            print("     Realizando robot: Move IN to OK\n")
            error_code = self.move("In", "OKparts",None,None)
            if error_code != 0:
                print("     1ERROR REALIZANDO : Move IN to OK\n")
            else:
                error_code = self.__robot.digital_write(self.__jig1.in_port_c,0)
                sleep(1)
                error_code = self.__robot.digital_write(self.__jig1.in_port_p,0)
                if error_code != 0:
                    print("     ERROR REALIZANDO : Move IN to OK\n")
                    self.__shared_resource.get_SR().change_bit_from_int(8,1)
                    err_reg[4] = 1
                    err_reg[5] = 0
                    err_reg[6] = 0
                    err_reg[7] = 1
                    for i in range (8):
                        self.__shared_resource.get_ER().change_bit_from_int(i, err_reg[len(err_reg)-1-i])
                else:
                    print("     Se ha realizando robot: Move IN to OK\n")
        self.__shared_resource.get_SR().change_bit_from_int(2, 1)
