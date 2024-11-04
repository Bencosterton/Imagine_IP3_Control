#Make sure to replace IP adress and port number with those for your router.
#IP address in line 105
#Port in line 10

import socket
import time
import re

class IP3Router:
    def __init__(self, host, port=PORT):
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
            command = f"~XPOINT?D${{{dst}}}\\\n"
            self.sock.sendall(command.encode())

            time.sleep(0.5)

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

    def route(self, src, dst, retries=3):
        """Attempt to route a source to a destination using the XPOINT command syntax."""
        for attempt in range(retries):
            self.clear_buffer()
            command = f"~XPOINT:S${{{src}}};D${{{dst}}}\\\n"  
            self.sock.sendall(command.encode())

            time.sleep(0.5)  

            response = self.sock.recv(4096).decode()
            print(f"Router Response: '{response.strip()}'") # Some loggins

            # Check routing is made
            if "!" in response:
                print(f"Error in routing command. Response: '{response.strip()}'")
                return False

            # Confirm the route
            if f"S${{{src}}};D${{{dst}}}" in response:
                print(f"Successfully routed Source '{src}' to Destination '{dst}'")
                return True
            else:
                print(f"Attempt {attempt + 1} failed. Unexpected response.")

        print(f"Failed to route Source '{src}' to Destination '{dst}' after {retries} attempts. Final Response: '{response.strip()}'")
        return False


    def close(self):
        self.sock.close()

    def clear_route(self, src, retries=3):
        """Clear the route for a source."""
        for attempt in range(retries):
            self.clear_buffer()
            command = f"~XPOINT%D${{{src}}}\\\n"  # Clear the route
            self.sock.sendall(command.encode())

            time.sleep(1.0)  # Delay for response

            response = self.sock.recv(4096).decode()
            print(f"Clear Route Response: '{response.strip()}'")

            if "cleared" in response or f"D${{{src}}}" not in response:
                print(f"Successfully cleared route for Source '{src}'")
                return True
            else:
                print(f"Attempt {attempt + 1} failed. Response: '{response.strip()}'")

        print(f"Failed to clear route for Source '{src}' after {retries} attempts.")
        return False

router = IP3Router('ROUTER-IP')

while True:
    action = input("Enter 'status' to check a route, 'route' to make a route, or 'quit' to exit: ").strip().lower()
    if action == 'quit':
        break
    elif action == 'status':
        dst = input("Enter the destination name: ").strip()
        router.status(dst)
    elif action == 'route':
        src = input("Enter the source name: ").strip()
        dst = input("Enter the destination name: ").strip()
        router.route(src, dst)

router.close()
