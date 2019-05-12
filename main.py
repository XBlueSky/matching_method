from edge.edge import Edge
from fog_set.fog_set import Fog_Set
from constant.constant import Constant
from argparse import ArgumentParser

parser = ArgumentParser(description= "Greedy Method")
parser.add_argument("filename", help="testcase file path")
args = parser.parse_args()

# Initial

# Constant: traffic, ratio, max_latency, least_error
constant = Constant(1000, 0.01, 1, 1)

# Edge: capacity, max_servers, cost
edge = Edge(10, 10, 100)
edge.set_traffic(constant.traffic)

# Fog_Set: ratio, edge_transmission_rate, fog_transmission_rate, capacity, total_fogs, testcase file
fogs_num = args.filename.split("_")
file_name = "testcase/"+args.filename
fog_set = Fog_Set(constant.ratio, 1250, 1250, 125, 5, int(fogs_num[1]), file_name)
fog_set.set_traffic(constant.traffic)

# 0/1 knapsack problem with (1 − 1/ sqrt(e)) bound
traffic = constant.traffic
bundle_list = []
empty_list = []
algorithm = 'CP'

while traffic > constant.least_error:
    # Edge and all of fog would calculate its own maximum traffic
    if edge.used == False:
        edge.algorithm(traffic, constant.max_latency, constant.least_error)
        bundle_list.append({'id': 'edge', 'traffic': edge.max_traffic, 'cost': edge.edge_cost(), 'CP': edge.max_traffic / edge.edge_cost(), 'chosen': False})

    for f in fog_set.fog_list:
        if f.used == False:
            f.algorithm(traffic, constant.max_latency, constant.least_error, algorithm)
            if f.max_traffic > 0:
                bundle_list.append({'id': f.index, 'traffic': f.max_traffic, 'cost': f.fog_cost(), 'CP': f.max_traffic / cost, 'chosen': False})
            else:
                empty_list.append({'id': f.index, 'traffic': 0, 'cost': 0, 'CP': 0, 'chosen': False})

    if not bundle_list:
        if algorithm == 'max':
            print("There is no enough capacity")
            break
        else:
            algorithm = 'max'
            traffic = constant.traffic
            bundle_list.clear()
            edge.clear()
            fog_set.clear()
            continue

    # Sort by CP value
    bundle_list.sort(key=lambda b : b['CP'], reverse=True)
    for bundle in bundle_list:
        if traffic - bundle['traffic'] >= 0 and bundle['traffic'] > 0:
            traffic = traffic - bundle['traffic']
            bundle['chosen'] = True
        else:
            break
    
    for bundle in bundle_list:
        if bundle['chosen'] == True:
            if bundle['id'] == 'edge':
                edge.used = True
            else:
                fog_set.fog_list[bundle['id']].used = True
        else:
            if bundle['id'] == 'edge':
                edge.clear()
            else:
                fog_set.fog_list[bundle['id']].clear()
    
    for empty in empty_list:
        fog_set.fog_list[empty['id']].clear()

    empty_list.clear()
    bundle_list.clear()

edge.display()
fog_set.display()