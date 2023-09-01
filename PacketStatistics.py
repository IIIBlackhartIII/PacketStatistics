import socket
import time
import matplotlib.pyplot as plt 
import matplotlib.animation as anim
from threading import Thread
import numpy as np
import tkinter as tk
import tkinter.simpledialog as tksimple

## PROMPT USER SETUP ##
root =  tk.Tk()
query_PORT = tksimple.askinteger("UDP PORT", "Enter Listen Port")
root.destroy()

### UDP SETUP ###
UDP_IP = "0.0.0.0" #listen on all available network interfaces
UDP_RECEIVE_PORT = query_PORT #choose port number

#setup listen socket
server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) 

# Bind the socket to the IP address and port
receive_address = (UDP_IP, UDP_RECEIVE_PORT)
server.bind(receive_address)

# Packet Buffer Init #
delta_times = [] #list of delta times for stats analysis
last_received = time.perf_counter() #stores time since last packet for delta timing 
wait_packets = 32 #how many packets before we start outputting stats?
first_packet = True #bool to toggle what to do on first received

mean_time = 0 #used to display the mean
max_length = 120 #max length of statistics list

stat_debug_text = "" #string for stat debugs

def packet_timing_loop():
    global delta_times
    global mean_time
    global max_length 
    global last_received
    global wait_packets
    global first_packet
    global stat_debug_text

    while True:
        # Receive data
        data, address = server.recvfrom(1024)  # default buffer size 1024 bytes
        
        if (data != None):
            if (first_packet):
                #if this is the first packet, only update our receive time, subsequent packets will be stored with deltas
                last_received = time.perf_counter() #current time
                first_packet = False #we have the first packet, don't run this block again
            else:
                time_since_last = time.perf_counter() - last_received #calc delta time since last packet
                delta_times.append(time_since_last * 1000) #add to list of delta time for stats
                last_received = time.perf_counter() #update the time since last to right now

                #remove first index if list length too long
                if (len(delta_times) > max_length):
                    del delta_times[0]

                #start displaying stats if we have enough packets
                if (len(delta_times) > wait_packets):
                    #statistics
                    packet_mean = np.mean(delta_times)                    
                    packet_max = np.max(delta_times)
                    packet_min = np.min(delta_times)
                    mean_time = packet_mean

                    #output log statistics
                    stat_debug_text = str("Mean = {meanstr:.2f}ms / Min = {minstr:.2f}ms / Max = {maxstr:.2f}ms").format(meanstr = packet_mean, minstr = packet_min, maxstr = packet_max)
                    print(stat_debug_text,  end="\r")

print ("Listening For Packets!")

### PLOTTING SETUP ###
plt.style.use('dark_background')
fig = plt.figure(figsize=(16,9))
ax = fig.add_subplot()

def graph_anim(i):
    ax.clear() #clear old chart
    ax.eventplot(delta_times, colors=["b"]) #draw new chart data points
    ax.set_xlabel(str("Delta Time (ms) /// {stats_text}").format(stats_text = stat_debug_text)) #set axis label with updating stats data
    ax.set_ylabel(str("UDP Listening Enpoint = {IP}:{Port}").format(IP = UDP_IP, Port = UDP_RECEIVE_PORT)) #use y-axis label to display IP info
    ax.set_yticks([]) #no y-axis ticks
    plt.axvline(x=mean_time, color='white') #add a horizontal line at the mean
    fig.canvas.draw() #draw the canvas


### RUNTIME ###

## Multi Threading Setup! ##
t1 = Thread(target = packet_timing_loop)
t1.start()

animgraph = anim.FuncAnimation(fig,graph_anim,interval=33,cache_frame_data=False)
plt.show()
