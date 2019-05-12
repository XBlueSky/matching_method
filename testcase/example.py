###################################################################
# Input File example                                              #
###################################################################
# 1250  (10 Gbps)  Transmission rate of edge (MB/s)               #
# 1250  (10 Gbps)  Transmission rate of fog node (MB/s)           #
# 1                least error                                    #
############################    Edge   ############################
# 2                Number of edges                                #
# 300 500          Traffic inputs (MB/s)                          #
# 0.01 0.01        Ratio of the Input traffic and output traffic  #
# 1 1              Maximum latency (s)                            #
# 15 20            Capacity of single server (MB/s)               #
# 15 20            Unit cost of single server in edge             #
# 15 10            Maximum servers in edge                        #
############################    Fog    ############################
# 3                Number of fogs                                 #
# 5  5  5          Capacity of each vehicle (MB/s)                #
# 10 10 10         Unit cost of vehicle                           #
# 10 20 20         Current vehicles in fog                        #
# 5  10 5          Vehicles arrival rate in fog                   #
# 1  5  10         Vehicles departure rate in fog                 #
###################################################################