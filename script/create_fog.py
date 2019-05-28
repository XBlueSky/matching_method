import random
from argparse import ArgumentParser

# do argument parser
parser = ArgumentParser()
parser.add_argument("edge_num", help="Input number of edges")
parser.add_argument("fog_num", help="Input number of fogs")
# parser.add_argument("cost", help="Input fixed cost number or diff")
args = parser.parse_args()

edge_para = ["traffic", "ratio", "latency", "capacity/cost", "server_num"]
fog_para = ["capacity/cost", "current_num", "arrival", "departure"]

for version in range(1):
    with open("../testcase/edge_" + args.edge_num + "_v" + str(version + 1), 'w') as fp:

        capacity_list = []
        for para in edge_para:
            if para == "traffic":
                for i in range(int(args.edge_num)):
                    traffic = random.randrange(100,500,100)
                    fp.write(str(traffic) + " ")
            
            if para == "ratio":
                for i in range(int(args.edge_num)):
                    ratio = 0.01
                    fp.write(str(ratio) + " ")

            elif para == "latency":
                for i in range(int(args.edge_num)):
                    latency = 1
                    fp.write(str(latency) + " ")

            elif para == "capacity/cost":
                for i in range(int(args.edge_num)):
                    # capacity = 100
                    capacity = random.randrange(100,200,10)
                    capacity_list.append(capacity)
                    fp.write(str(capacity) + " ")
                fp.write("\n")
                for i in range(int(args.edge_num)):
                    cost = capacity_list[i]
                    fp.write(str(cost) + " ")

            elif para == "server_num":
                for i in range(int(args.edge_num)):
                    # server_num = random.randint(1, 10)
                    server_num = 1
                    fp.write(str(server_num) + " ")
            
            fp.write("\n")


    with open("../testcase/fog_" + args.fog_num + "_v" + str(version + 1), 'w') as fp:
        capacity_list = []
        for para in fog_para:

            if para == "capacity/cost":
                for i in range(int(args.fog_num)):
                    capacity = 5
                    capacity_list.append(capacity)
                    fp.write(str(capacity) + " ")
                fp.write("\n")
                for i in range(int(args.fog_num)):
                    cost = capacity_list[i] * 2
                    fp.write(str(cost) + " ")

            elif para == "current_num":
                for i in range(int(args.fog_num)):
                    server_num = random.randint(20, 100)
                    fp.write(str(server_num) + " ")

            elif para == "arrival":
                for i in range(int(args.fog_num)):
                    server_num = random.randint(0, 20)
                    fp.write(str(server_num) + " ")

            elif para == "departure":
                for i in range(int(args.fog_num)):
                    server_num = random.randint(0, 20)
                    fp.write(str(server_num) + " ")
            
            fp.write("\n")