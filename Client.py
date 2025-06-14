import socket
import os
from base64 import b64decode
import sys
import hashlib

# Define a class for file transfer client
class FileTransferClient:

    def __init__(self, server_ip, server_port, list_path):

        #ser adress , and UDP socket, and file list, chunk size
        self.server = (server_ip, server_port)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.file_queue = self._read_file_list(list_path)
        self.socket_timeout = 2
        self.max_attempts = 5
        self.chunk_size = 1000

        # Print test information to test
        print("student Name: ZhuFeiyu")
        print("ID 20233006387")
        print("Thanks for your guidance, professor!")
        print(f"\nInitialize Client. Server IP: {server_ip}, Server Port: {server_port}")
        print(f"\nReading file list from {list_path}...")

    # Read file list from given path
    def _read_file_list(self, path):

        print(f"\nReading file list from {path}")
        with open(path, 'r') as file:
            return [line.strip() for line in file if line.strip()]

    # Communicate with server with retries
    def _communicate(self, socket_obj, msg, destination, current_timeout):

        print(f"\nSending message '{msg}' to {destination}. Current timeout: {current_timeout} seconds")
        for attempt in range(self.max_attempts):
            try:
                # Send message to server
                socket_obj.sendto(msg.encode(), destination)
                print(f"\nMessage sent. Waiting for a reply...")


                # Receive reply form server
                reply, _ = socket_obj.recvfrom(1024)
                print(f"\nReceived reply: {reply.decode()}")
                return reply.decode()
            except socket.timeout:

                current_timeout *= 2
                socket_obj.settimeout(current_timeout)

                # testing message
                print(f"\n  Attempt {attempt + 1} timed out. Retry with a timeout of {current_timeout} seconds...")

        raise ConnectionError("Max retries reached")

    # Execute file transfer process
    def execute_transfers(self):

        print("\nStarting file transfer process...")

        for target_file in self.file_queue:

            print(f"\n\nRequesting file: {target_file}")
            try:

                response = self._communicate(
                    self.udp_socket,
                    f"DOWNLOAD {target_file}",
                    self.server,
                    self.socket_timeout
                )

                if response.startswith("OK"):

                    print("\nServer responded with OK. Parsing file size and data port...")

                    parts = response.split()
                    try:
                        file_size = int(parts[parts.index("SIZE")+1])
                        data_port = int(parts[parts.index("PORT")+1])

                        print(f"\nFile size: {file_size} bytes, Data port: {data_port}")

                        # Download the file
                        self._download_file(target_file, file_size, data_port)
                    except (ValueError, IndexError):
                        print("\n  Invalid server response format. Skipping this file...")
                        continue

                elif response.startswith("ERR"):
                    print(f"\n  Server error: {response[4:]}")
                else:
                    print(f"\n  Unexpected response: {response}")

            except Exception as e:
                print(f"\n  Transfer failed: {str(e)}")

        #show transfer complete
        print("\nFile transfer process completed.")

    # Download file from server , set relevante informations
    def _download_file(self, filename, file_size, data_port):
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        data_socket.settimeout(self.socket_timeout)
        endpoint = (self.server[0], data_port)
        print(f"\n[{filename}] Connecting to data port {data_port} for downloading {file_size} bytes...")

        try:
            # Print downloading infomation
            print(f"\n[{filename}] Downloading {file_size} bytes", end='', flush=True)
            received = 0
            with open(filename, 'wb') as f:
                while received < file_size:
                    start = received
                    end = min(start + self.chunk_size - 1, file_size - 1)
                    
                    print(f"\n\n[{filename}] Requesting bytes from {start} to {end}...")

                    # Communicate to get file chunk
                    response = self._communicate(
                        data_socket,
                        f"FILE {filename} GET START {start} END {end}",
                        endpoint,
                        self.socket_timeout
                    )
                    if not response.startswith(f"FILE {filename}"):
                        raise RuntimeError("Invalid response format")

                    if "OK" in response:
                        try:
                            # Find start of data
                            data_start = response.find("DATA") + 5
                            chunk = b64decode(response[data_start:].encode())
                            f.write(chunk)
                            received += len(chunk)
                            print("#", end='', flush=True)
                        except Exception as e:
                            raise RuntimeError(f"Data decoding error: {str(e)}")
                    else:
                        # server error
                        raise RuntimeError(f"Server error: {response}")

                print("\n\nRequesting to close the file transfer...")
                # Communicate to close transfer
                close_response = self._communicate(
                    data_socket,
                    f"FILE {filename} CLOSE",
                    endpoint,
                    self.socket_timeout
                )
                if "CLOSE_OK" in close_response:

                    # test excute: transfer success
                    print("\n  Transfer completed successfully")
                else:
                    print("\n  Warning: Close confirmation missing")

            # Verify file integrity
            self._verify_file(filename)

        finally:
            data_socket.close()

    # Verify file integrity
    def _verify_file(self, filename):
        print(f"\nVerifying the integrity of {filename}...")

        # Create MD5 hash object
        file_hash = hashlib.md5()
        with open(filename, 'rb') as f:
            while chunk := f.read(8192):
                file_hash.update(chunk)

        # Print hash number
        print(f"\n  File hash: {file_hash.hexdigest()}")

if __name__ == "__main__":
    print("student Name: ZhuFeiyu")
    print("ID 20233006387")
    print("Thanks for your guidance, professor!")
    if len(sys.argv) != 4:
        print("\nUsage: python UDPclient.py <HOST> <PORT> <FILE_LIST>")
        sys.exit(1)

    # Create and execute transfer
    client = FileTransferClient(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    client.execute_transfers()