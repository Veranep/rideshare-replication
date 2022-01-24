import osmnx as ox
import networkx as nx
import pandas as pd
import numpy as np
import csv
from datetime import datetime
import sys
import geopy.distance
from collections import defaultdict

def print_txt(data):
    print(len(data))
    for key in data:
        print(f'Flows: {key}-{key}')
        for flows in data[key]:
            print(f'{flows[0]}, {flows[1]}, {float(data[key][flows])}')
    return

G = nx.read_gpickle('manhattan_graph.gpickle')
nodes = ox.graph_to_gdfs(G, edges=False)
osmid_to_nodeid = dict(zip(list(nodes.index), list(range(nodes.shape[0]))))
formatstring = '%Y-%m-%d %H:%M:%S'

with open('yellow_tripdata_2016-04.csv', newline='') as csvfile:
    i = 0
    flow = 0
    day = 1
    f = open(f"test_flow_5000_{day}.txt", 'w')
    sys.stdout = f  
    reader = csv.DictReader(csvfile)
    print('1440')
    data_day = {flow: defaultdict(int)}

    # Loop through rows csv
    for row in reader:
        new_time = datetime.strptime(row['tpep_pickup_datetime'], formatstring)

        # Set begin time
        if i == 0:
            last_time = new_time
        
        # Start new day file
        if new_time.day != last_time.day:
            day += 1
            flow = 0
            last_time = new_time

            print_txt(data_day)
            f.close()

            f = open(f"test_flow_5000_{day}.txt", 'w')
            sys.stdout = f  
            print('1440')
            data_day = {flow: defaultdict(int)}
            
            
        # Start new flow of 60 seconds
        if (new_time - last_time).total_seconds() > 59:
            last_time = new_time
            flow += 1
            data_day[flow] = defaultdict(int)
        
        # Retrieve pickup and destination from csv 
        pickup_osmid = ox.distance.nearest_nodes(G, float(row['pickup_longitude']), float(row['pickup_latitude']))
        dest_osmid = ox.distance.nearest_nodes(G, float(row['dropoff_longitude']), float(row['dropoff_latitude']))

        nearest_node_pickup = (nodes.loc[pickup_osmid]['y'], nodes.loc[pickup_osmid]['x'])
        nearest_node_dropoff = (nodes.loc[dest_osmid]['y'], nodes.loc[dest_osmid]['x'])
        pickup = (float(row['pickup_latitude']), float(row['pickup_longitude']))
        dropoff = (float(row['dropoff_latitude']), float(row['dropoff_longitude']))

        if geopy.distance.distance(nearest_node_pickup, pickup).km < 0.1 and geopy.distance.distance(nearest_node_dropoff, dropoff).km < 0.1:
            data_day[flow][(osmid_to_nodeid[pickup_osmid], osmid_to_nodeid[dest_osmid])] += 1

        i += 1
        if i == 1000:
            break

    print_txt(data_day)
    f.close()