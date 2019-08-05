from edge.edge import Edge
from fog_set.fog import Fog
from m_m_c.m_m_c import m_m_c_latency

# x: (n_i, hat^n_j)
# args: (cost...)
def objective_func(x, *args):
    edge_num    = args[0]
    fog_num     = args[1]
    cost    = args[2:2+edge_num+fog_num]
    res     = 0
    for i in range(len(cost)):
        res = res + x[i] * args[i]
    return res 

# x: (beta_ij...)
# args: (lambda^in_i)
def edge_traffic(x, args):
    return args - sum([args * x_i for x_i in x])

# x: (n_i)
# args: (mu_i)
def edge_capacity(x, args):
    return x * args

# x: (beta_ij)
# args: (lambda^in_i)
def fog_traffic(x, args):
    return x * args

# x: (hat^n_j)
# args: (mu_V)
def fog_capacity(x, args):
    return x * args

# x: (n_i, beta_ij)
# args: (mu_i, latency, lambda^in_i)
def case_1_latenct(x, args):
    return args[1] - m_m_c_latency(x[0], args[2] - sum([args * x_i for x_i in x[1:]]), args[0])

# x: (hat^n_j, beta_ij)
# args: (mu_V, latency, lambda^in_i)
def case_2_latenct(x, args):
    return args[1] - (m_m_c_latency(x[0], x[1]*args[2], args[0]) + m_m_c_latency(1, x[1]*args[2], 1250) + m_m_c_latency(1,  x[1]*args[2]*0.01, 1250))

# x: (n_i..., hat^n_j..., beta_ij...)
# args: (|E|, |F|, c_i..., hat^c_j...,  lambda^in_i..., mu_i..., mu_V, L^max_i...)
def constraints(x, *args):
    
    edge_num    = args[0]
    fog_num     = args[1]
    traffic     = args[2+edge_num+fog_num:2+2*edge_num+fog_num]
    mu_i        = args[2+2*edge_num+fog_num:2+3*edge_num+fog_num]    
    mu_j        = args[2+3*edge_num+fog_num:2+3*edge_num+fog_num+1]
    latency     = args[2+3*edge_num+fog_num+1:2+4*edge_num+fog_num+1]

    n_i         = x[0:edge_num]
    n_j         = x[edge_num:edge_num+fog_num]
    beta_ij     = x[edge_num+fog_num:]

    constraints = []
    constraint_1 = []
    for e_i in range(edge_num):
        constraint_1.append(edge_capacity(n_i[e_i], mu_i[e_i]) - edge_traffic(beta_ij[e_i*fog_num:(e_i+1)*fog_num], traffic[e_i]))
    constraints.append(constraint_1)

    constraint_2 = []
    for f_i in range(fog_num):
        constraint_2.append(fog_capacity(n_j[f_i], mu_j[0]) - fog_traffic(beta_ij[f_i], traffic[0]))
    constraints.append(constraint_2)

    constraint_3 = []
    for e_i in range(edge_num):
        x_i = []
        x_i.append(n_i[e_i])
        x_i.append(beta_ij[e_i*fog_num:(e_i+1)*fog_num])
        args_i = []
        args_i.append(mu_i[e_i])
        args_i.append(latency[e_i])
        args_i.append(traffic[e_i])
        constraint_3.append(case_1_latenct(x_i, args_i))
    constraints.append(constraint_3)
    
    constraint_4 = []
    for f_i in range(fog_num):
        x_i = []
        x_i.append(n_j[f_i])
        x_i.append(beta_ij[f_i])
        args_i = []
        args_i.append(mu_j[0])
        args_i.append(latency[0])
        args_i.append(traffic[0])
        constraint_4.append(case_1_latenct(x_i, args_i))
    constraints.append(constraint_4)

    return constraints