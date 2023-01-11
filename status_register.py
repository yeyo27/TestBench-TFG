from threading import Semaphore

class Status_Register:

    __SR: int #This is the register value
    __semaphore_SR: Semaphore #Semaphore to synchronize events

    def __init__(self):
        self.__SR = 0
        self.__semaphore_SR = Semaphore(1)

    def __int_to_bin(self, num: int):
        #Transforms an integer into a 16-bits binary number.
        #Its range is from 0 to 65535 with big endian format).
        # Returns a string with the 16-bit number.
        bin_n = bin(num)[2:]
        while (15-len(bin_n)) >= 0:
            bin_n = "0" + bin_n
        return bin_n

    def __bin_to_int(self, num: str):
        #Receives a string number and transforms it into a binary number.
        #It consists of a casting from binary string to integer with base 2.
        return int(num, 2)

    def __reverse_bin_bit(self, num_bin: str, index: int):
        #Reverses a specific binary number (0 into 1 and 1 into 0) from a string, according to the index parameter.
        #The result is the input number with the index position bit reversed as a string variable
        list_num = [char for char in num_bin]
        N = len(list_num)-1
        list_num[N - index] = "0" if list_num[N - index] == "1" else "1"

        return "".join(list_num)

    def __change_bin_bit(self, num_bin: str, index: int, bit_value: int):
        #Changes the value of a binary number, according to index (position in the base binary number) and bit_value (1 or 0).
        list_num = [char for char in num_bin]
        N = len(list_num)-1
        list_num[N - index] = str(bit_value)

        return "".join(list_num)


    def change_bit_from_int(self, index: int, bit_value: int):
        #This method calls the function int_to_bin to do a cast from integer to binary, after acquiring a resource from the semaphore.
        #Once we have the binary number, one bit is changed according to the specified index, using change_bin_bit.
        #Finally, the status register turns into an integer again and the previously acquired resource is released.
        self.__semaphore_SR.acquire()
        self.__SR = self.__bin_to_int(self.__change_bin_bit(self.__int_to_bin(self.__SR), index, bit_value))
        self.__semaphore_SR.release()

    def reverse_bit_from_int(self, index: int):
        #Same philosophy as change_bit_from_int
        self.__semaphore_SR.acquire()
        self.__SR = self.__bin_to_int(self.__reverse_bin_bit(self.__int_to_bin(self.__SR), index))
        self.__semaphore_SR.release()

    def get_value(self) -> int:
        #Acquires a resource, saves the attribute __SR in a variable and releases the acquired resource.
        self.__semaphore_SR.acquire()
        sr = self.__SR
        self.__semaphore_SR.release()
        return sr