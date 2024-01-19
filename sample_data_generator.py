from random import randint

import numpy as np
import pandas as pd

cities = {
    "London": "United Kingdom",
    "Manchester": "United Kingdom",
    "Birmingham": "United Kingdom",
    "Copenhagen": "Denmark",
    "Berlin": "Germany",
    "Munich": "Germany",
    "Prague": "Czech Republic",
    "Warsaw": "Poland",
    "Wroclaw": "Poland",
    "Budapest": "Hungary",
    "Bucharest": "Romania",
}

def get_random_profit():
    profit = (
            100 * randint(5,15) +
            100 * randint(5,20) * np.random.binomial(n=1, p=0.2)
    )
    return profit

data_rows = []
for city, country in cities.items():
    for day in range(1,32):
        if np.random.uniform() > 0.5:
            data_rows.append((f"{day}-01-2024", city, get_random_profit(), country))


dataframe = pd.DataFrame(
    data_rows,
    columns=["date", "city", "profit", "country"]
)

dataframe.to_csv("sample_data.csv")