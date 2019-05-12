from argparse import ArgumentParser
from m_m_c.m_m_c import m_m_c_latency

parser = ArgumentParser(description= "Bisection Method")
parser.add_argument("traffic", help="How much traffic")
parser.add_argument("max_latency")
parser.add_argument("active_number")
parser.add_argument("capacity")
args = parser.parse_args()

def bisection_method(traffic, max_latency, active_servers, capacity, least_error):
    lower   = 1
    upper   = traffic
    flag    = False

    while (lower + least_error) <= upper:
        mid = (lower + upper) / 2
        total_latency = m_m_c_latency(active_servers, mid, capacity)

        if total_latency <= max_latency:
            flag    = True
            lower   = mid
        else:
            upper   = mid

    if flag:
        return lower
    else:
        return -1

print(bisection_method(int(args.traffic), int(args.max_latency), int(args.active_number), int(args.capacity), 0.01))