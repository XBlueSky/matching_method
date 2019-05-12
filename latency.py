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

# traffic_list        = []
latency_list    = []
total_cost          = []
edge_cost           = []
fog_cost            = []
total_cost_fixed    = []
edge_cost_fixed     = []
fog_cost_fixed      = []
CP_cost             = []
cost_cost           = []
traffic_cost        = []

total_cost_list     = []
edge_cost_list      = []
fog_cost_list       = []

# Initial

# Constant: traffic, ratio, max_latency, least_error
constant = Constant(1500, 0.01, 1, 1)

# Edge: capacity, max_servers, cost
edge = Edge(200, 5, 200)

for i in range(10):
    total_cost          = []
    edge_cost           = []
    fog_cost            = []

    # Fog_Set: ratio, edge_transmission_rate, fog_transmission_rate, capacity, total_fogs, testcase file
    # fogs_num = args.filename.split("_")
    # file_name = "testcase/"+args.filename
    # fog_set = Fog_Set(constant.ratio, 1250, 1250, 125, 5, int(fogs_num[1]), file_name)
    fog_set = Fog_Set(constant.ratio, 1250, 1250, 125, 5, 10, "testcase/Sfog_10_v" + str(i+1))

    for l in [x * 0.01 for x in range(5, 200, 5)]:
    # for l in [x * 0.1 for x in range(0, 100, 1)]:
        success = True
        # for cost_type in ['fixed', 'diff']:
        for cost_type in ['diff']:
        # for algorithm_type in ['cost', 'traffic', 'CP']:
            # 0/1 knapsack problem with (1 − 1/ sqrt(e)) bound
            traffic = constant.traffic
            latency = l
            bundle_list = []
            empty_list = []
            algorithm = 'CP'
            while traffic > constant.least_error:
                # Edge and all of fog would calculate its own maximum traffic
                if edge.used == False:
                    edge.algorithm(traffic, latency, constant.least_error)
                    bundle_list.append({'id': 'edge', 'traffic': edge.max_traffic, 'cost': edge.edge_cost(), 'CP': edge.max_traffic / edge.edge_cost(), 'chosen': False})

                for f in fog_set.fog_list:
                    if f.used == False:
                        f.algorithm(traffic, latency, constant.least_error, 'diff', algorithm)
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
                        print("change", l)
                        algorithm = 'max'
                        traffic = constant.traffic
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
                
            
            if success:
                if cost_type == 'fixed':
                    # latency_list.append(l)
                    total_cost_fixed.append(edge.edge_cost() + fog_set.fog_set_fixed_cost(10))
                    edge_cost_fixed.append(edge.edge_cost())
                    fog_cost_fixed.append(fog_set.fog_set_fixed_cost(10))
                else:
            #     # data['latency'].append('{:10.2f}'.format(l))
                # latency_list.append('{:10.2f}'.format(l))
                # for i, c in enumerate(collections):
                #     if i == 0:
                #         data[c].append(edge.max_traffic / constant.traffic)
                #     else:
                #         if fog_set.fog_list[i - 1].max_traffic > 0:
                #             data[c].append(fog_set.fog_list[i - 1].max_traffic / constant.traffic)
                #         else:
                #             data[c].append(0)
                # data['latency'].append('{:10.2f}'.format(l))
                # latency_list.append('{:10.2f}'.format(l))
                # for i, c in enumerate(collections):
                #     if i == 0:
                #         data[c].append(edge.active_servers)
                #     else:
                #         data[c].append(fog_set.fog_list[i - 1].used_vehicles)
                    if i == 0:
                        latency_list.append('{:10.2f}'.format(l))
                    total_cost.append(edge.edge_cost() + fog_set.fog_set_cost())
                    edge_cost.append(edge.edge_cost())
                    fog_cost.append(fog_set.fog_set_cost())
            
            # if algorithm_type == 'CP':
            #     latency_list.append(l)
            #     CP_cost.append(edge.edge_cost() + fog_set.fog_set_cost())
            # elif algorithm_type == 'cost':
            #     cost_cost.append(edge.edge_cost() + fog_set.fog_set_cost())
            # else:
            #     traffic_cost.append(edge.edge_cost() + fog_set.fog_set_cost())
            edge.clear()
            fog_set.clear()

    total_cost_list.append(total_cost)
    edge_cost_list.append(edge_cost)
    fog_cost_list.append(fog_cost)

totalCost          = []
edgeCost           = []
fogCost            = []

for index in range(len(total_cost)):
    totalCost.append(sum([ c[index] for c in total_cost_list]) / len(total_cost_list))
    edgeCost.append(sum([ c[index] for c in edge_cost_list]) / len(total_cost_list))
    fogCost.append(sum([ c[index] for c in fog_cost_list]) / len(total_cost_list))

# output to static HTML file
# output_file("graph/S_fog/latency/cost_2000.html")

# p = figure(x_range=latency_list, plot_width=1600, plot_height=900, title="500-traffic edge and fog distribution",
#             tooltips="$name \ @$name")

# p.vbar_stack(collections, x='latency', width=0.9, color=colors, source=data,
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
p = figure(plot_width=600, plot_height=400, x_axis_label='Max latency', y_axis_label='Cost', tooltips=TOOLTIPS)
# p = figure(title="traffic to cost", x_axis_label='traffic', y_axis_label='cost')

# add a line renderer with legend and line thickness
p.line(latency_list, totalCost, legend="Total Cost", line_width=4, line_dash='solid')
p.line(latency_list, edgeCost, legend="Edge Cost", line_width=4, line_color="dodgerblue", line_dash='dotted')
p.line(latency_list, fogCost, legend="Fog Cost", line_width=4, line_color="deepskyblue", line_dash="dashdot")
# p.line(latency_list, total_cost_fixed, legend="total-fixed.", line_width=3, line_color="red")
# p.line(latency_list, edge_cost_fixed, legend="edge-fixed.", line_width=3, line_color="tomato")
# p.line(latency_list, fog_cost_fixed, legend="fog-fixed.", line_width=3, line_color="pink")
# p.line(latency_list, CP_cost, legend="CP.", line_width=3)
# p.line(latency_list, cost_cost, legend="cost.", line_width=3, line_color="#e84d60")
# p.line(latency_list, traffic_cost, legend="traffic.", line_width=3, line_color="lightseagreen")


# p.circle(latency_list, totalCost, size=7)
# p.triangle(latency_list, edgeCost, fill_color="dodgerblue", line_color="dodgerblue", size=7)
# p.square(latency_list, fogCost, fill_color="deepskyblue", line_color="deepskyblue", size=7)
# p.circle(latency_list, total_cost_fixed, fill_color="red", line_color="red", size=7)
# p.circle(latency_list, edge_cost_fixed, fill_color="tomato", line_color="tomato", size=7)
# p.circle(latency_list, fog_cost_fixed, fill_color="pink", line_color="pink", size=7)
# p.circle(latency_list, CP_cost, size=7)
# p.circle(latency_list, cost_cost, fill_color="#e84d60", line_color="#e84d60", size=7)
# p.circle(latency_list, traffic_cost, fill_color="lightseagreen", line_color="lightseagreen", size=7)


p.xaxis.axis_label_text_font_size = "15pt"
p.yaxis.axis_label_text_font_size = "15pt"
p.xaxis.major_label_text_font_size = "12pt"
p.yaxis.major_label_text_font_size = "12pt"
# p.legend.location = "top_left"
# show the results
# show(p)
p.output_backend = "svg"
export_svgs(p, filename="graph/S_fog/latency/cost_1500.svg")


# edge.display()
# fog_set.display()