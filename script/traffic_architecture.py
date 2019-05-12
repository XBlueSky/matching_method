from edge.edge import Edge
from fog_set.fog_set import Fog_Set
from constant.constant import Constant
from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.core.properties import value
from bokeh.io import export_svgs
import random
from argparse import ArgumentParser

# parser = ArgumentParser(description= "Greedy Method")
# parser.add_argument("filename", help="testcase file path")
# args = parser.parse_args()

traffic_list        = []
# latency_list    = []

total_cost_fixed    = []
edge_cost_fixed     = []
fog_cost_fixed      = []
CP_cost             = []
cost_cost           = []
traffic_cost        = []

total_cost_list     = []
edge_cost_list      = []
fog_cost_list       = []
total_cost_list_2   = []
edge_cost_list_2    = []
fog_cost_list_2     = []
# Initial

# Constant: traffic, ratio, max_latency, least_error
constant = Constant(500, 0.01, 1, 1)

# Edge: capacity, max_servers, cost
edge = Edge(200, 5, 200)

for i in range(10):
    total_cost          = []
    edge_cost           = []
    fog_cost            = []
    total_cost_2        = []
    edge_cost_2         = []
    fog_cost_2          = []
    # Fog_Set: ratio, edge_transmission_rate, fog_transmission_rate, vehicle_transmission_rate, capacity, total_fogs, testcase file
    # fogs_num = args.filename.split("_")
    # file_name = "testcase/"+args.filename
    # fog_set = Fog_Set(constant.ratio, 1250, 1250, 125, 5, int(fogs_num[1]), file_name)
    fog_set = Fog_Set(constant.ratio, 1250, 1250, 125, 5, 10, "testcase/Sfog_10_v" + str(i+1))

    # collections = ["edge_10"]
    # colors      = ['#0D3331', 'darkslategray', "#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
    # for f in fog_set.fog_list:
    #     collections.append("F" + str(f.index) + "_" + str(f.total_vehicles))
    # data = dict((c,[]) for c in collections)
    # data['traffic'] = []

    for t in range(50, 2550, 50):
        
        # edge.set_traffic(t)
        # fog_set.set_traffic(t)
        
        # for cost_type in ['fixed', 'diff']:
        for cost_type in ['diff']:
        # for algorithm_type in ['cost', 'traffic', 'CP']:
            
            for architecture in [2, 3]:
            
                success = True
                traffic = t
                bundle_list = []
                empty_list = []
                algorithm = 'CP'
                if architecture == 2:            
                    edge.algorithm(traffic, constant.max_latency, constant.least_error)
                    bundle_list.append({'id': 'edge', 'traffic': edge.max_traffic, 'cost': edge.edge_cost(), 'CP': edge.max_traffic / edge.edge_cost(), 'chosen': False})
                        
                    fog_set.vehicle_list.algorithm(traffic, constant.max_latency, constant.least_error)
                    for v in fog_set.vehicle_list.vehicle_set:
                        if cost_type == 'fixed':
                            cost = 10
                        else:
                            cost = v.cost
                        if v.max_traffic > 0:
                            bundle_list.append({'id': v.index, 'traffic': v.max_traffic, 'cost': cost, 'CP': v.max_traffic / cost, 'chosen': False})
                    
                    # Sort by CP value
                    # if algorithm_type == 'CP':
                    #     bundle_list.sort(key=lambda b : b['CP'], reverse=True)
                    # elif algorithm_type == 'cost':
                    #     bundle_list.sort(key=lambda b : b['cost'], reverse=False)
                    # else:
                    #     bundle_list.sort(key=lambda b : b['traffic'], reverse=True)
                    bundle_list.sort(key=lambda b : b['CP'], reverse=True)

                    traffic_sum = 0
                    for bundle in bundle_list:
                        if traffic_sum + bundle['traffic'] <= traffic:
                            traffic_sum = traffic_sum + bundle['traffic']
                            bundle['chosen'] = True
                        else:
                            if traffic_sum < traffic:
                                traffic_sum = traffic_sum + bundle['traffic']
                                bundle['chosen'] = True
                            break

                    for bundle in bundle_list:
                        if bundle['chosen'] == True:
                            if bundle['id'] == 'edge':
                                edge.used = True
                            else:
                                fog_set.vehicle_list.vehicle_set[bundle['id']].used_bit = True
                    bundle_list.clear()

                    # if traffic_sum < traffic:
                    #     # print("There is no enough capacity")
                    #     success = False
                    #     break
                
                else:
                    while traffic > constant.least_error:
                        # Edge and all of fog would calculate its own maximum traffic
                        if edge.used == False:
                            edge.algorithm(traffic, constant.max_latency, constant.least_error)
                            bundle_list.append({'id': 'edge', 'traffic': edge.max_traffic, 'cost': edge.edge_cost(), 'CP': edge.max_traffic / edge.edge_cost(), 'chosen': False})

                        for f in fog_set.fog_list:
                            if f.used == False:
                                f.algorithm(traffic, constant.max_latency, constant.least_error, 'diff', algorithm)
                                if cost_type == 'fixed':
                                    cost = f.fog_fixed_cost(10)
                                else:
                                    cost = f.fog_cost()
                                # cost = f.fog_cost()
                                if f.max_traffic > 0:
                                    bundle_list.append({'id': f.index, 'traffic': f.max_traffic, 'cost': cost, 'CP': f.max_traffic / cost, 'chosen': False})
                                else:
                                    empty_list.append({'id': f.index, 'traffic': 0, 'cost': 0, 'CP': 0, 'chosen': False})

                        if not bundle_list:
                            if algorithm == 'max':
                                print("There is no enough capacity")
                            #     success = False
                                break
                            else:
                                print("change", t)
                                algorithm = 'max'
                                traffic = t
                                bundle_list.clear()
                                edge.clear()
                                fog_set.clear()
                                continue

                        # Sort by CP value
                        # if algorithm_type == 'CP':
                        #     bundle_list.sort(key=lambda b : b['CP'], reverse=True)
                        # elif algorithm_type == 'cost':
                        #     bundle_list.sort(key=lambda b : b['cost'], reverse=False)
                        # else:
                        #     bundle_list.sort(key=lambda b : b['traffic'], reverse=True)
                        bundle_list.sort(key=lambda b : b['CP'], reverse=True)
                        traffic_sum = 0
                        for bundle in bundle_list:
                            if traffic_sum + bundle['traffic'] <= traffic:
                                traffic_sum = traffic_sum + bundle['traffic']
                                bundle['chosen'] = True
                            else:
                                break
                        
                        traffic = traffic - traffic_sum
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

                if success:
                    if architecture == 2:
                        if cost_type == 'fixed':
                            total_cost_2.append(edge.edge_cost() + fog_set.vehicle_list.total_vehicle_fixed_cost(10))
                            edge_cost_2.append(edge.edge_cost())
                            fog_cost_2.append(fog_set.vehicle_list.total_vehicle_fixed_cost(10))
                        else:
                            total_cost_2.append(edge.edge_cost() + fog_set.vehicle_list.total_vehicle_cost())
                            edge_cost_2.append(edge.edge_cost())
                            fog_cost_2.append(fog_set.vehicle_list.total_vehicle_cost())

                    else:
                        # data['traffic'].append(str(t))
                        # traffic_list.append(str(t))
                        # for i, c in enumerate(collections):
                        #     if i == 0:
                        #         data[c].append(edge.max_traffic)
                        #     else:
                        #         if fog_set.fog_list[i - 1].max_traffic > 0:
                        #             data[c].append(fog_set.fog_list[i - 1].max_traffic)
                        #         else:
                        #             data[c].append(0)
                        # data['traffic'].append(str(t))
                        # traffic_list.append(str(t))
                        # for i, c in enumerate(collections):
                        #     if i == 0:
                        #         data[c].append(edge.active_servers)
                        #     else:
                        #         data[c].append(fog_set.fog_list[i - 1].used_vehicles)
                        if cost_type == 'fixed':
                            if i == 0:
                                traffic_list.append(t)
                            total_cost.append(edge.edge_cost() + fog_set.fog_set_fixed_cost(10))
                            edge_cost.append(edge.edge_cost())
                            fog_cost.append(fog_set.fog_set_fixed_cost(10))
                        else:
                            if i == 0:
                                traffic_list.append(t)
                            total_cost.append(edge.edge_cost() + fog_set.fog_set_cost())
                            edge_cost.append(edge.edge_cost())
                            fog_cost.append(fog_set.fog_set_cost())
                    
                    # if algorithm_type == 'CP':
                    #     traffic_list.append(t)
                    #     CP_cost.append(edge.edge_cost() + fog_set.fog_set_cost())
                    # elif algorithm_type == 'cost':
                    #     cost_cost.append(edge.edge_cost() + fog_set.fog_set_cost())
                    # else:
                    #     traffic_cost.append(edge.edge_cost() + fog_set.fog_set_cost())
                    
                    # edge.display()
                    # fog_set.display()

                edge.clear()
                fog_set.clear()
    
    total_cost_list.append(total_cost)
    edge_cost_list.append(edge_cost)
    fog_cost_list.append(fog_cost)
    total_cost_list_2.append(total_cost_2)
    edge_cost_list_2.append(edge_cost_2)
    fog_cost_list_2.append(fog_cost_2)

totalCost          = []
edgeCost           = []
fogCost            = []
totalCost_2        = []
edgeCost_2         = []
fogCost_2          = []
for index in range(len(total_cost)):
    totalCost.append(sum([ c[index] for c in total_cost_list]) / len(total_cost_list))
    edgeCost.append(sum([ c[index] for c in edge_cost_list]) / len(total_cost_list))
    fogCost.append(sum([ c[index] for c in fog_cost_list]) / len(total_cost_list))
    totalCost_2.append(sum([ c[index] for c in total_cost_list_2]) / len(total_cost_list))
    edgeCost_2.append(sum([ c[index] for c in edge_cost_list_2]) / len(total_cost_list))
    fogCost_2.append(sum([ c[index] for c in fog_cost_list_2]) / len(total_cost_list))



    
# output to static HTML file
# output_file("graph/traffic-cost.html")
# output_file("graph/S_fog/architecture/cost.html")

# p = figure(x_range=traffic_list, plot_width=1600, plot_height=900, title="traffic distribution",
#             tooltips="$name \ @$name")

# p.vbar_stack(collections, x='traffic', width=0.9, line_width=0, line_color='white',fill_color=colors, source=data,
#              legend=[value(x) for x in collections])

# p.y_range.start = 0
# p.x_range.range_padding = 0.1
# p.xgrid.grid_line_color = None
# p.axis.minor_tick_line_color = None
# p.outline_line_color = None
# p.legend.location = "top_left"
# p.legend.orientation = "horizontal"

TOOLTIPS = [
        ("index", "$index"),
        ("traffic", "$x"),
        ("cost", "$y"),
    ]

# create a new plot with a title and axis labels
p = figure(plot_width=750, plot_height=500, x_axis_label='Araival Traffic', y_axis_label='Cost', tooltips=TOOLTIPS)

# add a line renderer with legend and line thickness

p.line(traffic_list, totalCost, legend="Total.", line_width=2)
p.line(traffic_list, edgeCost, legend="Edge.", line_width=2, line_color="dodgerblue")
p.line(traffic_list, fogCost, legend="Fog.", line_width=2, line_color="deepskyblue")
p.line(traffic_list, totalCost_2, legend="Total Two-tier.", line_width=2, line_color="red", line_dash="4 4")
p.line(traffic_list, edgeCost_2, legend="Edge Two-tier.", line_width=2, line_color="tomato", line_dash="4 4")
p.line(traffic_list, fogCost_2, legend="Fog Two-tier.", line_width=2, line_color="orange", line_dash="4 4")
# p.line(traffic_list, CP_cost, legend="CP.", line_width=3)
# p.line(traffic_list, cost_cost, legend="cost.", line_width=3, line_color="#e84d60")
# p.line(traffic_list, traffic_cost, legend="traffic.", line_width=3, line_color="lightseagreen")

# p.circle(traffic_list, totalCost_2, fill_color="red", line_color="red", size=7)
# p.circle(traffic_list, edgeCost_2, fill_color="tomato", line_color="tomato", size=7)
# p.circle(traffic_list, fogCost_2, fill_color="pink", line_color="pink", size=7)
# p.circle(traffic_list, totalCost, size=7)
# p.circle(traffic_list, edgeCost, fill_color="dodgerblue", line_color="dodgerblue", size=7)
# p.circle(traffic_list, fogCost, fill_color="deepskyblue", line_color="deepskyblue", size=7)
# p.circle(traffic_list, CP_cost, size=7)
# p.circle(traffic_list, cost_cost, fill_color="#e84d60", line_color="#e84d60", size=7)
# p.circle(traffic_list, traffic_cost, fill_color="lightseagreen", line_color="lightseagreen", size=7)

p.xaxis.axis_label_text_font_size = "12pt"
p.yaxis.axis_label_text_font_size = "12pt"
p.legend.location = "top_left"
# show the results
# show(p)
p.output_backend = "svg"
export_svgs(p, filename="graph/S_fog/architecture/cost.svg")


