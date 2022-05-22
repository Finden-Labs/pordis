import tkinter as tk
import socket, os, selectors, threading, types, time

from tkinter import *
from tkinter.ttk import *
from tkinter.filedialog import askopenfile 
from common.net import Net
from common.constants import Constants
from common.crypto import Crypto
from common.user import User
from client.mainwindow import MainWindow
from common.files import Files

# handles client connection, monitors for incoming socket data every 0.01 sec
class NetworkingThread(threading.Thread):
    def __init__(self, client):
        super().__init__()
        self.client = client
    
    # read config files, connect to server
    def run(self):
        self.client.log("Connecting to " + self.client.config["server_address"] + ":" + self.client.config["server_port"] + "...")
        self.client.user.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.user.socket.settimeout(10)
        try:
            self.client.user.socket.connect((self.client.config["server_address"], int(self.client.config["server_port"])))
        except:
            self.client.log("Connection failed.")
            return

        self.client.log("Connected.")

        self.client.user.encryption_enabled = False
        self.client.user.socket.setblocking(False)
        data = types.SimpleNamespace(inb=b"", outb=b"")
        self.client.selector.register(self.client.user.socket, selectors.EVENT_READ | selectors.EVENT_WRITE, data=data)
        
        # check socket every millisecond for new data
        while not self.client.stop_networking_thread:
            time.sleep(0.01)
            events = self.client.selector.select()
            for key, mask in events:
                sock = key.fileobj

                if mask & selectors.EVENT_READ:
                    received_data = Net.ReceiveAll(sock)
                    
                    # if the socket receives new data...
                    if received_data:
                        self.client.parse_message(received_data)
                    else:
                        self.client.log("Server connection closed.")
                        self.client.stop_networking_thread = True
                if mask & selectors.EVENT_WRITE and data.outb:
                    sock.send(data.outb)
        
        self.client.selector.unregister(sock)
        self.client.user.disconnect()

class Client:
    def __init__(self):
        self.networking_thread = None
        self.stop_networking_thread = False
        self.last_send = 0
        self.selector = selectors.DefaultSelector()
        self.shared_secret_half = os.urandom(16)
        self.server_public_key = ""

        self.window = tk.Tk()
        self.window.resizable(False, False)
        self.window.title("")
        self.load_configuration()
        self.main_window = MainWindow(self, self.config["font_size"])
        Crypto.LoadKeys()
        
        if int(self.config["connect_on_startup"]):
            self.connect_to_server()
        else:
            self.log("You can use the /connect [host] command to connect to a server.", True)
            self.log("Write /help for more commands.", True)

        self.window.mainloop()
        self.disconnect_from_server()

    def load_configuration(self):
        self.user_list = []
        self.config = Files.ReadIniFile("conf/client_configuration.ini")
        self.bookmarks = Files.ReadIniFile("conf/bookmarks.ini")
        
        self.user = User(self.config["username"].encode("utf-8"))

    def disconnect_from_server(self):
        self.stop_networking_thread = True
        if self.networking_thread and self.networking_thread.is_alive():
            self.networking_thread.join()
            self.log("Disconnected.")

    def connect_to_bookmark(self, bookmark_name):
        if self.bookmarks and self.bookmarks[bookmark_name]:
            if ":" in self.bookmarks[bookmark_name]:
                self.config["server_address"] = self.bookmarks[bookmark_name].split(":")[0]
                self.config["server_port"] = self.bookmarks[bookmark_name].split(":")[1]
            else:
                self.config["server_address"] = self.bookmarks[bookmark_name]
            self.connect_to_server()
        else:
            self.log("Unknown bookmark.")

    def connect_to_server(self):
        self.disconnect_from_server()

        self.stop_networking_thread = False
        self.networking_thread = NetworkingThread(self)
        self.networking_thread.start()

    def log(self, text: str, brief=False):
        if Constants.DEBUG_ON:
            print(text)
        if brief:
            self.main_window.append_to_chat_log(text.encode("utf-8"), False, False)
        else:
            self.main_window.append_to_chat_log(text.encode("utf-8"), True)

    def unserialize_user_list(self, payload: bytes) -> list:
        list = []
        offset = 0
        while offset < len(payload):
            username_length = int.from_bytes(payload[offset+2:offset+6], "little")
            list.append({
                "unique_id": payload[offset:offset + 2],
                "username": payload[offset+6:offset+6+username_length],
                "admin": bool(payload[offset+6+username_length])
            })
            offset += 12 + username_length
        return list

    def parse_message(self, data):
        command, payload = Net.Unpack(data, self.user)
        # to do: https://www.educative.io/edpresso/what-is-the-python-struct-module
        # https://www.codingem.com/python-else-in-loop/
        if command == Constants.CMD_STOREKEY:
            self.log("Initiated encryption handshake with server.")
            self.server_public_key = Crypto.ImportPublicKey(payload)
            self.send(Constants.CMD_STOREKEY, Crypto.ExportPublicKey())
            self.send(Constants.CMD_STORESECRET, Crypto.RSAEncrypt(self.shared_secret_half, self.server_public_key))
        elif command == Constants.CMD_STORESECRET:
            self.log("Received keys from server.")
            server_shared_secret_half = Crypto.RSADecrypt(payload)[:16]
            self.user.shared_secret = server_shared_secret_half + self.shared_secret_half
            self.send(Constants.CMD_ENABLEENCRYPTION)
        elif command == Constants.CMD_ENABLEENCRYPTION:
            self.log("Connection is now encrypted.")
            self.user.encryption_enabled = True
            self.send(Constants.CMD_USER, self.user.username)
        elif command == Constants.CMD_CHAT:
            self.main_window.append_to_chat_log(payload)
        elif command == Constants.CMD_SERVERCHAT:
            self.main_window.append_to_chat_log(payload, True)
        elif command == Constants.CMD_USER_ID:
            self.user.unique_id = int.from_bytes(payload, "little")
        elif command == Constants.CMD_MOTD:
            self.main_window.append_to_chat_log(payload, False, False)
        elif command == Constants.CMD_USER_LIST:
            self.user_list = self.unserialize_user_list(payload)
            self.user.is_admin = False
            
            for user in self.user_list:
                if int.from_bytes(user["unique_id"], "little") == self.user.unique_id and user["admin"]:
                    self.user.is_admin = True
            self.main_window.on_user_list_changed()
        elif command == Constants.CMD_PLAINMSG:
            self.log(payload.decode("utf-8"), True)
        elif Constants.DEBUG_ON:
            print("Received unknown command from server: " + command.decode("utf-8"))

    def do_command(self, command: str):
        parameters = ""
        if len(command.split(" ", 1)) > 1:
            parameters = command.split(" ", 1)[1]
        command = command.split(" ", 1)[0]

        # This should probably be moved to the server using a generic CMD_CHATCOMMAND for simplicity and maintainability
        if command =="/help":
            self.log("\n***********************\n", True)
            self.log("\nAvailable chat commands:", True)
            self.log("/connect [host] to connect to a server. You can specify a port number.", True)
            self.log("/connectbmark [bookmarkname] to connect to a bookmarked server.", True)
            self.log("/bmark [name] [address] to bookmark a server.", True)
            self.log("You can edit conf/bookmarks.ini to bookmark your servers.", True)
            self.log("/disconnect to close the connection.", True)
            self.log("/nick [username] to change your name.", True)
            self.log("\nYou can edit the file conf/client_configuration.ini to connect to a server automatically.\n", True)

            if self.user.is_admin:
                self.log("\nYou can configure the server settings in conf/server_configuration.ini.", True)
                self.log("The number you see next to the user names are their IDs.", True)
                self.log("/admin [ID] to toggle a user's admin status.", True)
                self.log("/kick [ID] to kick a user.", True)
                self.log("/ban [ID] to ban a user permanently.", True)

            self.log("\n***********************\n", True)

        elif command =="/bmark":
            if parameters and len(parameters.split(" ")) == 2:
                parameters = parameters.split(" ")
                self.bookmarks[parameters[0]] = parameters[1]
                Files.WriteIniFile("conf/bookmarks.ini", self.bookmarks)
            else:
                self.log("Needs to be '/bmark [name] [address]' with an optional port number.", True)
                return False
        elif command == "/nick":
            new_nick = parameters.encode("utf-8")
            self.send(Constants.CMD_USER, new_nick)
            self.user.username = new_nick
        elif command == "/disconnect":
            self.disconnect_from_server()
        elif command == "/connect":
            if parameters:
                self.config["server_address"] = parameters
            self.connect_to_server()
        elif command == "/connectbmark":
            if not parameters:
                self.log("No bookmark name specified. Must be one of: " + " ".join([line.split("=")[0] for line in Files.ReadIniFile("conf/bookmarks.ini")]), True)
                return False
            self.connect_to_bookmark(parameters)
        elif command == "/kick":
            self.send(Constants.CMD_KICK, parameters.encode("utf-8"))
        elif command == "/ban":
            self.send(Constants.CMD_BAN, parameters.encode("utf-8"))
        elif command == "/admin":
            self.send(Constants.CMD_TOGGLE_ADMIN, parameters.encode("utf-8"))
        else:
            self.log("Unknown command.", True)
        
        return True

    def on_chat_input(self, message):
        if message[0] == "/":
            return self.do_command(message)
        else:
            self.send(Constants.CMD_CHAT, message.encode("utf-8"))
        
        return True

    def send(self, command, payload = b"", throttle=True):
        if not self.user.socket:
            self.log("You are not connected.")
            return
        
        if throttle and time.time() - self.last_send < 0.1:
            if Constants.DEBUG_ON:
                print("Throttling.")
            time.sleep(0.1)

        data = Net.Pack(command, payload, self.user)
        bytes_sent = 0

        if Constants.DEBUG_ON:
            print("Sending " + str(len(data) - bytes_sent) + " bytes...", end="\r")
        while bytes_sent < len(data):
            bytes_sent += self.user.socket.send(data)
            if Constants.DEBUG_ON:
                print("Sending " + str(len(data) - bytes_sent) + " bytes...", end="\r")

        self.last_send = time.time()

        if Constants.DEBUG_ON:
            print("Sent " + str(bytes_sent) + " bytes.                  ")