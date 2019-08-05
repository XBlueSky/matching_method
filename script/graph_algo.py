from bokeh.plotting import figure, output_file, show, ColumnDataSource
from bokeh.core.properties import value
from bokeh.io import export_svgs
import random
import csv

xaxis_list = []
total_list = []
total_list_2 = []
total_list_3 = []
with open('graph/final/algo/0-200_normal_S_cost.csv', newline='') as csvfile:

    # space for delimiter
    rows = csv.reader(csvfile, delimiter=' ')

    for row in rows:
        xaxis_list.append(row[0])
        total_list.append(row[1])
        total_list_2.append(row[2])
        total_list_3.append(row[3])

# print(xaxis_list, total_list, total_list_2, total_list_3)
# Graphic Design in Bokeh

# create a new plot with a title and axis labels

TOOLTIPS = [
        ("index", "$index"),
        ("traffic", "$x"),
        ("cost", "$y"),
    ]

p = figure(plot_width=600, plot_height=400, x_axis_label='Araival Traffic Mean (mb/s)', y_axis_label='Total Cost ($)', x_range=(-5, 205), y_range=(-20, 1020), tooltips=TOOLTIPS)

# Default
p.line(xaxis_list, total_list, legend="multi-EVF matching", line_width=2, line_color="red")
p.line(xaxis_list, total_list_2, legend="PSO(maxiter: 500)", line_width=1, line_color="tomato")
p.line(xaxis_list, total_list_3, legend="PSO(maxiter: 50)", line_width=1, line_color="orange")

p.circle(xaxis_list, total_list, legend="multi-EVF matching", fill_color="red", line_color="red", size=7)
p.x(xaxis_list, total_list_2, legend="PSO(maxiter: 500)", line_color="tomato", size=5)
p.circle(xaxis_list, total_list_3, legend="PSO(maxiter: 50)", fill_color="white", line_color="orange", size=5)

p.xaxis.axis_label_text_font_size = "15pt"
p.yaxis.axis_label_text_font_size = "15pt"
p.xaxis.major_label_text_font_size = "12pt"
p.yaxis.major_label_text_font_size = "12pt"
p.legend.location = "top_left"

p.output_backend = "svg"
export_svgs(p, filename="graph/final/algo/pso/0-200_normal_S_cost.svg")

with open('graph/final/algo/pso/csv/0-200_normal_S_cost.csv', 'w', newline='') as csvfile:

    # space for delimiter
    writer = csv.writer(csvfile, delimiter=' ')

    # writer.writerow(['Traffic', 'Total cost by Matching', 'Edge cost by Matching', 'Fog cost by Matching', 'Total cost by Trivial', 'Edge cost by Trivial', 'Fog cost by Trivial'])
    writer.writerow(['Traffic', 'multi-EVF matching', 'PSO(maxiter: 500)', 'PSO(maxiter: 50)'])
    
    for i in range(len(xaxis_list)):
        # writer.writerow([xaxis_list[i], total_list[i], total_edge_list[i], total_fog_list[i], total_list_2[i], total_edge_list_2[i], total_fog_list_2[i]])
        writer.writerow([xaxis_list[i], total_list[i], total_list_2[i], total_list_3[i]])