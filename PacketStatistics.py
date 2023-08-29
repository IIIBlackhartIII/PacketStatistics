import socket
import statistics as stat
import time

## UDP Setup ##
UDP_IP = "0.0.0.0" #listen on all available network interfaces
UDP_RECEIVE_PORT = 6301 #choose port number

#setup listen socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

# Bind the socket to the IP address and port
receive_address = (UDP_IP, UDP_RECEIVE_PORT)
server.bind(receive_address)

# Packet Buffer Init#
delta_times = [] #list of delta times for stats analysis
max_length = 100 #max length of statistics list
last_received = time.time() #stores time since last packet for delta timing 
first_packet = True #setup what to do for first packet
stats_length = 12 #how many packets before we start outputting stats?
ms_length = 5 #how many decimals to show in time values

def convert_string_length(input_float : float, length_limit : int):
    string_convert = str(input_float * 1000)
    return string_convert[:length_limit]

print ("Listening For Packets!")

#################
### MAIN LOOP ###
#################
while True:
    # Receive data
    data, address = server.recvfrom(1024)  # default buffer size 1024 bytes
    
    if (data != None):
        if (first_packet):
            #if this is the first packet, only update our receive time, subsequent packets will be stored with deltas
            last_received = time.time() #current time
            first_packet = False #we have the first packet, don't run this block again
        else:
            time_since_last = time.time() - last_received #calc delta time since last packet
            delta_times.append(time_since_last) #add to list of delta time for stats
            last_received= time.time() #update the time since last to right now
            
            #remove first index if list length too long
            if (len(delta_times) > max_length):
                del delta_times[0] 
            
            #start displaying stats if we have enough packets
            if (len(delta_times) > stats_length):
                #statistics
                packet_mean = stat.mean(delta_times) 
                packet_median = stat.median(delta_times) 
                packet_variance = stat.pvariance(delta_times, packet_mean)
                packet_max = max(delta_times)
                packet_min = min(delta_times)
                
                #convert to strings for print
                packet_mean_str = convert_string_length(packet_mean,ms_length)
                packet_median_str = convert_string_length(packet_median,ms_length)
                packet_variance_str = convert_string_length(packet_variance,ms_length)
                packet_max_str = convert_string_length(packet_max,ms_length)
                packet_min_str = convert_string_length(packet_min,ms_length)
                
                #display statistics
                print("Mean = " + packet_mean_str + " ms / Median = " + packet_median_str + " ms / Variance = " + packet_variance_str + " / Min = " + packet_min_str + " ms / Max = " + packet_max_str + " ms",  end="\r")