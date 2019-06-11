from m_m_c.m_m_c import m_m_c_latency
import numpy as np

class Fog:

    def __init__(self, index, capacity, cost, current_vehicles, arrival_rate, departure_rate, edge_transmission_rate, fog_transmission_rate):
        self.available                  = True
        self.used                       = False
        self.edge_table                 = []
        self.vehicle_to_edge            = []
        self.index                      = index
        self.capacity                   = capacity
        self.cost                       = cost
        self.edge_transmission_rate     = edge_transmission_rate
        self.fog_transmission_rate      = fog_transmission_rate
        self.max_vehicles               = current_vehicles + arrival_rate - departure_rate
        self.used_vehicles              = 0
        self.sum_used_vehicles          = 0
        self.traffic                    = 0
    
    def computation_latency(self, traffic, used_vehicles):
        return m_m_c_latency(used_vehicles, traffic, self.capacity)

    def edge_communication_latency(self, traffic):
        return m_m_c_latency(1, traffic, self.edge_transmission_rate)
    
    def fog_communication_latency(self, traffic):
        return m_m_c_latency(1, traffic, self.fog_transmission_rate)
    
    def fog_cost(self):
        return self.used_vehicles * self.cost
    
    def fog_capacity(self):
        return self.used_vehicles * self.capacity
    
    def clear(self):
        if self.available:
            self.max_traffic    = 0
            self.traffic        = 0
            self.used_vehicles  = 0
            self.latency        = 0
            self.used           = False

    def response(self):
        response_list = []
        self.edge_table.sort(key=lambda e : e['cmp_value'], reverse=True)

        for e in self.edge_table:
            if self.max_vehicles - e['used_vehicles'] >= 0:
                self.max_vehicles = self.max_vehicles - e['used_vehicles']
                self.used_vehicles = self.used_vehicles + e['used_vehicles']
                self.traffic = self.traffic + e['traffic']
                self.vehicle_to_edge.append({'edge': e['index'], 'used_vehicles': e['used_vehicles']})
                response_list.append(e['index'])

        self.edge_table.clear()
        return response_list

    def trivial_algorithm(self, traffic, max_latency, least_error):
        vehicles = self.used_vehicles
        self.traffic_algorithm(traffic, max_latency, least_error)
        self.max_vehicles = self.max_vehicles - self.used_vehicles
        self.used_vehicles = self.used_vehicles + vehicles
        return self.max_traffic

    # offloading computation from edge to fog
    def traffic_algorithm(self, traffic, max_latency, least_error):
        
        # start from maximum vehicles
        used_vehicles = self.max_vehicles

        # find maximum traffic
        # check arrival traffic is larger than the traffic that can be handle in this fog
        if self.computation_latency(traffic, used_vehicles) > max_latency:

            # bisection method variation
            self.max_traffic = self.bisection_method(traffic, used_vehicles, max_latency, least_error)

        else:
            self.max_traffic = traffic

        # find minmum number of used vehicles to handle the traffic
        # linear search
        while self.computation_latency(self.max_traffic, used_vehicles) <= max_latency:
            used_vehicles = used_vehicles - 1 
        
        self.used_vehicles = used_vehicles + 1
        self.latency = self.computation_latency(self.max_traffic, self.used_vehicles)

    def bisection_method(self, traffic, used_vehicles, max_latency, least_error):
        lower   = 0
        upper   = traffic
        flag    = False

        while (lower + least_error) <= upper:
            mid = (lower + upper) / 2
            total_latency = self.edge_communication_latency(mid) + self.computation_latency(mid, used_vehicles) + self.fog_communication_latency(mid)

            if total_latency <= max_latency:
                flag    = True
                lower   = mid
            else:
                upper   = mid

        if flag:
            return lower
        else:
            return -1