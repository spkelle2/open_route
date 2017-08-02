import pandas as pd
import numpy as np
import itertools
import collections

def record_fleet_mileage(fleet_size, date_index, fleet_mileage, objective,
    fleet_upper_bound):
    """Records the total mileage run by the fleet each day

    Assigns the mileage to all possible fleet sizes greater than or equal to
    the minimum fleet size.

    Parameters
    ----------
    fleet_size : int
        The number of haulers in the fleet for this iteration

    date_index : int
        The index of the date for which is currently being solved

    fleet_mileage : numpy.ndarray
        The total number of miles that a fleet of a given size would need to
        run each day to meet all of the demand.

    objective : int
        The total number of miles the fleet ran to meet all demand on this day

    fleet_upper_bound : int
        The maximum number of haulers that can be available on one day

    Returns
    -------
    fleet_mileage : numpy.ndarray
        The total number of miles that a fleet of a given size would need to
        run each day to meet all of the demand.
    """
    
    while fleet_size <= fleet_upper_bound:
        fleet_mileage[fleet_size, date_index] = objective
        fleet_size += 1

    return fleet_mileage

def record_hauler_hours(hauler_hours, hauler_routes, variables, handle,
    travel_rate, fleet_size, date_index, locations, travel_matrix,
    daily_demand):
    """Records the number of minutes each hauler works each day

    Sums the time taken by each hauler to run all of his assigned routes in a
    day. Gives the greatest amount of work to the lowest indexed haulers.
    Restricted to there being 10 or fewer locations on a graph for each day.

    Parameters
    ----------
    hauler_hours : numpy.ndarray
        How many minutes each hauler works each day

    hauler_routes : dict
        Running list of the routes that each equipment hauler runs each day

    variables : dict
        The number of times each hauler travels each route on a given day

    handle : int
        How long it takes on average for a hauler to unload or reload his trailer

    travel_rate : float
        How many miles per minute a hauler can drive on average

    fleet_size : int
        The number of haulers in the fleet for this iteration

    date_index : int
        The index of the date for which is currently being solved

    locations : list
        The indices of all sites the haulers will visit on a given day (including
        the hub)

    travel_matrix : numpy.ndarray
        How many miles the route from location i to location j is

    daily_demand : pandas.core.series.Series
        The sites with demand on a given day and their corresponding demand

    Returns
    -------
    hauler_hours : numpy.ndarray
        How many minutes each hauler works each day
    """

    prob_vars = sorted(variables, key=lambda x: x.name[-1])
    hauler_numbers = range(fleet_size)

    todays_routes = []

    for k in hauler_numbers:

        current_hauler_routes = []
        minutes_worked = 0
        
        for v in prob_vars:
            # ignore variable if it does not represent a traveled route
            mask1 = (v.name[0] == 'x' and v.varValue != 0.0)            
            mask2, mask3, mask4 = False, False, False

            # make sure we have an x variable before doing other tests
            if mask1:

                # ignore variable if the route is from start-hub to end-hub 
                mask2 = (int(v.name[2]) != locations[0] or
                    int(v.name[4]) != locations[-1])

                # ignore variable if the route is from start-hub to start-hub
                mask3 = (int(v.name[2]) != locations[0] or 
                    int(v.name[4]) != locations[0])
                
                # ignore variable if it's not the current hauler  
                mask4 = (int(v.name[-1]) == k)

            if mask1 and mask2 and mask3 and mask4:
                print(v.name, ' = ', v.varValue)
                i = int(v.name[2])
                j = int(v.name[4])
                minutes_worked += v.varValue*(travel_matrix[i, j]/travel_rate
                        + handle)

                # map i from its relative index to its original
                if i == 0 or i == len(locations) - 1:
                    i = 'hub'
                else:
                    i = 'site ' + str(daily_demand.index[i-1])


                # map j from its relative index to its original
                if j == len(locations) - 1 or j == 0:
                    j = 'hub'
                else:
                    j = 'site ' + str(daily_demand.index[j-1])

                if i != j:
                    current_hauler_routes.append(('(%s, %s)' % (i, j), v.varValue))

        todays_routes.append(('hauler %s' % (k + 1),
                collections.OrderedDict(current_hauler_routes)))

        # assume we have one less handle than sites visited
        minutes_worked -= handle
        hauler_hours[k, date_index] = minutes_worked

        print('hauler %s = %s' % (k, minutes_worked))

    hauler_routes.append(('day %s' % (date_index + 1),
        collections.OrderedDict(todays_routes)))

    return hauler_hours, hauler_routes
