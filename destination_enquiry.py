import socket
import time
import re

class IP3Router:
    def __init__(self, host, port=52116):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))
        print(f"Connected to router at {self.host}:{self.port}")

    def clear_buffer(self):
        """Clear any existing data in the socket buffer to prevent mixed responses."""
        self.sock.settimeout(0.1)  
        try:
            while self.sock.recv(4096):
                pass
        except socket.timeout:
            pass
        self.sock.settimeout(None)  

    def status(self, dst, retries=3):
        """Send the status command and attempt to get a valid response."""
        for attempt in range(retries):
            self.clear_buffer() 
            command = f"~XPOINT?D${{{dst}}}\\"
            self.sock.sendall(command.encode())

            # Wait to allow the router time to process
            time.sleep(0.2)  

            # response
            response = self.sock.recv(4096).decode()

            if f"D${{{dst}}}" in response:
                match = re.search(r"S\${(.*?)}\\", response)
                if match:
                    source = match.group(1)
                    print(f"Source '{source}' is routed to Destination '{dst}'")
                    return source 
                else:
                    print(f"Could not parse source for {dst}. Raw response: '{response.strip()}'")
                    return None

            print(f"Attempt {attempt + 1} failed. Retrying...")

        print(f"Failed to get a valid response for {dst} after {retries} attempts.")
        return None 

    def close(self):
        self.sock.close()

router = IP3Router('10.10.116.104')

while True:
    dst = input("Enter the destination name: ").strip()
    if dst.lower() == 'quit':
        break
    router.status(dst)

router.close()
