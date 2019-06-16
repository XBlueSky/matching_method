from edge.edge import Edge
from fog_set.fog import Fog
from constant.constant import Constant
from distribution.distribution import Distribution
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.core.properties import value
from bokeh.io import export_svgs
import random
import csv
from argparse import ArgumentParser

parser = ArgumentParser(description= "Matching Method")
parser.add_argument("edge_file", help="testcase file path")
parser.add_argument("fog_file", help="testcase file path")
args = parser.parse_args()

# Initial

# Constant: edge_transmission_rate, fog_transmission_rate, least_error
constant = Constant(1250, 1250, 1)

xaxis_list              = []
total_list              = []
total_edge_list         = []
total_fog_list          = []
total_list_2            = []
total_edge_list_2       = []
total_fog_list_2        = []
total_list_3            = []
cost_capacity_parm      = 1
server_num              = 1
loop                    = 50
total_vehicles          = 300

for traffic in range(0, 650, 50):
    # Variable: traffic
    xaxis_list.append(traffic)
    
    cost_set        = []
    for algo_type in range(3):
        
        total_edge_cost = 0
        total_fog_cost = 0

        for iteration in range(loop):
            print(str(traffic) + "-" + str(algo_type) + "-" + str(iteration))
            max_servers_set = []
            traffic_set     = []
            
            # Edge: traffic, ratio, max_latency, capacity, max_servers, cost
            edge_set = []
            edge_filename = "testcase/"+args.edge_file
            edge_file = open(edge_filename,'r')
            for i,line in enumerate(edge_file):
                if i % 6 == 0:
                    # if algo_type == 0 and iteration == 0:
                    for num in list( map( int, line.split())):
                        traffic_set.append(random.normalvariate(traffic, traffic / 5))
                    # traffic_set = list( map( int, line.split()))
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
                edge_set.append(Edge(i, traffic_set[i], ratio_rate_set[i], max_latency_set[i], cost_capacity_parm*capacity_set[i], max_servers_set[i], cost_capacity_parm*cost_set[i], constant.least_error))

            edge_file.close()

            # Fog: capacity, cost, current_vehicles, arrival_rate, departure_rate, edge_transmission_rate, fog_transmission_rate
            fog_set = []
            arrival_rate_set        = []
            departure_rate_set      = []
            current_vehicles_set    = []
            fog_filename = "testcase/"+args.fog_file
            fog_file = open(fog_filename,'r')
            for i,line in enumerate(fog_file):
                if i % 5 == 0:
                    capacity_set = list( map( int, line.split()))
                elif i % 5 == 1:
                    # for num in list( map( int, line.split())):
                    #     cost_set.append(random.randint(1,20))
                    cost_set = list( map( int, line.split()))
                elif i % 5 == 2:
                    current_vehicles_set = list( map( int, line.split()))
                elif i % 5 == 3:
                    for num in list( map( int, line.split())):
                        arrival_rate_set.append(0)
                    # arrival_rate_set = list( map( int, line.split()))
                else:
                    for num in list( map( int, line.split())):
                        departure_rate_set.append(0)
                    # departure_rate_set = list( map( int, line.split()))

            # current_vehicles_set = Distribution.exponential(total_vehicles, len(capacity_set))

            for i in range(len(capacity_set)):
                fog_set.append(Fog(i, capacity_set[i], cost_set[i], current_vehicles_set[i], arrival_rate_set[i], departure_rate_set[i], constant.edge_transmission_rate, constant.fog_transmission_rate))
                for e in edge_set:
                    e.append_fog_list(i, capacity_set[i], cost_set[i], current_vehicles_set[i], arrival_rate_set[i], departure_rate_set[i], constant.edge_transmission_rate, constant.fog_transmission_rate)
            fog_file.close()
            
            # Matching method
            if algo_type == 0:
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

                    # print(proposal_list)
                    response_list = []
                    for f in fog_set:
                        response_list.append(f.response())
                    response = [item for sublist in response_list for item in sublist]
                    # print(response)
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
                                e.fog_list[f.index].max_vehicles = f.max_vehicles
                                if f.max_vehicles == 0:
                                    e.fog_list[f.index].available = False

                    # Make sure all of preference list would not be empty
                    for e in edge_set:
                        if e.available:
                            loop_flag = True
                            break
                        loop_flag = False

            # Trivial Method (number)
            if algo_type == 1 and traffic > 0:
                edge_traffic_set = []
                for e in edge_set:
                    edge_traffic = e.trivial_algorithm()
                    if edge_traffic > e.least_error:
                        edge_traffic_set.append({'index': e.index, 'traffic': edge_traffic})
                # print(edge_traffic_set)

                while len(edge_traffic_set) > 0:
                    edge_traffic_set.sort(key=lambda b : b['traffic'], reverse=True)

                    fog_vehicles_set = []
                    for f in fog_set:
                        fog_vehicles_set.append({'index': f.index, 'vehicles': f.max_vehicles})
                    fog_vehicles_set.sort(key=lambda b : b['vehicles'], reverse=True)

                    fog_traffic = fog_set[fog_vehicles_set[0]['index']].trivial_algorithm(edge_traffic_set[0]['traffic'], edge_set[edge_traffic_set[0]['index']].max_latency, edge_set[edge_traffic_set[0]['index']].least_error)
                    edge_traffic_set[0]['traffic'] = edge_traffic_set[0]['traffic'] - fog_traffic

                    if(edge_traffic_set[0]['traffic'] < edge_set[edge_traffic_set[0]['index']].least_error):
                        del edge_traffic_set[0]
            
            # Trivial Method (cost)
            if algo_type == 2 and traffic > 0:
                edge_traffic_set = []
                for e in edge_set:
                    edge_traffic = e.trivial_algorithm()
                    if edge_traffic > e.least_error:
                        edge_traffic_set.append({'index': e.index, 'traffic': edge_traffic})
                # print(edge_traffic_set)

                while len(edge_traffic_set) > 0:
                    edge_traffic_set.sort(key=lambda b : b['traffic'], reverse=True)

                    fog_cost_set = []
                    for f in fog_set:
                        if f.max_vehicles > 0:
                            fog_cost_set.append({'index': f.index, 'cost': f.max_vehicles})
                    fog_cost_set.sort(key=lambda b : b['cost'], reverse=False)

                    fog_traffic = fog_set[fog_cost_set[0]['index']].trivial_algorithm(edge_traffic_set[0]['traffic'], edge_set[edge_traffic_set[0]['index']].max_latency, edge_set[edge_traffic_set[0]['index']].least_error)
                    edge_traffic_set[0]['traffic'] = edge_traffic_set[0]['traffic'] - fog_traffic

                    if(edge_traffic_set[0]['traffic'] < edge_set[edge_traffic_set[0]['index']].least_error):
                        del edge_traffic_set[0]

            # Collect total edge cost from edge set
            for e in edge_set:
                # e.display()
                total_edge_cost = total_edge_cost + e.edge_cost()
            
            # Collect total fog cost from edge set
            for f in fog_set:
                total_fog_cost = total_fog_cost + f.fog_cost()

            # print(total_fog_cost)

            edge_set.clear()
            fog_set.clear()

        if algo_type == 0:
            # total_edge_list.append(total_edge_cost / loop)
            # total_fog_list.append(total_fog_cost / loop)
            total_list.append((total_edge_cost + total_fog_cost) / loop)
        elif algo_type == 1:
            # total_edge_list_2.append(total_edge_cost / loop)
            # total_fog_list_2.append(total_fog_cost / loop)
            total_list_2.append((total_edge_cost + total_fog_cost) / loop)
        else:
            total_list_3.append((total_edge_cost + total_fog_cost) / loop)
            
                

# Graphic Design in Bokeh

# create a new plot with a title and axis labels

TOOLTIPS = [
        ("index", "$index"),
        ("traffic", "$x"),
        ("cost", "$y"),
    ]

p = figure(plot_width=600, plot_height=400, x_axis_label='Araival Traffic Mean (mb/s)', y_axis_label='Total Cost ($)', tooltips=TOOLTIPS)

# Default
p.line(xaxis_list, total_list, legend="matching", line_width=2, line_color="red")
p.line(xaxis_list, total_list_2, legend="trivial(number)", line_width=1, line_color="tomato")
p.line(xaxis_list, total_list_3, legend="trivial(cost)", line_width=1, line_color="orange")

p.circle(xaxis_list, total_list, legend="matching", fill_color="red", line_color="red", size=7)
p.x(xaxis_list, total_list_2, legend="trivial(number)", line_color="tomato", size=5)
p.circle(xaxis_list, total_list_3, legend="trivial(cost)", fill_color="white", line_color="orange", size=5)

# p.line(xaxis_list, total_list, legend="Total cost by Matching", line_width=2, line_color="red")
# p.line(xaxis_list, total_edge_list, legend="Edge cost by Matching", line_width=1, line_color="tomato")
# p.line(xaxis_list, total_fog_list, legend="Fog cost by Matching", line_width=1, line_color="orange")

# p.circle(xaxis_list, total_list, legend="Total cost by Matching", fill_color="red", line_color="red", size=7)
# p.x(xaxis_list, total_edge_list, legend="Edge cost by Matching", line_color="tomato", size=5)
# p.circle(xaxis_list, total_fog_list, legend="Fog cost by Matching", fill_color="white", line_color="orange", size=5)

# p.line(xaxis_list, total_list_2, legend="Total cost by Trivial", line_width=3, line_dash='solid')
# p.line(xaxis_list, total_edge_list_2, legend="Edge cost by Trivial", line_width=2, line_color="dodgerblue" ,line_dash='dotted')
# p.line(xaxis_list, total_fog_list_2, legend="Fog cost by Trivial", line_width=2, line_color="deepskyblue", line_dash="dashdot")

p.xaxis.axis_label_text_font_size = "15pt"
p.yaxis.axis_label_text_font_size = "15pt"
p.xaxis.major_label_text_font_size = "12pt"
p.yaxis.major_label_text_font_size = "12pt"
p.legend.location = "top_left"

p.output_backend = "svg"
export_svgs(p, filename="graph/final/algo/0-600_normal_L_cost.svg")

with open('graph/final/algo/csv/0-600_normal_L_cost.csv', 'w', newline='') as csvfile:

    # space for delimiter
    writer = csv.writer(csvfile, delimiter=' ')

    # writer.writerow(['Traffic', 'Total cost by Matching', 'Edge cost by Matching', 'Fog cost by Matching', 'Total cost by Trivial', 'Edge cost by Trivial', 'Fog cost by Trivial'])
    writer.writerow(['Traffic', 'matching', 'trivial(number)', 'trivial(cost)'])
    
    for i in range(len(xaxis_list)):
        # writer.writerow([xaxis_list[i], total_list[i], total_edge_list[i], total_fog_list[i], total_list_2[i], total_edge_list_2[i], total_fog_list_2[i]])
        writer.writerow([xaxis_list[i], total_list[i], total_list_2[i], total_list_3[i]])