from pulp import *
import numpy as np

def route_fleet(fixed_parameters, variable_parameters, haulers):
	"""An Integer Program for determining if a given sized fleet of equipment
	haulers can feasibly meet the demand for drop-offs and pick-ups in a
	given day

	Parameters
	----------
	fixed_parameters : dict
	    Parameters that are constant for any variation and region (as defined
	    in the main function)

	variable_parameters : dict
		The parameters that vary by day but are still needed for our model
		to run

	haulers : list
		A list of indices for all available equipment haulers in the fleet

	Returns
	-------
	results : dict
		Returns whether or not the IP solved to optimality, the total number
		of miles run by the fleet, and the number of times each hauler ran
		each route available to be travelled this day.

	"""

	# instantiate parameters for equipment hauler routing problem
	rate = fixed_parameters['travel_rate']
	L = fixed_parameters['day_length']
	handle = fixed_parameters['handle']

	route_constraints = variable_parameters['route_constraints']
	demand = variable_parameters['demand_list']
	travel = variable_parameters['travel_matrix']
	subsets = variable_parameters['subsets']
	locations = variable_parameters['locations']
	customers = variable_parameters['customers']

	subset_indices = range(len(subsets))
	end_hub = locations[-1]

	# A large number
	M = 100

	# Create a variable, "prob", to contain our problem data
	prob = LpProblem("morton_function_4", LpMinimize)

	# Create problem variables
	# Number of times a route from one site to another is run by a given hauler 
	x = LpVariable.dicts('x', (locations,locations,haulers), lowBound = 0,
	        upBound = None, cat = 'Integer')

	# Whether or not a subset of site locations is traveled to by a given hauler
	y = LpVariable.dicts('y', (subset_indices,haulers), lowBound = 0, upBound = 1,
		cat = 'Integer')	

	# 2.1
	# Objective is to minimize total distance traveled by all haulers
	prob += lpSum([lpSum([lpSum([travel[i][j]*x[i][j][k] for k in haulers])
	    for j in locations]) for i in locations])

	# 2.2
	# Each hauler must leave the start_hub (locations[0]) each day (but can return
	# to un/reload) but it cannot go from start_hub to start_hub
	for k in haulers:
	    prob += lpSum([x[0][j][k] for j in list(set(locations)-set([0]))]) >= 1,''

	# 2.3
	# If a hauler goes to a site, he must also leave from that site
	for h in customers:
	    for k in haulers:
	        prob += (lpSum([x[i][h][k] for i in locations]) - lpSum([x[h][j][k]
	            for j in locations])) == 0,''

	# 2.4
	# All haulers must return to the end-of-day hub (can be same physical location
	# as start-of-day hub)
	for k in haulers:
	    prob += lpSum([x[i][end_hub][k] for i in locations]) == 1,''

	# 2.5
	# A hauler may only operate L hours in a day
	# We add one handle's worth of time to workable day as we assume hauler's trailer
	# will either be ready before day starts or not needed to be changed at end of day 
	for k in haulers:
	    prob += lpSum([lpSum([x[i][j][k]*(handle + int(travel[i][j]/rate))
	        for i in locations]) for j in locations]) <= L + handle,''

	# 2.6
	# Each site's demand for dropped-off/picked-up equipment sets must be met
	for i in customers:
	    prob += lpSum([lpSum([x[i][j][k] for j in locations]) for k in haulers]) \
	            == abs(demand[i]),''

	# 2.7
	# Haulers are limited by how many times a given route between two sites
	# can be traveled
	for i in locations:
	    for j in locations:
	        prob += lpSum([x[i][j][k] for k in haulers]) <= route_constraints[i][j],''
	
	# 2.8
	# Whether or not a hauler travels amongst a set of customers
	for k in haulers:
		for m in subset_indices:
			prob += lpSum([lpSum([x[i][j][k] for i in subsets[m]])
				for j in subsets[m]]) <= y[m][k]*M
	
	# 2.9
	# If a hauler travels amongst a set of customers, it must leave that set
	for k in haulers:
	    for m in subset_indices:
	        prob += lpSum([lpSum([x[i][j][k] for i in subsets[m]]) for j
	        	in list(set(locations)-set(subsets[m]))]) >= y[m][k],''
	
	# The problem data is written to an lp file
	prob.writeLP('morton_toy_problem.lp')

	# The problem is solved using PuLP's choice of Solver
	prob.solve()

	results = {
		'status': LpStatus[prob.status],
		'objective': value(prob.objective),
		'variables': prob.variables()
	}

	return results
