import os, types, socket, time
from datetime import datetime

from common.crypto import Crypto
from common.user import User
from common.constants import Constants
from common.net import Net
from common.files import Files
from server.clienthandler import ClientHandler

def run_server_threaded():
    server = Server()
    server.start()

class Server():
    def __init__(self):
        self.done = False
        self.last_send = 0
        self.shared_secret_half = os.urandom(16)
        self.user_list = []
        self.socket_users = {}
        self.kick_cooldowns = {}
        self.config = {}

    def start(self):
        self.log("Loading RSA keys...", False)
        Crypto.LoadKeys()
        self.log("done.", True, False)

        self.load_configuration()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(("0.0.0.0", int(self.config["server_port"])))
            server_socket.listen()
            self.log("Server now listening. Press CTRL+BREAK to interrupt.")

            try:
                while not self.done:
                    time.sleep(0.01)
                    new_socket, addr = server_socket.accept()
                    if addr[0] in Files.ReadListFile("banned_ips.txt"):
                        Net.SendAll(new_socket, Net.Pack(Constants.CMD_PLAINMSG, b"\nYou have been banned permanently.\n"))
                        new_socket.close()
                    elif addr[0] in self.kick_cooldowns:
                        if time.time() >= self.kick_cooldowns[addr[0]]:
                            del self.kick_cooldowns[addr[0]]
                        else:
                            Net.SendAll(new_socket, Net.Pack(Constants.CMD_PLAINMSG, b"\nYou have been banned for " + str(self.config["kick_duration"] or 60).encode("utf-8") + b" minutes.\n"))
                            new_socket.close()
                    else:
                        self.log("New connection from " + addr[0] + ".")
                        ClientHandler(self, new_socket, addr).start()
            except KeyboardInterrupt:
                self.done = True
            
            for user in self.user_list:
                user.disconnect()

    def load_configuration(self):
        self.config = Files.ReadIniFile("conf/server_configuration.ini")

    def broadcast(self, command: bytes, payload: bytes, exclude_users=[]):
        for user in self.user_list:
            if user not in exclude_users:
                self.send(user, command, payload)

    def send(self, user, command, payload = b"", throttle=True):
        if throttle and time.time() - self.last_send < 0.1:
            time.sleep(0.1)

        data = Net.Pack(command, payload, user)
        Net.SendAll(user.socket, data)
        self.last_send = time.time()
    
    def on_user_list_changed(self):
        self.broadcast(Constants.CMD_USER_LIST, self.serialize_user_list())
    
    def serialize_user_list(self) -> bytes:
        output = b""
        for user in self.user_list:
            output += user.unique_id + len(user.username).to_bytes(4, "little") + user.username + (1 if user.is_admin else 0).to_bytes(1, "little")
        return output

    def log(self, text: str, new_line=True, timestamp=True):
        print(("[" + datetime.now().strftime("%d/%m/%Y %H:%M:%S") + "] " if timestamp else "") + text, end="\n" if new_line else "")

    def kick_user(self, kicked_user):
        self.kick_cooldowns[kicked_user.address[0]] = time.time() + (int(self.config["kick_duration"]) or 60) * 60
        kicked_user.connection_thread.disconnect = True
    
    def is_user_admin(self, user):
        if user.username.decode("utf-8") + "@" + user.address[0] in Files.ReadListFile("admins.txt"):
            return True
        else:
            return False

    def ban_user(self, banned_user):
        banned_users = Files.ReadListFile("banned_ips.txt")
        banned_users.append(banned_user.address[0])
        Files.WriteListFile("banned_ips.txt", banned_users)
        banned_user.connection_thread.disconnect = True

    def parse_message(self, user, data):
        command, payload = Net.Unpack(data, user)

        if command == Constants.CMD_STOREKEY:
            self.log("Received public key from " + user.address[0] + ".")
            user.public_key = Crypto.ImportPublicKey(payload)

        elif command == Constants.CMD_STORESECRET:
            self.log("Received shared secret half from " + user.address[0] + ".")
            client_shared_secret_half = Crypto.RSADecrypt(payload)[:16]
            user.shared_secret = self.shared_secret_half + client_shared_secret_half
            self.send(user, Constants.CMD_STORESECRET, Crypto.RSAEncrypt(self.shared_secret_half, user.public_key))

        elif command == Constants.CMD_ENABLEENCRYPTION:
            self.log("Received request to enable encryption from " + user.address[0] + ".")
            self.send(user, Constants.CMD_ENABLEENCRYPTION)
            user.encryption_enabled = True

        elif command == Constants.CMD_KICK:
            if not self.is_user_admin(user):
                self.send(user, Constants.CMD_SERVERCHAT, b"You are not an admin (" + user.username + b"@" + user.address[0].encode("utf-8") + b").")
            elif not payload:
                self.send(user, Constants.CMD_SERVERCHAT, b"You must specify a user ID.")
            else:
                kicked_user = next((user for user in self.user_list if int.from_bytes(user.unique_id, "little") == int(payload.decode("utf-8"))), None)
                if kicked_user == user:
                    self.send(user, Constants.CMD_SERVERCHAT, b"You can't run this command on yourself.")
                elif kicked_user:
                    self.send(kicked_user, Constants.CMD_SERVERCHAT, b"You have been kicked.")
                    self.kick_user(kicked_user)
                else:
                    self.send(user, Constants.CMD_SERVERCHAT, b"User not found.")

        elif command == Constants.CMD_BAN:
            if not self.is_user_admin(user):
                self.send(user, Constants.CMD_SERVERCHAT, b"You are not an admin.")
            elif not payload:
                self.send(user, Constants.CMD_SERVERCHAT, b"You must specify a user ID.")
            else:
                banned_user = next((user for user in self.user_list if int.from_bytes(user.unique_id, "little") == int(payload.decode("utf-8"))), None)
                if banned_user == user:
                    self.send(user, Constants.CMD_SERVERCHAT, b"You can't run this command on yourself.")
                elif banned_user:
                    self.send(banned_user, Constants.CMD_SERVERCHAT, b"You have been banned.")
                    self.ban_user(banned_user)
                else:
                    self.send(user, Constants.CMD_SERVERCHAT, b"User not found.")

        elif command == Constants.CMD_TOGGLE_ADMIN:
            if not self.is_user_admin(user):
                self.send(user, Constants.CMD_SERVERCHAT, b"You are not an admin.")
            elif not payload:
                self.send(user, Constants.CMD_SERVERCHAT, b"You must specify a user ID.")
            else:
                other_user = next((user for user in self.user_list if int.from_bytes(user.unique_id, "little") == int(payload.decode("utf-8"))), None)
                
                if other_user == user:
                    self.send(user, Constants.CMD_SERVERCHAT, b"You can't run this command on yourself.")
                elif other_user:
                    other_user.is_admin = not other_user.is_admin
                    other_user_line = other_user.username.decode("utf-8") + "@" + other_user.address[0]
                    admin_list = Files.ReadListFile("admins.txt")

                    if other_user.is_admin:
                        if not other_user_line in admin_list:
                            admin_list.append(other_user_line)
                        self.send(user, Constants.CMD_SERVERCHAT, other_user.username + b" is now an admin.")
                        self.send(other_user, Constants.CMD_SERVERCHAT, b"You are now an admin.")
                    else:
                        if other_user_line in admin_list:
                            admin_list.remove(other_user_line)
                        self.send(user, Constants.CMD_SERVERCHAT, other_user.username + b" is no longer an admin.")
                        self.send(other_user, Constants.CMD_SERVERCHAT, b"You are no longer an admin.")

                    Files.WriteListFile("admins.txt", admin_list)

                    self.broadcast(Constants.CMD_USER_LIST, self.serialize_user_list())

        elif command == Constants.CMD_USER:
            self.log("Received username " + payload.decode("utf-8") + " from " + user.address[0] + ".")

            if payload.decode("utf-8") + "@" + user.address[0] in Files.ReadListFile("admins.txt"):
                user.is_admin = True
            else:
                user.is_admin = False

            if user.username:
                self.broadcast(Constants.CMD_SERVERCHAT, user.username + b" is now known as " + payload)
            else:
                self.broadcast(Constants.CMD_SERVERCHAT, payload + b" has joined the chat.")
                self.send(user, Constants.CMD_USER_ID, user.unique_id)
                if os.path.exists("motd.txt"):
                    with open("motd.txt", "r") as f:
                        self.send(user, Constants.CMD_MOTD, b"\n" + f.read().encode("utf-8") + b"\n")
            user.username = payload
            self.on_user_list_changed()

        elif command == Constants.CMD_CHAT:
            self.log("Received chat message from " + user.address[0] + ".")
            chat_message = user.username + b": " + payload
            self.log(chat_message.decode("utf-8"))
            self.broadcast(Constants.CMD_CHAT, chat_message)

        else:
            self.log("Received unknown command from " + user.address[0] + ": " + command)


