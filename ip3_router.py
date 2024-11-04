import socket
import time
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IP3Router:
    def __init__(self, host, port=52116):
        self.host = host
        self.port = port
        self.sock = None
        self.connected = False
        logger.info(f"IP3Router initialized with host {host}:{port}")

    def connect(self):
        """Establish connection to the router."""
        if self.connected:
            return True
            
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5) 
            self.sock.connect((self.host, self.port))
            self.connected = True
            logger.info(f"Connected to router at {self.host}:{self.port}")
            return True
        except (socket.error, ConnectionRefusedError) as e:
            logger.error(f"Failed to connect to router: {str(e)}")
            self.connected = False
            return False

    def ensure_connection(self):
        """Ensure connection is established before operations."""
        if not self.connected:
            return self.connect()
        return True

    def clear_buffer(self):
        """Clear any existing data in the socket buffer to prevent mixed responses."""
        if not self.ensure_connection():
            return False

        self.sock.settimeout(0.1)
        try:
            while self.sock.recv(4096):
                pass
        except socket.timeout:
            pass
        self.sock.settimeout(None)

    def status(self, dst, retries=3):
        """Send the status command and attempt to get a valid response."""
        if not self.ensure_connection():
            return None

        for attempt in range(retries):
            try:
                self.clear_buffer()
                command = f"~XPOINT?D${{{dst}}}\\\n"
                self.sock.sendall(command.encode())

                time.sleep(0.5)

                response = self.sock.recv(4096).decode()

                if f"D${{{dst}}}" in response:
                    match = re.search(r"S\${(.*?)}\\", response)
                    if match:
                        source = match.group(1)
                        logger.info(f"Source '{source}' is routed to Destination '{dst}'")
                        return source
                    else:
                        logger.warning(f"Could not parse source for {dst}. Raw response: '{response.strip()}'")
                        return None

                logger.warning(f"Attempt {attempt + 1} failed. Retrying...")

            except socket.error as e:
                logger.error(f"Socket error during status check: {str(e)}")
                self.connected = False
                if attempt == retries - 1:
                    return None
                time.sleep(1) 

        logger.error(f"Failed to get a valid response for {dst} after {retries} attempts.")
        return None

    def route(self, src, dst, retries=3):
        """Attempt to route a source to a destination using the XPOINT command syntax."""
        for attempt in range(retries):
            self.clear_buffer()
            command = f"~XPOINT:S${{{src}}};D${{{dst}}}\\\n"  
            self.sock.sendall(command.encode())

            time.sleep(0.5)  

            response = self.sock.recv(4096).decode()
            print(f"Router Response: '{response.strip()}'")

            current_source = self.status(dst)
            if current_source == src:
                print(f"Successfully routed Source '{src}' to Destination '{dst}'")
                return True
            else:
                print(f"Attempt {attempt + 1} failed. Unexpected response.")

        print(f"Failed to route Source '{src}' to Destination '{dst}' after {retries} attempts. Final Response: '{response.strip()}'")
        return False

    def close(self):
        """Close the connection to the router."""
        if self.sock:
            self.sock.close()
            self.connected = False
            logger.info("Router connection closed")

    def clear_route(self, src, retries=3):
        """Clear the route for a source."""
        if not self.ensure_connection():
            return False

        for attempt in range(retries):
            try:
                self.clear_buffer()
                command = f"~XPOINT%D${{{src}}}\\\n"
                self.sock.sendall(command.encode())

                time.sleep(1.0)

                response = self.sock.recv(4096).decode()
                logger.info(f"Clear Route Response: '{response.strip()}'")

                if "cleared" in response or f"D${{{src}}}" not in response:
                    logger.info(f"Successfully cleared route for Source '{src}'")
                    return True
                else:
                    logger.warning(f"Attempt {attempt + 1} failed. Response: '{response.strip()}'")

            except socket.error as e:
                logger.error(f"Socket error during clear route: {str(e)}")
                self.connected = False
                if attempt == retries - 1:
                    return False
                time.sleep(1)  

        logger.error(f"Failed to clear route for Source '{src}' after {retries} attempts.")
        return False