from edge.edge import Edge
from fog_set.fog import Fog
from constant.constant import Constant
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.core.properties import value
from bokeh.io import export_svgs
from argparse import ArgumentParser
import csv

parser = ArgumentParser(description= "Matching Method")
parser.add_argument("edge_file", help="testcase file path")
parser.add_argument("fog_file", help="testcase file path")
args = parser.parse_args()

# Initial

# Constant: edge_transmission_rate, fog_transmission_rate, least_error
constant = Constant(1250, 1250, 1)

xaxis_list              = []
total_cost_list         = []
total_edge_cost_list    = []
total_fog_cost_list     = []
server_num              = 1

for fog_cost in range(1, 21):
    # Variable: Fog cost
    # fog_cost = (iteration + 1) * 5
    xaxis_list.append(fog_cost)
    max_servers_set = []

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
            for num in list( map( int, line.split())):
                max_servers_set.append(server_num)
            # max_servers_set = list( map( int, line.split()))
      
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
        fog_set.append(Fog(i, capacity_set[i], fog_cost, current_vehicles_set[i], arrival_rate_set[i], departure_rate_set[i], constant.edge_transmission_rate, constant.fog_transmission_rate))
        for e in edge_set:
            e.append_fog_list(i, capacity_set[i], fog_cost, current_vehicles_set[i], arrival_rate_set[i], departure_rate_set[i], constant.edge_transmission_rate, constant.fog_transmission_rate)
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
            fog_set[p['f_id']].edge_table.append({'index': p['e_id'], 'used_vehicles': p['used_vehicles'], 'cmp_value': p['cmp_value'], 'traffic': p['traffic']})

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

    # Collect total edge cost from edge set
    total_edge_cost = 0
    for e in edge_set:
        # e.display()
        total_edge_cost = total_edge_cost + e.edge_cost()
    total_edge_cost_list.append(total_edge_cost)
    
    # Collect total fog cost from edge set
    total_fog_cost = 0
    for f in fog_set:
        total_fog_cost = total_fog_cost + f.fog_cost()
    print(total_fog_cost)
    total_fog_cost_list.append(total_fog_cost)

    total_cost_list.append(total_edge_cost + total_fog_cost)
    edge_set.clear()
    fog_set.clear()


# Graphic Design in Bokeh

# create a new plot with a title and axis labels

TOOLTIPS = [
        ("index", "$index"),
        ("traffic", "$x"),
        ("cost", "$y"),
    ]

p = figure(plot_width=600, plot_height=400, x_axis_label='Cost of vehicle ($)', y_axis_label='Total Cost ($)', tooltips=TOOLTIPS)

p.line(xaxis_list, total_cost_list, legend="Total Cost", line_width=2, line_color="red")
p.line(xaxis_list, total_edge_cost_list, legend="Edge Cost", line_width=1, line_color="tomato")
p.line(xaxis_list, total_fog_cost_list, legend="Fog Cost", line_width=1, line_color="orange")

p.circle(xaxis_list, total_cost_list, legend="Total Cost", fill_color="red", line_color="red", size=7)
p.x(xaxis_list, total_edge_cost_list, legend="Edge Cost", line_color="tomato", size=5)
p.circle(xaxis_list, total_fog_cost_list, legend="Fog Cost", fill_color="white", line_color="orange", size=5)

p.xaxis.axis_label_text_font_size = "15pt"
p.yaxis.axis_label_text_font_size = "15pt"
p.xaxis.major_label_text_font_size = "12pt"
p.yaxis.major_label_text_font_size = "12pt"

p.output_backend = "svg"
export_svgs(p, filename="graph/fog_cost/1-20_S.svg")

with open('graph/fog_cost/csv/1-20_S.csv', 'w', newline='') as csvfile:

    # space for delimiter
    writer = csv.writer(csvfile, delimiter=' ')

    writer.writerow(['Traffic', 'Total Cost', 'Edge Cost', 'Fog Cost'])
    # writer.writerow(['Traffic', 'Total Cost of One Server Each Edge', 'Total Cost of Three Server Each Edge', 'Total Cost of Five Server Each Edge'])
    
    for i in range(len(xaxis_list)):
        writer.writerow([xaxis_list[i], total_cost_list[i], total_edge_cost_list[i], total_fog_cost_list[i]])
        # writer.writerow([xaxis_list[i], total_1_list[i], total_3_list[i], total_5_list[i]])