# Travelling Salesman 

This is an attempt to help my friend with a real world application of band tour planning. 
Let's say that you have bunch of festivals or other events across Europe at which you can play with your band.

Some of them are more profitable than others, but may be in a far away city. And also you cannot play at a concert and travel to another city on the same day!

How do you plan your tour to maximize your profit?


So it is basically a more interesting version of the travelling salesman problem, except the profit varies based on when you play in a given city.
Also it could easily be implemented that the plane ticket price varies over time, although at the moment I am taking 
constant values with respect to time.

This is basically a quadratic integer programming problem. I have implemented the formulation using `pyomo` 
with `scip` as the solver. 

I know nothing about festivals and how much money bands can make, so I have written the `sample_data_generator.py` to give myself something to work with.