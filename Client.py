class FileTransferClient:

    def __init__(self, server_ip, server_port, list_path):

        self.server = (server_ip, server_port)
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.file_queue = self._read_file_list(list_path)
        self.socket_timeout = 2
        self.max_attempts = 5
        self.chunk_size = 1000

        print("student Name: ZhuFeiyu")
        print("ID 20233006387")
        print("Thanks for your guidance, professor!")
        print(f"\nInitialize Client. Server IP: {server_ip}, Server Port: {server_port}")
        print(f"\nReading file list from {list_path}...")
        
    def _read_file_list(self, path):

        print(f"\nReading file list from {path}")
        with open(path, 'r') as file:
            return [line.strip() for line in file if line.strip()]
        
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
        
        