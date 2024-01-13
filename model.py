from pprint import pprint

import numpy as np
import pandas as pd
import pyomo.environ as pyo
from pyomo.environ import ConcreteModel, Set, Param, Var, Objective, maximize, value, Constraint, Expression

from sample_data_generator import cities

dates = [f"{x}-01-2024" for x in range(1, 32)]
# Creation of a Concrete Model
model = ConcreteModel()

concerts_df = pd.read_csv("sample_data.csv")
profits_data = {(row["city"], row["date"]): row["profit"] for _, row in concerts_df.iterrows()}
for city in cities:
    for date in dates:
        if (city, date) not in profits_data:
            profits_data[(city, date)] = 0

transportation_costs_df = pd.read_csv("transportation_costs.csv").set_index('Unnamed: 0')
costs = {}
for index, row in transportation_costs_df.iterrows():
    for column_name, cell_value in row.items():
        if pd.isna(cell_value):
            continue
        costs[(column_name, index)] = cell_value
        costs[(index, column_name)] = cell_value

model.cities = Set(initialize=cities.keys(), doc="Cities")
model.dates = Set(initialize=dates, doc="Dates")

model.profits = Param(model.cities, model.dates, initialize=profits_data, doc="Profits")
model.transportation_costs = Param(model.cities, model.cities, initialize=costs, doc="Transportation")
# Assuming start in the first city, in the case London
# model.initial_position_vector = Param(model.cities, initialize=np.array([1] + [0] * (len(model.cities)-1)))

# Variables

model.concerts_played = Var(model.cities, model.dates, initialize=0, bounds=(0, 1), doc="Attended concerts",
                            domain=pyo.Binary)
model.flights_taken = Var(model.cities, model.cities, model.dates, initialize=0, bounds=(0, 1), doc="Flights taken",
                          domain=pyo.Binary)


def init_constraint_rule(model, city_A, city_B, date):
    if city_A == city_B == "London":
        value = 1
    else:
        value = 0
    return model.flights_taken[city_A, city_B, date] == value


# model.init_constraint = Constraint(model.cities, model.cities, model.dates, rule=init_constraint_rule)

# TODO cannot have more than x concerts in a single country

def satisfy_non_multitasking(model, day):
    return (
                   sum(model.concerts_played[city, day] for city in model.cities) +
                   sum(model.flights_taken[city_A, city_B, day] for city_A in model.cities for city_B in model.cities)
           ) <= 1


def satisfy_non_teleportation(model):
    current_position_vector = {city: 1 if city == "London" else 0 for city in model.cities}
    total_teleportations_list = []
    for date in model.dates:
        total_teleportations_list.append(
            sum(
                (1 - current_position_vector[city]) * model.concerts_played[city, date] for city in
                model.cities
            )
        )
        # the following teleports are basically the same as flying from another airport
        # it would lead to living in two cities at the same time, then switching back and forth without having to fly.
        # FIXME however, at this point this is causing non-linearity. I need to think about this.
        total_teleportations_list.append(
            sum(
                (
                    (1 - current_position_vector[city_A]) * model.flights_taken[city_A, city_B, date]
                    for city_B in model.cities
                    for city_A in model.cities
                )
            )
        )
        for city_A in model.cities:
            # current_position_vector[city_A] = Expression(
            #    expr=current_position_vector[city_A] + sum(
            #        (model.flights_taken[city_B, city_A, date] - model.flights_taken[city_A, city_B, date]) for city_B
            #        in model.cities
            #    )
            # )
            current_position_vector[city_A] = current_position_vector[city_A] + sum(
                (model.flights_taken[city_B, city_A, date] - model.flights_taken[city_A, city_B, date]) for city_B
                in model.cities
            )

    return sum(total_teleportations_list) == 0


def total_profit(model):
    revenue = sum(
        model.concerts_played[city, date] * model.profits[city, date] for city in model.cities for date in model.dates)
    cost = sum(
        model.flights_taken[city_A, city_B, date] * model.transportation_costs[city_A, city_B]
        for city_A in model.cities for city_B in model.cities for date in model.dates
    )
    return revenue - cost


# model.init_constraint = Constraint(model.cities, model.cities, model.dates, rule=init_constraint_rule)
# model.non_teleportation = Constraint(model.cities, model.cities, model.dates, rule=satisfy_non_teleportation_test, doc='Non-teleportation')
model.non_teleportation = Constraint(rule=satisfy_non_teleportation, doc='Non-teleportation')
model.discreteness = Constraint(model.dates, rule=satisfy_non_multitasking)
model.objective = Objective(rule=total_profit, sense=maximize)


def pyomo_postprocess(options=None, instance=None, results=None):
    model.concerts_played.display()
    return model.concerts_played, model.flights_taken


from pyomo.opt import SolverFactory
import pyomo.environ

#model.non_teleportation.pprint()
solver_name = "ipopt"
opt = SolverFactory(f"{solver_name}", executable=rf'C:\{solver_name}\bin\{solver_name}.exe')
opt.options['acceptable_tol'] = 1e-8

results = opt.solve(model)
results.write()
print("\nDisplaying Solution\n" + '-' * 60)
x, y = pyomo_postprocess(None, model, results)

pprint(({key: value(val) for key, val in dict(x).items() if value(val) > 0.8}, {key: value(val) for key, val in dict(y).items() if value(val) > 0.8}))
