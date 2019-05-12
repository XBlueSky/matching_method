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

total_cost_list     = []
edge_cost_list      = []
fog_cost_list       = []
total_cost_d_list     = []
edge_cost_d_list      = []
fog_cost_d_list       = []
total_cost_fixed_list     = []
edge_cost_fixed_list      = []
fog_cost_fixed_list       = []
CP_cost_list        = []
cost_cost_list      = []
traffic_cost_list   = []
fixed_cost = 5
# Initial

# Constant: traffic, ratio, max_latency, least_error
constant = Constant(500, 0.01, 1, 1)

for capacity in [0]:
    # Edge: capacity, max_servers, cost
    if capacity == 0:
        edge = Edge(200, 5, 200)
    else:
        edge = Edge(1000, 1, 1000)

    for i in range(1):
        total_cost          = []
        edge_cost           = []
        fog_cost            = []
        total_cost_d          = []
        edge_cost_d           = []
        fog_cost_d           = []
        total_cost_fixed    = []
        edge_cost_fixed     = []
        fog_cost_fixed      = []
        CP_cost             = []
        cost_cost           = []
        traffic_cost        = []



        # Fog_Set: ratio, edge_transmission_rate, fog_transmission_rate, capacity, total_fogs, testcase file
        # fogs_num = args.filename.split("_")
        # file_name = "testcase/"+args.filename
        # fog_set = Fog_Set(constant.ratio, 1250, 1250, 125, 5, int(fogs_num[1]), file_name)
        fog_set = Fog_Set(constant.ratio, 1250, 1250, 125, 5, 10, "testcase/Sfog_10_v" + str(i+1))

        collections = ["edge_10"]
        colors      = ['#0D3331', 'darkslategray', "#75968f", "#a5bab7", "#c9d9d3", "#e2e2e2", "#dfccce", "#ddb7b1", "#cc7878", "#933b41", "#550b1d"]
        for f in fog_set.fog_list:
            collections.append("F" + str(f.index) + "_" + str(f.total_vehicles))
        data = dict((c,[]) for c in collections)
        data['traffic'] = []

        for t in range(0, 3200, 200):
            
            # edge.set_traffic(t)
            # fog_set.set_traffic(t)
            success = True
            # for cost_type in ['fixed', 'diff']:
            for cost_type in ['diff']:
            # for algorithm_type in ['cost', 'traffic', 'CP']:
                # 0/1 knapsack problem with (1 − 1/ sqrt(e)) bound
                traffic = t
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
                            if cost_type == 'fixed':
                                f.algorithm(traffic, constant.max_latency, constant.least_error, fixed_cost, algorithm)
                                cost = f.fog_fixed_cost(fixed_cost)
                            else:
                                f.algorithm(traffic, constant.max_latency, constant.least_error, 'diff', algorithm)
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

                if cost_type == 'fixed':
                    if success:
                        total_cost_fixed.append(edge.edge_cost() + fog_set.fog_set_fixed_cost(fixed_cost))
                        edge_cost_fixed.append(edge.edge_cost())
                        fog_cost_fixed.append(fog_set.fog_set_fixed_cost(fixed_cost))
                else:
                    data['traffic'].append(str(t))
                    traffic_list.append(str(t))
                    for i, c in enumerate(collections):
                        if i == 0:
                            data[c].append(edge.max_traffic)
                        else:
                            if fog_set.fog_list[i - 1].max_traffic > 0:
                                data[c].append(fog_set.fog_list[i - 1].max_traffic)
                            else:
                                data[c].append(0)
                    # data['traffic'].append(str(t))
                    # traffic_list.append(str(t))
                    # for i, c in enumerate(collections):
                    #     if i == 0:
                    #         data[c].append(edge.active_servers)
                    #     else:
                    #         data[c].append(fog_set.fog_list[i - 1].used_vehicles)
                    # if capacity == 0:
                    #     if i == 0:
                    #         traffic_list.append(t)
                    #     if success:
                    #         total_cost.append(edge.edge_cost() + fog_set.fog_set_cost())
                    #         edge_cost.append(edge.edge_cost())
                    #         fog_cost.append(fog_set.fog_set_cost())
                    #     else:
                    #         total_cost.append(0)
                    #         edge_cost.append(0)
                    #         fog_cost.append(0)
                    # else:
                    #     total_cost_d.append(edge.edge_cost() + fog_set.fog_set_cost())
                    #     edge_cost_d.append(edge.edge_cost())
                    #     fog_cost_d.append(fog_set.fog_set_cost())
                
                    # if algorithm_type == 'CP':
                    #     if i == 0:
                    #         traffic_list.append(t)
                    #     CP_cost.append(edge.edge_cost() + fog_set.fog_set_cost())
                    # elif algorithm_type == 'cost':
                    #     cost_cost.append(edge.edge_cost() + fog_set.fog_set_cost())
                    # else:
                    #     traffic_cost.append(edge.edge_cost() + fog_set.fog_set_cost())
                    
                    # edge.display()
                    # fog_set.display()

                edge.clear()
                fog_set.clear()


        # CP_cost_list.append(CP_cost)
        # cost_cost_list.append(cost_cost)
        # traffic_cost_list.append(traffic_cost)
        # if capacity == 0:
        #     total_cost_list.append(total_cost)
        #     edge_cost_list.append(edge_cost)
        #     fog_cost_list.append(fog_cost)
        #     total_cost_fixed_list.append(total_cost_fixed)
        #     edge_cost_fixed_list.append(edge_cost_fixed)
        #     fog_cost_fixed_list.append(fog_cost_fixed)
        # else:
        #     total_cost_d_list.append(total_cost_d)
        #     edge_cost_d_list.append(edge_cost_d)
        #     fog_cost_d_list.append(fog_cost_d)
            

totalCost          = []
edgeCost           = []
fogCost            = []
totalCostD          = []
edgeCostD           = []
fogCostD            = []
totalCostFixed          = []
edgeCostFixed           = []
fogCostFixed            = []

# for index in range(len(traffic_list)):
#     totalCost.append(sum([ c[index] for c in total_cost_list]) / len(total_cost_list))
#     edgeCost.append(sum([ c[index] for c in edge_cost_list]) / len(total_cost_list))
#     fogCost.append(sum([ c[index] for c in fog_cost_list]) / len(total_cost_list))
#     totalCostD.append(sum([ c[index] for c in total_cost_d_list]) / len(total_cost_d_list))
#     edgeCostD.append(sum([ c[index] for c in edge_cost_d_list]) / len(total_cost_d_list))
#     fogCostD.append(sum([ c[index] for c in fog_cost_d_list]) / len(total_cost_d_list))
    # totalCostFixed .append(sum([ c[index] for c in total_cost_fixed_list]) / len(total_cost_fixed_list))
    # edgeCostFixed .append(sum([ c[index] for c in edge_cost_fixed_list]) / len(total_cost_fixed_list))
    # fogCostFixed .append(sum([ c[index] for c in fog_cost_fixed_list]) / len(total_cost_fixed_list))

# CPCost          = []
# costCost           = []
# trafficCost            = []

# for index in range(len(traffic_list)):
#     CPCost.append(sum([ c[index] for c in CP_cost_list]) / len(CP_cost_list))
#     costCost.append(sum([ c[index] for c in cost_cost_list]) / len(cost_cost_list))
#     trafficCost.append(sum([ c[index] for c in traffic_cost_list]) / len(traffic_cost_list))

# output to static HTML file
# output_file("graph/traffic-cost.html")
# output_file("graph/S_fog/traffic/cost.html")

p = figure(x_range=traffic_list, plot_width=750, plot_height=500, x_axis_label='Araival Traffic', y_axis_label='Traffic Distribution', y_range=(0, 3500),
            tooltips="$name \ @$name")

p.vbar_stack(collections, x='traffic', width=0.8, line_width=0, line_color='white',fill_color=colors, source=data,
             legend=[value(x) for x in collections])

p.y_range.start = 0
p.x_range.range_padding = 0.1
p.xgrid.grid_line_color = None
p.axis.minor_tick_line_color = None
p.outline_line_color = None
p.legend.location = "top_left"
p.legend.orientation = "horizontal"

TOOLTIPS = [
        ("index", "$index"),
        ("traffic", "$x"),
        ("cost", "$y"),
    ]

# create a new plot with a title and axis labels
# p = figure(plot_width=750, plot_height=500, x_axis_label='Araival Traffic', y_axis_label='Cost', tooltips=TOOLTIPS)

# add a line renderer with legend and line thickness
# p.line(traffic_list, totalCost, legend="Total", line_width=2)
# p.line(traffic_list, edgeCost, legend="Edge.", line_width=2, line_color="dodgerblue")
# p.line(traffic_list, fogCost, legend="Fog.", line_width=2, line_color="deepskyblue")
# p.line(traffic_list, totalCostD, legend="Total Central.", line_width=2, line_color="red", line_dash="4 4")
# p.line(traffic_list, edgeCostD, legend="Edge Central.", line_width=2, line_color="tomato", line_dash="4 4")
# p.line(traffic_list, fogCostD, legend="Fog Central.", line_width=2, line_color="orange", line_dash="4 4")
# p.line(traffic_list, totalCostFixed, legend="total-fixed.", line_width=3, line_color="red")
# p.line(traffic_list, edgeCostFixed, legend="edge-fixed.", line_width=3, line_color="tomato")
# p.line(traffic_list, fogCostFixed, legend="fog-fixed.", line_width=3, line_color="pink")
# p.line(traffic_list, CPCost, legend="CP.", line_width=3)
# p.line(traffic_list, costCost, legend="cost.", line_width=3, line_color="#e84d60")
# p.line(traffic_list, trafficCost, legend="traffic.", line_width=3, line_color="lightseagreen")


# p.circle(traffic_list, totalCost, size=7)
# p.circle(traffic_list, edgeCost, fill_color="dodgerblue", line_color="dodgerblue", size=7)
# p.circle(traffic_list, fogCost, fill_color="deepskyblue", line_color="deepskyblue", size=7)
# p.circle(traffic_list, totalCostD, fill_color="red", line_color="red", size=7)
# p.circle(traffic_list, edgeCostD, fill_color="tomato", line_color="tomato", size=7)
# p.circle(traffic_list, fogCostD, fill_color="pink", line_color="pink", size=7)
# p.circle(traffic_list, totalCostFixed, fill_color="red", line_color="red", size=7)
# p.circle(traffic_list, edgeCostFixed, fill_color="tomato", line_color="tomato", size=7)
# p.circle(traffic_list, fogCostFixed, fill_color="pink", line_color="pink", size=7)
# p.circle(traffic_list, CPCost, size=7)
# p.circle(traffic_list, costCost, fill_color="#e84d60", line_color="#e84d60", size=7)
# p.circle(traffic_list, trafficCost, fill_color="lightseagreen", line_color="lightseagreen", size=7)

p.xaxis.axis_label_text_font_size = "12pt"
p.yaxis.axis_label_text_font_size = "12pt"
# p.legend.location = "top_left"

# show the results
# show(p)
p.output_backend = "svg"
export_svgs(p, filename="graph/S_fog/traffic/traffic_allocation.svg")