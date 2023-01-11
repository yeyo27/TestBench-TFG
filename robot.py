"""
Created on Fri Nov 12 10:01 2021
First expansion on Mon March 13 9:35 2022

@author: Sergio Ramirez Ojea
Modificated and expanded by Sergio Mesa Martin
"""

import time
import traceback
from threading import Thread
from shared_resource import Shared_Resource
import time
import xarm

class Robot():
    def __init__(self, sr: Shared_Resource):
        self.__sr                = sr #Shared resource instance
        self.__ip                = self.__sr.config["Robot_arm"]["Robot_ip"] #Stores ip from config file through Shared resource
        self.__arm               = None #This variable will store the xarm instance, initially None
        self.__params            = None #Parameters dictionary, initially None

        self.__gripper_open_pin  = 12 #DI4 of controller box. Open gripper when activated
        self.__gripper_close_pin = 13 #DI5 of controller box. Close gripper when activated
        self.__emergency_stop    = 14 #DI6 of controller box. Stops the arm motion
        self.__manual_mode       = 15 #DI7 of controller box. Sets mode to manual mode

        self.__gripper_pin       = 6 #Gripper port (CO6 of robot controller)
        self.__gripper_close     = 0 #Tool input port 0
        self.__gripper_open      = 1 #Tool input port 1

        #Flags and variables
        self.es_is_pressed       = False #Indicates if emergency stop is pressed or not
        self.__threshold         = 7 #wait threshold in degrees

    def ini(self):                       # Initialize robot
        """
            Initialize robot
        """
        def __pprint(*args, **kwargs):
            try:
                stack_tuple = traceback.extract_stack(limit=2)[0]
                print('\n\n[{}][{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), stack_tuple[1], ' '.join(map(str, args)))+"\n\n")
                self.__sr.logger.write('\n\n[{}][{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), stack_tuple[1], ' '.join(map(str, args)))+"\n\n")
            except:
                print("\n\n" *args, **kwargs + "\n\n")
                self.__sr.logger.write("\n\n" *args, **kwargs + "\n\n")
        
        def __error_warn_change_callback(data):                   # Register error/warn changed callback
            if data and data['error_code'] != 0:
                self.__params['quit'] = True
                __pprint('err={}, quit'.format(data['error_code']))
                self.__arm.release_error_warn_changed_callback(__error_warn_change_callback)

        def __state_changed_callback(data):                       # Register state changed callback
            if data and data['state'] == 4:
                if self.__arm.version_number[0] >= 1 and self.__arm.version_number[1] >= 1 and self.__arm.version_number[2] > 0:
                    self.__params['quit'] = True
                    __pprint('state=4, quit')
                    self.__arm.release_state_changed_callback(__state_changed_callback)

        def __connect_changed_callback(data):                     # Register connect changed callback
            if data and not data['connected']:
                self.__params['quit'] = True
                self.__sr.params["Arm Connected"]=data["connected"]
                __pprint('disconnect, connected={}, reported={}, quit'.format(data['connected'], data['reported']))
                self.logprint(self.__sr.params["Arm Connected"])
                self.__arm.release_connect_changed_callback(__error_warn_change_callback)
        
        

        
        self.__arm = xarm.wrapper.XArmAPI(self.__ip) #Instance of the robot arm using xarm library
        
        __pprint('xArm-Python-SDK Version:{}'.format(xarm.version.__version__))
        
        #The following set of functions enable the robot arm
        self.__arm.clean_warn()
        self.__arm.clean_error()
        self.__arm.motion_enable(True)
        self.__arm.set_mode(0)
        self.__arm.set_state(0)
        
        variables = {'speed': 0, 'potentiometer': 0}        # Not used. Only purpose is looking up their sintax

        #Parameters initialization
        self.__params = {'speed': self.__sr.params["Linear Speed"], 'acc': 50000, 'angle_speed': self.__sr.config["Robot_arm"]["Angle_speed"], 'angle_acc': 1145, 'events': {}, 'variables': variables, 'callback_in_thread': True, 'quit': False}

        self.__arm.register_error_warn_changed_callback(__error_warn_change_callback)

        self.__arm.register_state_changed_callback(__state_changed_callback)

        if hasattr(self.__arm, 'register_count_changed_callback'):     # Register counter value changed callback
            def count_changed_callback(data):
                if not self.__params['quit']:
                    __pprint('counter val: {}'.format(data['count']))
            self.__arm.register_count_changed_callback(count_changed_callback)

        self.__arm.register_connect_changed_callback(__connect_changed_callback)
        
        self.__sr.params["Arm Connected"] = True
        
        self.change_payload("empty")

        #Buttons configuration
        self.__arm.set_cgpio_digital_input_function(self.__emergency_stop, 1) #Sets emergency stop function

        #Definition and start of button pad thread
        self.pad = Thread(target= self.button_pad_thread)
        self.pad.start()
        
    def fin(self):                       # Release robot
        """
            Release robot
        """
        self.pad.join()
        
        def __pprint(*args, **kwargs):
            try:
                stack_tuple = traceback.extract_stack(limit=2)[0]
                print('[{}][{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), stack_tuple[1], ' '.join(map(str, args))))
                self.__sr.logger.write('[{}][{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), stack_tuple[1], ' '.join(map(str, args))))
            except:
                print(*args, **kwargs)
                self.__sr.logger.write(*args, **kwargs)
        
        def __error_warn_change_callback(data):                   # Register error/warn changed callback
            if data and data['error_code'] != 0:
                self.__params['quit'] = True
                __pprint('err={}, quit'.format(data['error_code']))
                self.__arm.release_error_warn_changed_callback(__error_warn_change_callback)

        def __state_changed_callback(data):                       # Register state changed callback
            if data and data['state'] == 4:
                if self.__arm.version_number[0] >= 1 and self.__arm.version_number[1] >= 1 and self.__arm.version_number[2] > 0:
                    self.__params['quit'] = True
                    __pprint('state=4, quit')
                    self.__arm.release_state_changed_callback(__state_changed_callback)
        
        def __count_changed_callback(data):
                if not self.__params['quit']:
                    __pprint('counter val: {}'.format(data['count']))
        
        # release all event
        if hasattr(self.__arm, 'release_count_changed_callback'):
            self.__arm.release_count_changed_callback(__count_changed_callback)
        self.__arm.release_error_warn_changed_callback(__state_changed_callback)
        self.__arm.release_state_changed_callback(__state_changed_callback)
        self.__arm.release_connect_changed_callback(__error_warn_change_callback)

    # -------------------------------------------------------------------------------------------------------------------------
    #From now on, every function is created by Sergio:


    def button_pad_thread(self):
        # This method is designed to work as a thread. Reads the state of the emergency stop and, depending on the value,
        # enables or disables the other buttons

        #Flags for pad
        enabled     = True
        manual_mode = False
        is_open     = False
        is_closed   = False
        paused      = False

        while not self.__sr.Quit:
            try:
                code_es, value_es = self.digital_read(self.__emergency_stop)
            except:
                code_es = None
                value_es = None

            if code_es == 0 and value_es == 0: #Emergency stop is pressed
                #if ES is on, we enable the other buttons and robot motion is disabled
                self.es_is_pressed = True
                
                if enabled:
                    #Once emergency stop is pressed, its function is disabled to allow manual mode button
                    self.__arm.set_cgpio_digital_input_function(self.__emergency_stop, 0)
                    enabled = False


                #Manual mode button setting
                if not manual_mode: #Manual mode enabled if previously disabled
                    self.__arm.set_cgpio_digital_input_function(self.__manual_mode, 12) #Manual mode enabled
                    manual_mode = True
                    
                #while manual mode button is not pressed, arm state is set to 4 to disable arm motion
                code_mm,value_mm = self.digital_read(self.__manual_mode)
                if code_mm == 0 and value_mm == 1 and not paused:
                    self.__arm.set_state(4)
                    paused = True
                elif code_mm == 0 and value_mm == 0 and paused:
                    paused = False

                #Reading of the open button from the pad
                code_op, value_op = self.digital_read(self.__gripper_open_pin) 
                if code_op == 0 and value_op == 0: #If it is on and not previously pressed, we activate the corresponding pin
                    if not is_open:
                        code_op = self.gripper_action(self.__gripper_pin,0)
                        if code_op == 0:
                            self.change_payload("empty") #payload changes according to the gripper state
                            is_open = True
                            is_closed = False

                #Reading of the close buttom from the pad
                code_cl, value_cl = self.digital_read(self.__gripper_close_pin) 
                if code_cl == 0 and value_cl == 0: #If it is on and not previously pressed, we activate the corresponding pin
                    if not is_closed:
                        code_cl = self.gripper_action(self.__gripper_pin,1) 
                        if code_cl == 0:
                            self.change_payload("full") #payload changes according to the gripper state
                            is_closed = True
                            is_open = False

                #If central position, it is not closed nor open
                if code_cl == 0 and code_op == 0 and value_cl == 1 and value_op == 1:
                    is_closed = False
                    is_open = False

            elif code_es == 0 and value_es == 1: #Emergency stop is not pressed
                 
                self.es_is_pressed = False
                
                if manual_mode: #Manual mode disabled if previously enabled
                    self.__arm.set_cgpio_digital_input_function(self.__manual_mode, 0) #Manual mode disabled
                    manual_mode = False

                if not enabled: #Robot enabled if disabled previously
                    self.__arm.set_cgpio_digital_input_function(self.__emergency_stop, 1) #emergency stop recovers its functioning
                    self.enable_robot() #Enable robot just in case there was any previous errors
                    enabled = True
                
    def speed_set(self, speed_value: float):
        if not self.__params['quit']: #If arm is not stopped, updates arm parameters
            self.__params['speed'] = speed_value
            self.__sr.params["Linear Speed"] = speed_value
            self.__params['angle_speed'] = self.__sr.config["Robot_arm"]["Angle_speed"]
            self.__params['angle_acc'] = 1145

    def digital_read(self, digital_pin_to_read: int):
        #Function which receives the digitial pin port as a n interger and returns the read value, 0 or 1.
        return self.__arm.get_cgpio_digital(digital_pin_to_read) #Error code is also necessary

    def digital_write(self,digital_pin_to_write: int, value:int): #Write input value (0 or 1) in desired pin
        return self.__arm.set_cgpio_digital(digital_pin_to_write,value) #Only returns error code

    def read_state(self): #Read current arm state
        return self.__arm.get_state()[1] #Only returns state value, not error code
    
    def change_payload(self,load_type): #Changes paylaod according to the input string
        #weight in kg and cdm in mm
        payload = [0, 0,0,0] #Initially 0

        if load_type == "full":
            payload = self.__sr.config["Robot_arm"]["Full_payload"]
        else:
            payload = self.__sr.config["Robot_arm"]["Empty_payload"]

        self.__sr.params["Payload"] = payload #Update status register parameter for interface

        return self.__arm.set_tcp_load(payload[0],payload[1:4]) #Return error code
    
    def digital_read_tool(self,pin:int):
        return self.__arm.get_tgpio_digital(pin)

    def gripper_action(self,digital_pin:int,value:int): #activates or deactivates the end effector gripper
        #End Effector  logic is the opposite to the controller one
        timeout = float(self.__sr.config["Robot_arm"]["Gripper_timeout"]) #Timeout in seconds
        error_msg = [] #Error message. Initially a blank list

        if value == 1: #If selected value is  1, we want to close the gripper
            pin = self.__gripper_close
            error_msg = "Error cerrando gripper"

        elif value == 0: #If value is 0, we want to open it
            pin = self.__gripper_open
            error_msg = "Error abriendo gripper"

        code = self.digital_write(digital_pin,value) #Set controller output value
        
        time0 = time.time() #Get current time
        while time.time() - time0 <= timeout: #Reading corresponding sensor within a time limit
            code,value_g = self.__arm.get_tgpio_digital(pin)
            if value_g == 1 or code != 0: #If sensor read is correct or error, break the loop
                break;

        if code !=0 or value_g == 0: #If value is wrong or error, print
            code = 1
            print("\n"+error_msg)
            self.__sr.logger.write("\n"+error_msg)
        else:
            pass
        
        return code

    def move_to_XYZ_list(self, coords: list, radio = -1.0, esperar = False):
                    # Units: x, y, z = mm, actitud_ = rad.
        def __pprint(*args, **kwargs):
            try:
                stack_tuple = traceback.extract_stack(limit=2)[0]
                print('[{}][{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), stack_tuple[1], ' '.join(map(str, args))))
                self.__sr.logger.write('[{}][{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), stack_tuple[1], ' '.join(map(str, args))))
            except:
                print(*args, **kwargs)
                self.__sr.logger.write(*args, **kwargs)
        code = 0
        if self.__arm.error_code == 0 and not self.__params['quit']: #If motion is possible, this is no error nor quit
            #Cartesian motion
            code1 = self.__arm.set_position(*coords, speed=self.__params['speed'], mvacc=self.__params['acc'], radius=radio, wait=esperar)
            code = self.__arm.error_code #Stores controller error
            if code != 0 or code1 != 0 or self.es_is_pressed: #If error, motion disabled
                code = 1
                self.__params['quit'] = True
                __pprint('set_servo_angle, code={}'.format(code))
        else:
            code = 1
        return code

    def move_arms_list(self, arms_status, radio = -1.0, esperar = False): 
                    # Unit: degrees (º)
        def __pprint(*args, **kwargs):
            try:
                stack_tuple = traceback.extract_stack(limit=2)[0]
                print('[{}][{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), stack_tuple[1], ' '.join(map(str, args))))
                self.__sr.logger.write('[{}][{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), stack_tuple[1], ' '.join(map(str, args))))
            except:
                print(*args, **kwargs)
                self.__sr.logger.write(*args, **kwargs)
        
        code = 0
        if self.__arm.error_code == 0 and not self.__params['quit']: #If motion is possible, this is no error nor quit
            #Joint motion
            code1 = self.__arm.set_servo_angle(angle=[arms_status[0], arms_status[1], arms_status[2], arms_status[3], arms_status[4], arms_status[5]], speed=self.__params['speed'], mvacc=self.__params['angle_acc'], radius=radio, wait=esperar)
            if not esperar: #If wait is false, we use the wait method to wait manually, which allows a smoother trajectory
                code1 = self.wait_func(arms_status)
            code = self.__arm.error_code #Stores controller error
            if code != 0 or code1 != 0 or self.es_is_pressed: #If error, motion disabled
                code = 1
                self.__params['quit'] = True
                __pprint('set_servo_angle, code={}'.format(code))
        else:
            code = 1
        return code

    def get_xyz_pos(self):
        code, pos = self.__arm.get_position(is_radian = False) #Get cartesian position
        return code, pos

    def get_joint_pos(self):
        code, pos = self.__arm.get_servo_angle(is_radian = False) #Get joints values
        return code,pos

    def move_upwards(self):
        code = 0 #Error initially zero
        code, current_pos = self.__arm.get_position(is_radian = False) #Get current position
        if current_pos[2]<=330.0 and code == 0: #If Z is below 330 mm and no error
            current_pos[2] = 390.0 #New Z is set to 400 mm
            print("\nMoving in XYZ")
            self.__sr.logger.write("\nMoving in XYZ")
            code = self.move_to_XYZ_list(current_pos[0:3]) #Linear motion with same roll, pitch, yaw and new Z
        else:
            pass #Otherwise we do not set a new position
        return code

    def wait_func(self, destination:list):
        #Method to block the flow to avoid using wait=true for motion functions
        diff_l = [721,721,721,721,721,721] #joint range is +-360º, so we ensure it is out of range

        code, current_pos = self.__arm.get_servo_angle(is_radian=False) #Get current joint values

        while max(diff_l) >= self.__threshold and not self.__sr.Quit and not self.es_is_pressed: #Comparison of threshold and highest value difference
            if code != 0 or self.__arm.error_code != 0: #If error, break the loop
                break;
            for i in range(6): #Calculation of the difference in every iteration
                diff_l[i] = abs(destination[i] - current_pos[i])
            code, current_pos = self.__arm.get_servo_angle(is_radian=False)
            
        return code

    def enable_robot(self):
        #Calls enable button methods
        self.__arm.clean_warn()
        self.__arm.clean_error()
        self.__arm.motion_enable(True)
        self.__arm.set_mode(0)
        self.__arm.set_state(0)
        self.__params['quit'] = False #quit is set to false to allow motion again

    def read_controller_error(self):
        return self.__arm.error_code #Read error parameter and return

    def set_arm_sensitivity(self,value:int):
        code = self.__arm.set_collision_sensitivity(value)
        return code
    
    def robot_conn_status(self):
        return self.__arm.connected
    # -------------------------------------------------------------------------------------------------------------------------
