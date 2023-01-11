# Producer
from io import TextIOWrapper
from threading import Thread
from shared_resource import Shared_Resource
from socket import socket, AF_INET, SOCK_STREAM
from typing import Tuple
from datetime import datetime

class Server_Aleman(Thread):

    __shared_resource: Shared_Resource #Instance of shared resource object
    __address: Tuple[str, int] #Host address as a tuple

    def __init__(self, shared_resource: Shared_Resource, address: Tuple[str, int]):
        Thread.__init__(self) #Overrides __init__ construct
        self.__shared_resource = shared_resource
        self.__address = address
        self.__s = socket(AF_INET, SOCK_STREAM) #TCP socket instance with default parameters
        self.conn = None #Connected socket variable is initialized

    def run(self):
        now = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        filename = "sc/logs/mspm/Data_" +now +".txt"
        self.f = open(filename,"a")

        try:
            self.__s.bind(self.__address) #Bind input address to the socket instace
            print("\nMSPM Tower socket binded")
            self.__shared_resource.logger.write("\nMSPM Tower socket binded")
            self.__s.listen(1) #Mark the socket as a passive socket to accept incoming connections, in other words, a server.
            print("\nWaiting to connect (Tower)")
            self.__shared_resource.logger.write("\nWaiting to connect (Tower)")
        except:
            self.__shared_resource.Quit=True
            print("Creating socket failed, please restart the program")
            
        try:
            (self.conn, addr) = self.__s.accept() #Accept incoming connection from client
            self.conn.settimeout(None)            #Timeout for the following methods is none
            #self.conn = conn
            self.__shared_resource.params["MSPM Connected"] = True #Interface variable is updated
            
            print("\n\n*******************************" +
                    "\n Connected \n" + "*******************************")
            self.__shared_resource.logger.write("\n*******************************" +
                "\n Connected \n" + "*******************************\n")
        except:
            #If this exception arises, program must be restarted because of connection issues
            self.__shared_resource.logger.write("Connection error. Please restart all the programs\n")
            #self.__shared_resource.Quit = True #Quit set to true to close threads
        

        # Awaiting for message
        while not self.__shared_resource.Quit: #While interface is not closed
            try:
                data = (self.conn.recv(1024)).decode("ascii") #Blocking function to receive a message from client
            except (ConnectionAbortedError, ConnectionResetError, IOError) as e:
                #If error arises then call to reconnect method, i.e., client disconnected
                self.__shared_resource.logger.write("\n"+str(e)) #Interface log printing of error
                self.__shared_resource.params["MSPM Connected"] = False #Connection status update
                if not self.__shared_resource.Quit: #while interface is not closed
                    self.conn = self.reconnect(self.conn) #Try reconnection to client
                else:
                    data = "" #If exception, data is not defined
            
            lineaLog="" #Line of log file initialize
            now = datetime.now().strftime("[%H:%M:%S:%f]")  #Store the current time in a variable 
            lineaLog="T:\t"+ now + "\t" + data[0:len(data)-1] #Give format to the line (Source: [Time] Data)
            #self.print_data_log(self.f,data) 
            
            #Definition of replies depending on message data received from client
            if data == "STATE?\n": #Status Register request
                reply = str(self.__shared_resource.get_SR().get_value()) + "\n"
            elif data == "*IDN?\n": #System name ID request
                reply = "ROBOT_PREMO, V1.0" + "\n"
            elif data == "*IDN_LASER?\n": #Laser ID request
                reply = "LASER_MARKER_PREMO, V1.0" + "\n"
            elif data == "ERR_REG?\n": #Error register request
                reply = str(self.__shared_resource.get_ER().get_value()) + "\n"
            elif data == "DUT_SERIAL_NB?\n": #DUT Serial number request
                sn_file_route = "sc/serial_number/serial_number.txt" #Route of the file containing the serial number
                sn_file = open(sn_file_route,"r") #Open file
                reply = sn_file.readline() + "\n" #Read from file and attach \n
                sn_file.close() #Close file
            else:
                reply = "ACK\n"
                self.__shared_resource.add_order(data) #Adds the received order to the list
                print("List of orders to execute: ", self.__shared_resource.get_orders())
                self.__shared_resource.logger.write(content=("\nList of orders to execute: "+ str(self.__shared_resource.get_orders())))


            if data != "STATE?\n" and data!= "ERR_REG?\n": #If request is not a register value, we print information
                print("I sent a message back in response to: ",data)
                self.__shared_resource.logger.write("\nI sent a message back in response to: "+data)
                print("\n\tReply: ", reply)
                self.__shared_resource.logger.write("\n\tReply: "+reply)

            try:
                self.conn.send(reply.encode("ascii")) #Sends the encoded reply to the client
                now = datetime.now().strftime("[%H:%M:%S:%f]") #Store the current time in a variable            
                lineaLog=lineaLog+"\tR:\t"+ now + "\t" + reply[0:len(reply)-1]+ "\n" #Log line is updated
                self.print_data_log(self.f,lineaLog) #Print file

            except (ConnectionAbortedError, ConnectionResetError, IOError) as e: #Again exception handling
                #If no connection, reconnect
                self.__shared_resource.logger.write("\n"+str(e))
                self.__shared_resource.params["MSPM Connected"] = False
                if not self.__shared_resource.Quit:
                    self.conn = self.reconnect(self.conn)
        self.f.close() #Once loop is finished, file is closed
    
    def reconnect(self,conn:socket):
        conn.close() #Close previous created connection
        print("\nClient was disconnected")
        self.__shared_resource.logger.write("\nClient was disconnected")
        self.__s = socket(AF_INET, SOCK_STREAM) #Creates an instance again
        print("\nRe-creating socket")
        self.__shared_resource.logger.write("\nRe-creating socket")
        self.__s.bind(self.__address) #Bind the addres to the socket
        self.__s.listen(1) #Stablishes a passive socket (server)
        print("\nWaiting to connect")
        self.__shared_resource.logger.write("\nWaiting to connect")
        while not self.__shared_resource.Quit:
            try:
                (conn, addr) = self.__s.accept() #Waits for incoming connections
                conn.settimeout(None)
                self.__shared_resource.params["MSPM Connected"] = True
                break;
            except:
                pass;

        print("*******************************" +
            "\n Connected \n" + "*******************************")
        self.__shared_resource.logger.write("\n*******************************" +
        "\n Connected \n" + "*******************************\n")
        return conn #Returns new socket object

    def print_data_log(self,file : TextIOWrapper,data):
        file.write(data) #Write in the file
        file.flush() #Avoid blank files when writing

    def end_connection(self): #Unblock socket methods (accept and recv). Simply close socket
        s = socket(AF_INET, SOCK_STREAM)
        try:
            self.conn.setblocking(False)
        except:
            pass
        try:
            s.connect(self.__address)
            reply="ACK\n"
            s.send(reply.encode("ascii"))
        except:
            pass
        try:
            reply="ACK\n"
            s.send(reply.encode("ascii"))
        except:
            pass
        try:
            self.conn.close() #Close already connected socket
        except:
            pass
        self.__s.close() #Tries closing non-connected socket
        
            

        
        

