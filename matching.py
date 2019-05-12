from edge.edge import Edge
from fog_set.fog import Fog
from constant.constant import Constant
from argparse import ArgumentParser

parser = ArgumentParser(description= "Matching Method")
parser.add_argument("edge_file", help="testcase file path")
parser.add_argument("fog_file", help="testcase file path")
args = parser.parse_args()

# Initial

# Constant: edge_transmission_rate, fog_transmission_rate, least_error
constant = Constant(1250, 1250, 1)

# Edge: traffic, ratio, max_latency, capacity, max_servers, cost
edge_set = []
edge_filename = "testcase/"+args.edge_file
edge_file = open(edge_filename,'r')
for i,line in enumerate(edge_file):
    if i % 6 == 0:
        traffic_set = list( map( int, line.split()))
    elif i % 6 == 1:
        ratio_rate_set = list( map( float, line.split()))
    elif i % 6 == 2:
        max_latency_set = list( map( float, line.split()))
    elif i % 6 == 3:
        capacity_set = list( map( int, line.split()))
    elif i % 6 == 4:
        cost_set = list( map( int, line.split()))
    else:
        max_servers_set = list( map( int, line.split()))
        
for i in range(len(traffic_set)):
    edge_set.append(Edge(i, traffic_set[i], ratio_rate_set[i], max_latency_set[i], capacity_set[i], max_servers_set[i], cost_set[i], constant.least_error))

edge_file.close()

# Fog: capacity, cost, current_vehicles, arrival_rate, departure_rate, edge_transmission_rate, fog_transmission_rate
fog_set = []
fog_filename = "testcase/"+args.fog_file
fog_file = open(fog_filename,'r')
for i,line in enumerate(fog_file):
    if i % 5 == 0:
        capacity_set = list( map( int, line.split()))
    elif i % 5 == 1:
        cost_set = list( map( int, line.split()))
    elif i % 5 == 2:
        current_vehicles_set = list( map( int, line.split()))
    elif i % 5 == 3:
        arrival_rate_set = list( map( int, line.split()))
    else:
        departure_rate_set = list( map( int, line.split()))

for i in range(len(capacity_set)):
    fog_set.append(Fog(i, capacity_set[i], cost_set[i], current_vehicles_set[i], arrival_rate_set[i], departure_rate_set[i], constant.edge_transmission_rate, constant.fog_transmission_rate))
    for e in edge_set:
        e.append_fog_list(i, capacity_set[i], cost_set[i], current_vehicles_set[i], arrival_rate_set[i], departure_rate_set[i], constant.edge_transmission_rate, constant.fog_transmission_rate)
fog_file.close()

# Matching method
loop_flag = True
while loop_flag:

    # Edge makes a proposal to fog with its marginal value
    proposal_list = []
    for e in edge_set:
        if e.available:
            proposal = e.propose()
            if proposal is not None:
                proposal_list.append(proposal)

    # Fog choose the edge from its preference list
    for p in proposal_list:
        fog_set[p['f_id']].edge_table.append({'index': p['e_id'], 'used_vehicles': p['used_vehicles'], 'cmp_value': p['cmp_value']})

    print(proposal_list)
    response_list = []
    for f in fog_set:
        response_list.append(f.response())
    response = [item for sublist in response_list for item in sublist]
    print(response)
    # This edge gets response from the corresponding fog
    for e in edge_set:
        if e.available:
            if e.index in response:
                e.confirm()
            else:
                e.preference_list.clear()
                e.clearAll()

            # Update the vehicles information of fog
            for f in fog_set:
                if e.fog_list[f.index].available:
                    e.fog_list[f.index].max_vehicles = f.max_vehicles
                    if f.max_vehicles == 0:
                        e.fog_list[f.index].available = False

    # Make sure all of preference list would not be empty
    for e in edge_set:
        if e.available:
            loop_flag = True
            break
        loop_flag = False

for e in edge_set:
    e.display()