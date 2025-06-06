class FileTransferHandler(threading.Thread):
    def __init__(self, file_name, client_info, transfer_port):
        super().__init__()
        self.target_file = file_name
        self.client_info = client_info
        self.comm_port = transfer_port
        self.data_socket = None
        self.block_size = 1000
        self.full_path = os.path.join("server_files", file_name)
        print(f"Initializing file transfer handler for {self.target_file} on port {self.comm_port}...")

    def setup_connection(self):
        self.data_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.data_socket.settimeout(5.0)
        self.data_socket.bind(('', self.comm_port))
        print(f"UDP socket setup on port {self.comm_port}.")