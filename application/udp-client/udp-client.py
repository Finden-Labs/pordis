import socket, threading
from socket import *
# from common.files import Files

class UDPClient:
    def __init__(self):
        self.networking_thread = None
        self.stop_networking_thread = False
        self.last_send = 0
        #self.load_configuration()

    def load_configuration(self):
        # self.config = Files.ReadIniFile("conf/udp_client_configuration.ini")
        exit
    
    # read config files, connect to server
    def start(self):
        s = socket(AF_INET,SOCK_DGRAM)
        #host = self.config.server_address
        # port = self.config.server_port
        host = "0.0.0.0"
        port = 61123
        buf = 1024
        addr = (host,port)

        file_name=b'hello_world.txt' # get filename from client.py
        s.sendto(file_name,addr)

        f=open(file_name,"rb")
        data = f.read(buf)
        while (data):
            if(s.sendto(data,addr)):
                print("sending ...")
                data = f.read(buf)
        s.close()
        f.close()
        print("Successfully sent file")

client = UDPClient()
client.start()