

def get_city_constraint_for_a_given_city(start_city, day=0):
    def satisfy_start_in_specific_city(model):
        return model.positions[start_city, day] == 1
    return satisfy_start_in_specific_city


def satisfy_being_in_one_place(model, date):
    return sum(model.positions[city, date] for city in model.cities) == 1


def total_profit(model):
    revenue = sum(
        model.positions[city, date - 1] * model.positions[city, date] * model.profits[city, date] for city in model.cities
        for date in model.dates if date != 0
    )

    cost = sum(
        model.positions[city_A, date - 1] * model.positions[city_B, date] * model.transportation_costs[city_A, city_B]
        for city_A in model.cities for city_B in model.cities
        for date in model.dates if date != 0
    )
    return revenue - cost
