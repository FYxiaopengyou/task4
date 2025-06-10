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
        