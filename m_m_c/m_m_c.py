import math
import decimal

# decimal.getcontext().prec = 2

def simplify_factorial(k, c, utilization):
    if k > 80:
        res = math.factorial(80) / (c * utilization) ** 80
        for i in range(80, k):
            res = res * ((i + 1) / (c * utilization))
        return res
    else:
        return math.factorial(k) / (c * utilization) ** k

def m_m_c_latency_formula(c, arrival, service):
    
    # check constraint
    if arrival < (c * service) and arrival > 0:
        utilization = arrival / (c * service)
        # Erlang_value = decimal.Decimal(1) / (decimal.Decimal(1) + (decimal.Decimal(1) - decimal.Decimal(utilization)) * (math.factorial(decimal.Decimal(c)) / (decimal.Decimal(c) * decimal.Decimal(utilization)) ** decimal.Decimal(c)) * sum([(decimal.Decimal(c) * decimal.Decimal(utilization)) ** decimal.Decimal(k) / math.factorial(decimal.Decimal(k)) for k in range(c)]))
        # return float(Erlang_value / (decimal.Decimal(c) * decimal.Decimal(service) - decimal.Decimal(arrival)) + decimal.Decimal(1) / decimal.Decimal(service))
    
        Erlang_value = 1 / (1 + (1 - utilization) * (math.factorial(c) / (c * utilization) ** c) * sum([(c * utilization) ** k / math.factorial(k) for k in range(c)]))
        return Erlang_value / (c * service - arrival) + 1 / service
    
    else:
        return math.inf

def m_m_c_latency(c, arrival, service):
    
    # check constraint
    if arrival < (c * service) and arrival > 0:
        utilization = arrival / (c * service)

        Erlang_value = 1 / (1 + (1 - utilization) * simplify_factorial(c, c, utilization) * sum([1 / simplify_factorial(k, c, utilization) for k in range(c)]))
        return Erlang_value / (c * service - arrival) + 1 / service
    
    else:
        return math.inf

# print(m_m_c_latency_formula(200, 5, 1))