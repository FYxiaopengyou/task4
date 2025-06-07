

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
