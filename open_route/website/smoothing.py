from pulp import *
import numpy as np
import pandas as pd

def smoothing_model(d, s):
	"""The integer program responsible for smoothing 'period' days of demand

	Minimizes the total number of demand for any one day, while ensuring all
	demand for each site is met within the time window.

	Parameters
	----------
	d : numpy.ndarray
		The number of drop-offs or pick-ups each site needs each day

	s : list
		Three dimensional list describing the alternative delivery dates
		each site has for each day it has demand. If a site has no demand on
		a given day, its list of alternatives is empty.
	
	Returns
	-------
	results : dict
		Whether or not the IP solved to optimality, what the largest
		demand for the period was after smoothing, and the newly assigned
		demands to each site each day.
	"""

	num_locations, num_days = d.shape
	locations = range(num_locations)
	days = range(num_days)

	prob = LpProblem("smoothing", LpMinimize)

	# variable detailing number of drop-offs/pick-ups in each day in time window
	# for each site
	w = LpVariable.dicts('w', (locations,days), lowBound = 0, upBound = None,
		cat = 'Integer')

	# variable detailing max number of drop-offs/pickups at all sites in each day
	z = LpVariable('z', lowBound = 0, upBound = None, cat = 'Integer')

	# 1.1
	# minimize greatest amount of drop-offs/pick-ups on one day in current period
	prob += z

	# 1.2
	# sum of pick-ups/drop-offs for each site over all days in window must
	# equal magnitude of demand on original date for that site
	for i in locations:
		for l in days:
			if len(s[i][l]) > 0:
				prob += lpSum([w[i][l_prime] for l_prime in s[i][l]]) \
						== abs(d[i][l])

	# 1.3
	# z must be greater than or equal to each day's sum of deliveries
	for l in days:
		prob += lpSum([w[i][l] for i in locations]) <= z

	prob.writeLP('smoothing.lp')

	prob.solve()

	results = {
		'status': LpStatus[prob.status],
		'objective': value(prob.objective),
		'variables': prob.variables()
	}

	return results

# run the smoothing algorithm for each period of time from start_date to end_date
def iterate(period_inputs, current_start_index):
	"""Smoothes 'period' days of demand data
	
	Pulls the original demand data for the next 'period' days to be smoothed.
	Creates a matrix of possible days each site can have drop-offs or pick-ups,
	constrained by the 'window' and the 'period' of days being considered.
	Smoothes 'period' days of demand and records the new number of drop-offs
	and pick-ups to be made to each site each day in this period.

	Parameters
	----------
	period_inputs : dict
	    The variables recording how 'smooth' the demand being adjusted 'period'
	    days at a time can be. Includes how many days are in a period, how many
	    days are in our window, the dataframe recording demand, an array
	    storing how much demand each day has after smoothing, the largest
	    demand seen for any one day, and a flag for if this period length
	    returns a feasible solution for every 'period' days smoothed.

	current_start_index : int
	    The column of the demand dataframe from which the next 'period' days
	    of demand will begin to be smoothed

	Returns
	-------
	period_inputs : dict
		Inputs recording statistics on the smoothed demand and the smoothed
		demand itself are saved to their respective variables and returned.
	"""
	period = period_inputs['period']
	demand_df = period_inputs['demand_df']
	window = period_inputs['window']
	feasible = period_inputs['feasible']
	daily_totals = period_inputs['daily_totals']
	largest_objective = period_inputs['largest_objective']
	
	# set the index where the smoothing algorithm will stop for this iteration
	current_end_index = current_start_index + period

	# pull the data between the indices
	df = demand_df.iloc[:,current_start_index:current_end_index]
	d = df.values

	locations, days = d.shape
	
	# matrix to store which days are drop-offs and need to have negative values
	# when we finish
	transform = np.ones((locations,days))
	
	# lists the dates within the time window for drop-off/pick-up if a site has
	# demand for a drop-off/pick-up that day 
	s = [[[] for i in range(days)] for i in range(locations)]
	
	for i in range(locations):
	    for l in range(days):
	        
	        # list all days drop-off(s) for a site can occur and mark them in
	        # our transform matrix so we can return their negative values
	        # after smoothing
	        if d[i,l] < 0:
	            magnitude = min(window, l+1)
	            s[i][l] = range(l-(magnitude-1), l+1)
	            for day in s[i][l]:
	                transform[i,day] = -1
	        
	        # list all days pick-up(s) for a site can occur if it has demand
	        # for pick-up(s) that day
	        if d[i,l] > 0:
	            magnitude = min(window, period-l)
	            s[i][l] = range(l, l+magnitude)

	# spread the drop-off(s) and pick-up(s) of all sites as evenly as possible
	# keeping them all within the time window
	results = smoothing_model(d,s)

	status = results['status']
	objective = results['objective']
	variables = results['variables']

	# if the solver does not optimally assign all drop-offs/pick-ups, mark this
	# period length as infeasible so its results will not be considered
	if status != 'Optimal':
		feasible = False

	# assign the number of visits each site will be made each day by parsing
	# site and date values from variables
	for v in variables:
		if v.name[0] == 'w':    
		    first_underscore_index = v.name.find('_')
		    second_underscore_index = v.name.rfind('_')

		    i = int(v.name[first_underscore_index+1:second_underscore_index])
		    l = int(v.name[second_underscore_index+1:])

		    d[i,l] = v.varValue

	# record absolute values of deliveries made daily
	daily_totals[current_start_index:current_end_index] = d.sum(axis=0)

	# return negative values to site visits that represent drop-offs
	d = np.multiply(d, transform)

	# returned smoothed demands back to the corresponding spot in the demand df
	demand_df.iloc[:,current_start_index:current_end_index] = d

	# update max number of deliveries for this period length if needed
	if objective > largest_objective:
		largest_objective = objective

	period_inputs['demand_df'] = demand_df
	period_inputs['daily_totals'] = daily_totals
	period_inputs['feasible'] = feasible
	period_inputs['largest_objective'] = largest_objective

	return period_inputs

def smooth_demand(demand_df, variation, window, start_date, end_date):
	"""Smooth the demand for drop-offs and pick-ups for a given variation as
	much as possible constrained to the time window

	Defines a list of period lengths. For each period length, demand is smoothed
	'period length' days at a time. Returns the smoothed demand for the entire
	time range corresponding to the length of period which results in the lowest
	variance in total daily demand.

	Parameters
	----------
    demand_df : pandas.core.fame.DataFrame
	    dataframe of demands to be smoothed

	variation : str
	    which variation of a proposed region for which we want to smooth demand

	window : str
	    The number of different days to allow a job site to have equipment
	    dropped-off or picked-up

	start_date : str
		The first day in our range of time we are considering ('yyyy-mm-dd'
		format)

	end_date : str
		The last day in our range of time we are considering ('yyyy-mm-dd'
		format)

	Returns
	-------
	mv_demand_df : pandas.core.frame.DataFrame
	    The minimum variance demand dataframe is the demand for each job site
	    each day, spread as smoothly as possible, constrained to the size of
	    our window
	"""

    #print('smoothing demand for %s' % variation)

	# number of days to do at once
	periods = np.array([5]) #arange(3,11)

	# minimum variance of all seen period lengths
	min_variance = 999 
	
	# the period length and objective for the period length with minimum variance
	mv_period = 999
	mv_objective = 999

    # need to find a way to refresh df if running for multiple periods
	for period in periods:

        # commented out for web app
		# dataframe with demands for drop-offs/pick-ups at each site each day
        #demand_df = pd.read_excel(file_path, sheetname=variation, index_col=0)
		
		# drop columns outside of date range
		start_index = demand_df.columns.get_loc(start_date)
		end_index = demand_df.columns.get_loc(end_date)
		demand_df = demand_df.iloc[:,start_index:end_index+1]
		num_days = len(demand_df.columns)

		# total number of drop-offs and pick-ups that will be made each day
		daily_totals = np.zeros(num_days)
				
		# whether or not the smoothing algorithm returns a feasible answer
		# for a given length of periods
		feasible = True

		# indices from which our smoothing algorithm will start
		indices = range(0, num_days, period)
		
		# record the largest minimum value we'll see throughout
		# all iterations in this period
		largest_objective = 0

		period_inputs = {
			'period': period,
			'window': window,
			'demand_df': demand_df,
			'daily_totals': daily_totals,
			'largest_objective': largest_objective,
			'feasible': feasible
		}

		for current_start_index in indices:

			# if on last index, adjust the copy of period to remaining number of days
			if (indices.index(current_start_index) == len(indices)-1 and
				num_days % period != 0):

				period_inputs['period'] = num_days % period
				period_inputs['period']

			period_inputs = iterate(period_inputs, current_start_index)

		variance = period_inputs['daily_totals'].var()

		if feasible == True:
			if variance < min_variance:
				
				mv_demand_df = period_inputs['demand_df']
				min_variance = variance
				mv_period = period
				mv_objective = period_inputs['largest_objective']

    #print('best period had length %s with a variance of %s and objective %s' % 
        #(mv_period, min_variance, mv_objective))

	return mv_demand_df

