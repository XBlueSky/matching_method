from fog_set.vehicle import Vehicle
from m_m_c.m_m_c import m_m_c_latency

class Vehicle_Set:
    vehicle_set     = []
    total_vehicles  = 0
    def __init__(self, capacity, edge_transmission_rate, vehicle_transmission_rate):
        self.vehicle_set                = []
        self.total_vehicles             = 0
        self.capacity                   = capacity
        self.edge_transmission_rate     = edge_transmission_rate
        self.vehicle_transmission_rate  = vehicle_transmission_rate
    
    def append_vehicle(self, vehicle_num, cost_set = [], consumption_rate_set = [], initial_power_set = [], threshold_power_set = []):
        for i in range(vehicle_num):
            self.vehicle_set.append( Vehicle( self.total_vehicles, cost_set[i], consumption_rate_set[i], initial_power_set[i], threshold_power_set[i]))
            self.total_vehicles = self.total_vehicles + 1

    def computation_latency(self, traffic, used_vehicles):
        return m_m_c_latency(used_vehicles, traffic, self.capacity)

    def edge_communication_latency(self, traffic):
        return m_m_c_latency(1, traffic, self.edge_transmission_rate)
    
    def vehicle_communication_latency(self, traffic):
        return m_m_c_latency(1, traffic, self.vehicle_transmission_rate)

    def total_vehicle_cost(self):
        return sum([v.used_bit * v.cost for v in self.vehicle_set])

    def total_vehicle_fixed_cost(self, cost):
        return sum([v.used_bit * cost for v in self.vehicle_set])

    def clear(self):
        self.max_traffic    = 0
        self.used_vehicles  = 0
        self.latency        = 0
        self.used           = False
        for f in self.vehicle_set:
            f.used_bit = False

    # offloading computation from edge to fog
    def algorithm(self, traffic, max_latency, least_error):

        for v in self.vehicle_set:
            if v.usage_time > max_latency:
                v.max_traffic = self.bisection_method(traffic, 1, max_latency, least_error)
            else:
                v.max_traffic = self.bisection_method(traffic, 1, v.usage_time, least_error)
        
    def bisection_method(self, traffic, used_vehicles, max_latency, least_error):
        lower   = 0
        upper   = traffic
        flag    = False

        while (lower + least_error) <= upper:
            mid = (lower + upper) / 2
            total_latency = self.edge_communication_latency(mid) + self.computation_latency(mid, used_vehicles) + self.vehicle_communication_latency(mid)

            if total_latency <= max_latency:
                flag    = True
                lower   = mid
            else:
                upper   = mid

        if flag:
            return lower
        else:
            return 0