from pprint import pprint
from datetime import date
import pandas as pd
import pyomo.environ as pyo
from pyomo.environ import ConcreteModel, Set, Param, Var, Objective, maximize, value, Constraint, Expression

from formulas import get_city_constraint_for_a_given_city, satisfy_being_in_one_place, total_profit
from sample_data_generator import cities
from utils import get_date_index

date_zero = date(2023, month=12, day=31)


def main():
    #dates = range(0, 32)
    dates = range(0, 32)

    # Creation of a Concrete Model
    model = ConcreteModel()

    concerts_df = pd.read_csv("sample_data.csv")
    profits_data = {(row["city"], get_date_index(row["date"], date_zero)): row["profit"] for _, row in concerts_df.iterrows()}
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

    model.positions = Var(model.cities, model.dates, initialize=0, bounds=(0, 1), doc="Positions",
                              domain=pyo.Binary)

    model.one_place = Constraint(model.dates, rule=satisfy_being_in_one_place)
    model.specific_start = Constraint(rule=get_city_constraint_for_a_given_city("London"))
    model.specific_end = Constraint(rule=get_city_constraint_for_a_given_city("London", day=len(dates) - 1))

    model.objective = Objective(rule=total_profit, sense=maximize)


    def pyomo_postprocess(options=None, instance=None, results=None):
        return model.positions

    from pyomo.opt import SolverFactory

    opt = SolverFactory("scip")

    opt.options['acceptable_tol'] = 1e-8

    results = opt.solve(model)
    results.write()
    print("\nDisplaying Solution\n" + '-' * 60)
    positions = pyomo_postprocess(None, model, results)

    pprint(sorted({key: value(val) for key, val in dict(positions).items() if value(val) > 0.8}, key=lambda x: x[1]))


if __name__ == "__main__":
    main()