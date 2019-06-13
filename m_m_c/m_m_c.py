import math
import decimal

decimal.getcontext().prec = 2
def m_m_c_latency(c, arrival, service):
    
    # check constraint
    if arrival < (c * service) and arrival > 0:
        utilization = arrival / (c * service)
        # Erlang_value = decimal.Decimal(1) / (decimal.Decimal(1) + (decimal.Decimal(1) - decimal.Decimal(utilization)) * (math.factorial(decimal.Decimal(c)) / (decimal.Decimal(c) * decimal.Decimal(utilization)) ** decimal.Decimal(c)) * sum([(decimal.Decimal(c) * decimal.Decimal(utilization)) ** decimal.Decimal(k) / math.factorial(decimal.Decimal(k)) for k in range(c)]))
        # return float(Erlang_value / (decimal.Decimal(c) * decimal.Decimal(service) - decimal.Decimal(arrival)) + decimal.Decimal(1) / decimal.Decimal(service))
    
        Erlang_value = 1 / (1 + (1 - utilization) * (math.factorial(c) / (c * utilization) ** c) * sum([(c * utilization) ** k / math.factorial(k) for k in range(c)]))
        return Erlang_value / (c * service - arrival) + 1 / service
    
    else:
        return math.inf