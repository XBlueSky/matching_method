import random
from argparse import ArgumentParser

# do argument parser
parser = ArgumentParser()
parser.add_argument("edge_num", help="Input number of edges")
parser.add_argument("fog_num", help="Input number of fogs")
# parser.add_argument("cost", help="Input fixed cost number or diff")
args = parser.parse_args()

for i in range(1):
    with open("../testcase/edge_" + args.edge_num + "_v" + str(i+1), 'w') as fp:

        for i in range(int(args.edge_num)):

            vehicle_num = random.randint(1, 100)

            # cost
            if args.cost == "diff":
                for v in range(vehicle_num):
                    # if i == 9:
                    #     diff_cost = random.randint(5, 50)
                    # elif i % 3 == 0:
                    #     diff_cost = random.randint(1, 10)
                    # elif i % 3 == 1:
                    #     diff_cost = random.randint(20, 30)
                    # elif i % 3 == 2:
                    #     diff_cost = random.randint(40, 50)
                    diff_cost = random.randint(1, 50)
                        
                    fp.write(str(diff_cost) + " ")
            else:
                for v in range(vehicle_num):
                    fp.write(args.cost + " ")
            fp.write("\n")

            # consumptoin rate
            for v in range(vehicle_num):
                consumption_rate = random.randint(1, 9)
                # consumption_rate = 5
                fp.write(str(consumption_rate) + " ")
            fp.write("\n")

            # power constraint
            initial_power       = []
            threshold_power     = []
            for v in range(vehicle_num):
                # if i == 9:
                #     initial = random.randint(30, 100)
                #     threshold = random.randint(10, 50)
                # elif i % 3 == 0:
                #     initial = random.randint(30, 40)
                #     threshold = random.randint(30, 35)
                # elif i % 3 == 1:
                #     initial = random.randint(50, 70)
                #     threshold = random.randint(30, 35)
                # elif i % 3 == 2:
                #     initial = random.randint(80, 100)
                #     threshold = random.randint(30, 35)
                if i == 9:
                    initial = random.randint(30, 40)
                    threshold = random.randint(30, 35)
                else:
                    initial = random.randint(30, 100)
                    threshold = random.randint(10, 50)
                if initial < threshold:
                    initial_power.append(threshold)
                    threshold_power.append(initial)
                elif initial > threshold:
                    initial_power.append(initial)
                    threshold_power.append(threshold)
                else:
                    initial_power.append(initial+1)
                    threshold_power.append(threshold)
            for v in range(vehicle_num):
                fp.write(str(initial_power[v]) + " ")
            fp.write("\n")
            for v in range(vehicle_num):
                fp.write(str(threshold_power[v]) + " ")
            fp.write("\n")