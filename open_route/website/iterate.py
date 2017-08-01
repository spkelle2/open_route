import numpy as np
import pandas as pd
import datetime

from parameters import make_parameters
from hauler_routing import route_fleet
from recording import record_fleet_mileage, record_hauler_hours

from smoothing import smooth_demand
from reporting import make_report

def solve_day(fixed_parameters, daily_inputs):
    """Determine the usage of semi-trucks and equipment haulers for a given day.

    Creates parameters specific to solving a given day's truck and hauler usage.
    Uses extension of a Vehicle Routing problem to determine how many
    semi-trucks/haulers were needed, how many miles were driven, and how long
    each hauler works.

    Parameters
    ----------
    fixed_parameters : dict
        Parameters that are constant for any variation and region (as defined
        in the main function)

    daily_inputs : dict
        inputs needed each day to make remaining parameters and record the
        outputs of our routing model

    Returns
    -------
    fleet_mileage : numpy.ndarray
        How many miles a fleet of a given size runs on a given day

    hauler_hours : numpy.ndarray
        How many minutes each hauler works each day

    """

    # make the remaining parameters used to solve a day's equipment hauler routing
    variable_parameters = make_parameters(fixed_parameters, daily_inputs)

    # declare variables created in other functions to be used in this one
    fleet_upper_bound = fixed_parameters['fleet_upper_bound']
    travel_rate = fixed_parameters['travel_rate']
    handle = fixed_parameters['handle']
    
    date_index = daily_inputs['date_index']
    fleet_mileage = daily_inputs['fleet_mileage']
    hauler_hours = daily_inputs['hauler_hours']
    hauler_routes = daily_inputs['hauler_routes']
    daily_demand = daily_inputs['daily_demand']

    demand_list = variable_parameters['demand_list']
    locations = variable_parameters['locations']
    travel_matrix = variable_parameters['travel_matrix']

    # start fleet size at 0 and increment until feasible
    fleet_size = 0
    
    # boolean stating if problem can be solved for given sized fleet
    feasible = False

    # if our demand_list includes more than our "start-of-day" hub and
    # "end-of-day" hub, we have demand for equipment haulers and solve
    # routing problem
    if len(demand_list)>2:
        abs_demand_list = np.absolute(demand_list)
        pickups = np.sum(abs_demand_list[1:-1])
        
        # use the smaller of two values for best run time
        upper_bound = min(pickups, fleet_upper_bound)

        while fleet_size <= upper_bound and not feasible: 
            # create a list of equipment haulers as our last parameter
            haulers = range(fleet_size)

            # this solves the equipment hauler routing problem
            results = route_fleet(fixed_parameters, variable_parameters, haulers)      
            
            status = results['status']
            objective = results['objective']
            variables = results['variables']

            # don't record a mileage for a given size fleet if infeasible
            if status == 'Infeasible' or status == 'Undefined':
                fleet_mileage[fleet_size, date_index] = np.nan
                
            elif status == 'Optimal':
                feasible = True
                
                # record mileage run by fleet
                fleet_mileage = record_fleet_mileage(fleet_size, date_index,
                    fleet_mileage, objective, fleet_upper_bound)
                
                # record hours that each hauler in fleet works
                hauler_hours, hauler_routes  = record_hauler_hours(hauler_hours,
                    hauler_routes, variables, handle, travel_rate, fleet_size,
                    date_index, locations, travel_matrix, daily_demand)
                
                print('trucks, status, objective = %s, %s, %s' % (fleet_size, status,
                    objective))

            # if we reach upper bound still infeasible, large negative number
            # will make it easy to find
            if not feasible and fleet_size == upper_bound:
                print('trucks, status = %s, %s' % (fleet_size, status))
                objective_matrix[fleet_size, date_index] = -9999999

            fleet_size = fleet_size + 1
    
    # if we do not have any sites with demand (aka len(demand_list) = 2)
    # print the following and move to next day
    else:
        print('No Demand!')
            
    return fleet_mileage, hauler_hours, hauler_routes

def solve_variation(fixed_parameters, demand_df):
    """ Find truck, hauler, and equipment usages for all days in our range.

    Finds and smoothes delivery demand for all days. Determines day by day
    usage of all assets. Creates report detailing usage over whole range.

    Parameters
    ----------
    fixed_parameters : dict
        Parameters that are constant for any variation and region (as defined
        in the main function)

    demand_df : pandas.core.frame.DataFrame
        demand for number of drop-offs or pick-ups that each site has for
        each day. This df has already been smoothed for the web edition
    """

    # declare needed fixed_parameters (do this before the functions using them
    # need them so they don't need to be created more than once)
    start_date = fixed_parameters['start_date']
    end_date = fixed_parameters['end_date']
    fleet_upper_bound = fixed_parameters['fleet_upper_bound']
    window = fixed_parameters['window']

    num_dates = len(demand_df.columns)
    
    # matrix to store miles run by each fleet of a given size each day
    fleet_mileage = np.zeros((fleet_upper_bound + 1, num_dates))
    
    # matrix to store hours worked by each hauler each day
    hauler_hours = np.zeros((fleet_upper_bound + 1, num_dates))

    # dictionary to store routes run by each hauler each day
    hauler_routes = {}
    
    # record the sites with demand and how large that demand is each day
    for date in demand_df.columns:
        daily_demand = demand_df[date]
        daily_demand = daily_demand[daily_demand != 0]

        date_index = demand_df.columns.get_loc(date)

        # inputs needed each day to make remaining parameters for equipment
        # hauler routing
        daily_inputs = {
            'fleet_mileage': fleet_mileage,
            'hauler_hours': hauler_hours,
            'hauler_routes' : hauler_routes,
            'date': date,
            'daily_demand': daily_demand,
            'date_index': date_index
        }
    
        fleet_mileage, hauler_hours, hauler_routes = solve_day(fixed_parameters,
                                                               daily_inputs)

    # convert fleet_mileage and hauler_hours to dataframes and save as csv's 
    mileage_df = pd.DataFrame(data = fleet_mileage, columns = demand_df.columns)
    #mileage_df.to_csv('%s objective.csv' % variation)

    hours_df = pd.DataFrame(data = hauler_hours, columns = demand_df.columns)
    #hours_df.to_csv('%s trucker.csv' % variation)

    data = {
        'demand_df': demand_df,
        'mileage_df': mileage_df,
        'hours_df': hours_df,
        'hauler_routes': hauler_routes
    }

    # make report to record a summary of the results for this variation
    return(make_report(data, fixed_parameters))

