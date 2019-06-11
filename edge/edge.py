from m_m_c.m_m_c import m_m_c_latency
from fog_set.fog import Fog
import prettytable as pt
import copy
import math

class Edge:

    def __init__(self, index, traffic, ratio, max_latency, capacity, max_servers, cost, least_error):
        self.available          = True
        self.used               = False
        self.fog_list           = []
        self.preference_list    = []
        self.index              = index
        self.traffic            = traffic
        self.total_traffic      = traffic
        self.ratio              = ratio
        self.max_latency        = max_latency
        self.least_error        = least_error
        self.capacity           = capacity
        self.max_servers        = max_servers
        self.cost               = cost
        self.active_servers     = 0
        self.max_traffic        = 0
        self.fog_traffic        = 0
    
    # def append_fog_list(self, fog = Fog):
    #     self.fog_list.append(copy.deepcopy(fog))
    #     self.preference_list.append({'index': fog.index, 'vehicles': fog.max_vehicles})

    def append_fog_list(self, index, capacity, cost, current_vehicles, arrival_rate, departure_rate, edge_transmission_rate, fog_transmission_rate):
        self.fog_list.append( Fog(index, capacity, cost, current_vehicles, arrival_rate, departure_rate, edge_transmission_rate, fog_transmission_rate))
        # self.preference_list.append({'index': index, 'vehicles': current_vehicles + arrival_rate - departure_rate})

    def set_traffic(self, traffic):
        self.total_traffic      = traffic

    def computation_latency(self, traffic, active_servers):
        # check number of servers constraint
        if active_servers <= self.max_servers:
            return m_m_c_latency(active_servers, traffic, self.capacity)
        else:
            return -1

    def edge_cost(self):
        return self.active_servers * self.cost
    
    def edge_capacity(self):
        return self.active_servers * self.capacity

    def fog_set_cost(self):
        return sum([f.fog_cost() for f in self.fog_list])

    def clear(self):
        if self.available:
            self.active_servers     = 0
            self.max_traffic        = 0
            self.latency            = 0
            self.used               = False
        
    def clearAll(self):
        self.clear()
        for f in self.fog_list:
            f.clear()

    def propose(self):

        # Preference by marginal value
        cmp_value = self.marginal_value()

        # There is no fog which this edge wants to contend
        if cmp_value < 0:
            return None

        else:
            return {'e_id': self.index, 'f_id': self.preference_list[0]['index'], 'used_vehicles': self.preference_list[0]['used_vehicles'], 'cmp_value': cmp_value, 'traffic': self.fog_traffic}

    def confirm(self):
        self.greedy_algortithm(self.traffic, self.max_latency, self.least_error, -1)
        self.fog_list[self.preference_list[0]['index']].available = False
        self.traffic = self.traffic - self.fog_list[self.preference_list[0]['index']].max_traffic
        if self.traffic > self.least_error:
            self.clearAll()
        self.preference_list.clear()
        

    def rebuild_preference(self):
        # Preference for maximum vehicles in fog
        # for f in self.fog_list:
        #     for p in self.preference_list:
        #         if f.index == p['index']:
        #             p['vehicles'] = f.max_vehicles
        # self.preference_list.sort(key=lambda p : p['vehicles'], reverse=True)

        # Preference for maximum used vehicles after greedy algortithm
        for f in self.fog_list:
            if f.available and f.used:
                self.preference_list.append({'index': f.index, 'used_vehicles': f.used_vehicles})
        self.preference_list.sort(key=lambda p : p['used_vehicles'], reverse=True)

    def marginal_value(self):
        # optmized cost in edge and fogs
        self.greedy_algortithm(self.traffic, self.max_latency, self.least_error, -1)
        all_cost = self.edge_cost() + self.fog_set_cost()

        self.rebuild_preference()
        # There is no fog which this edge wants to contend
        if not self.preference_list:
            self.available = False
            return -1
        self.fog_traffic = self.fog_list[self.preference_list[0]['index']].max_traffic
        self.clearAll()

        # optmized cost in edge and fogs w/o exception fog
        self.greedy_algortithm(self.traffic, self.max_latency, self.least_error, self.preference_list[0]['index'])
        exception_cost = self.edge_cost() + self.fog_set_cost()
        self.clearAll()

        return exception_cost - all_cost if exception_cost - all_cost > 0 else 0

    def greedy_algortithm(self, traffic, max_latency, least_error, exception_id):
        bundle_list     = []
        empty_list      = []

        while traffic > least_error:
            # Edge and all of fog would calculate its own maximum traffic
            if self.available and self.used == False:
                self.traffic_algorithm(traffic, max_latency, least_error)
                bundle_list.append({'id': 'edge', 'traffic': self.max_traffic, 'cost': self.edge_cost(), 'CP': self.max_traffic / self.edge_cost(), 'chosen': False})

            for f in self.fog_list:
                if f.available and f.used == False and f.index != exception_id:
                    f.traffic_algorithm(traffic, max_latency, least_error)
                    if f.max_traffic > 0:
                        bundle_list.append({'id': f.index, 'traffic': f.max_traffic, 'cost': f.fog_cost(), 'CP': f.max_traffic / f.fog_cost(), 'chosen': False})
                    else:
                        empty_list.append({'id': f.index, 'traffic': 0, 'cost': 0, 'CP': 0, 'chosen': False})

            # Sort by CP value
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
                        self.used = True
                    else:
                        self.fog_list[bundle['id']].used = True
                else:
                    if bundle['id'] == 'edge':
                        self.clear()
                    else:
                        self.fog_list[bundle['id']].clear()
            
            for empty in empty_list:
                self.fog_list[empty['id']].clear()

            empty_list.clear()
            bundle_list.clear()

    def trivial_algorithm(self):
        self.traffic_algorithm(self.traffic, self.max_latency, self.least_error)
        if self.max_traffic > 0:
            self.used = True
        self.traffic = self.traffic - self.max_traffic
        return self.traffic

    # local computation in edge
    def traffic_algorithm(self, traffic, max_latency, least_error):
        
        # start from maximum servers
        active_servers = self.max_servers

        # find maximum traffic
        # check arrival traffic is larger than the traffic that can be handle in edge
        if self.computation_latency(traffic, active_servers) > max_latency:

            # bisection method variation
            self.max_traffic = self.bisection_method(traffic, active_servers, max_latency, least_error)

        else:
            self.max_traffic = traffic

        # find minmum number of active servers to handle the traffic
        # linear search
        while self.computation_latency(self.max_traffic, active_servers) <= max_latency:
            active_servers = active_servers - 1 
        
        self.active_servers = active_servers + 1
        self.latency = self.computation_latency(self.max_traffic, self.active_servers)

    def bisection_method(self, traffic, active_servers, max_latency, least_error):
        lower   = 1
        upper   = traffic
        flag    = False

        while (lower + least_error) <= upper:
            mid = (lower + upper) / 2
            total_latency = self.computation_latency(mid, active_servers)

            if total_latency <= max_latency:
                flag    = True
                lower   = mid
            else:
                upper   = mid

        if flag:
            return lower
        else:
            return -1


    def display(self):
        edge_table = pt.PrettyTable()
        edge_table.field_names = ["Traffic", "Offloading Probability", "Active servers number", "Cost", "Latency"]
        edge_table.add_row([self.max_traffic, self.max_traffic / self.total_traffic, self.active_servers, self.edge_cost(), self.latency])
        edge_data = edge_table.get_string()

        fog_table = pt.PrettyTable()
        fog_table.add_column("Index", ["Traffic", "Probability", "Used vehicles", "Cost", "Latency"])
        for f in self.fog_list:
            fog_table.add_column (str(f.index), [f.max_traffic, f.max_traffic / self.total_traffic, f.used_vehicles, f.fog_cost(), f.latency])
        fog_data = fog_table.get_string()

        with open('graph/table/Edge' + str(self.index) + '.txt', 'w') as f:
            f.write("Edge"+ str(self.index) + "\n")
            f.write(edge_data)
            f.write("\nVehicular-Fog\n")
            f.write(fog_data)

        # self.fog_list.sort(key=lambda f : f.index)

        # # print("Fog")
        # # print(table)
        # used_bits_table = pt.PrettyTable()
        # used_bits_table.add_column("Vehicles / Fog", [str(i) for i in range(self.max_vehicles)])
        # for index, f in enumerate(self.used_bits_table()):
        #     f = [int(i) for i in f]
        #     f.extend(["N/A"] * (self.max_vehicles - len(f)))
        #     used_bits_table.add_column(str(index), f)
        # # print(used_bits_table)

        # data = table.get_string()
        # vData = used_bits_table.get_string()
        # with open('graph/table/' + str(self.total_traffic) + '.txt', "a") as f:
        #     f.write(data)
        #     f.write(vData)