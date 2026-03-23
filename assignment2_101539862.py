"""
Author: JunyongChoi
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

# TODO: Import the required modules (Step ii)
# socket, threading, sqlite3, os, platform, datetime
import socket
import threading
import sqlite3
import os
import platform
import datetime

# TODO: Print Python version and OS name (Step iii)
print("Python version:",platform.python_version())
print("Operating System:",os.name)

# TODO: Create the common_ports dictionary (Step iv)
# Add a 1-line comment above it explaining what it stores
# Saved common port number & corresponding service name.
common_ports = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    8080: "HTTP-Alt"
}

# TODO: Create the NetworkTool parent class (Step v)
class NetworkTool:
# - Constructor: takes target, stores as private self.__target
    def __init__(self, target):
        self.__target = target
# Q3: What is the benefit of using @property and @target.setter?
# Using @property and @target.setter allows controlled access to the private __target attribute while maintaining encapsulation.
# Instead of accessing self.__target directly, the setter can validate input and prevent invalid values such as an empty string.
# This ensures that the object remains in a valid state and improves code safety and maintainability.
    @property
    def target(self):
        return self.__target

# - @target.setter with empty string validation
    @target.setter
    def target(self, value):
        if value != "":
            self.__target = value
        else:
            print("Error: Target cannot be empty")

# - Destructor: prints "NetworkTool instance destroyed"
    def __del__(self):
        print("NetworkTool instance destroyed")






# Q1: How does PortScanner reuse code from NetworkTool?
# TODO: Your 2-4 sentence answer here... (Part 2, Q1)
# PortScanner reuses code from NetworkTool through inheritance, which allows it to access the target attribute and its getter/setter methods.
# Instead of redefining how the target is stored and validated, PortScanner calls super().__init__(target) to initialize it using the parent class logic.
# For example, PortScanner uses self.target (from NetworkTool) in scan_port() when calling sock.connect_ex((self.target, port)).
class PortScanner(NetworkTool):
# - Constructor: call super().__init__(target), initialize self.scan_results = [], self.lock = threading.Lock()
    def __init__(self, target):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()
# - Destructor: print "PortScanner instance destroyed", call super().__del__()
    def __del__(self):
        print("PortScanner instance destroyed")
        super().__del__()
# - scan_port(self, port):
    def scan_port(self, port):







        sock = None
#     Q4: What would happen without try-except here?
# Without the try-except block, any socket error (such as an unreachable host or network issue) would cause the program to crash.
# This would stop the entire scanning process instead of allowing the program to continue scanning other ports.
# The try-except ensures that errors are handled gracefully and the program remains stable.
        try:
             
#     - Create socket, set timeout, connect_ex
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))
#     - Determine Open/Closed status
            if result == 0:
                status = "Open"
            else:
                status = "Closed"
#     - Look up service name from common_ports (use "Unknown" if not found)
            service_name = common_ports.get(port, "Unknown")
#     - Acquire lock, append (port, status, service_name) tuple, release lock
            self.lock.acquire()
            self.scan_results.append((port, status, service_name))
            self.lock.release()
#     - Catch socket.error, print error message
        except socket.error as e:
            print(f"Error scaning port {port}: {e}")
#     - Close socket in finally block
        finally:
            if sock:
                sock.close()
#




# - get_open_ports(self):
    def get_open_ports(self):
#     - Use list comprehension to return only "Open" results
        return[result for result in self.scan_results if result[1] == "Open"]
#



#     Q2: Why do we use threading instead of scanning one port at a time?
# I use threading to scan multiple ports at the same time, which significantly improves performance compared to scanning them sequentially.
# Without threading, each port would be scanned one by one, and due to timeouts, scanning 1024 ports could take a very long time.
# By using threads, the program can check many ports concurrently, reducing the total scan time.
    def scan_range(self, start_port, end_port):
#     - Create threads list
        threads = []

#     - Create Thread for each port targeting scan_port
        for port in range(start_port, end_port + 1):
            thread = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(thread)
#     - Start all threads (one loop)
        for thread in threads:
            thread.start()
#     - Join all threads (separate loop)
        for thread in threads:
            thread.join()


# TODO: Create save_results(target, results) function (Step vii)
    def save_results(target, results):
# - Connect to scan_history.db
        try:
            conn = sqlite3.connect("scan_history.db")
            cursor = conn.cursor()
# - CREATE TABLE IF NOT EXISTS scans (id, target, port, status, service, scan_date)
            cursor.execute("""CREATE TABLE IF NOT EXISTS scans 
                           (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                            target TEXT,
                            port INTEGER,
                            status TEXT,
                            service TEXT,
                            scan_date TEXT
                           )
                            """)
# - INSERT each result with datetime.datetime.now()
            for port, status, service in results:
                cursor.execute("""
                    INSERT INTO scans (target, port, status, service, scan_date)
                    Values (?, ?, ?, ?, ?)
                """, (target, port, status, service, str(datetime.datetime.now())))
# - Commit, close
            conn.commit()
            conn.close()
# - Wrap in try-except for sqlite3.Error
        except sqlite3.Error as e:
            print("Database error:", e)


# TODO: Create load_past_scans() function (Step viii)
    def load_past_scans():
# - Connect to scan_history.db
        try:
            conn = sqlite3.connect("scan_history.db")
            cursor = conn.cursor()
# - SELECT all from scans
            cursor.execute("SELECT target, port, status, service, scan_date FROM scans")
# - Print each row in readable format
            rows = cursor.fetchall()
# - Handle missing table/db: print "No past scans found."
            if not rows:
                print("No past scans found.")
            else:
                for target, port, status, service, scan_date in rows:
                    print(f"[{scan_date}] {target} : Port {port} ({service}) - {status}")
# - Close connection
            conn.close()
        except sqlite3.Error:
            print("No past scans found.")    


# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    
    # TODO: Get user input with try-except (Step ix)
    target = input("Enter target IP address: ").strip()
    # - Target IP (default "127.0.0.1" if empty)
    if target == "":
        target = "127.0.0.1"
    # - Start port (1-1024)
    try:
        start_port = int(input("Enter starting port number (1-1024): "))
    # - End port (1-1024, >= start port)
        end_port = int(input("Enter ending port number (1-1024): "))

    # - Range check: "Port must be between 1 and 1024."
        if start_port < 1 or start_port > 1024 or end_port < 1 or end_port > 1024:
            print("Port must be between 1 and 1024.")
        elif end_port < start_port:
            print("End port must be greater than or equal to Start port") # end_port must be greater than or equal to start_port
    # TODO: After valid input (Step x)
        else:
    # - Create PortScanner object
            scanner = PortScanner(target)
    # - Print "Scanning {target} from port {start} to {end}..."
            print(f"Scanning {target} from port {start_port} to {end_port}...")
    # - Call scan_range()
            scanner.scan_range(start_port, end_port)
    # - Call get_open_ports() and print results
            open_ports = scanner.get_open_ports()
    # - Print total open ports found
            print(f"---Scan Results for {target} ---")
            for port,status,service in open_ports:
                print(f"Port {port}: {status} ({service})")
            print("------")
            print(f"Total open ports found: {len(open_ports)}")
    # - Call save_results()
            save_results(target, scanner.scan_results)
    # - Ask "Would you like to see past scan history? (yes/no): "
            choice = input("Would you like to see past scan history? (yes/no): ").strip().lower()
    # - If "yes", call load_past_scans()
            if choice == "yes":
                load_past_scans()           
    # - Catch ValueError: "Invalid input. Please enter a valid integer."
    except ValueError:
        print("Invalid input. Please enter a valid integer.")


# Q5: New Feature Proposal
# One additional feature I would add is a "Port Risk Classifier" that categorizes open ports based on their security risk level.
# This feature would use a nested if-statement to classify ports as high, medium, or low risk depending on common vulnerable port numbers.
# It would help users quickly understand which open ports may pose security concerns instead of just listing them.
# Diagram: See diagram_101539862.png in the repository root
