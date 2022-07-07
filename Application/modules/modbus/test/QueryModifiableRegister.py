import os
import threading
import struct
from time import sleep
from System.Core.Global import *
from System.Core.Colors import *
from System.Core.Modbus import *
from System.Lib import ipcalc


class Module:
    info = {
        "Name": "Query Modifiable Register",
        "Author": ["maqi"],
        "Description": "Query Modifiable Register",
    }
    options = {
        "RHOSTS": ["192.168.233.74", True, "The target address range or CIDR identifier"],
        "RPORT": [21502, False, "The port number for modbus protocol"],
        "UID": [1, True, "Modbus Slave UID."],
        "Quantity": ["0x0002", True, "Registers Values."],
        "Threads": [1, False, "The number of concurrent threads"],
        "Output": [True, False, "The stdout save in output directory"],
    }
    output = ""
    address = []

    def exploit(self):

        moduleName = self.info["Name"]
        print(
            bcolors.OKBLUE + "[+]" + bcolors.ENDC + " Module " + moduleName + " Start"
        )
        ips = list()
        for ip in ipcalc.Network(self.options["RHOSTS"][0]):
            ips.append(str(ip))
        while ips:
            for i in range(int(self.options["Threads"][0])):
                if len(ips) > 0:
                    thread = threading.Thread(target=self.do, args=(ips.pop(0),))
                    thread.start()
                    THREADS.append(thread)
                else:
                    break
            for thread in THREADS:
                thread.join()
        if self.options["Output"][0]:
            open(
                mainPath
                + "/Output/"
                + moduleName
                + "_"
                + self.options["RHOSTS"][0].replace("/", "_")
                + ".txt",
                "a",
            ).write("=" * 30 + "\n" + self.output + "\n\n")
        self.output = ""

    def printLine(self, str, color):
        self.output += str + "\n"
        if str.find("[+]") != -1:
            print(str.replace("[+]", color + "[+]" + bcolors.ENDC))
        elif str.find("[-]") != -1:
            print(str.replace("[-]", color + "[+]" + bcolors.ENDC))
        else:
            print(str)

    def do(self, ip):
        c = connectToTarget(ip, self.options["RPORT"][0])
        if c == None:
            self.printLine("[-] Modbus is not running on : " + ip, bcolors.WARNING)
            return None
        self.printLine("[+] Connecting to " + ip, bcolors.OKGREEN)
        for i in range(0x0800, 0x09f2, int(self.options["Quantity"][0], 16)):
            # 读两个寄存器
            ans = c.sr1(
                ModbusADU(transId=getTransId(), unitId=int(self.options["UID"][0]))
                / ModbusPDU03_Read_Holding_Registers(
                    startAddr=int(self.options["StartAddr"][0], 16),
                    quantity=int(self.options["Quantity"][0], 16),
                ),
                timeout=timeout,
                verbose=0,
            )
            ans = ModbusADU_Answer(bytes(ans))
            read_1 = struct.unpack('>f', bytes(ans)[-4:])[0]
            # 写两个寄存器
            write_1 = read_1 + 1
            ans = c.sr1(
                ModbusADU(transId=getTransId(), unitId=int(self.options["UID"][0]))
                / ModbusPDU10_Write_Multiple_Registers(
                    startAddr=int(self.options["StartAddr"][0], 16),
                    quantity=int(self.options["Quantity"][0], 16),
                    outputsValue=struct.pack('>f', write_1)
                ),
                timeout=timeout,
                verbose=0,
            )
            ans = ModbusADU_Answer(bytes(ans))
            sleep(2)
            # 读两个寄存器
            ans = c.sr1(
                ModbusADU(transId=getTransId(), unitId=int(self.options["UID"][0]))
                / ModbusPDU03_Read_Holding_Registers(
                    startAddr=int(self.options["StartAddr"][0], 16),
                    quantity=int(self.options["Quantity"][0], 16),
                ),
                timeout=timeout,
                verbose=0,
            )
            ans = ModbusADU_Answer(bytes(ans))
            read_2 = struct.unpack('>f', bytes(ans)[-4:])[0]
            print(f'read_1:{read_1},read_2:{read_2}')
            if write_1 == read_2:
                print(f"{hex(i)} address can be modifiable!")
                self.address.append(hex(i))
            print(self.address)
            self.address.clear()
