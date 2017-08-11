import pandas as pd
import numpy as np
import itertools

def make_demand_list(daily_demand):
    """Converts our daily demand from a pandas series to a list and adds the
    demands (0 demand) for where haulers start and end their days

    Parameters
    ----------
    daily_demand : pandas.core.series.Series
        How much demand each site has on a given day, given that the site
        needs at least one drop-off or one pick-up

    Returns
    -------
    demand_list : list
        Demands for all locations (job sites with demands and the hub) to be
        included on our graph for the day's hauler routing
    """

    demand_list = daily_demand.tolist()
    demand_list.insert(0,0)
    demand_list.append(0)

    return demand_list  


def make_route_constraints(demand_list):
    """Makes a matrix detailing how many times the route from site i to site j
    can be travelled by all haulers in one day

    The following constraints apply to the number of times the route from i to j
    can be travelled. Travelling the route from i to j never happens if they both
    need drop-offs, both need pick-ups, or i is where a hauler ends his day. If
    i and j have opposite demand types (one with drop-offs, the other pick-ups),
    i to j can be travelled as many times as the minimum absolute value of
    demand had by the two sites. We place no constraint on how many times a hauler
    can return to the hub to reload his trailer.

    Parameters
    ----------
    demand_list : list
        Demands for all locations (job sites with demands and the hub) to be
        included on our graph for the day's hauler routing

    Returns
    -------
    route_constraints : numpy.ndarray
        The number of times the route between any two locations can be
        travelled by all haulers
    """
    
    length = len(demand_list)
    route_constraints = np.zeros((length, length))
    
    for i in range(length):
        for j in range(length):

            # if we can travel from i to j, how many times we can take that route
            # is limited by the site with lesser magnitude of demand
            if demand_list[i]*demand_list[j] < 0:
                route_constraints[i,j] = min(abs(demand_list[i]), abs(demand_list[j]))
            
            # we place no constraints on how often a hauler can enter and leave
            # start-hub, as well as how many times it can enter end-hub
            elif i == 0 or j == 0 or j == length-1:
                route_constraints[i,j] = 100
            
            # if a route is between sites with same kind of demand or emanates from
            # end-hub, it cannot be travelled
            else:
                route_constraints[i,j] = 0
    
    return route_constraints


def make_travel_matrix(daily_demand, site_df, travel_rate, day_length, handle):
    """Makes a matrix describing how long the route from location i to location
    j is

    Takes the difference in coordinates for each location to be visited on a given
    day and converts them to mileage. Rounds routes that are greater than one
    day's worth of miles to the max miles that can be done in one day.

    Parameters
    ----------
    daily_demand : pandas.core.series.Series
        How much demand each site has on a given day, given that the site
        needs at least one drop-off or one pick-up

    site_df : pandas.core.frame.DataFrame
        The latitude and longitude for each of our sites

    travel_rate : float
        How many miles per minute a hauler can drive on average

    day_length : int
        How many minutes per day a hauler can work

    handle : int
        How long it takes on average for a hauler to unload or reload his trailer

    Returns
    -------
    travel_matrix : numpy.ndarray
        How many miles the route from location i to location j is
    """
    
    locations = daily_demand.index.tolist()
    
    # 0 and 6 are ID's for our hubs (matched to index.html)
    locations.insert(0,0)
    locations.append(6)

    length = len(locations)
    travel_matrix = np.zeros((length,length))

    # max distance that can be covered in one day by one hauler
    max_dist = int((day_length - handle)*travel_rate/2.0)
    

    for i in range(length):
        for j in range(length):

            a = locations[i]
            b = locations[j]

            # find coords of each site, find the differences, convert them to miles
            lat1 = site_df.loc[site_df['Project #'] == a, 'Lat'].iloc[0]
            long1 = site_df.loc[site_df['Project #'] == a, 'Long'].iloc[0]

            lat2 = site_df.loc[site_df['Project #'] == b, 'Lat'].iloc[0]
            long2 = site_df.loc[site_df['Project #'] == b, 'Long'].iloc[0]
            
            # 69 miles between latitudes and 53 for longitudes in USA
            actual_dist = int(69*abs(lat1 - lat2) + 53*abs(long1 - long2))

            # round actual distance to the maximum, making the assumption that the
            # hauler could legally run a bit longer to finish day or finish negligbly
            # early the next day
            travel_matrix[i,j] = min(max_dist, actual_dist)

    return travel_matrix

def make_subsets(customers, demand_list):
    """Make all even sized subsets of customers (job sites) to be visited each
    day, excluding those where all customers have the same kind of demand (all
    drop-offs or all pick-ups)

    Needed for ensuring the routes each hauler makes this day are all connected

    Parameters
    ----------
    customers : list
        A list of the indices corresponding to each job site with a demand on
        a given day

    demand_list : list
        Demands for all locations (job sites with demands and the hub) to be
        included on our graph for the day's hauler routing

    Returns
    -------
    subsets : list
        The list of all even sized subsets of customers where both types of
        demand are present
    """ 

    demand = np.array(demand_list)
    subsets = []
    
    for L in range(2, len(customers)):
        for subset in itertools.combinations(customers, L):
            
            sub = list(subset)
            index = np.array(sub)
            sub_demand = demand[index]
            if len(np.unique(np.sign(sub_demand)))==2 and len(sub)%2 == 0:
                subsets.append(sub)
    
    subsets.append(customers)
    
    return subsets


def make_parameters(fixed_parameters, daily_inputs):
    """Create the remaining parameters (all of which vary by day) to solve
    our daily routing problem

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
    variable_parameters : dict
        The parameters that vary by day but are still needed for our model
        to run
    """

    travel_rate = fixed_parameters['travel_rate']
    day_length = fixed_parameters['day_length']
    handle = fixed_parameters['handle']
    site_df = fixed_parameters['site_df']

    daily_demand = daily_inputs['daily_demand']

    demand_list = make_demand_list(daily_demand)

    # list of sites included in equipment hauler routing problem
    locations = range(len(demand_list))

    # list of sites in EHRP with demand (gets rid of hubs)
    customers = locations[1:-1]

    route_constraints = make_route_constraints(demand_list)

    travel_matrix = make_travel_matrix(daily_demand, site_df, travel_rate,
                                   day_length, handle)

    subsets = make_subsets(customers, demand_list)


    variable_parameters = {
    'demand_list': demand_list,
    'route_constraints': route_constraints,
    'travel_matrix': travel_matrix,
    'subsets': subsets,
    'locations': locations,
    'customers': customers
    }

    return variable_parameters
