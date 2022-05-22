import socket, time, sys
from socket import *
from common.files import Files
from common.net import Net
from common.constants import Constants
from datetime import datetime

def run_udp_server_threaded():
    server = UDPServer()
    server.start()

class UDPServer():
    def __init__(self):
        self.done = False
        self.load_configuration()

    def start(self):
        with socket(AF_INET, SOCK_DGRAM) as s:
            #host = self.config.server_address
            #port = self.config.server_port
            host = "127.0.0.1"
            port = 61123
            addr = (host,port)
            buf = 1024
            s.bind(addr)

            self.log("Server now listening. Press CTRL+BREAK to interrupt.")
            try:
                while not self.done:
                    time.sleep(0.01)
                    data = s.recvfrom(buf)
                    msg = data[0]
                    client_src = data[1] 
                    self.log("File Downloaded; God is GREAT!")
            except KeyboardInterrupt:
                self.done = True

    def load_configuration(self):
        self.config = Files.ReadIniFile("conf/udp_server_configuration.ini") # fix

    def log(self, text: str, new_line=True, timestamp=True):
        print(("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] " if timestamp else "") + text, end="\n" if new_line else "")
run_udp_server_threaded()