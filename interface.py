from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from PIL import Image, ImageTk
import webbrowser
from shared_resource import Shared_Resource
import json
import os
from tkinter.scrolledtext import ScrolledText
import sys
from functools import partial
import pathlib


class Console(ScrolledText):
    def __init__(self, *args, **kwargs):
        kwargs.update({"state": "disabled"})
        ScrolledText.__init__(self, *args, **kwargs)
        #self.bind("<Destroy>", self.reset)
        #self.redirect_logging()
        self.old_stdout = sys.stdout
    
    def delete(self, *args, **kwargs):
        self.config(state="normal")
        self.delete(*args, **kwargs)
        self.config(state="disabled")
    
    def write(self, content):
        try:
            self.configure(state="normal")  # make field editable
            self.insert("end", content)  # write text to textbox
            self.see("end")  # scroll to end
            self.configure(state="disabled")  # make field readonly
        except:
            pass
        
    def redirect_logging(self):
        sys.stdout = self
        sys.stderr = self
        
    def reset(self):
        sys.stdout = self.old_stdout

    def flush(self):  # needed for file like object
        pass

class test_bench_gui():

    def __init__(self, sr:Shared_Resource, master:Tk):
        self.root=master
        self.sr=sr
        ####Variables####

        ##Status tab##
        #Parameters
        self.current_lspeed      = DoubleVar(value=self.sr.params["Linear Speed"]) #linear speed
        self.current_aspeed      = DoubleVar(value=self.sr.config["Robot_arm"]["Angle_speed"]) #angle speed
        self.current_payload     = StringVar(value=str(self.sr.params["Payload"]))
        self.arm_mode            = IntVar(value=self.sr.params["Arm Mode"])
        self.robot_error         = IntVar(value=self.sr.params["Robot Error"])
        self.current_step        = StringVar(value=self.sr.params["Current Step"])
        self.joint_pos           = StringVar(value=str(self.sr.params["Joint Position"]))
        self.cart_pos            = StringVar(value=str(self.sr.params["Cartesian Position"]))
        self.mspm_conn           = BooleanVar(value=self.sr.params["MSPM Connected"])
        #Registers
        self.status_register     = StringVar(value=str(bin(self.sr.get_SR().get_value())[2:].zfill(16)))
        self.error_register      = StringVar(value=str(bin(self.sr.get_ER().get_value())[2:].zfill(8)))


        #Timeouts
        self.alarm_length        = DoubleVar(value=self.sr.config["Robot_controller"]["Alarm_length"])
        self.read_in_interval    = DoubleVar(value=self.sr.config["Robot_controller"]["Read_in_interval"])
        self.close_timeout       = DoubleVar(value=self.sr.config["Robot_controller"]["Close_timeout"])
        self.check_close_timeout = DoubleVar(value=self.sr.config["Robot_controller"]["Close_timeout_check"])
        self.status_open_timeout = DoubleVar(value=self.sr.config["Robot_controller"]["Status_open_to"])
        self.gripper_timeout     = DoubleVar(value=self.sr.config["Robot_arm"]["Gripper_timeout"])

        ##Config tab##
        self.home_speed      = DoubleVar(value=self.sr.config["Robot_controller"]["Home_linear_speed"])
        self.in_slow_speed   = DoubleVar(value=self.sr.config["Robot_controller"]["Slow_linear_speed"])
        self.in_fast_speed   = DoubleVar(value=self.sr.config["Robot_controller"]["Fast_linear_speed"])
        self.in_aspeed       = DoubleVar(value=self.sr.config["Robot_arm"]["Angle_speed"])
        self.in_alarm_length = DoubleVar(value=self.sr.config["Robot_controller"]["Alarm_length"])
        self.in_read_in      = DoubleVar(value=self.sr.config["Robot_controller"]["Read_in_interval"])
        self.in_close_to     = DoubleVar(value=self.sr.config["Robot_controller"]["Close_timeout"])
        self.in_close_check  = DoubleVar(value=self.sr.config["Robot_controller"]["Close_timeout_check"])
        self.in_status_open  = DoubleVar(value=self.sr.config["Robot_controller"]["Status_open_to"])
        self.in_emp_payload  = StringVar(value=str(self.sr.config["Robot_arm"]["Empty_payload"]))
        self.in_full_payload = StringVar(value=str(self.sr.config["Robot_arm"]["Full_payload"]))
        self.in_gripper_to   = DoubleVar(value=self.sr.config["Robot_arm"]["Gripper_timeout"])


        #Homes
        self.home_var           = StringVar(value=str(self.sr.config["Points"]["Home"]))
        self.in_home_var        = StringVar(value=str(self.sr.config["Points"]["Home"]))

        self.home_in_hp_var     = StringVar(value=str(self.sr.config["Points"]["HomeInHiPot"]))
        self.in_home_in_hp_var  = StringVar(value=str(self.sr.config["Points"]["HomeInHiPot"]))

        self.home_hp_lcr_var    = StringVar(value=str(self.sr.config["Points"]["HomeHiPotLCR"]))
        self.in_home_hp_lcr_var = StringVar(value=str(self.sr.config["Points"]["HomeHiPotLCR"]))

        self.home_lcr_pt_var    = StringVar(value=str(self.sr.config["Points"]["HomeLCRPowTow"]))
        self.in_home_lcr_pt_var = StringVar(value=str(self.sr.config["Points"]["HomeLCRPowTow"]))

        self.home_pt_ok_var     = StringVar(value=str(self.sr.config["Points"]["HomePowTowOKparts"]))
        self.in_home_pt_ok_var  = StringVar(value=str(self.sr.config["Points"]["HomePowTowOKparts"]))

        self.home_hp_ng_var     = StringVar(value=str(self.sr.config["Points"]["HomeHiPotNoGood"]))
        self.in_home_hp_ng_var  = StringVar(value=str(self.sr.config["Points"]["HomeHiPotNoGood"]))

        self.home_lcr_ng_var    = StringVar(value=str(self.sr.config["Points"]["HomeLCRNoGood"]))
        self.in_home_lcr_ng_var = StringVar(value=str(self.sr.config["Points"]["HomeLCRNoGood"]))

        self.home_pt_ng_var     = StringVar(value=str(self.sr.config["Points"]["HomePowTowNoGood"]))
        self.in_home_pt_ng_var  = StringVar(value=str(self.sr.config["Points"]["HomePowTowNoGood"]))

        #In Station
        self.in_piu_var = StringVar(value=str(self.sr.config["Points"]["In"]["PiU"]))
        self.in_in_piu_var = StringVar(value=str(self.sr.config["Points"]["In"]["PiU"]))

        self.in_prepi_var = StringVar(value=str(self.sr.config["Points"]["In"]["PrePi"]))
        self.in_in_prepi_var = StringVar(value=str(self.sr.config["Points"]["In"]["PrePi"]))

        self.in_pi_var = StringVar(value=str(self.sr.config["Points"]["In"]["Pi"]))
        self.in_in_pi_var = StringVar(value=str(self.sr.config["Points"]["In"]["Pi"]))

        #HiPot Station
        self.hp_piu_var = StringVar(value=str(self.sr.config["Points"]["HiPot"]["PiU"]))
        self.in_hp_piu_var = StringVar(value=str(self.sr.config["Points"]["HiPot"]["PiU"]))

        self.hp_preprepi_var = StringVar(value=str(self.sr.config["Points"]["HiPot"]["PrePrePi"]))
        self.in_hp_preprepi_var = StringVar(value=str(self.sr.config["Points"]["HiPot"]["PrePrePi"]))

        self.hp_prepi_var = StringVar(value=str(self.sr.config["Points"]["HiPot"]["PrePi"]))
        self.in_hp_prepi_var = StringVar(value=str(self.sr.config["Points"]["HiPot"]["PrePi"]))

        self.hp_pi_var = StringVar(value=str(self.sr.config["Points"]["HiPot"]["Pi"]))
        self.in_hp_pi_var = StringVar(value=str(self.sr.config["Points"]["HiPot"]["Pi"]))

        self.hp_pl_var = StringVar(value=str(self.sr.config["Points"]["HiPot"]["Pl"]))
        self.in_hp_pl_var = StringVar(value=str(self.sr.config["Points"]["HiPot"]["Pl"]))

        #LCR Station
        self.lcr_piu_var = StringVar(value=str(self.sr.config["Points"]["LCR"]["PiU"]))
        self.in_lcr_piu_var = StringVar(value=str(self.sr.config["Points"]["LCR"]["PiU"]))

        self.lcr_preprepi_var = StringVar(value=str(self.sr.config["Points"]["LCR"]["PrePrePi"]))
        self.in_lcr_preprepi_var = StringVar(value=str(self.sr.config["Points"]["LCR"]["PrePrePi"]))

        self.lcr_prepi_var = StringVar(value=str(self.sr.config["Points"]["LCR"]["PrePi"]))
        self.in_lcr_prepi_var = StringVar(value=str(self.sr.config["Points"]["LCR"]["PrePi"]))

        self.lcr_pi_var = StringVar(value=str(self.sr.config["Points"]["LCR"]["Pi"]))
        self.in_lcr_pi_var = StringVar(value=str(self.sr.config["Points"]["LCR"]["Pi"]))

        self.lcr_pl_var = StringVar(value=str(self.sr.config["Points"]["LCR"]["Pl"]))
        self.in_lcr_pl_var = StringVar(value=str(self.sr.config["Points"]["LCR"]["Pl"]))

        #PowTow Station
        self.pt_piu_var = StringVar(value=str(self.sr.config["Points"]["PowTow"]["PiU"]))
        self.in_pt_piu_var = StringVar(value=str(self.sr.config["Points"]["PowTow"]["PiU"]))

        self.pt_preprepi_var = StringVar(value=str(self.sr.config["Points"]["PowTow"]["PrePrePi"]))
        self.in_pt_preprepi_var = StringVar(value=str(self.sr.config["Points"]["PowTow"]["PrePrePi"]))

        self.pt_prepi_var = StringVar(value=str(self.sr.config["Points"]["PowTow"]["PrePi"]))
        self.in_pt_prepi_var = StringVar(value=str(self.sr.config["Points"]["PowTow"]["PrePi"]))

        self.pt_pi_var = StringVar(value=str(self.sr.config["Points"]["PowTow"]["Pi"]))
        self.in_pt_pi_var = StringVar(value=str(self.sr.config["Points"]["PowTow"]["Pi"]))

        self.pt_pl_var = StringVar(value=str(self.sr.config["Points"]["PowTow"]["Pl"]))
        self.in_pt_pl_var = StringVar(value=str(self.sr.config["Points"]["PowTow"]["Pl"]))

        #NoGood Station
        self.ng_piu_var = StringVar(value=str(self.sr.config["Points"]["NoGood"]["PiU"]))
        self.in_ng_piu_var = StringVar(value=str(self.sr.config["Points"]["NoGood"]["PiU"]))

        self.ng_prepi_var = StringVar(value=str(self.sr.config["Points"]["NoGood"]["PrePi"]))
        self.in_ng_prepi_var = StringVar(value=str(self.sr.config["Points"]["NoGood"]["PrePi"]))

        self.ng_pl_var = StringVar(value=str(self.sr.config["Points"]["NoGood"]["Pl"]))
        self.in_ng_pl_var = StringVar(value=str(self.sr.config["Points"]["NoGood"]["Pl"]))

        #OkParts Station
        self.ok_piu_var = StringVar(value=str(self.sr.config["Points"]["OKparts"]["PiU"]))
        self.in_ok_piu_var = StringVar(value=str(self.sr.config["Points"]["OKparts"]["PiU"]))

        self.ok_prepi_var = StringVar(value=str(self.sr.config["Points"]["OKparts"]["PrePi"]))
        self.in_ok_prepi_var = StringVar(value=str(self.sr.config["Points"]["OKparts"]["PrePi"]))

        self.ok_pl_var = StringVar(value=str(self.sr.config["Points"]["OKparts"]["Pl"]))
        self.in_ok_pl_var = StringVar(value=str(self.sr.config["Points"]["OKparts"]["Pl"]))

        #Connection status
        self.robot_conn = StringVar()

        #Limits reading
        self.limits, error = self.read_json("sc/conf/var_limits.txt",check="limits")

        #Methods sharing
        self.sr.updateparams = partial(self.update_parameters)
        self.sr.saveparams   = partial(self.save_params)
        self.sr.loadparams   = partial(self.load_params)
        self.sr.resetparams  = partial(self.reset_parameters)



        ####Menu####
        self.menu_bar = Menu(self.root)
        self.file_menu = Menu(self.menu_bar,tearoff=0)
        self.help_menu = Menu(self.menu_bar,tearoff=0)
        self.root.config(menu=self.menu_bar)

        #File section
        self.menu_bar.add_cascade(label="File",menu=self.file_menu)
        self.file_menu.add_command(label="Exit", command = self.exit_app)

        #Help section
        self.menu_bar.add_cascade(label = "Help", menu = self.help_menu)
        self.help_menu.add_command(label = "Open xArm Studio", command = self.open_xarm_studio)
        self.help_menu.add_command(label = "xArm Documentation", command = self.open_xarm_documentation)
        self.help_menu.add_command(label = "xARM SDK API Document", command = self.open_api_doc)
        self.help_menu.add_command(label = "xARM SDK API Code Document", command = self.open_api_code_doc)
        self.help_menu.add_command(label = "EzCAD Laser Documentation", command = self.open_ezcad_doc)
        
        ####Logo Banner####
        self.banner = Frame(self.root)
        self.banner.config(bg="light gray")
        self.banner.pack(expand=True, fill="both")
        #Logo
        logo = Image.open("sc/img/logopremo.PNG")
        logo=logo.resize((100,100))
        self.logo=ImageTk.PhotoImage(logo)
        self.logolabel = Label(self.banner,image=self.logo,bg="light gray")
        self.logolabel.photo=self.logo
        self.logolabel.grid(row=0,column=0)
        #System name
        guiname = Label(self.banner, text="Measurement System", bg="light gray",font=("Arial",20)) #Change to real name
        guiname.config(anchor="e")
        guiname.grid(row=0,column=1,ipadx=50)

        ####Tab control creation####
        self.tab_control = ttk.Notebook(self.root)

        #Tab3 creation (Configuration)
        self.tab3 = Frame(self.tab_control)
        self.tab3.config(bg="light gray", width = "400", height= "400" ,relief="raised",bd=1)
        self.tab_control.tab3 = self.tab3

        #Tab1 creation (Parameters)
        self.tab1 = Frame(self.tab_control)
        self.tab1.config(bg="light gray", width = 400, height= 350)
        self.tab_control.tab1=self.tab1

        #Tab2 creation (Configuration)
        self.tab2 = Frame(self.tab_control)
        self.tab2.config(bg="light gray", width = "400", height= "400" ,relief="raised",bd=1)
        self.tab_control.tab2 = self.tab2

        #Tab4 creation (Control)
        self.tab4 = Frame(self.tab_control)
        self.tab4.config(bg="light gray", width = "400", height= "400" ,relief="raised",bd=1)
        self.tab_control.tab4 = self.tab4

        self.root.tabcontrol = self.tab_control

        ####Tabs packing####
        self.tab_control.pack(expand = True, fill = 'both')


        ###########Tab3###########
        ####Row0####
        self.mspm_conn_label = Label(self.tab3, text = "MSPM Connected: ", bg="light gray")
        self.mspm_conn_label.grid(row=2,column=1)
        self.tab3.mspmlabel = self.mspm_conn_label #testing

        self.mspm_conn_value = Label(self.tab3, textvariable=self.mspm_conn, bg= "light gray")
        self.mspm_conn_value.grid(row = 2, column = 2)
        self.tab3.mspmvalue = self.mspm_conn_value #testing

        ####Row1####
        self.arm_mode_label = Label(self.tab3, text = "Arm Mode: ", bg="light gray")
        self.arm_mode_label.grid(row=3,column=1)
        self.tab3.armmodelabel = self.arm_mode_label #testing

        self.arm_mode_value = Label(self.tab3, textvariable=self.arm_mode, bg= "light gray")
        self.arm_mode_value.grid(row = 3, column = 2)
        self.tab3.armmodevalue = self.arm_mode_value #testing

        ####Row2####
        self.robot_error_label = Label(self.tab3, text = "Robot Error: ", bg="light gray")
        self.robot_error_label.grid(row=4,column=1)
        self.tab3.roboterrorlabel = self.robot_error_label #testing

        self.robot_error_value = Label(self.tab3, textvariable=self.robot_error, bg= "light gray")
        self.robot_error_value.grid(row = 4, column = 2)
        self.tab3.roboterrorvalue = self.robot_error_value #testing


        ####Row3####
        self.status_register_label = Label(self.tab3, text = "Status Register: ", bg="light gray")
        self.status_register_label.grid(row=5,column=1)
        self.tab3.statusreglabel = self.status_register_label #testing

        self.status_register_value = Label(self.tab3, textvariable=self.status_register, bg= "light gray")
        self.status_register_value.grid(row = 5, column = 2)
        self.tab3.statusregvalue = self.status_register_value #testing

        ####Row4####
        self.error_register_label = Label(self.tab3, text = "Error Register: ", bg="light gray")
        self.error_register_label.grid(row=6,column=1)
        self.tab3.errorreglabel = self.error_register_label #testing

        self.error_register_value = Label(self.tab3, textvariable=self.error_register, bg= "light gray")
        self.error_register_value.grid(row = 6, column = 2)
        self.tab3.errorregvalue = self.error_register_value

        ####Row5####
        self.current_step_label = Label(self.tab3, text = "Current Step: ", bg="light gray")
        self.current_step_label.grid(row=7,column=1)
        self.tab3.currsteplabel = self.current_step_label

        self.current_step_value = Label(self.tab3, textvariable=self.current_step, bg= "light gray")
        self.current_step_value.grid(row = 7, column = 2)
        self.tab3.currstepvalue = self.current_step_value

        ####Row6####
        self.joint_pos_label = Label(self.tab3, text = "Joint Position: ", bg="light gray")
        self.joint_pos_label.grid(row=8,column=1)
        self.tab3.jointposlabel = self.joint_pos_label

        self.joint_pos_value = Label(self.tab3, textvariable=self.joint_pos, bg= "light gray")
        self.joint_pos_value.grid(row = 8, column = 2)
        self.tab3.jointposvalue = self.joint_pos_value

        ####Row7####
        self.cart_pos_label = Label(self.tab3, text = "Cartesian Position: ", bg="light gray")
        self.cart_pos_label.grid(row=9,column=1)
        self.tab3.cartposlabel = self.cart_pos_label

        self.cart_pos_value = Label(self.tab3, textvariable=self.cart_pos, bg= "light gray")
        self.cart_pos_value.grid(row = 9, column = 2)
        self.tab3.cartposvalue = self.cart_pos_value

        ####Row8####
        self.log_widget = Console(self.tab3)
        self.log_widget.grid(row=10,column=0,rowspan=6,columnspan=3)
        self.sr.logger=self.log_widget
        self.tab3.log = self.log_widget

        self.tab_control.add(self.tab3,text="Robot Status")

        ###########Tab1###########
        ####Section definition####
        self.tab1_params = Frame(self.tab1)
        self.tab1_params.config(bg="light gray", width = "200", height= "200" ,relief="flat",bd = 1)
        self.tab1_params.grid(row=0,column=0,sticky='n')

        self.tab1_times = Frame(self.tab1)
        self.tab1_times.config(bg="light gray", width = "200", height= "200", relief="flat", bd=1)
        self.tab1_times.grid(row=1,column=0,sticky='n')


        ####Arm Parameters section####
        #Headers
        self.tab1_params_title = Label(self.tab1_params, text = "Arm Parameter", bg="light gray", relief="solid", bd=1)
        self.tab1_params_title.grid(row=0,column=0,ipadx=70)

        self.tab1_params_value = Label(self.tab1_params, text = "Value", bg="light gray", relief="solid", bd=1)
        self.tab1_params_value.grid(row=0,column=1,ipadx=80)

        self.tab1_params_units = Label(self.tab1_params, text = "Unit", bg="light gray", relief="solid", bd=1)
        self.tab1_params_units.grid(row=0,column=2,ipadx=110)

        #Linear speed
        self.lspeed_label = Label(self.tab1_params, text = "Linear Speed", bg="light gray")
        self.lspeed_label.grid(row=1,column=0, pady = 10)

        self.lspeed_value = Label(self.tab1_params, textvariable=self.current_lspeed, bg= "light gray")
        self.lspeed_value.grid(row = 1, column = 1)

        self.lspeed_unit = Label(self.tab1_params, text = "mm/s", bg="light gray")
        self.lspeed_unit.grid(row=1,column=2, pady = 10)

        #Angle speed
        self.aspeed_label = Label(self.tab1_params, text = "Angle Speed", bg="light gray")
        self.aspeed_label.grid(row=2,column=0, pady = 10)

        self.aspeed_value = Label(self.tab1_params, textvariable=self.current_aspeed, bg= "light gray")
        self.aspeed_value.grid(row = 2, column = 1)

        self.aspeed_unit = Label(self.tab1_params, text = "°/s", bg="light gray")
        self.aspeed_unit.grid(row=2,column=2, pady = 10)

        #Payload
        self.payload_label = Label(self.tab1_params, text = "Payload", bg="light gray")
        self.payload_label.grid(row=3,column=0, pady = 10)

        self.payload_value = Label(self.tab1_params, textvariable=self.current_payload, bg= "light gray")
        self.payload_value.grid(row = 3, column = 1)

        self.payload_unit = Label(self.tab1_params, text = "[weight(kg), x(mm), y(mm), z(mm)]", bg="light gray")
        self.payload_unit.grid(row=3,column=2, pady = 10)


        ####System times section####
        #Headers
        self.tab1_times_title = Label(self.tab1_times, text = "System Times", bg="light gray", relief="solid", bd=1)
        self.tab1_times_title.grid(row=0,column=0,ipadx=124)

        self.tab1_times_value = Label(self.tab1_times, text = "Value (seconds)", bg="light gray",relief="solid", bd=1)
        self.tab1_times_value.grid(row=0,column=1,ipadx=124)


        #Alarm Length
        self.alength_label = Label(self.tab1_times, text = "Alarm Length", bg="light gray")
        self.alength_label.grid(row=1,column=0, pady = 10)

        self.alength_value = Label(self.tab1_times, textvariable=self.alarm_length, bg= "light gray")
        self.alength_value.grid(row = 1, column = 1)

        #Read In Interval
        self.readin_label = Label(self.tab1_times, text = "Read In Interval", bg="light gray")
        self.readin_label.grid(row=2,column=0, pady = 10)

        self.readin_value = Label(self.tab1_times, textvariable=self.read_in_interval, bg= "light gray")
        self.readin_value.grid(row = 2, column = 1)

        #Close Jig Timeout
        self.close_to_label = Label(self.tab1_times, text = "Close Jig Timeout", bg="light gray")
        self.close_to_label.grid(row=3,column=0,pady=10)

        self.close_to_value = Label(self.tab1_times, textvariable=self.close_timeout,bg="light gray")
        self.close_to_value.grid(row=3,column=1,pady=10)

        #Check Close Timeout
        self.check_close_label = Label(self.tab1_times, text = "Check Close Timeout", bg="light gray")
        self.check_close_label.grid(row=4,column=0,pady=10)

        self.check_close_to_value = Label(self.tab1_times, textvariable=self.check_close_timeout,bg="light gray")
        self.check_close_to_value.grid(row=4,column=1,pady=10)

        #Status Open Timeout
        self.status_open_to_label = Label(self.tab1_times, text = "Status Open Timeout", bg="light gray")
        self.status_open_to_label.grid(row=5,column=0,pady=10)

        self.status_open_to_value = Label(self.tab1_times, textvariable=self.status_open_timeout,bg="light gray")
        self.status_open_to_value.grid(row=5,column=1,pady=10)

        #Gripper timeout
        self.gripper_timeout_label = Label(self.tab1_times, text= "Gripper Timeout", bg="light gray")
        self.gripper_timeout_label.grid(row=6,column=0,pady=10)

        self.gripper_timeout_value = Label(self.tab1_times, textvariable=self.gripper_timeout,bg="light gray")
        self.gripper_timeout_value.grid(row=6,column=1,pady=10)

        self.tab_control.add(self.tab1,text="Parameters")

        ###########Tab2###########
        ####Header names####
        self.params_label = Label(self.tab2,text="Parameter")
        self.params_label.grid(row=0,column=0, ipadx = 70)
        self.params_label.config(bg="light gray",fg="black", relief = "solid", bd=1)
        self.tab2.paramslabel = self.params_label

        self.newvalue_label = Label(self.tab2,text="New Value")
        self.newvalue_label.grid(row=0,column=1, ipadx = 80)
        self.newvalue_label.config(bg="light gray",fg="black", relief = "solid", bd=1)
        self.tab2.newvaluelabel = self.newvalue_label

        self.units_label = Label(self.tab2,text="Unit")
        self.units_label.grid(row=0,column=2, ipadx = 110)
        self.units_label.config(bg="light gray",fg="black", relief = "solid", bd=1)
        self.tab2.unitlabels = self.units_label

        ####Home speed####
        #Param name
        self.hs_label = Label(self.tab2,text="Home Speed", bg="light gray")
        self.hs_label.grid(row=1,column=0)
        self.tab2.hslabel = self.hs_label
        #Desired value
        self.hs_input = Entry(self.tab2,width=10,textvariable=self.home_speed)
        self.hs_input.grid(row=1,column=1,pady = 10)
        self.hs_input.config(justify = "center")
        self.tab2.hsinput = self.hs_input
        #Unit
        self.hs_unit = Label(self.tab2,text="mm/s",bg="light gray")
        self.hs_unit.grid(row=1,column=2)
        self.tab2.hsunit = self.hs_unit

        ####Low speed####
        #Param name
        self.ss_label = Label(self.tab2,text="Slow speed")
        self.ss_label.grid(row=2,column=0)
        self.ss_label.config(bg="light gray",fg="black",pady = 10)
        self.tab2.sslabel = self.ss_label
        #Desired input
        self.ss_input = Entry(self.tab2,width=10,textvariable=self.in_slow_speed)
        self.ss_input.grid(row=2,column=1,pady = 10)
        self.ss_input.config(justify = "center")
        self.tab2.ssinput = self.ss_input
        #Unit
        self.ss_unit = Label(self.tab2,text="mm/s",bg="light gray")
        self.ss_unit.grid(row=2,column=2)
        self.tab2.ssunit = self.ss_unit

        ####Fast Speed####
        #Param name
        self.fs_label = Label(self.tab2,text="Fast speed")
        self.fs_label.grid(row=3,column=0)
        self.fs_label.config(bg="light gray",fg="black",pady = 10)
        self.tab2.fslabel = self.fs_label
        #Desired input
        self.fs_input = Entry(self.tab2,width=10,textvariable=self.in_fast_speed)
        self.fs_input.grid(row=3,column=1,pady = 10)
        self.fs_input.config(justify = "center")
        self.tab2.fsinput = self.fs_input
        #Unit
        self.fs_unit = Label(self.tab2,text="mm/s",bg="light gray")
        self.fs_unit.grid(row=3,column=2)
        self.tab2.fsunit = self.fs_unit

        ####Angle speed####
        #Param name
        self.as_label = Label(self.tab2,text="Angle Speed")
        self.as_label.grid(row=4,column=0)
        self.as_label.config(bg="light gray",fg="black",pady = 10)
        self.tab2.aslabel = self.as_label
        #desired value
        self.as_input = Entry(self.tab2,width=10,textvariable=self.in_aspeed)
        self.as_input.grid(row=4,column=1,pady = 10)
        self.as_input.config(justify = "center")
        self.tab2.asinput = self.as_input
        #Unit
        self.as_unit = Label(self.tab2,text="°/s",bg="light gray")
        self.as_unit.grid(row=4,column=2)
        self.tab2.asunit = self.as_unit

        ####Alarm length####
        #Param name
        self.al_label = Label(self.tab2,text="Alarm Length")
        self.al_label.grid(row=5,column=0)
        self.al_label.config(bg="light gray",fg="black",pady = 10)
        self.tab2.allabel = self.al_label
        #Desired value
        self.al_input = Entry(self.tab2,width=10,textvariable=self.in_alarm_length)
        self.al_input.grid(row=5,column=1,pady = 10)
        self.al_input.config(justify = "center")
        self.tab2.alinput = self.al_input
        #Unit
        self.al_unit = Label(self.tab2,text="seconds",bg="light gray")
        self.al_unit.grid(row=5,column=2)
        self.tab2.alunit = self.al_unit

        ####Read in interval####
        #Param name
        self.ri_label = Label(self.tab2,text="Read In Interval")
        self.ri_label.grid(row=6,column=0)
        self.ri_label.config(bg="light gray",fg="black",pady = 10)
        self.tab2.rilabel = self.ri_label
        #Desired value
        self.ri_input = Entry(self.tab2,width=10,textvariable=self.in_read_in)
        self.ri_input.grid(row=6,column=1,pady = 10)
        self.ri_input.config(justify = "center")
        self.tab2.riinput = self.ri_input
        #Unit
        self.ri_unit = Label(self.tab2,text="seconds",bg="light gray")
        self.ri_unit.grid(row=6,column=2)
        self.tab2.riunit = self.ri_unit

        ####Close Jig timeout####
        #Param name
        self.cljig_label = Label(self.tab2,text="Close Jig Timeout")
        self.cljig_label.grid(row=7,column=0)
        self.cljig_label.config(bg="light gray",fg="black",pady = 10)
        self.tab2.cljijlabel = self.cljig_label
        #Desired value
        self.cljig_input = Entry(self.tab2,width=10,textvariable=self.in_close_to)
        self.cljig_input.grid(row=7,column=1,pady = 10)
        self.cljig_input.config(justify = "center")
        self.tab2.cljijinput = self.cljig_input
        #Unit
        self.cljig_unit = Label(self.tab2,text="seconds",bg="light gray")
        self.cljig_unit.grid(row=7,column=2)
        self.tab2.cljijunit = self.cljig_unit

        ####Check close timeout####
        #Param name
        self.checkcl_label = Label(self.tab2, text="Check Close Timeout")
        self.checkcl_label.grid(row=8,column=0)
        self.checkcl_label.config(bg="light gray",fg="black",pady = 10)
        self.tab2.checkcllabel = self.checkcl_label
        #Desired value
        self.checkcl_input = Entry(self.tab2,width=10,textvariable=self.in_close_check)
        self.checkcl_input.grid(row=8,column=1,pady = 10)
        self.checkcl_input.config(justify = "center")
        self.tab2.checkclinput = self.checkcl_input
        #Unit
        self.checkcl_unit = Label(self.tab2,text="seconds",bg="light gray")
        self.checkcl_unit.grid(row=8,column=2)
        self.tab2.checkclunit = self.checkcl_unit

        ####Status open timeout####
        #Param name
        self.sto_label = Label(self.tab2, text="Status Open Timeout")
        self.sto_label.grid(row=9,column=0)
        self.sto_label.config(bg="light gray",fg="black",pady = 10)
        self.tab2.stolabel = self.sto_label
        #Desired value
        self.sto_input = Entry(self.tab2,width=10,textvariable=self.in_status_open)
        self.sto_input.grid(row=9,column=1,pady = 10)
        self.sto_input.config(justify = "center")
        self.tab2.stoinput = self.sto_input
        #Unit
        self.sto_unit = Label(self.tab2,text="seconds",bg="light gray")
        self.sto_unit.grid(row=9,column=2)
        self.tab2.stounit = self.sto_unit

        ####Gripper Timeout####
        #Param name
        self.gripper_to_label = Label(self.tab2, text="Gripper Timeout")
        self.gripper_to_label.grid(row=10,column=0)
        self.gripper_to_label.config(bg="light gray",fg="black",pady = 10)
        self.tab2.grippertolabel = self.gripper_to_label
        #Desired value
        self.gripper_to_input = Entry(self.tab2,width=10,textvariable=self.in_gripper_to)
        self.gripper_to_input.grid(row=10,column=1,pady = 10)
        self.gripper_to_input.config(justify = "center")
        self.tab2.grippertoinput = self.gripper_to_input
        #Unit
        self.gripper_to_unit = Label(self.tab2,text="seconds",bg="light gray")
        self.gripper_to_unit.grid(row=10,column=2)
        self.tab2.grippertounit = self.gripper_to_unit

        ####Empty Payload####
        #Param name
        self.emp_p_label = Label(self.tab2, text="Empty Payload")
        self.emp_p_label.grid(row=11,column=0)
        self.emp_p_label.config(bg="light gray",fg="black",pady = 10)
        self.tab2.emplabel = self.emp_p_label
        #Desired value
        self.emp_p_input = Entry(self.tab2,width=25,textvariable=self.in_emp_payload)
        self.emp_p_input.grid(row=11,column=1,pady = 10)
        self.emp_p_input.config(justify = "center")
        self.tab2.empinput = self.emp_p_input
        #Unit
        self.emp_p_unit = Label(self.tab2,text="[weight(kg), x(mm), y(mm), z(mm)]",bg="light gray")
        self.emp_p_unit.grid(row=11,column=2)
        self.tab2.empunit = self.emp_p_unit

        ####Full payload####
        #Param name
        self.full_p_label = Label(self.tab2, text="Full Payload")
        self.full_p_label.grid(row=12,column=0)
        self.full_p_label.config(bg="light gray",fg="black",pady = 10)
        self.tab2.fullplabel = self.full_p_label
        #Desired value
        self.full_p_input = Entry(self.tab2,width=25,textvariable=self.in_full_payload)
        self.full_p_input.grid(row=12,column=1,pady = 10)
        self.full_p_input.config(justify = "center")
        self.tab2.fullpinput = self.full_p_input
        #Unit
        self.fullp_unit = Label(self.tab2,text="[weight(kg), x(mm), y(mm), z(mm)]",bg="light gray")
        self.fullp_unit.grid(row=12,column=2)
        self.tab2.fullpunit = self.full_p_input

        ####Buttons####
        #Update Button
        self.update_btn = Button(self.tab2, text="Update Parameters", command =self.update_parameters, bg = "light gray",bd=1, width=14)
        self.update_btn.grid(row = 13, column = 0)
        self.tab2.updatebtn = self.update_btn
        #Reset button
        self.reset_btn = Button(self.tab2, text="Reset Parameters", bg = "light gray",command = self.reset_parameters,bd=1,width=20)
        self.reset_btn.grid(row = 13, column = 1)
        self.tab2.resetbtn = self.reset_btn
        #Save params Button
        self.savep_btn = Button(self.tab2, text="Save Parameters", command =self.save_params, bg = "light gray",bd=1,width=14)
        self.savep_btn.grid(row = 14, column = 0)
        self.tab2.savepbtn = self.savep_btn
        #Load last params Button
        self.load_btn = Button(self.tab2, text="Load Last Parameters", command =self.load_params, bg = "light gray",bd=1,width=20)
        self.load_btn.grid(row = 14, column = 1)
        self.tab2.loadbtn = self.load_btn
        #Edit positions button
        self.editpos_btn = Button(self.tab2, text="Edit Positions", bg = "light gray",command = self.edit_pos,bd=1, height=3)
        self.editpos_btn.grid(row = 13, column = 2,rowspan=2)
        self.tab2.editposbtn = self.editpos_btn

        self.tab_control.add(self.tab2,text="Configuration")

        ####Tab4####
        #Open LCR
        self.openlcr_btn = Button(self.tab4, text="Open LCR Jig", command=self.sr.openlcr, bg="light gray", bd=1, width=14)
        self.openlcr_btn.pack()#grid(row=0, column=0)
        self.openlcr_btn.place(x=330, y=200,anchor="center")
        self.tab2.openlcrbtn = self.openlcr_btn

        #Close LCR
        self.closelcr_btn = Button(self.tab4, text="Close LCR Jig", command=self.sr.closelcr, bg="light gray", bd=1, width=14)
        self.closelcr_btn.pack()#.grid(row=1, column=0)
        self.closelcr_btn.place(x=330, y=250,anchor="center")
        self.tab2.closelcrbtn = self.closelcr_btn
        
        #Autoverification
        self.autover_btn = Button(self.tab4, text="Autoverification", command=self.sr.verify, bg="light gray", bd=1, width=14)
        self.autover_btn.pack()#.grid(row=1, column=0)
        self.autover_btn.place(x=330, y=300,anchor="center")
        self.tab2.autover = self.autover_btn
        
        #Reconnect robot
        self.robot_btn = Button(self.tab4, text="Reconnect robot", command=self.robot_ini, bg="light gray", bd=1, width=14)
        self.robot_btn.pack()#.grid(row=1, column=0)
        self.robot_btn.place(x=330, y=350,anchor="center")
        self.tab2.robot = self.robot_btn

        self.tab_control.add(self.tab4,text="Controls")

    def read_json(self, filename:str, check:str):
        js = None
        error = 0
        def __check_format(dic):
            error = 0
            try:
                ##Points verification##
                if check == "points":
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
                elif check == "params":
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
                elif check=="limits":
                    for x in dic:
                        for i in dic[x]:
                            if not isinstance(dic[x][i],(int,float)):
                                error = 1
                                break
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
                if error:
                    raise ValueError("Wrong format or values in file")
            except:
                messagebox.showerror("Fatal Error","File has incorrect values!")
                error = 1
        else:
            messagebox.showerror("Fatal Error","File is missing!")
            error = 1

        return js, error

    def params_upd(self):
        self.current_lspeed.set(self.sr.params["Linear Speed"])
        self.current_aspeed.set(self.sr.config["Robot_arm"]["Angle_speed"])
        self.current_payload.set(str(self.sr.params["Payload"]))
        self.arm_mode.set(self.sr.params["Arm Mode"])
        self.robot_error.set(self.sr.params["Robot Error"])
        self.current_step.set(self.sr.params["Current Step"])
        self.joint_pos.set(str(self.sr.params["Joint Position"]))
        self.cart_pos.set(str(self.sr.params["Cartesian Position"]))
        self.mspm_conn.set(self.sr.params["MSPM Connected"])
        self.status_register.set(str(bin(self.sr.get_SR().get_value())[2:].zfill(16)))
        self.error_register.set(str(bin(self.sr.get_ER().get_value())[2:].zfill(8)))
        self.root.after(1000,self.params_upd)

    def str_to_list(self,string:str):
        if string[0]!="[" and string[len(string)-1] != "]":
            raise Exception("Incorrect format")
        string = string[1:len(string)-1]
        string = string.replace(",","")
        out_list=string.split()
        for i in range(len(out_list)):
                out_list[i] = float(out_list[i])
        return out_list

    def show_param_error(self):
        messagebox.showerror("Error!","Some parameters are incorrect or out of range")

    def show_warning(self):
        messagebox.showwarning("Warning","Arm in motion, changes will apply when stopped")
        
    def robot_ini(self):
        if not self.sr.params["Arm Connected"]:
            try:
                self.sr.robotini()
            except:
                messagebox.showerror("Error","Arm is not ready yet!")
        else:
            messagebox.showwarning("Warning","Arm is already connected!")

    ####Config tab methods####
    def update_parameters(self):
        error = False
        if not self.sr.inmotion:
            try:
                if self.limits["Home_linear_speed"]["Lower"]<=self.home_speed.get()<=self.limits["Home_linear_speed"]["Upper"]:
                    self.sr.config["Robot_controller"]["Home_linear_speed"]=self.home_speed.get()
                else:
                    error = True

                if self.limits["Slow_linear_speed"]["Lower"]<=self.in_slow_speed.get()<=self.limits["Slow_linear_speed"]["Upper"]:
                    self.sr.config["Robot_controller"]["Slow_linear_speed"]=self.in_slow_speed.get()
                else:
                    error = True

                if self.limits["Fast_linear_speed"]["Lower"]<=self.in_fast_speed.get()<=self.limits["Fast_linear_speed"]["Upper"]:
                    self.sr.config["Robot_controller"]["Fast_linear_speed"]=self.in_fast_speed.get()
                else:
                    error = True

                if self.limits["Angle_speed"]["Lower"]<self.in_aspeed.get()<=self.limits["Angle_speed"]["Upper"]:
                    self.sr.config["Robot_arm"]["Angle_speed"]=self.in_aspeed.get()
                else:
                    error = True

                if self.limits["Alarm_length"]["Lower"]<=self.in_alarm_length.get()<=self.limits["Alarm_length"]["Upper"]:
                    self.sr.config["Robot_controller"]["Alarm_length"]=self.in_alarm_length.get()
                    self.alarm_length.set(self.in_alarm_length.get())
                else:
                    error = True
                
                if self.limits["Read_in_interval"]["Lower"]<=self.in_read_in.get()<=self.limits["Read_in_interval"]["Upper"]:
                    self.sr.config["Robot_controller"]["Read_in_interval"]=self.in_read_in.get()
                    self.read_in_interval.set(self.in_read_in.get())
                else:
                    error = True
                
                if self.limits["Close_timeout"]["Lower"]<=self.in_close_to.get()<=self.limits["Close_timeout"]["Upper"]:
                    self.sr.config["Robot_controller"]["Close_timeout"]=self.in_close_to.get()
                    self.close_timeout.set(self.in_close_to.get())
                else:
                    error = True

                if self.limits["Close_timeout_check"]["Lower"]<=self.in_close_check.get()<=self.limits["Close_timeout_check"]["Upper"]:
                    self.sr.config["Robot_controller"]["Close_timeout_check"]=self.in_close_check.get()
                    self.check_close_timeout.set(self.in_close_check.get())
                else:
                    error = True

                if self.limits["Status_open_to"]["Lower"]<=self.in_status_open.get()<=self.limits["Status_open_to"]["Upper"]:
                    self.sr.config["Robot_controller"]["Status_open_to"]=self.in_status_open.get()
                    self.status_open_timeout.set(self.in_status_open.get())
                else:
                    error = True
                
                if self.limits["Gripper_timeout"]["Lower"]<=self.in_gripper_to.get()<=self.limits["Gripper_timeout"]["Upper"]:
                    self.sr.config["Robot_arm"]["Gripper_timeout"]=self.in_gripper_to.get()
                    self.gripper_timeout.set(self.in_gripper_to.get())
                else:
                    error = True

                emp_p = self.str_to_list(self.in_emp_payload.get())
                if len(emp_p)==4 and emp_p[0]>=self.limits["Payload"]["Lower"] and emp_p[0]<=self.limits["Payload"]["Upper"]:
                    self.sr.config["Robot_arm"]["Empty_payload"]=emp_p
                else:
                    error = True

                full_p = self.str_to_list(self.in_full_payload.get())
                if len(full_p)==4 and full_p[0]>=self.limits["Payload"]["Lower"] and full_p[0]<=self.limits["Payload"]["Upper"]:
                    self.sr.config["Robot_arm"]["Full_payload"]=full_p
                else:
                    error = True
            except:
                self.show_param_error()
            self.sr.wantupdate = False
        else:
            self.show_warning()
            self.sr.wantupdate = True

        if error:
            self.show_param_error()

    def reset_parameters(self):
        if not self.sr.inmotion:
            config, error = self.read_json("sc/conf/config.txt","params")
            
            if error != 1:
                self.sr.config["Robot_controller"] = config["Robot_controller"]
                self.sr.config["Robot_arm"] = config["Robot_arm"]

                self.home_speed.set(self.sr.config["Robot_controller"]["Home_linear_speed"])

                self.in_slow_speed.set(self.sr.config["Robot_controller"]["Slow_linear_speed"])

                self.in_fast_speed.set(self.sr.config["Robot_controller"]["Fast_linear_speed"])

                self.in_aspeed.set(self.sr.config["Robot_arm"]["Angle_speed"])

                self.in_alarm_length.set(self.sr.config["Robot_controller"]["Alarm_length"])
                self.alarm_length.set(self.sr.config["Robot_controller"]["Alarm_length"])

                self.in_read_in.set(self.sr.config["Robot_controller"]["Read_in_interval"])
                self.read_in_interval.set(self.sr.config["Robot_controller"]["Read_in_interval"])

                self.in_close_to.set(self.sr.config["Robot_controller"]["Close_timeout"])
                self.close_timeout.set(self.sr.config["Robot_controller"]["Close_timeout"])


                self.in_close_check.set(self.sr.config["Robot_controller"]["Close_timeout_check"])
                self.check_close_timeout.set(self.sr.config["Robot_controller"]["Close_timeout_check"])


                self.in_status_open.set(self.sr.config["Robot_controller"]["Status_open_to"])
                self.status_open_timeout.set(self.sr.config["Robot_controller"]["Status_open_to"])

                self.in_gripper_to.set(self.sr.config["Robot_arm"]["Gripper_timeout"])
                self.gripper_timeout.set(self.sr.config["Robot_arm"]["Gripper_timeout"])

                self.in_emp_payload.set(str(self.sr.config["Robot_arm"]["Empty_payload"]))

                self.in_full_payload.set(str(self.sr.config["Robot_arm"]["Full_payload"]))

            self.sr.wantreset = False
        else:
            self.show_warning()
            self.sr.wantreset = True

    def save_params(self):
        def __update_parameters():
            error = False
            try:
                if self.limits["Home_linear_speed"]["Lower"]<=self.home_speed.get()<=self.limits["Home_linear_speed"]["Upper"]:
                    self.sr.config["Robot_controller"]["Home_linear_speed"]=self.home_speed.get()
                else:
                    error = True

                if self.limits["Slow_linear_speed"]["Lower"]<=self.in_slow_speed.get()<=self.limits["Slow_linear_speed"]["Upper"]:
                    self.sr.config["Robot_controller"]["Slow_linear_speed"]=self.in_slow_speed.get()
                else:
                    error = True

                if self.limits["Fast_linear_speed"]["Lower"]<=self.in_fast_speed.get()<=self.limits["Fast_linear_speed"]["Upper"]:
                    self.sr.config["Robot_controller"]["Fast_linear_speed"]=self.in_fast_speed.get()
                else:
                    error = True

                if self.limits["Angle_speed"]["Lower"]<self.in_aspeed.get()<=self.limits["Angle_speed"]["Upper"]:
                    self.sr.config["Robot_arm"]["Angle_speed"]=self.in_aspeed.get()
                else:
                    error = True

                if self.limits["Alarm_length"]["Lower"]<=self.in_alarm_length.get()<=self.limits["Alarm_length"]["Upper"]:
                    self.sr.config["Robot_controller"]["Alarm_length"]=self.in_alarm_length.get()
                    self.alarm_length.set(self.in_alarm_length.get())
                else:
                    error = True
                
                if self.limits["Read_in_interval"]["Lower"]<=self.in_read_in.get()<=self.limits["Read_in_interval"]["Upper"]:
                    self.sr.config["Robot_controller"]["Read_in_interval"]=self.in_read_in.get()
                    self.read_in_interval.set(self.in_read_in.get())
                else:
                    error = True
                
                if self.limits["Close_timeout"]["Lower"]<=self.in_close_to.get()<=self.limits["Close_timeout"]["Upper"]:
                    self.sr.config["Robot_controller"]["Close_timeout"]=self.in_close_to.get()
                    self.close_timeout.set(self.in_close_to.get())
                else:
                    error = True

                if self.limits["Close_timeout_check"]["Lower"]<=self.in_close_check.get()<=self.limits["Close_timeout_check"]["Upper"]:
                    self.sr.config["Robot_controller"]["Close_timeout_check"]=self.in_close_check.get()
                    self.check_close_timeout.set(self.in_close_check.get())
                else:
                    error = True

                if self.limits["Status_open_to"]["Lower"]<=self.in_status_open.get()<=self.limits["Status_open_to"]["Upper"]:
                    self.sr.config["Robot_controller"]["Status_open_to"]=self.in_status_open.get()
                    self.status_open_timeout.set(self.in_status_open.get())
                else:
                    error = True
                
                if self.limits["Gripper_timeout"]["Lower"]<=self.in_gripper_to.get()<=self.limits["Gripper_timeout"]["Upper"]:
                    self.sr.config["Robot_arm"]["Gripper_timeout"]=self.in_gripper_to.get()
                    self.gripper_timeout.set(self.in_gripper_to.get())
                else:
                    error = True

                emp_p = self.str_to_list(self.in_emp_payload.get())
                if len(emp_p)==4 and emp_p[0]>=self.limits["Payload"]["Lower"] and emp_p[0]<=self.limits["Payload"]["Upper"]:
                    self.sr.config["Robot_arm"]["Empty_payload"]=emp_p
                else:
                    error = True

                full_p = self.str_to_list(self.in_full_payload.get())
                if len(full_p)==4 and full_p[0]>=self.limits["Payload"]["Lower"] and full_p[0]<=self.limits["Payload"]["Upper"]:
                    self.sr.config["Robot_arm"]["Full_payload"]=full_p
                else:
                    error = True
            except:
                self.show_param_error()
            
            if error:
                self.show_param_error()
        
        if not self.sr.inmotion:
            __update_parameters()
            item = self.sr.config
            with open("sc/conf/last_config.txt", "w")as file:
                json.dump(fp=file, indent=4, obj=item)
            self.sr.wantsave = False
        else:
            self.show_warning()
            self.sr.wantsave = True
    
    def load_params(self):
        if not self.sr.inmotion:
            config, error = self.read_json("sc/conf/last_config.txt","params")

            if error != 1:
                self.sr.config["Robot_controller"] = config["Robot_controller"]
                self.sr.config["Robot_arm"] = config["Robot_arm"]

                self.home_speed.set(self.sr.config["Robot_controller"]["Home_linear_speed"])

                self.in_slow_speed.set(self.sr.config["Robot_controller"]["Slow_linear_speed"])

                self.in_fast_speed.set(self.sr.config["Robot_controller"]["Fast_linear_speed"])

                self.in_aspeed.set(self.sr.config["Robot_arm"]["Angle_speed"])

                self.in_alarm_length.set(self.sr.config["Robot_controller"]["Alarm_length"])
                self.alarm_length.set(self.sr.config["Robot_controller"]["Alarm_length"])

                self.in_read_in.set(self.sr.config["Robot_controller"]["Read_in_interval"])
                self.read_in_interval.set(self.sr.config["Robot_controller"]["Read_in_interval"])

                self.in_close_to.set(self.sr.config["Robot_controller"]["Close_timeout"])
                self.close_timeout.set(self.sr.config["Robot_controller"]["Close_timeout"])


                self.in_close_check.set(self.sr.config["Robot_controller"]["Close_timeout_check"])
                self.check_close_timeout.set(self.sr.config["Robot_controller"]["Close_timeout_check"])


                self.in_status_open.set(self.sr.config["Robot_controller"]["Status_open_to"])
                self.status_open_timeout.set(self.sr.config["Robot_controller"]["Status_open_to"])

                self.in_gripper_to.set(self.sr.config["Robot_arm"]["Gripper_timeout"])
                self.gripper_timeout.set(self.sr.config["Robot_arm"]["Gripper_timeout"])

                self.in_emp_payload.set(str(self.sr.config["Robot_arm"]["Empty_payload"]))

                self.in_full_payload.set(str(self.sr.config["Robot_arm"]["Full_payload"]))

            self.sr.wantload = False
        else:
            self.show_warning()
            self.sr.wantload = True

    def edit_pos(self):

        def __set_label(master:Misc, l_row, l_col ,size=None , intext=None, textvar=None,ix=0,iy=0):
            label_name = Label(master, text = intext, textvariable=textvar, bg="light gray",width=size)
            label_name.grid(row=l_row,column=l_col,ipadx=ix,ipady=iy)
            return label_name
        
        def __set_entry(master:Misc, textvar, e_row, e_col, size=25):
            entry_name = Entry(master,width=size,textvariable=textvar)
            entry_name.grid(row=e_row,column=e_col,pady = 10)
            entry_name.config(justify = "center")
            return entry_name

        def update_pos():
            if not self.sr.inmotion:
                error = False
                try:
                    home_pos = self.str_to_list(self.in_home_var.get())
                    if len(home_pos)==6 and home_pos[0]>-360 and home_pos[0]<360:
                        self.sr.config["Points"]["Home"]=home_pos
                        self.home_var.set(self.in_home_var.get())
                    else:
                        error = True
                    
                    home_in_hp_pos = self.str_to_list(self.in_home_in_hp_var.get())
                    if len(home_in_hp_pos)==6 and home_in_hp_pos[0]>-360 and home_in_hp_pos[0]<360:
                        self.sr.config["Points"]["HomeInHiPot"]=home_in_hp_pos
                        self.home_in_hp_var.set(self.in_home_in_hp_var.get())
                    else:
                        error = True
                    
                    home_hp_lcr_pos = self.str_to_list(self.in_home_hp_lcr_var.get())
                    if len(home_hp_lcr_pos)==6 and home_hp_lcr_pos[0]>-360 and home_hp_lcr_pos[0]<360:
                        self.sr.config["Points"]["HomeHiPotLCR"]=home_hp_lcr_pos
                        self.home_hp_lcr_var.set(self.in_home_hp_lcr_var.get())
                    else:
                        error = True
                    
                    home_lcr_pt_pos = self.str_to_list(self.in_home_lcr_pt_var.get())
                    if len(home_lcr_pt_pos)==6 and home_lcr_pt_pos[0]>-360 and home_lcr_pt_pos[0]<360:
                        self.sr.config["Points"]["HomeLCRPowTow"]=home_lcr_pt_pos
                        self.home_lcr_pt_var.set(self.in_home_lcr_pt_var.get())
                    else:
                        error = True
                    
                    home_pt_ok_pos = self.str_to_list(self.in_home_pt_ok_var.get())
                    if len(home_pt_ok_pos)==6 and home_pt_ok_pos[0]>-360 and home_pt_ok_pos[0]<360:
                        self.sr.config["Points"]["HomePowTowOKparts"]=home_pt_ok_pos
                        self.home_pt_ok_var.set(self.in_home_pt_ok_var.get())
                    else:
                        error = True

                    home_hp_ng_pos = self.str_to_list(self.in_home_hp_ng_var.get())
                    if len(home_hp_ng_pos)==6 and home_hp_ng_pos[0]>-360 and home_hp_ng_pos[0]<360:
                        self.sr.config["Points"]["HomeHiPotNoGood"]=home_hp_ng_pos
                        self.home_hp_ng_var.set(self.in_home_hp_ng_var.get())
                    else:
                        error = True

                    home_lcr_ng_pos = self.str_to_list(self.in_home_lcr_ng_var.get())
                    if len(home_lcr_ng_pos)==6 and home_lcr_ng_pos[0]>-360 and home_lcr_ng_pos[0]<360:
                        self.sr.config["Points"]["HomeLCRNoGood"]=home_lcr_ng_pos
                        self.home_lcr_ng_var.set(self.in_home_lcr_ng_var.get())
                    else:
                        error = True

                    home_pt_ng_pos = self.str_to_list(self.in_home_pt_ng_var.get())
                    if len(home_pt_ng_pos)==6 and home_pt_ng_pos[0]>-360 and home_pt_ng_pos[0]<360:
                        self.sr.config["Points"]["HomePowTowNoGood"]=home_pt_ng_pos
                        self.home_pt_ng_var.set(self.in_home_pt_ng_var.get())
                    else:
                        error = True

                    inpiu_pos = self.str_to_list(self.in_in_piu_var.get())
                    if len(inpiu_pos)==6 and inpiu_pos[0]>-360 and inpiu_pos[0]<360:
                        self.sr.config["Points"]["In"]["PiU"]=inpiu_pos
                        self.in_piu_var.set(self.in_in_piu_var.get())
                    else:
                        error = True

                    inprepi_pos = self.str_to_list(self.in_in_prepi_var.get())
                    if len(inprepi_pos)==6 and inprepi_pos[0]>-360 and inprepi_pos[0]<360:
                        self.sr.config["Points"]["In"]["PrePi"]=inprepi_pos
                        self.in_prepi_var.set(self.in_in_prepi_var.get())
                    else:
                        error = True

                    inpi_pos = self.str_to_list(self.in_in_pi_var.get())
                    if len(inpi_pos)==6 and inpi_pos[0]>-360 and inpi_pos[0]<360:
                        self.sr.config["Points"]["In"]["Pi"]=inpi_pos
                        self.in_pi_var.set(self.in_in_pi_var.get())
                    else:
                        error = True

                    hppiu_pos = self.str_to_list(self.in_hp_piu_var.get())
                    if len(hppiu_pos)==6 and hppiu_pos[0]>-360 and hppiu_pos[0]<360:
                        self.sr.config["Points"]["HiPot"]["PiU"]=hppiu_pos
                        self.hp_piu_var.set(self.in_hp_piu_var.get())
                    else:
                        error = True

                    hppreprepi_pos = self.str_to_list(self.in_hp_preprepi_var.get())
                    if len(hppreprepi_pos)==6 and hppreprepi_pos[0]>-360 and hppreprepi_pos[0]<360:
                        self.sr.config["Points"]["HiPot"]["PrePrePi"]=hppreprepi_pos
                        self.hp_preprepi_var.set(self.in_hp_preprepi_var.get())
                    else:
                        error = True

                    hpprepi_pos = self.str_to_list(self.in_hp_prepi_var.get())
                    if len(hpprepi_pos)==6 and hpprepi_pos[0]>-360 and hpprepi_pos[0]<360:
                        self.sr.config["Points"]["HiPot"]["PrePi"]=hpprepi_pos
                        self.hp_prepi_var.set(self.in_hp_prepi_var.get())
                    else:
                        error = True

                    hppi_pos = self.str_to_list(self.in_hp_pi_var.get())
                    if len(hppi_pos)==6 and hppi_pos[0]>-360 and hppi_pos[0]<360:
                        self.sr.config["Points"]["HiPot"]["Pi"]=hppi_pos
                        self.hp_pi_var.set(self.in_hp_pi_var.get())
                    else:
                        error = True

                    hppl_pos = self.str_to_list(self.in_hp_pl_var.get())
                    if len(hppl_pos)==6 and hppl_pos[0]>-360 and hppl_pos[0]<360:
                        self.sr.config["Points"]["HiPot"]["Pl"]=hppl_pos
                        self.hp_pl_var.set(self.in_hp_pl_var.get())
                    else:
                        error = True

                    lcrpiu_pos = self.str_to_list(self.in_lcr_piu_var.get())
                    if len(lcrpiu_pos)==6 and lcrpiu_pos[0]>-360 and lcrpiu_pos[0]<360:
                        self.sr.config["Points"]["LCR"]["PiU"]=lcrpiu_pos
                        self.lcr_piu_var.set(self.in_lcr_piu_var.get())
                    else:
                        error = True

                    lcrpreprepi_pos = self.str_to_list(self.in_lcr_preprepi_var.get())
                    if len(lcrpreprepi_pos)==6 and lcrpreprepi_pos[0]>-360 and lcrpreprepi_pos[0]<360:
                        self.sr.config["Points"]["LCR"]["PrePrePi"]=lcrpreprepi_pos
                        self.lcr_preprepi_var.set(self.in_lcr_preprepi_var.get())
                    else:
                        error = True

                    lcrprepi_pos = self.str_to_list(self.in_lcr_prepi_var.get())
                    if len(lcrprepi_pos)==6 and lcrprepi_pos[0]>-360 and lcrprepi_pos[0]<360:
                        self.sr.config["Points"]["LCR"]["PrePi"]=lcrprepi_pos
                        self.lcr_prepi_var.set(self.in_lcr_prepi_var.get())
                    else:
                        error = True
                    
                    lcrpi_pos = self.str_to_list(self.in_lcr_pi_var.get())
                    if len(lcrpi_pos)==6 and lcrpi_pos[0]>-360 and lcrpi_pos[0]<360:
                        self.sr.config["Points"]["LCR"]["Pi"]=lcrpi_pos
                        self.lcr_pi_var.set(self.in_lcr_pi_var.get())
                    else:
                        error = True
                    
                    lcrpl_pos = self.str_to_list(self.in_lcr_pl_var.get())
                    if len(lcrpl_pos)==6 and lcrpl_pos[0]>-360 and lcrpl_pos[0]<360:
                        self.sr.config["Points"]["LCR"]["Pl"]=lcrpl_pos
                        self.lcr_pl_var.set(self.in_lcr_pl_var.get())
                    else:
                        error = True

                    ptpiu_pos = self.str_to_list(self.in_pt_piu_var.get())
                    if len(ptpiu_pos)==6 and ptpiu_pos[0]>-360 and ptpiu_pos[0]<360:
                        self.sr.config["Points"]["PowTow"]["PiU"]=ptpiu_pos
                        self.pt_piu_var.set(self.in_pt_piu_var.get())
                    else:
                        error = True

                    ptpreprepi_pos = self.str_to_list(self.in_pt_preprepi_var.get())
                    if len(ptpreprepi_pos)==6 and ptpreprepi_pos[0]>-360 and ptpreprepi_pos[0]<360:
                        self.sr.config["Points"]["PowTow"]["PrePrePi"]=ptpreprepi_pos
                        self.pt_preprepi_var.set(self.in_pt_preprepi_var.get())
                    else:
                        error = True
                    
                    ptprepi_pos = self.str_to_list(self.in_pt_prepi_var.get())
                    if len(ptprepi_pos)==6 and ptprepi_pos[0]>-360 and ptprepi_pos[0]<360:
                        self.sr.config["Points"]["PowTow"]["PrePi"]=ptprepi_pos
                        self.pt_prepi_var.set(self.in_pt_prepi_var.get())
                    else:
                        error = True
                    
                    ptpi_pos = self.str_to_list(self.in_pt_pi_var.get())
                    if len(ptpi_pos)==6 and ptpi_pos[0]>-360 and ptpi_pos[0]<360:
                        self.sr.config["Points"]["PowTow"]["Pi"]=ptpi_pos
                        self.pt_pi_var.set(self.in_pt_pi_var.get())
                    else:
                        error = True
                    
                    ptpl_pos = self.str_to_list(self.in_pt_pl_var.get())
                    if len(ptpl_pos)==6 and ptpl_pos[0]>-360 and ptpl_pos[0]<360:
                        self.sr.config["Points"]["PowTow"]["Pl"]=ptpl_pos
                        self.pt_pl_var.set(self.in_pt_pl_var.get())
                    else:
                        error = True

                    ngpiu_pos = self.str_to_list(self.in_ng_piu_var.get())
                    if len(ngpiu_pos)==6 and ngpiu_pos[0]>-360 and ngpiu_pos[0]<360:
                        self.sr.config["Points"]["NoGood"]["PiU"]=ngpiu_pos
                        self.ng_piu_var.set(self.in_ng_piu_var.get())
                    else:
                        error = True

                    ngprepi_pos = self.str_to_list(self.in_ng_prepi_var.get())
                    if len(ngprepi_pos)==6 and ngprepi_pos[0]>-360 and ngprepi_pos[0]<360:
                        self.sr.config["Points"]["NoGood"]["PrePi"]=ngprepi_pos
                        self.ng_prepi_var.set(self.in_ng_prepi_var.get())
                    else:
                        error = True
                    
                    ngpl_pos = self.str_to_list(self.in_ng_pl_var.get())
                    if len(ngpl_pos)==6 and ngpl_pos[0]>-360 and ngpl_pos[0]<360:
                        self.sr.config["Points"]["NoGood"]["Pl"]=ngpl_pos
                        self.ng_pl_var.set(self.in_ng_pl_var.get())
                    else:
                        error = True

                    okpiu_pos = self.str_to_list(self.in_ok_piu_var.get())
                    if len(okpiu_pos)==6 and okpiu_pos[0]>-360 and okpiu_pos[0]<360:
                        self.sr.config["Points"]["OKparts"]["PiU"]=okpiu_pos
                        self.ok_piu_var.set(self.in_ok_piu_var.get())
                    else:
                        error = True
                    
                    okprepi_pos = self.str_to_list(self.in_ok_prepi_var.get())
                    if len(okprepi_pos)==6 and okprepi_pos[0]>-360 and okprepi_pos[0]<360:
                        self.sr.config["Points"]["OKparts"]["PrePi"]=okprepi_pos
                        self.ok_prepi_var.set(self.in_ok_prepi_var.get())
                    else:
                        error = True
                    
                    okpl_pos = self.str_to_list(self.in_ok_pl_var.get())
                    if len(okpl_pos)==6 and okpl_pos[0]>-360 and okpl_pos[0]<360:
                        self.sr.config["Points"]["OKparts"]["Pl"]=okpl_pos
                        self.ok_pl_var.set(self.in_ok_pl_var.get())
                    else:
                        error = True
                except:
                    self.show_param_error()
                if error:
                    self.show_param_error()
            else:
                self.show_warning()
            
        def reset_pos():
            if not self.sr.inmotion:
                config, error = self.read_json("sc/conf/config.txt","points")

                if error != 1:
                    self.sr.config["Points"]=config["Points"]
                    #Homes
                    self.home_var.set(str(self.sr.config["Points"]["Home"]))
                    self.in_home_var.set(str(self.sr.config["Points"]["Home"]))

                    self.home_in_hp_var.set(str(self.sr.config["Points"]["HomeInHiPot"]))
                    self.in_home_in_hp_var.set(str(self.sr.config["Points"]["HomeInHiPot"]))

                    self.home_hp_lcr_var.set(str(self.sr.config["Points"]["HomeHiPotLCR"]))
                    self.in_home_hp_lcr_var.set(str(self.sr.config["Points"]["HomeHiPotLCR"]))

                    self.home_lcr_pt_var.set(str(self.sr.config["Points"]["HomeLCRPowTow"]))
                    self.in_home_lcr_pt_var.set(str(self.sr.config["Points"]["HomeLCRPowTow"]))

                    self.home_pt_ok_var.set(str(self.sr.config["Points"]["HomePowTowOKparts"]))
                    self.in_home_pt_ok_var.set(str(self.sr.config["Points"]["HomePowTowOKparts"]))

                    self.home_hp_ng_var.set(str(self.sr.config["Points"]["HomeHiPotNoGood"]))
                    self.in_home_hp_ng_var.set(str(self.sr.config["Points"]["HomeHiPotNoGood"]))

                    self.home_lcr_ng_var.set(str(self.sr.config["Points"]["HomeLCRNoGood"]))
                    self.in_home_lcr_ng_var.set(str(self.sr.config["Points"]["HomeLCRNoGood"]))

                    self.home_pt_ng_var.set(str(self.sr.config["Points"]["HomePowTowNoGood"]))
                    self.in_home_pt_ng_var.set(str(self.sr.config["Points"]["HomePowTowNoGood"]))

                    #In Station
                    self.in_piu_var.set(str(self.sr.config["Points"]["In"]["PiU"]))
                    self.in_in_piu_var.set(str(self.sr.config["Points"]["In"]["PiU"]))

                    self.in_prepi_var.set(str(self.sr.config["Points"]["In"]["PrePi"]))
                    self.in_in_prepi_var.set(str(self.sr.config["Points"]["In"]["PrePi"]))

                    self.in_pi_var.set(str(self.sr.config["Points"]["In"]["Pi"]))
                    self.in_in_pi_var.set(str(self.sr.config["Points"]["In"]["Pi"]))

                    #HiPot Station
                    self.hp_piu_var.set(str(self.sr.config["Points"]["HiPot"]["PiU"]))
                    self.in_hp_piu_var.set(str(self.sr.config["Points"]["HiPot"]["PiU"]))

                    self.hp_preprepi_var.set(str(self.sr.config["Points"]["HiPot"]["PrePrePi"]))
                    self.in_hp_preprepi_var.set(str(self.sr.config["Points"]["HiPot"]["PrePrePi"]))

                    self.hp_prepi_var.set(str(self.sr.config["Points"]["HiPot"]["PrePi"]))
                    self.in_hp_prepi_var.set(str(self.sr.config["Points"]["HiPot"]["PrePi"]))

                    self.hp_pi_var.set(str(self.sr.config["Points"]["HiPot"]["Pi"]))
                    self.in_hp_pi_var.set(str(self.sr.config["Points"]["HiPot"]["Pi"]))

                    self.hp_pl_var.set(str(self.sr.config["Points"]["HiPot"]["Pl"]))
                    self.in_hp_pl_var.set(str(self.sr.config["Points"]["HiPot"]["Pl"]))

                    #LCR Station
                    self.lcr_piu_var.set(str(self.sr.config["Points"]["LCR"]["PiU"]))
                    self.in_lcr_piu_var.set(str(self.sr.config["Points"]["LCR"]["PiU"]))

                    self.lcr_preprepi_var.set(str(self.sr.config["Points"]["LCR"]["PrePrePi"]))
                    self.in_lcr_preprepi_var.set(str(self.sr.config["Points"]["LCR"]["PrePrePi"]))

                    self.lcr_prepi_var.set(str(self.sr.config["Points"]["LCR"]["PrePi"]))
                    self.in_lcr_prepi_var.set(str(self.sr.config["Points"]["LCR"]["PrePi"]))

                    self.lcr_pi_var.set(str(self.sr.config["Points"]["LCR"]["Pi"]))
                    self.in_lcr_pi_var.set(str(self.sr.config["Points"]["LCR"]["Pi"]))

                    self.lcr_pl_var.set(str(self.sr.config["Points"]["LCR"]["Pl"]))
                    self.in_lcr_pl_var.set(str(self.sr.config["Points"]["LCR"]["Pl"]))

                    #PowTow Station
                    self.pt_piu_var.set(str(self.sr.config["Points"]["PowTow"]["PiU"]))
                    self.in_pt_piu_var.set(str(self.sr.config["Points"]["PowTow"]["PiU"]))

                    self.pt_preprepi_var.set(str(self.sr.config["Points"]["PowTow"]["PrePrePi"]))
                    self.in_pt_preprepi_var.set(str(self.sr.config["Points"]["PowTow"]["PrePrePi"]))

                    self.pt_prepi_var.set(str(self.sr.config["Points"]["PowTow"]["PrePi"]))
                    self.in_pt_prepi_var.set(str(self.sr.config["Points"]["PowTow"]["PrePi"]))

                    self.pt_pi_var.set(str(self.sr.config["Points"]["PowTow"]["Pi"]))
                    self.in_pt_pi_var.set(str(self.sr.config["Points"]["PowTow"]["Pi"]))

                    self.pt_pl_var.set(str(self.sr.config["Points"]["PowTow"]["Pl"]))
                    self.in_pt_pl_var.set(str(self.sr.config["Points"]["PowTow"]["Pl"]))

                    #NoGood Station
                    self.ng_piu_var.set(str(self.sr.config["Points"]["NoGood"]["PiU"]))
                    self.in_ng_piu_var.set(str(self.sr.config["Points"]["NoGood"]["PiU"]))

                    self.ng_prepi_var.set(str(self.sr.config["Points"]["NoGood"]["PrePi"]))
                    self.in_ng_prepi_var.set(str(self.sr.config["Points"]["NoGood"]["PrePi"]))

                    self.ng_pl_var.set(str(self.sr.config["Points"]["NoGood"]["Pl"]))
                    self.in_ng_pl_var.set(str(self.sr.config["Points"]["NoGood"]["Pl"]))

                    #OkParts Station
                    self.ok_piu_var.set(str(self.sr.config["Points"]["OKparts"]["PiU"]))
                    self.in_ok_piu_var.set(str(self.sr.config["Points"]["OKparts"]["PiU"]))

                    self.ok_prepi_var.set(str(self.sr.config["Points"]["OKparts"]["PrePi"]))
                    self.in_ok_prepi_var.set(str(self.sr.config["Points"]["OKparts"]["PrePi"]))

                    self.ok_pl_var.set(str(self.sr.config["Points"]["OKparts"]["Pl"]))
                    self.in_ok_pl_var.set(str(self.sr.config["Points"]["OKparts"]["Pl"]))
            else:
                self.show_warning()
        
        def save_pos():
            update_pos()
            if not self.sr.inmotion:
                item = self.sr.config
                with open("sc/conf/last_config.txt", "w")as file:
                    json.dump(fp=file, indent=4, obj=item)

        def load_pos():
            if not self.sr.inmotion:
                config, error = self.read_json("sc/conf/last_config.txt","points")
                if error != 1:
                    self.sr.config["Points"]=config["Points"]
                    #Homes
                    self.home_var.set(str(self.sr.config["Points"]["Home"]))
                    self.in_home_var.set(str(self.sr.config["Points"]["Home"]))

                    self.home_in_hp_var.set(str(self.sr.config["Points"]["HomeInHiPot"]))
                    self.in_home_in_hp_var.set(str(self.sr.config["Points"]["HomeInHiPot"]))

                    self.home_hp_lcr_var.set(str(self.sr.config["Points"]["HomeHiPotLCR"]))
                    self.in_home_hp_lcr_var.set(str(self.sr.config["Points"]["HomeHiPotLCR"]))

                    self.home_lcr_pt_var.set(str(self.sr.config["Points"]["HomeLCRPowTow"]))
                    self.in_home_lcr_pt_var.set(str(self.sr.config["Points"]["HomeLCRPowTow"]))

                    self.home_pt_ok_var.set(str(self.sr.config["Points"]["HomePowTowOKparts"]))
                    self.in_home_pt_ok_var.set(str(self.sr.config["Points"]["HomePowTowOKparts"]))

                    self.home_hp_ng_var.set(str(self.sr.config["Points"]["HomeHiPotNoGood"]))
                    self.in_home_hp_ng_var.set(str(self.sr.config["Points"]["HomeHiPotNoGood"]))

                    self.home_lcr_ng_var.set(str(self.sr.config["Points"]["HomeLCRNoGood"]))
                    self.in_home_lcr_ng_var.set(str(self.sr.config["Points"]["HomeLCRNoGood"]))

                    self.home_pt_ng_var.set(str(self.sr.config["Points"]["HomePowTowNoGood"]))
                    self.in_home_pt_ng_var.set(str(self.sr.config["Points"]["HomePowTowNoGood"]))

                    #In Station
                    self.in_piu_var.set(str(self.sr.config["Points"]["In"]["PiU"]))
                    self.in_in_piu_var.set(str(self.sr.config["Points"]["In"]["PiU"]))

                    self.in_prepi_var.set(str(self.sr.config["Points"]["In"]["PrePi"]))
                    self.in_in_prepi_var.set(str(self.sr.config["Points"]["In"]["PrePi"]))

                    self.in_pi_var.set(str(self.sr.config["Points"]["In"]["Pi"]))
                    self.in_in_pi_var.set(str(self.sr.config["Points"]["In"]["Pi"]))

                    #HiPot Station
                    self.hp_piu_var.set(str(self.sr.config["Points"]["HiPot"]["PiU"]))
                    self.in_hp_piu_var.set(str(self.sr.config["Points"]["HiPot"]["PiU"]))

                    self.hp_preprepi_var.set(str(self.sr.config["Points"]["HiPot"]["PrePrePi"]))
                    self.in_hp_preprepi_var.set(str(self.sr.config["Points"]["HiPot"]["PrePrePi"]))

                    self.hp_prepi_var.set(str(self.sr.config["Points"]["HiPot"]["PrePi"]))
                    self.in_hp_prepi_var.set(str(self.sr.config["Points"]["HiPot"]["PrePi"]))

                    self.hp_pi_var.set(str(self.sr.config["Points"]["HiPot"]["Pi"]))
                    self.in_hp_pi_var.set(str(self.sr.config["Points"]["HiPot"]["Pi"]))

                    self.hp_pl_var.set(str(self.sr.config["Points"]["HiPot"]["Pl"]))
                    self.in_hp_pl_var.set(str(self.sr.config["Points"]["HiPot"]["Pl"]))

                    #LCR Station
                    self.lcr_piu_var.set(str(self.sr.config["Points"]["LCR"]["PiU"]))
                    self.in_lcr_piu_var.set(str(self.sr.config["Points"]["LCR"]["PiU"]))

                    self.lcr_preprepi_var.set(str(self.sr.config["Points"]["LCR"]["PrePrePi"]))
                    self.in_lcr_preprepi_var.set(str(self.sr.config["Points"]["LCR"]["PrePrePi"]))

                    self.lcr_prepi_var.set(str(self.sr.config["Points"]["LCR"]["PrePi"]))
                    self.in_lcr_prepi_var.set(str(self.sr.config["Points"]["LCR"]["PrePi"]))

                    self.lcr_pi_var.set(str(self.sr.config["Points"]["LCR"]["Pi"]))
                    self.in_lcr_pi_var.set(str(self.sr.config["Points"]["LCR"]["Pi"]))

                    self.lcr_pl_var.set(str(self.sr.config["Points"]["LCR"]["Pl"]))
                    self.in_lcr_pl_var.set(str(self.sr.config["Points"]["LCR"]["Pl"]))

                    #PowTow Station
                    self.pt_piu_var.set(str(self.sr.config["Points"]["PowTow"]["PiU"]))
                    self.in_pt_piu_var.set(str(self.sr.config["Points"]["PowTow"]["PiU"]))

                    self.pt_preprepi_var.set(str(self.sr.config["Points"]["PowTow"]["PrePrePi"]))
                    self.in_pt_preprepi_var.set(str(self.sr.config["Points"]["PowTow"]["PrePrePi"]))

                    self.pt_prepi_var.set(str(self.sr.config["Points"]["PowTow"]["PrePi"]))
                    self.in_pt_prepi_var.set(str(self.sr.config["Points"]["PowTow"]["PrePi"]))

                    self.pt_pi_var.set(str(self.sr.config["Points"]["PowTow"]["Pi"]))
                    self.in_pt_pi_var.set(str(self.sr.config["Points"]["PowTow"]["Pi"]))

                    self.pt_pl_var.set(str(self.sr.config["Points"]["PowTow"]["Pl"]))
                    self.in_pt_pl_var.set(str(self.sr.config["Points"]["PowTow"]["Pl"]))

                    #NoGood Station
                    self.ng_piu_var.set(str(self.sr.config["Points"]["NoGood"]["PiU"]))
                    self.in_ng_piu_var.set(str(self.sr.config["Points"]["NoGood"]["PiU"]))

                    self.ng_prepi_var.set(str(self.sr.config["Points"]["NoGood"]["PrePi"]))
                    self.in_ng_prepi_var.set(str(self.sr.config["Points"]["NoGood"]["PrePi"]))

                    self.ng_pl_var.set(str(self.sr.config["Points"]["NoGood"]["Pl"]))
                    self.in_ng_pl_var.set(str(self.sr.config["Points"]["NoGood"]["Pl"]))

                    #OkParts Station
                    self.ok_piu_var.set(str(self.sr.config["Points"]["OKparts"]["PiU"]))
                    self.in_ok_piu_var.set(str(self.sr.config["Points"]["OKparts"]["PiU"]))

                    self.ok_prepi_var.set(str(self.sr.config["Points"]["OKparts"]["PrePi"]))
                    self.in_ok_prepi_var.set(str(self.sr.config["Points"]["OKparts"]["PrePi"]))

                    self.ok_pl_var.set(str(self.sr.config["Points"]["OKparts"]["Pl"]))
                    self.in_ok_pl_var.set(str(self.sr.config["Points"]["OKparts"]["Pl"]))
            else:
                self.show_warning()


        #Edit Position window definition
        self.ep_window = Toplevel(self.root)
        self.ep_window.title("Edit Positions")
        self.ep_window.resizable(True,True) #width, heigth

        #Positions tab
        self.pos_tab = ttk.Notebook(self.ep_window)

        #Homes_tab creation (NoGood Station)
        self.home_tab = Frame(self.pos_tab)
        self.home_tab.config(bg="light gray", width = 500, height= 400)
        self.pos_tab.add(self.home_tab,text="Home")

        #In_tab creation (In Station)
        self.in_tab = Frame(self.pos_tab)
        self.in_tab.config(bg="light gray", width = 500, height= 400)
        self.pos_tab.add(self.in_tab,text="In Station")

        #HP_tab creation (HiPot Station)
        self.hp_tab = Frame(self.pos_tab)
        self.hp_tab.config(bg="light gray", width = 500, height= 400)
        self.pos_tab.add(self.hp_tab,text="HiPot Station")

        #LCR_tab creation (LCR Station)
        self.lcr_tab = Frame(self.pos_tab)
        self.lcr_tab.config(bg="light gray", width = 400, height= 400)
        self.pos_tab.add(self.lcr_tab,text="LCR Station")

        #PowTow_tab creation (PowTow Station)
        self.pt_tab = Frame(self.pos_tab)
        self.pt_tab.config(bg="light gray", width = 500, height= 400)
        self.pos_tab.add(self.pt_tab,text="PowTow Station")

        #NG_tab creation (NoGood Station)
        self.ng_tab = Frame(self.pos_tab)
        self.ng_tab.config(bg="light gray", width = 500, height= 400)
        self.pos_tab.add(self.ng_tab,text="NoGood Station")

        #Ok_tab creation (OkParts Station)
        self.ok_tab = Frame(self.pos_tab)
        self.ok_tab.config(bg="light gray", width = 500, height= 400)
        self.pos_tab.add(self.ok_tab,text="OKparts Station")


        ####Pos tab packing####
        self.pos_tab.pack(expand = True, fill = 'both')


        ####Home tab####
        #Header row
        self.home_header = Label(self.home_tab, text = "Position", bg="light gray",fg="black", relief = "solid", bd=1)
        self.home_header.grid(row=0,column=0,ipadx=60)

        self.home_value_header = Label(self.home_tab, text = "Current Value: [J1, J2, J3, J4, J5, J6] (Degrees)", bg="light gray", fg="black", relief = "solid", bd=1)
        self.home_value_header.grid(row=0,column=1,ipadx=10)

        self.home_input_header = Label(self.home_tab, text = "New Value", bg="light gray", fg="black", relief = "solid", bd=1)
        self.home_input_header.grid(row=0,column=2,ipadx=101)
        #Home row
        __set_label(self.home_tab, intext="Home", l_row=1, l_col=0)
        __set_label(self.home_tab, size=30, textvar=self.home_var, l_row=1, l_col=1)
        __set_entry(self.home_tab, size=30, textvar=self.in_home_var, e_row=1, e_col=2)
        #HomeInHiPot row
        __set_label(self.home_tab, intext="HomeInHiPot", l_row=2, l_col=0)
        __set_label(self.home_tab, size=30, textvar=self.home_in_hp_var, l_row=2, l_col=1)
        __set_entry(self.home_tab, size=30, textvar=self.in_home_in_hp_var, e_row=2, e_col=2)
        #HomeHiPotLCR row
        __set_label(self.home_tab, intext="HomeHiPotLCR", l_row=3, l_col=0)
        __set_label(self.home_tab, size=30, textvar=self.home_hp_lcr_var, l_row=3, l_col=1)
        __set_entry(self.home_tab, size=30, textvar=self.in_home_hp_lcr_var, e_row=3, e_col=2)
        #HomeLCRPowTow row
        __set_label(self.home_tab, intext="HomeLCRPowTow", l_row=4, l_col=0)
        __set_label(self.home_tab, size=30, textvar=self.home_lcr_pt_var, l_row=4, l_col=1)
        __set_entry(self.home_tab, size=30, textvar=self.in_home_lcr_pt_var, e_row=4, e_col=2)
        #HomePowTowOkParts row
        __set_label(self.home_tab, intext="HomePowTowOKparts", l_row=5, l_col=0)
        __set_label(self.home_tab, size=30, textvar=self.home_pt_ok_var, l_row=5, l_col=1)
        __set_entry(self.home_tab, size=30, textvar=self.in_home_pt_ok_var, e_row=5, e_col=2)
        #HomeHiPotNoGood row
        __set_label(self.home_tab, intext="HomeHiPotNoGood", l_row=6, l_col=0)
        __set_label(self.home_tab, size=30, textvar=self.home_hp_ng_var, l_row=6, l_col=1)
        __set_entry(self.home_tab, size=30, textvar=self.in_home_hp_ng_var, e_row=6, e_col=2)
        #HomeLCRNoGood row
        __set_label(self.home_tab, intext="HomeLCRNoGood", l_row=7, l_col=0)
        __set_label(self.home_tab, size=30, textvar=self.home_lcr_ng_var, l_row=7, l_col=1)
        __set_entry(self.home_tab, size=30, textvar=self.in_home_lcr_ng_var, e_row=7, e_col=2)
        #HomePowNoGood row
        __set_label(self.home_tab, intext="HomePowNoGood", l_row=8, l_col=0)
        __set_label(self.home_tab, size=30, textvar=self.home_pt_ng_var, l_row=8, l_col=1)
        __set_entry(self.home_tab, size=30, textvar=self.in_home_pt_ng_var, e_row=8, e_col=2)
        #__set_label(home_tab,text=,l_row=,l_col=)
        #__set_entry(home_tab,textvar=,e_row=,e_col=)
        ##Buttons
        #Update Button
        self.updatehome_pos_btn = Button(self.home_tab, text="Update Positions", command =update_pos, bg = "light gray",bd=1, width=14)
        self.updatehome_pos_btn.grid(row = 9, column = 1)
        #Reset button
        self.resethome_btn = Button(self.home_tab, text="Reset Positions", bg = "light gray",command = reset_pos,bd=1,width=20)
        self.resethome_btn.grid(row = 9, column = 2)
        #Save params Button
        self.savehome_btn = Button(self.home_tab, text="Save Positions", command =save_pos, bg = "light gray",bd=1,width=14)
        self.savehome_btn.grid(row = 10, column = 1)
        #load last params Button
        self.loadhome_btn = Button(self.home_tab, text="Load Last Positions", command =load_pos, bg = "light gray",bd=1,width=20)
        self.loadhome_btn.grid(row = 10, column = 2)

        ####In tab####
        self.in_header = Label(self.in_tab, text = "Position", bg="light gray",fg="black", relief = "solid", bd=1)
        self.in_header.grid(row=0,column=0,ipadx=60)

        self.in_value_header = Label(self.in_tab, text = "Current Value: [J1, J2, J3, J4, J5, J6] (Degrees)", bg="light gray", fg="black", relief = "solid", bd=1)
        self.in_value_header.grid(row=0,column=1,ipadx=10)

        self.in_input_header = Label(self.in_tab, text = "New Value", bg="light gray", fg="black", relief = "solid", bd=1)
        self.in_input_header.grid(row=0,column=2,ipadx=101)
        #PickUp row
        __set_label(self.in_tab, intext="PiU", l_row=1, l_col=0)
        __set_label(self.in_tab, size=30, textvar=self.in_piu_var, l_row=1, l_col=1)
        __set_entry(self.in_tab, size=30, textvar=self.in_in_piu_var, e_row=1, e_col=2)
        #PrePick row
        __set_label(self.in_tab, intext="PrePi", l_row=2, l_col=0)
        __set_label(self.in_tab, size=30, textvar=self.in_prepi_var, l_row=2, l_col=1)
        __set_entry(self.in_tab, size=30, textvar=self.in_in_prepi_var, e_row=2, e_col=2)
        #Pick row
        __set_label(self.in_tab, intext="Pi", l_row=3, l_col=0)
        __set_label(self.in_tab, size=30, textvar=self.in_pi_var, l_row=3, l_col=1)
        __set_entry(self.in_tab, size=30, textvar=self.in_in_pi_var, e_row=3, e_col=2)
        ##Buttons
        #Update Button
        self.updatein_pos_btn = Button(self.in_tab, text="Update Positions", command =update_pos, bg = "light gray",bd=1, width=14)
        self.updatein_pos_btn.grid(row = 4, column = 1)
        #Reset button
        self.resetin_btn = Button(self.in_tab, text="Reset Positions", bg = "light gray",command = reset_pos,bd=1,width=20)
        self.resetin_btn.grid(row = 4, column = 2)
        #Save params Button
        self.savein_btn = Button(self.in_tab, text="Save Positions", command =save_pos, bg = "light gray",bd=1,width=14)
        self.savein_btn.grid(row = 5, column = 1)
        #load last params Button
        self.loadin_btn = Button(self.in_tab, text="Load Last Positions", command =load_pos, bg = "light gray",bd=1,width=20)
        self.loadin_btn.grid(row = 5, column = 2)


        ####HiPot tab####
        self.hp_header = Label(self.hp_tab, text = "Position", bg="light gray",fg="black", relief = "solid", bd=1)
        self.hp_header.grid(row=0,column=0,ipadx=60)

        self.hp_value_header = Label(self.hp_tab, text = "Current Value: [J1, J2, J3, J4, J5, J6] (Degrees)", bg="light gray", fg="black", relief = "solid", bd=1)
        self.hp_value_header.grid(row=0,column=1,ipadx=10)

        self.hp_input_header = Label(self.hp_tab, text = "New Value", bg="light gray", fg="black", relief = "solid", bd=1)
        self.hp_input_header.grid(row=0,column=2,ipadx=101)
        #PickUp row
        __set_label(self.hp_tab, intext="PiU", l_row=1, l_col=0)
        __set_label(self.hp_tab, size=30, textvar=self.hp_piu_var, l_row=1, l_col=1)
        __set_entry(self.hp_tab, size=30, textvar=self.in_hp_piu_var, e_row=1, e_col=2)
        #PrePrePick row
        __set_label(self.hp_tab, intext="PrePrePi", l_row=2, l_col=0)
        __set_label(self.hp_tab, size=30, textvar=self.hp_preprepi_var, l_row=2, l_col=1)
        __set_entry(self.hp_tab, size=30, textvar=self.in_hp_preprepi_var, e_row=2, e_col=2)
        #PrePick row
        __set_label(self.hp_tab, intext="PrePi", l_row=3, l_col=0)
        __set_label(self.hp_tab, size=30, textvar=self.hp_prepi_var, l_row=3, l_col=1)
        __set_entry(self.hp_tab, size=30, textvar=self.in_hp_prepi_var, e_row=3, e_col=2)
        #Pick row
        __set_label(self.hp_tab, intext="Pi", l_row=4, l_col=0)
        __set_label(self.hp_tab, size=30, textvar=self.hp_pi_var, l_row=4, l_col=1)
        __set_entry(self.hp_tab, size=30, textvar=self.in_hp_pi_var, e_row=4, e_col=2)
        #Place row
        __set_label(self.hp_tab, intext="Pl", l_row=5, l_col=0)
        __set_label(self.hp_tab, size=30, textvar=self.hp_pl_var, l_row=5, l_col=1)
        __set_entry(self.hp_tab, size=30, textvar=self.in_hp_pl_var, e_row=5, e_col=2)
        ##Buttons
        #Update Button
        updatehp_pos_btn = Button(self.hp_tab, text="Update Positions", command =update_pos, bg = "light gray",bd=1, width=14)
        updatehp_pos_btn.grid(row = 6, column = 1)
        #Reset button
        resethp_btn = Button(self.hp_tab, text="Reset Positions", bg = "light gray",command = reset_pos,bd=1,width=20)
        resethp_btn.grid(row = 6, column = 2)
        #Save params Button
        savehp_btn = Button(self.hp_tab, text="Save Positions", command =save_pos, bg = "light gray",bd=1,width=14)
        savehp_btn.grid(row = 7, column = 1)
        #load last params Button
        loadhp_btn = Button(self.hp_tab, text="Load Last Positions", command =load_pos, bg = "light gray",bd=1,width=20)
        loadhp_btn.grid(row = 7, column = 2)

        ####LCR tab####
        lcr_header = Label(self.lcr_tab, text = "Position", bg="light gray",fg="black", relief = "solid", bd=1)
        lcr_header.grid(row=0,column=0,ipadx=60)

        lcr_value_header = Label(self.lcr_tab, text = "Current Value: [J1, J2, J3, J4, J5, J6] (Degrees)", bg="light gray", fg="black", relief = "solid", bd=1)
        lcr_value_header.grid(row=0,column=1,ipadx=10)

        lcr_input_header = Label(self.lcr_tab, text = "New Value", bg="light gray", fg="black", relief = "solid", bd=1)
        lcr_input_header.grid(row=0,column=2,ipadx=101)
        #PickUp row
        __set_label(self.lcr_tab, intext="PiU", l_row=1, l_col=0)
        __set_label(self.lcr_tab, size=30, textvar=self.lcr_piu_var, l_row=1, l_col=1)
        __set_entry(self.lcr_tab, size=30, textvar=self.in_lcr_piu_var, e_row=1, e_col=2)
        #PrePrePick row
        __set_label(self.lcr_tab, intext="PrePrePi", l_row=2, l_col=0)
        __set_label(self.lcr_tab, size=30, textvar=self.lcr_preprepi_var, l_row=2, l_col=1)
        __set_entry(self.lcr_tab, size=30, textvar=self.in_lcr_preprepi_var, e_row=2, e_col=2)
        #PrePick row
        __set_label(self.lcr_tab, intext="PrePi", l_row=3, l_col=0)
        __set_label(self.lcr_tab, size=30, textvar=self.lcr_prepi_var, l_row=3, l_col=1)
        __set_entry(self.lcr_tab, size=30, textvar=self.in_lcr_prepi_var, e_row=3, e_col=2)
        #Pick row
        __set_label(self.lcr_tab, intext="Pi", l_row=4, l_col=0)
        __set_label(self.lcr_tab, size=30, textvar=self.lcr_pi_var, l_row=4, l_col=1)
        __set_entry(self.lcr_tab, size=30, textvar=self.in_lcr_pi_var, e_row=4, e_col=2)
        #Place row
        __set_label(self.lcr_tab, intext="Pl", l_row=5, l_col=0)
        __set_label(self.lcr_tab, size=30, textvar=self.lcr_pl_var, l_row=5, l_col=1)
        __set_entry(self.lcr_tab, size=30, textvar=self.in_lcr_pl_var, e_row=5, e_col=2)
        #Update Button
        updatelcr_pos_btn = Button(self.lcr_tab, text="Update Positions", command =update_pos, bg = "light gray",bd=1, width=14)
        updatelcr_pos_btn.grid(row = 6, column = 1)
        #Reset button
        resetlcr_btn = Button(self.lcr_tab, text="Reset Positions", bg = "light gray",command = reset_pos,bd=1,width=20)
        resetlcr_btn.grid(row = 6, column = 2)
        #Save params Button
        savelcr_btn = Button(self.lcr_tab, text="Save Positions", command =save_pos, bg = "light gray",bd=1,width=14)
        savelcr_btn.grid(row = 7, column = 1)
        #load last params Button
        loadlcr_btn = Button(self.lcr_tab, text="Load Last Positions", command =load_pos, bg = "light gray",bd=1,width=20)
        loadlcr_btn.grid(row = 7, column = 2)

        ####PowTow tab####
        pt_header = Label(self.pt_tab, text = "Position", bg="light gray",fg="black", relief = "solid", bd=1)
        pt_header.grid(row=0,column=0,ipadx=60)

        pt_value_header = Label(self.pt_tab, text = "Current Value: [J1, J2, J3, J4, J5, J6] (Degrees)", bg="light gray", fg="black", relief = "solid", bd=1)
        pt_value_header.grid(row=0,column=1,ipadx=10)

        pt_input_header = Label(self.pt_tab, text = "New Value", bg="light gray", fg="black", relief = "solid", bd=1)
        pt_input_header.grid(row=0,column=2,ipadx=101)
        #PickUp row
        __set_label(self.pt_tab, intext="PiU", l_row=1, l_col=0)
        __set_label(self.pt_tab, size=30, textvar=self.pt_piu_var, l_row=1, l_col=1)
        __set_entry(self.pt_tab, size=30, textvar=self.in_pt_piu_var, e_row=1, e_col=2)
        #PrePrePick row
        __set_label(self.pt_tab, intext="PrePrePi", l_row=2, l_col=0)
        __set_label(self.pt_tab, size=30, textvar=self.pt_preprepi_var, l_row=2, l_col=1)
        __set_entry(self.pt_tab, size=30, textvar=self.in_pt_preprepi_var, e_row=2, e_col=2)
        #PrePick row
        __set_label(self.pt_tab, intext="PrePi", l_row=3, l_col=0)
        __set_label(self.pt_tab, size=30, textvar=self.pt_prepi_var, l_row=3, l_col=1)
        __set_entry(self.pt_tab, size=30, textvar=self.in_pt_prepi_var, e_row=3, e_col=2)
        #Pick row
        __set_label(self.pt_tab, intext="Pi", l_row=4, l_col=0)
        __set_label(self.pt_tab, size=30, textvar=self.pt_pi_var, l_row=4, l_col=1)
        __set_entry(self.pt_tab, size=30, textvar=self.in_pt_pi_var, e_row=4, e_col=2)
        #Place row
        __set_label(self.pt_tab, intext="Pl", l_row=5, l_col=0)
        __set_label(self.pt_tab, size=30, textvar=self.pt_pl_var, l_row=5, l_col=1)
        __set_entry(self.pt_tab, size=30, textvar=self.in_pt_pl_var, e_row=5, e_col=2)
        #Update Button
        self.updatept_pos_btn = Button(self.pt_tab, text="Update Positions", command =update_pos, bg = "light gray",bd=1, width=14)
        self.updatept_pos_btn.grid(row = 6, column = 1)
        #Reset button
        self.resetpt_btn = Button(self.pt_tab, text="Reset Positions", bg = "light gray",command = reset_pos,bd=1,width=20)
        self.resetpt_btn.grid(row = 6, column = 2)
        #Save params Button
        self.savept_btn = Button(self.pt_tab, text="Save Positions", command =save_pos, bg = "light gray",bd=1,width=14)
        self.savept_btn.grid(row = 7, column = 1)
        #load last params Button
        self.loadpt_btn = Button(self.pt_tab, text="Load Last Positions", command =load_pos, bg = "light gray",bd=1,width=20)
        self.loadpt_btn.grid(row = 7, column = 2)


        ####NoGood tab####
        self.ng_header = Label(self.ng_tab, text = "Position", bg="light gray",fg="black", relief = "solid", bd=1)
        self.ng_header.grid(row=0,column=0,ipadx=60)

        self.ng_value_header = Label(self.ng_tab, text = "Current Value: [J1, J2, J3, J4, J5, J6] (Degrees)", bg="light gray", fg="black", relief = "solid", bd=1)
        self.ng_value_header.grid(row=0,column=1,ipadx=10)

        self.ng_input_header = Label(self.ng_tab, text = "New Value", bg="light gray", fg="black", relief = "solid", bd=1)
        self.ng_input_header.grid(row=0,column=2,ipadx=101)
        #PickUp row
        __set_label(self.ng_tab, intext="PiU", l_row=1, l_col=0)
        __set_label(self.ng_tab, size=30, textvar=self.ng_piu_var, l_row=1, l_col=1)
        __set_entry(self.ng_tab, size=30, textvar=self.in_ng_piu_var, e_row=1, e_col=2)
        #PrePick row
        __set_label(self.ng_tab, intext="PrePi", l_row=2, l_col=0)
        __set_label(self.ng_tab, size=30, textvar=self.ng_prepi_var, l_row=2, l_col=1)
        __set_entry(self.ng_tab, size=30, textvar=self.in_ng_prepi_var, e_row=2, e_col=2)
        #Pick row
        __set_label(self.ng_tab, intext="Pl", l_row=3, l_col=0)
        __set_label(self.ng_tab, size=30, textvar=self.ng_pl_var, l_row=3, l_col=1)
        __set_entry(self.ng_tab, size=30, textvar=self.in_ng_pl_var, e_row=3, e_col=2)
        #Update Button
        self.updateng_pos_btn = Button(self.ng_tab, text="Update Positions", command =update_pos, bg = "light gray",bd=1, width=14)
        self.updateng_pos_btn.grid(row = 4, column = 1)
        #Reset button
        self.resetng_btn = Button(self.ng_tab, text="Reset Positions", bg = "light gray",command = reset_pos,bd=1,width=20)
        self.resetng_btn.grid(row = 4, column = 2)
        #Save params Button
        self.saveng_btn = Button(self.ng_tab, text="Save Positions", command =save_pos, bg = "light gray",bd=1,width=14)
        self.saveng_btn.grid(row = 5, column = 1)
        #load last params Button
        self.loadng_btn = Button(self.ng_tab, text="Load Last Positions", command =load_pos, bg = "light gray",bd=1,width=20)
        self.loadng_btn.grid(row = 5, column = 2)

        ####OkParts tab####
        self.ok_header = Label(self.ok_tab, text = "Position", bg="light gray",fg="black", relief = "solid", bd=1)
        self.ok_header.grid(row=0,column=0,ipadx=60)

        ok_value_header = Label(self.ok_tab, text = "Current Value: [J1, J2, J3, J4, J5, J6] (Degrees)", bg="light gray", fg="black", relief = "solid", bd=1)
        ok_value_header.grid(row=0,column=1,ipadx=10)

        self.ok_input_header = Label(self.ok_tab, text = "New Value", bg="light gray", fg="black", relief = "solid", bd=1)
        self.ok_input_header.grid(row=0,column=2,ipadx=101)
        #PickUp row
        __set_label(self.ok_tab, intext="PiU", l_row=1, l_col=0)
        __set_label(self.ok_tab, size=30, textvar=self.ok_piu_var, l_row=1, l_col=1)
        __set_entry(self.ok_tab, size=30, textvar=self.in_ok_piu_var, e_row=1, e_col=2)
        #PrePick row
        __set_label(self.ok_tab, intext="PrePi", l_row=2, l_col=0)
        __set_label(self.ok_tab, size=30, textvar=self.ok_prepi_var, l_row=2, l_col=1)
        __set_entry(self.ok_tab, size=30, textvar=self.in_ok_prepi_var, e_row=2, e_col=2)
        #Pick row
        __set_label(self.ok_tab, intext="Pl", l_row=3, l_col=0)
        __set_label(self.ok_tab, size=30, textvar=self.ok_pl_var, l_row=3, l_col=1)
        __set_entry(self.ok_tab, size=30, textvar=self.in_ok_pl_var, e_row=3, e_col=2)
        #Update Button
        self.updateok_pos_btn = Button(self.ok_tab, text="Update Positions", command =update_pos, bg = "light gray",bd=1, width=14)
        self.updateok_pos_btn.grid(row = 4, column = 1)
        #Reset button
        self.resetok_btn = Button(self.ok_tab, text="Reset Positions", bg = "light gray",command = reset_pos,bd=1,width=20)
        self.resetok_btn.grid(row = 4, column = 2)
        #Save params Button
        self.saveok_btn = Button(self.ok_tab, text="Save Positions", command =save_pos, bg = "light gray",bd=1,width=14)
        self.saveok_btn.grid(row = 5, column = 1)
        #load last params Button
        self.loadok_btn = Button(self.ok_tab, text="Load Last Positions", command =load_pos, bg = "light gray",bd=1,width=20)
        self.loadok_btn.grid(row = 5, column = 2)

    ####File menu methods####
    def exit_app(self):
        answer = messagebox.askquestion("Confirm close","Are you sure you want to close the application?")
        if answer == "yes":
            self.root.destroy()
            self.sr.Quit = True

    ####Help menu methods####
    def open_xarm_documentation(self):
        wspace = pathlib.Path().resolve() 
        route = str(wspace) + "/sc/docs/xArm_User_Manual-V186.pdf"
        webbrowser.open(route)

    def open_xarm_studio(self):
        robot_ip = "192.168.100.243"
        webbrowser.open("http://"+ robot_ip + ":18333")

    def open_ezcad_doc(self):
        wspace = pathlib.Path().resolve()
        route = str(wspace) + "/sc/docs/EZCAD_2.10_software_Manual.pdf"
        webbrowser.open(route)
    
    def open_api_doc(self):
        wspace = pathlib.Path().resolve()
        route = str(wspace) + "/sc/docs/xArm-Python-SDK_xarm_api.mhtml"
        webbrowser.open(route)
    
    def open_api_code_doc(self):
        wspace = pathlib.Path().resolve()
        route = str(wspace) + "/sc/docs/xArm-Python-SDK_xarm_api_code.mhtml"
        webbrowser.open(route)

def test():

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
    
    sr = Shared_Resource(read_json("sc/conf/last_config.txt"))

    sr.openlcr  = True
    sr.closelcr = True
    sr.robotini = True
    sr.verify = True
    ####Root definition####
    root=Tk()
    ####Interface####
    root.title("Test Bench GUI")
    root.resizable(True,True) #width, heigth
    root.config(bg="light gray")



    interface = test_bench_gui(sr,root)
    interface.params_upd()

    root.mainloop()
    sr.Quit = True


#test()
