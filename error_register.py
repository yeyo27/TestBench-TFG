from threading import Semaphore
#This module use exactly the same attributes and methods of status_register.py
#For further information, please refer to status_register.py
class Error_Register:
    __ER: int #Register value
    __semaphore_ER: Semaphore #Semaphore to synchronize events

    def __init__(self):
        self.__ER = 0
        self.__semaphore_ER = Semaphore(1)

    def __int_to_bin(self, num: int):
        bin_n = bin(num)[2:]
        while (15-len(bin_n)) >= 0:
            bin_n = "0" + bin_n
        return bin_n

    def __bin_to_int(self, num: str):
        return int(num, 2)

    def __reverse_bin_bit(self, num_bin: str, index: int):
        list_num = [char for char in num_bin]
        N = len(list_num)-1
        list_num[N - index] = "0" if list_num[N - index] == "1" else "1"

        return "".join(list_num)

    def __change_bin_bit(self, num_bin: str, index: int, bit_value: int):
        list_num = [char for char in num_bin]
        N = len(list_num)-1
        list_num[N - index] = str(bit_value)

        return "".join(list_num)

    def reverse_bit_from_int(self, index: int):
        self.__semaphore_ER.acquire()
        self.__ER = self.__bin_to_int(self.__reverse_bin_bit(self.__int_to_bin(self.__ER), index))
        self.__semaphore_ER.release()

    def change_bit_from_int(self, index: int, bit_value: int):
        self.__semaphore_ER.acquire()
        self.__ER = self.__bin_to_int(self.__change_bin_bit(self.__int_to_bin(self.__ER), index, bit_value))
        self.__semaphore_ER.release()

    def get_value(self) -> int:
        self.__semaphore_ER.acquire()
        er = self.__ER
        self.__semaphore_ER.release()
        return er