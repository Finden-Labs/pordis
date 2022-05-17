from common.constants import Constants
from common.crypto import Crypto

class Net:
    def ReceiveAll(socket) -> bytes:
        complete_message = b""
        while len(complete_message) == 0 or len(complete_message) < int.from_bytes(complete_message[:4], "little"):
            complete_message += socket.recv(4096)
            if complete_message == b"":
                return False # Socket disconnected.

        if Constants.DEBUG_ON:
            print("Received " + str(len(complete_message)) + " raw bytes.")
        
        return complete_message
    
    def SendAll(socket, data):
        bytes_sent = 0
        while bytes_sent < len(data):
            bytes_sent += socket.send(data)

        if Constants.DEBUG_ON:
            print("Sent " + str(bytes_sent) + " raw bytes.")

        return bytes_sent

    def Unpack(received_data: bytes, user=None):
        if not received_data:
            return False
        
        # Strip total data length
        received_data = received_data[4:]

        if user and user.encryption_enabled:
            received_data = Crypto.Decrypt(received_data, user.shared_secret)
        
        command_length = int.from_bytes(received_data[:4], "little")
        command = received_data[4:4 + command_length]
        payload_length = int.from_bytes(received_data[4 + command_length:4 + command_length + 4], "little")
        payload = received_data[4 + command_length + 4:4 + command_length + 4 + payload_length]

        if Constants.DEBUG_ON:
            print("Received " + command.decode("utf-8") + " (" + str(command_length) + ") " + str(payload_length) + " bytes.")
        
        return command, payload
    
    def Pack(command: bytes, payload: bytes, user=None):
        unencrypted_segment = len(command).to_bytes(4, "little") + command + len(payload).to_bytes(4, "little") + payload

        if Constants.DEBUG_ON:
            print("Sending " + command.decode("utf-8") + " (" + str(len(command)) + ") " + str(len(payload)) + " bytes.")

        if user and user.encryption_enabled:
            encrypted_segment = Crypto.Encrypt(unencrypted_segment, user.shared_secret)
            return len(encrypted_segment).to_bytes(4, "little") + encrypted_segment
        else:
            return len(unencrypted_segment).to_bytes(4, "little") + unencrypted_segment