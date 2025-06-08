import socket
import threading
import os
from base64 import b64encode
import sys
import random

# Class to handle file transfer as a thread
class FileTransferHandler(threading.Thread):
    def __init__(self, file_name, client_info, transfer_port):
        super().__init__()
        self.target_file = file_name
        # Client information
        self.client_info = client_info

        #define port; block size; and path
        self.comm_port = transfer_port
        self.data_socket = None
        self.block_size = 1000
        self.full_path = os.path.join("server_files", file_name)
        print(f"Initializing file transfer handler for {self.target_file} on port {self.comm_port}...")

    # Set up UDP socket for data transfer
    def setup_connection(self):
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.data_socket.settimeout(5.0)
        self.data_socket.bind(('', self.comm_port))
        print(f"UDP socket setup on port {self.comm_port}.")

    # Process client's file request
    def process_file_request(self):
        if not os.path.exists(self.full_path):
            error_msg = f"FILE {self.target_file} ERR NOT_FOUND"
            self.data_socket.sendto(error_msg.encode(), self.client_info)
            print(f"{self.target_file} not found. Sent error to client.")
            return False
        print(f"{self.target_file} found. Starting transfer.")
        return True
    
    # Handle data transfer to client
    def handle_data_transfer(self, file_obj, file_length):
        while True:
            try:
                incoming_data, client_addr = self.data_socket.recvfrom(1024)
                message = incoming_data.decode().strip()

                if not message.startswith("FILE"):
                    continue

                if "CLOSE" in message:
                    self.data_socket.sendto(
                        f"FILE {self.target_file} CLOSE_OK".encode(),
                        client_addr
                    )
                    print(f"Received CLOSE from {client_addr}. Sent CLOSE_OK.")
                    break

                parts = message.split()
                if len(parts) < 6 or parts[1] != self.target_file:
                    continue

                try:
                    start_pos = int(parts[parts.index("START")+1])
                    end_pos = int(parts[parts.index("END")+1])

                    if start_pos < 0 or end_pos >= file_length or start_pos > end_pos:
                        error_msg = f"FILE {self.target_file} ERR INVALID_RANGE"
                        self.data_socket.sendto(error_msg.encode(), client_addr)
                        continue

                    file_obj.seek(start_pos)
                    data_block = file_obj.read(end_pos - start_pos + 1)

                    if not data_block:
                        error_msg = f"FILE {self.target_file} ERR READ_ERROR"
                        self.data_socket.sendto(error_msg.encode(), client_addr)
                        continue

                    encoded_block = b64encode(data_block).decode()
                    response = (
                        f"FILE {self.target_file} OK START {start_pos} "
                        f"END {end_pos} DATA {encoded_block}"
                    )
                    self.data_socket.sendto(response.encode(), client_addr)
                    print(f"Sent data from {start_pos} to {end_pos} of {self.target_file} to {client_addr}.")

                except (ValueError, IndexError):
                    error_msg = f"FILE {self.target_file} ERR INVALID_FORMAT"
                    self.data_socket.sendto(error_msg.encode(), client_addr)

            except socket.timeout:
                print("Socket timed out. Retrying...")
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")
                break
        print(f"Data transfer for {self.target_file} completed.")
        
    # this is a execution method 
    def run(self):
        self.setup_connection()

        if not self.process_file_request():
            self.data_socket.close()
            print(f"Transfer for {self.target_file} aborted. Socket closed on {self.comm_port}.")
            return

        try:
            with open(self.full_path, 'rb') as file_handle:
                file_size = os.path.getsize(self.full_path)
                self.handle_data_transfer(file_handle, file_size)
        except Exception as e:
            print(f"File handling error: {e}")
        finally:
            self.data_socket.close()
            print(f"Transfer for {self.target_file} on {self.comm_port} complete. Socket closed.")

class NetworkFileServer:
    def __init__(self, listen_port):
        print(f"Initializing server on port {listen_port}...")
        self.listener = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Bind listener to the given port
        self.listener.bind(('', listen_port))
        print(f"File sharing active on port {listen_port}.")
        
    def process_download_request(self, message, client_address):
        try:
            file_requested = message.split(maxsplit=1)[1].strip()
            file_location = os.path.join("server_files", file_requested)

            if os.path.exists(file_location):
                transfer_port = random.randint(50000, 51000)
                file_size = os.path.getsize(file_location)
                reply = f"OK {file_requested} SIZE {file_size} PORT {transfer_port}"
                self.listener.sendto(reply.encode(), client_address)
                print(f"{file_requested} found. Sent OK with size {file_size} and port {transfer_port} to {client_address}.")

                transfer_handler = FileTransferHandler(
                    file_requested,
                    client_address,
                    transfer_port
                )
                transfer_handler.start()
                print(f"Started thread for {file_requested} on port {transfer_port}.")
            else:
                reply = f"ERR {file_requested} NOT_FOUND"
                self.listener.sendto(reply.encode(), client_address)
                print(f"{file_requested} not found. Sent error to {client_address}.")

        except IndexError:
            print(f"Invalid request from {client_address}. Ignoring...")

    def service_loop(self):
        print("Waiting for requests...")
        while True:
            try:
                data_packet, client = self.listener.recvfrom(1024)
                message_content = data_packet.decode().strip()

                if message_content.startswith("DOWNLOAD"):
                    self.process_download_request(message_content, client)
                else:
                    continue

            except Exception as e:
                print(f"Service error: {e}")