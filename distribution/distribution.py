import random

class Distribution:
    @staticmethod
    def uniform(totoal_vehicles, fog_num):
        vehicles_set = [1] * fog_num
        fog_choice = list(range(fog_num))
        totoal_vehicles = totoal_vehicles - fog_num
        for i in range(totoal_vehicles):
            cur_choice = random.choice(fog_choice)
            vehicles_set[cur_choice] = vehicles_set[cur_choice] + 1
        return vehicles_set

    @staticmethod
    def exponential(totoal_vehicles, fog_num):
        vehicles_set = [1] * fog_num
        fog_choice = list(range(fog_num))
        totoal_vehicles = totoal_vehicles - fog_num
        for i in range(totoal_vehicles):
            cur_choice = random.choice(fog_choice)
            fog_choice.append(cur_choice)
            vehicles_set[cur_choice] = vehicles_set[cur_choice] + 1
        return vehicles_set