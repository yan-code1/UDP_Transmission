# Library Imports
import hashlib
import socket
import struct

'''
This part of the file defines some functions that we need to set up.
Functions:
    - create_checksum(packet)                                               Create a checksum with the hashlib library. Function is prebuilt. 
    - formatPacket(ack_number, seq_number, data_to_send, checksum)          Format packet into a structure appropriate to send. 
    - formatMessage(ack_number, seq_number, data_to_send)                   Simple function to print the packet data. 
    - sendData(ack_number, seq_number, data_to_send)                        Se=nd the data through to the server. 
'''

# Define a function to create a checksum.
class UDT_client:
    def __init__(self,address = ('127.0.0.1',8080)):
        # Create a socket.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.RECEIVER_ADDRESS = address

    def create_checksum(self,packet):
        return bytes(hashlib.md5(packet).hexdigest(), encoding='UTF-8')

    # Define a function to create a structure in the packet format.
    def formatPacket(self,ack_number, seq_number, data_to_send, checksum):
        # Encode the data.
        data_to_send = data_to_send.encode()
        data_values = [ack_number, seq_number, data_to_send]
        # Add a checksum if needed.
        if not checksum == None:
            data_values.append(checksum)
            return struct.Struct('I I 8s 32s').pack(*data_values)
        else:
            return struct.Struct('I I 8s').pack(*data_values)

    # Define a function to format the packet to print.
    def formatMessage(self,ack_number, seq_number, data_to_send):
        print("{ ack_number: ", ack_number, ", sequence_num: ", seq_number, ", data: " , data_to_send, " }")

    # Define a function to actually send the data.
    def sendData(self,ack_number, seq_number, data_to_send):
        # Calculate the required checksums.
        checksum = self.create_checksum(self.formatPacket(ack_number, seq_number, data_to_send, None))
        packet_data_final = self.formatPacket(ack_number, seq_number, data_to_send, checksum)
        # Create a socket.
        # sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Send packet.
        self.sock.sendto(packet_data_final, self.RECEIVER_ADDRESS)
        # Print with formatting.
        print("Packet being sent to server... ", self.RECEIVER_ADDRESS)
        self.formatMessage(ack_number, seq_number, data_to_send)
        # Set the socket timeout to 9ms.
        self.sock.settimeout(0.009)

        # Use a try catch to execute despite errors.
        try:
            # Accept the data and unpack it.
            data_received, server_address = self.sock.recvfrom(1024)
            packet_recieved = struct.Struct('I I 8s 32s').unpack(data_received)
            # Print an acknowledgement.
            print("Packet was received from server: ", server_address)
            self.formatMessage(packet_recieved[0], packet_recieved[1], packet_recieved[2])
            # Some packet details.
            packet_packed = (packet_recieved[0], packet_recieved[1], packet_recieved[2])
            packet_final = struct.Struct('I I 8s').pack(*packet_packed)
            # Check checksums.
            rec_checksum = self.create_checksum(packet_final)
            exp_checksum = self.create_checksum(self.formatPacket(0, seq_number, data_to_send, None))
            # Verify if the checksums for correctness and take actions.
            if exp_checksum == rec_checksum and packet_recieved[1] == seq_number:
                # Recieved correct data/packet.
                print("Received the corrent packet from the server. ")
            elif exp_checksum == rec_checksum:
                # Corrupt data. Resend packet.
                print("Data was corrupt. Resending the packet. ")
                self.sendData(ack_number, seq_number, data_to_send)
            else:
                print("Data was corrupt. Resending the packet. ")
                # Sequence incorrect. Resend packet.
                self.sendData(ack_number, seq_number, data_to_send)
            return
        # Except part.
        except socket.timeout:
            print("Timeout occured. Packets are being resent. ")
            # 9ms timeout expired. Resend the packet.
            self.sendData(ack_number, seq_number, data_to_send)

'''
This part of the file is the main and executes the functons above. It also sets up some stuff. 
'''
print("Running UDP Client. ")
# Define the connection parameters. Use localhost and port 8080
IP_ADDRESS = '127.0.0.1'
PORT_NUMBER = 8080
RECEIVER_ADDRESS = (IP_ADDRESS, PORT_NUMBER)

# ack is false.
ack_number = 1
seq_number = 0

# Data strings to be sent in a list. 
DATA_TO_SEND = ['NCC-1701', 'NCC-1422', 'NCC-1017']
sock = UDT_client(address=RECEIVER_ADDRESS)
# Loop to send each element of the data list via packets over UDP functions defined above. 
for data in DATA_TO_SEND: 
    sock.sendData(ack_number, seq_number, data)
    # Flip the Seq. 
    seq_number = 1 if seq_number == 0 else 0 

print("All packets have been sent. ")




