# Shared resource
from threading import Semaphore
from typing import List, Union
from status_register import Status_Register
from error_register import Error_Register

class Shared_Resource:

    __orders: List[str] #List of orders to execute
    __semaphore_orders : Semaphore #Semaphore instance to synchronize events
    __SR: Status_Register #Status register instance
    __ER: Error_Register #Error register instance

    def __init__(self, default_config):
        self.__orders = [] #Initially, orders is a blank list
        self.__semaphore_orders = Semaphore(1)
        self.__SR = Status_Register()
        self.__ER = Error_Register()
        self.logger = None
        
        #Configuration parameters of the entire system
        self.config = default_config #Stores the current config, initially default config
        self.params = {
                        "Linear Speed"      : self.config["Robot_controller"]["Home_linear_speed"],
                        "Payload"           : self.config["Robot_arm"]["Empty_payload"],
                        "Arm Mode"          : 0,
                        "Robot Error"       : 0,
                        "Current Step"      : "None",
                        "Joint Position"    : [0,0,0,0,0,0],
                        "Cartesian Position": [0,0,0],
                        "MSPM Connected"    : False,
                        "Arm Connected"     : False
                      }
        
        #Control flags
        self.Quit= False #Global quit variable

        #Control flags of interface buttons
        self.inmotion   = False
        self.wantupdate = False
        self.wantsave   = False
        self.wantload   = False
        self.wantreset  = False

    def add_order(self, order: str):
        """
            Adds an order to the end of the list

            Parameters:
            -----------

                _order (str) -> order to be added

            Return:
            -------

                None
        """
        if self.__orders == []:
            self.__semaphore_orders.acquire() #Acquires a semaphore resource, otherwise it waits until it is available.
            self.__orders.append(order) # Adds new order to the end of the list
            self.__semaphore_orders.release() #Releases the acquired resource
        else:
            print("ERROR. An order was received and list was not clear.\n")
            self.logger.write("\nERROR. An order was received and list was not clear.\n")

    def consume_order(self) -> Union[str, None]:
        """
            Returns the order to be executed after deleting it from list if possible, otherwise it returns None
        """
        self.__semaphore_orders.acquire() #Acquires a semaphore resource, otherwise it waits until it is available.
    
        order = None
        if self.__orders != []:
            order = self.__orders.pop(0)

        self.__semaphore_orders.release() #Releases the acquired resource

        return order

    def get_SR(self) -> Status_Register:
        #Returns status register value
        return self.__SR

    def get_ER(self) -> Error_Register:
        #Returns error register value
        return self.__ER

    def get_orders(self) -> List[str]:
        #Acquires a resource, saves the attribute __SR in a variable and releases the acquired resource.
        self.__semaphore_orders.acquire()
        orders = self.__orders.copy()
        self.__semaphore_orders.release()
        return orders
