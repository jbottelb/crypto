'''
Brad Budden and Josh Bottelberghe
Distributed Systems - Final Project
NameServer.py

Description: This program maintain a list of the 
active seed nodes in the network by pinging them
at a specified interval. Nodes hoping to join the system 
can reach out to this name server for the names of these
seed nodes. Since we are running the seed nodes
ourselves, we trust them to behave correctly. Incoming
nodes do have the option of identifying other
nodes in the system to connect to without the use
of the name server or seed nodes. Listens on a specified port.
'''

import sys
from flask import Flask
import threading
import socket
import time

active_seeds = set()
possible_seeds = [("student11.cse.nd.edu", 12000), ("student12.cse.nd.edu", 12000)]

app = Flask(__name__)

# requests to our server will return the current active seeds
@app.route("/")
def return_active_seeds():
    html_active_seeds = f"<p>Length={len(active_seeds)}<p>"
    for active_seed in active_seeds:
        html_active_seeds.append("<p>" + active_seed[0] + ":" + str(active_seed[1]) + "<p>")
    return html_active_seeds

# our daemon thread will ping the possible seed nodes
# every <ping_interval> number of seconds
def ping_seed_nodes(ping_interval):
    latest_ping = time.time()
    first_ping = True
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while 1:
        if time.time() - latest_ping > float(ping_interval) or first_ping:
            for ps in possible_seeds:
                try:
                    # see if seed node is running
                    sock.connect(ps)
                    # yes -> add to active seeds
                    active_seeds.add(ps)
                except:
                    # no -> remove from active seeds
                    active_seeds.discard(ps)
            first_ping = False
            latest_ping = time.time()            
            

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 NameServer.py <port> <ping_interval>")
        exit(-1)
    
    name_server_port = sys.argv[1]
    ping_interval = sys.argv[2]
    pinging_thread = threading.Thread(target=ping_seed_nodes, args=(ping_interval,), daemon=True)

    pinging_thread.start()
    app.run(host='0.0.0.0', port=name_server_port)


if __name__ == "__main__":
    main()