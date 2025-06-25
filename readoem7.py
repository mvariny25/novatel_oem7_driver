import struct
import socket
import time
format_string = '<BBBBHcBHHBBHILHH'# BIHBB'  # Example: Sync bytes, header length, message ID, etc.
    # 0 B Uchar 0xAA
    # 1 B Uchar 0x44
    # 2 B Uchar 0x12
    # 3 B Uchar header len
    # 4 H Ushort message ID
    # 5 c Char type -> 00
    # 6 B Uchar Port address
    # 7 H Ushort message length
    # 8 H Ushort sequence
    # 9 B Uchar idle time
    #10 B - time status
    #11 H Ushort gps week
    #12 I ms from gps week start
    #13 L Ulong recv status
    #14 H Ushort resv.
    #15 H Ushort version
    # ...
    # I CRC


header_dict_keys = ['SYNC1','SYNC2','SYNC3','header_len','message_id','type','port_address','message_len',
                    'sequence','idle_time','time_status','gps_week','gps_ms','recv_status','resv','version']
#def parse_novatel_message(data):
    # This is a simplified example, you'll need the actual Novatel message structure.
    # Replace with the correct format string for your message type.
    
    

def parse_novatel_log_file(filename):
    msgs = []
    with open(filename, 'rb') as f:
        while True:
            # Read data from the file (adjust the chunk size based on your message size)
            try:
                # Unpack the header
                header_size = struct.calcsize(format_string)
                data_header = f.read(header_size)
                if not data_header:
                    break  # End of file
                
                header = struct.unpack(format_string, data_header)
                header_dict = dict(zip(header_dict_keys,header))
                if(header_dict['SYNC1'] != 0xAA and
                   header_dict['SYNC2'] != 0x44 and
                   header_dict['SYNC3'] != 0x12):
                    print("Header error")
                    print(header_dict)
                    return None

                # Extract message ID and message length from the header
                message_id = header[4]  # Assuming message ID is at index 3
                message_length = header[7]  # Assuming message length is at index 5
                data_msg = f.read(message_length)
                # Read the message data
                #message_data = data[header_size : header_size + message_length]

                # read 4 CRC bytes
                data_crc = f.read(4)
                data_msg = {
                    'message_id': message_id,
                    'header': header_dict,
                    'header_data': data_header,
                    'message_data': data_msg,
                    'message_crc': data_crc,
                    'all_data': data_header + data_msg + data_crc
                }
                msgs.append(data_msg)

            except struct.error as e:
                print(f"Error parsing message: {e}")
                return None
    return msgs      

msgs = parse_novatel_log_file('bestpos_hwmonitor_range.dat')

UDP_IP = "127.0.0.1"
UDP_PORT = 5005
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

count = 0
for msg in msgs:
    print(f"{count} -> {28+msg['header']['message_len']+4 - len(msg['all_data'])}")
    count = count + 1 
    sock.sendto(msg['all_data'], (UDP_IP, UDP_PORT))
    time.sleep(0.01)
sock.close()
