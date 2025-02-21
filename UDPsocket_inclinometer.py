import socket
import csv  
from datetime import datetime  
import time
import os

NUM_PACKETS_PER_FILE = 26400 # Number of packets to write to each file
NUM_FILES = -1  # Set to -1 for infinite, or specify the number of files
BASE_PATH = "/data"  # Change this variable to set the base directory

# Configuration
UDP_IP = "10.20.3.3"
UDP_PORT = 8
LISTEN_IP = "10.20.1.3"
LISTEN_PORT = 55151
PACKET_SIZE = 641*2 + 42  # 600 bytes of data + 42 bytes UDP header

# Take timestamp and define function for filenames
timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
def generate_filename(file_idx):
    return f"{timestamp}_FILE{file_idx:04d}_cgem_az_encoder.csv"

# Create the folder
folder_name = f"{timestamp}_cgem_az_encoder"
full_path = os.path.join(BASE_PATH, folder_name)
os.makedirs(full_path, exist_ok=True)  # Create folder if it doesn't exist

# Initial filename, file and packet index
packet_idx = 0
file_idx = 1
filename = os.path.join(full_path, generate_filename(file_idx))

# Configure ethernet socket
protocol = socket.SOCK_DGRAM  # SOCK_DGRAM is for UDP
ip_family = socket.AF_INET  # AF_INET is for ipv4
sock = socket.socket(ip_family, protocol)

# Bind to the specific IP and port
sock.bind((LISTEN_IP, LISTEN_PORT)) # Can try using sock.bind(("0.0.0.0", LISTEN_PORT)) instead if having problems

# Print confirmation
print(f"Listening for UDP packets from {UDP_IP}:{UDP_PORT} on port {LISTEN_PORT}...")
print("Folder created at ", full_path)

def process_payload(payload):

	current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
	current_time_ns = time.time_ns() % 1_000_000_000
	
	payload_hex = payload.hex()
	
	# Split payload_hex by the separator
	samples_hex = payload_hex.split("89abcdef")
	
	value1_array = []
	value2_array = []
	value3_array = []
	value4_array = []
	value5_array = []
	value6_array = []
	status1_array = []
	status2_array = []
	status3_array = []
	status4_array = []
	status5_array = []
	status6_array = []
	time_array = []
	
	for i, sample_hex in enumerate(samples_hex):
		if len(sample_hex) < 32:
			if i != 40:
				print(f"Warning: Skipping invalid sample at index {i}: {sample_hex} with surrounding {samples_hex[i-5:i+5]} and payload {payload_hex[i*16+i*4-50:i+i*16*4+50]}")
			continue
	
	# Convert each hex segment to an integer 
	#TODO: make this way more efficient using numpy arrays and indexing directly, instead of 7 individual lists
		try:
			
			value1 = int(sample_hex[4:6] + sample_hex[2:4] + sample_hex[0:2], 16)
			value2 = int(sample_hex[10:12] + sample_hex[8:10] + sample_hex[6:8], 16)
			value3 = int(sample_hex[16:18] + sample_hex[14:16] + sample_hex[12:14], 16)
			value4 = int(sample_hex[22:24] + sample_hex[20:22] + sample_hex[18:20], 16)
			value5 = int(sample_hex[28:30] + sample_hex[26:28] + sample_hex[24:26], 16)
			value6 = int(sample_hex[34:36] + sample_hex[32:34] + sample_hex[30:32], 16)
			
			status1 = int(sample_hex[36:38], 16)
			status2 = int(sample_hex[38:40], 16)
			status3 = int(sample_hex[40:42], 16)
			status4 = int(sample_hex[42:44], 16)
			status5 = int(sample_hex[44:46], 16)
			status6 = int(sample_hex[46:48], 16)
			
			time_32bit = int(sample_hex[54:56] + sample_hex[52:54] + sample_hex[50:52] + sample_hex[48:50], 16) #24-32
			
			value1_array.append(value1)
			value2_array.append(value2)
			value3_array.append(value3)
			value4_array.append(value4)
			value5_array.append(value5)
			value6_array.append(value6)
			status1_array.append(status1)
			status2_array.append(status2)
			status3_array.append(status3)
			status4_array.append(status4)
			status5_array.append(status5)
			status6_array.append(status6)
			time_array.append(time_32bit)
			
			print(f"Value 1: {value1}, Value 2: {value2}, Value 3: {value3}, Value 4: {value4}, Value 5: {value5}, Value 6: {value6}, Time Int: {time_32bit}")
		
		except ValueError as e:
			print(f"Error processing sample: {sample_hex} - {e}")
		
	write = value1_array + value2_array + value3_array + value4_array + value5_array + value6_array + status1_array + status2_array + status3_array + status4_array + status5_array + status6_array + time_array
	
	write.append(int( (samples_hex[-1][2:4] + samples_hex[-1][0:2]) ,16))
	write.append(current_time)
	write.append(current_time_ns)
	
	# Write the list of integers to the CSV file
	with open(filename, mode="a", newline="") as file:
		writer = csv.writer(file)
		writer.writerow(write)
	
	print(len(write), "samples written to file. First value:", write[0])
 
# MAIN LOOP
try:
    while True:
        data, addr = sock.recvfrom(PACKET_SIZE)  # Receive packet
        if addr[0] == UDP_IP and addr[1] == UDP_PORT:
            data_payload = data[0:]  # UDP header is removed
            process_payload(data_payload)  # Process the payload (function above)
            packet_idx += 1
            if packet_idx == NUM_PACKETS_PER_FILE:
                print("All packets processed for current file. Next file initialized.")
                packet_idx = 0
                file_idx += 1
                if NUM_FILES != -1 and file_idx >= NUM_FILES:
                    print("All specified files processed. Exiting...")
                    break
                else:
                    filename = os.path.join(full_path, generate_filename(file_idx))
                    print(f"Writing to new file: {filename}")
        else:
            print(f"Ignored packet from {addr}")  # Ignore packets from other addresses/ports
except KeyboardInterrupt:
    print("Server stopped.")
finally:
    sock.close()