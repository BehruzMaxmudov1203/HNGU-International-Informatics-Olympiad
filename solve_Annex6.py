import csv
import math
import heapq
import os
import sys
from collections import defaultdict, deque

# File paths
BASE = 'Annex6-20260415/'
NODES = BASE + 'nodes.csv'
ROADS = BASE + 'roads.csv'
VEHICLES = BASE + 'vehicles.csv'
DEMAND = BASE + 'demand.csv'
POLICY = BASE + 'policy.txt'

CO2_LIMIT = 800

# Parse nodes
nodes = {}
if not os.path.exists(NODES):
    print(f"Xato: {NODES} topilmadi!")
    sys.exit(1)

with open(NODES, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        nodes[row['id']] = {
            'type': row['type'],
            'open': float(row['open']),
            'close': float(row['close'])
        }

warehouse_nodes = [k for k, v in nodes.items() if v['type'] == 'W']
if not warehouse_nodes:
    print("Xato: Omborda (type 'W') tugun topilmadi!")
    sys.exit(1)
warehouse = warehouse_nodes[0]

# Parse roads (only unblocked)
graph = defaultdict(list)
co2_map = {}
with open(ROADS, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row['blocked'] == '0':
            a, b = row['from'], row['to']
            d = float(row['distance'])
            c = float(row['co2_factor'])
            graph[a].append((b, d, c))
            graph[b].append((a, d, c))
            co2_map[(a, b)] = co2_map[(b, a)] = c

# Parse vehicles
vehicles = []
with open(VEHICLES, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        vehicles.append({
            'id': row['id'],
            'capacity': float(row['capacity']),
            'fuel_limit': float(row['fuel_limit']),
            'speed': float(row['speed']),
            'cooling': int(row['cooling'])
        })

# Parse demand
demands = []
with open(DEMAND, encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        demands.append({
            'node': row['node'],
            'water': float(row['water']),
            'food': float(row['food']),
            'med': float(row['med']),
            'priority': int(row['priority']),
            'expiry_hours': float(row['expiry_hours'])
        })

# Dijkstra for shortest path (distance, then co2, then lex)
def dijkstra(start, end):
    heap = [(0, 0, [start])]
    seen = {start: (0, 0)}
    while heap:
        dist, co2, path = heapq.heappop(heap)
        u = path[-1]
        if u == end:
            return dist, co2, path
        for v, d, c in graph[u]:
            new_dist = dist + d
            new_co2 = co2 + d * c
            if v not in seen or (new_dist, new_co2) < seen[v]:
                seen[v] = (new_dist, new_co2)
                heapq.heappush(heap, (new_dist, new_co2, path + [v]))
    return None

# Try to serve each demand with each vehicle
def can_serve(demand, vehicle):
    node = demand['node']
    total = demand['water'] + demand['food'] + demand['med']
    trips = math.ceil(total / vehicle['capacity'])
    # Cooling required?
    if demand['med'] > 0 and vehicle['cooling'] != 1:
        return None
    # Find shortest path
    res = dijkstra(warehouse, node)
    if not res:
        return None
    dist, co2, path = res
    # Expiry constraint
    if demand['med'] > 0:
        one_way_time = dist / vehicle['speed']
        if one_way_time > demand['expiry_hours']:
            return None
    # Trip time and working hours
    trip_time = 2 * (dist / vehicle['speed'])
    open_t = nodes[node]['open']
    close_t = nodes[node]['close']
    # All trips must fit in working hours
    first_arrival = max(open_t, 0)
    last_arrival = first_arrival + (trips - 1) * trip_time
    if last_arrival > close_t:
        return None
    # Fuel constraint
    total_distance = 2 * dist * trips
    if total_distance > vehicle['fuel_limit']:
        return None
    # CO2 for all trips
    total_co2 = 2 * co2 * trips
    return {
        'vehicle': vehicle['id'],
        'trips': trips,
        'total_distance': total_distance,
        'total_co2': total_co2,
        'priority': demand['priority'],
        'type': nodes[node]['type'],
        'node': node
    }

# Try all assignments, prioritize by hospital > school > residential, then priority, then CO2, then distance
results = []
for demand in demands:
    best = None
    for vehicle in vehicles:
        res = can_serve(demand, vehicle)
        if res:
            if (not best or
                (res['priority'] > best['priority']) or
                (res['priority'] == best['priority'] and res['type'] < best['type']) or
                (res['priority'] == best['priority'] and res['type'] == best['type'] and res['total_co2'] < best['total_co2']) or
                (res['priority'] == best['priority'] and res['type'] == best['type'] and res['total_co2'] == best['total_co2'] and res['total_distance'] < best['total_distance'])):
                best = res
    if best:
        results.append(best)

# Greedily select destinations under CO2 limit, prioritizing by hospital > school > residential, then priority, then CO2, then distance
def type_order(t):
    mapping = {'H': 0, 'S': 1, 'R': 2}
    return mapping.get(t, 99)  # Unknown types go last
results.sort(key=lambda x: (type_order(x['type']), -x['priority'], x['total_co2'], x['total_distance']))

served = []
total_co2 = 0
for r in results:
    if total_co2 + r['total_co2'] <= CO2_LIMIT:
        served.append(r)
        total_co2 += r['total_co2']

print(len(served))
