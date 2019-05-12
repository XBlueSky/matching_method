import math

def m_m_c_latency(c, arrival, service):
    
    # check constraint
    if arrival < (c * service):
        utilization = arrival / (c * service)
        Erlang_value = 1 / (1 + (1 - utilization) * (math.factorial(c) / (c * utilization) ** c) * sum([(c * utilization) ** k / math.factorial(k) for k in range(c)]))
        return Erlang_value / (c * service - arrival) + 1 / service
    
    else:
        return math.inf