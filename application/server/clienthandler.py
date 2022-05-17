import threading, os

from common.constants import Constants
from common.net import Net
from common.user import User
from common.crypto import Crypto

class ClientHandler(threading.Thread):
    def __init__(self, server, socket, addr):
        super().__init__()
        self.disconnect = False
        self.server = server
        self.socket = socket
        self.user = User()
        while not self.user.unique_id or self.user.unique_id in map(lambda user: user.unique_id, self.server.user_list):
            self.user.unique_id = os.urandom(2)
            if Constants.DEBUG_ON:
                self.server.log("User ID is " + str(int.from_bytes(self.user.unique_id, "little")))
        self.user.address = addr
        self.user.socket = socket
        self.user.connection_thread = self
        self.server.user_list.append(self.user)

        self.server.send(self.user, Constants.CMD_STOREKEY, Crypto.ExportPublicKey())
    
    def run(self):
        while not self.disconnect:
            try:
                received_data = Net.ReceiveAll(self.user.socket)
                if received_data:
                    self.server.parse_message(self.user, received_data)
                else:
                    self.server.log("Lost connection from " + self.user.address[0] + ".")
                    break
            except OSError:
                self.server.log("Lost connection from " + self.user.address[0] + ".")
                break
            except:
                pass
        
        self.user.socket.close()
        self.server.user_list.remove(self.user)
        self.server.on_user_list_changed()