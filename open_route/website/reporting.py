import pandas as pd
import numpy as np
import itertools
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader

# compute summary statistics for each equipment hauler
# hours_df (how much each hauler works each day) is passed in as df when run
def summarize(df):
    """Computes summary statistics for each equipment hauler

    Statistics include the following: total hours worked by each hauler in
    the time range, number of days each hauler recorded time working,
    proportion of working days each hauler actually worked, average hours
    each hauler records on days he works
    
    Parameters
    ----------
    df : DataFrame
        How many minutes each hauler works each day (from hours_df)
    
    Returns
    -------
    summary : pandas.core.frame.DataFrame
        A dataframe with the summary statistics outlined above
    """
    
    summary = pd.DataFrame(index = df.index)
    num_dates = float(len(df.columns))
    
    # number is in minutes so divide by 60
    summary['Hours Worked in Time Range'] = df.sum(axis=1)/60.
    summary['Days Utilized'] = (df[df.columns] > 0).sum(1)
    
    summary['Percentage of Working Days Utilized'] = \
        summary['Days Utilized'].apply(lambda x: x/num_dates*100.)
    
    summary['Average Hours Worked per Utilized Day'] = \
        summary['Hours Worked in Time Range']/summary['Days Utilized']
    
    # drop all equipment haulers who didn't work at all throughout the time range
    summary = summary[pd.notnull(summary['Average Hours Worked per Utilized Day'])]
    
    # round all statistics to nice-looking precision
    summary['Hours Worked in Time Range'] = summary['Hours Worked in Time Range'].round()
    summary['Percentage of Working Days Utilized'] = \
        summary['Percentage of Working Days Utilized'].round(1)
    summary['Average Hours Worked per Utilized Day'] = \
        summary['Average Hours Worked per Utilized Day'].round(1)
    
    # increment hauler indicies so first hauler shows up as 1
    summary.index += 1
    
    return summary

def equipment_usage_analysis(demand_df, directory_name):
    """Determines for each day whether or not a given set of equipment was
    used
    
    Parameters
    ----------
    demand_df : DataFrame
        How many sets of equipment each site needs dropped-off or picked up
        each day

    directory_name : str
        The path for the directory where we'll save our graphs

    Returns
    -------
    usage : numpy.ndarray
        A matrix of binaries representing whether or not a given set of
        equipment was utilized on a given day
    """

    # make a dictionary for 100 equipment sets and their locations
    equipment = np.arange(100)
    location = np.zeros(100)

    equip_dict = dict(zip(equipment, location))

    # get matrices' dimensions
    num_days = len(demand_df.columns)
    num_sites = len(demand_df.index)
    num_equip = len(equipment)

    # create matrix for whether or not a set of equipment gets used
    # on a given day
    usage = np.zeros((num_equip, num_days))

    demand = demand_df.values

    for day in range(num_days):
        # mark all equipment sets that start the day at a site as in use
        for key in equip_dict:
            if equip_dict[key] != 0:
                usage[key,day] = 1
        
        # if a site has a demand for x equipment sets to be picked-up on a given
        # day, free up x equipment sets
        for site in range(num_sites):
            if demand[site,day] > 0:
                pickups = int(demand[site,day])
                
                for iterations in range(pickups):
                    if site in set(equip_dict.values()):
                        equip_dict[equip_dict.values().index(site)] = 0
                    
        # if a site has a demand for x equipment sets to be dropped-off on a
        # given day, assign x equipment sets to that site (possible inclusions are
        # equipment sets that were just freed from other sites)
        for site in range(num_sites):
            if demand[site,day] < 0:
                dropoffs = int(abs(demand[site,day]))
                
                for iterations in range(dropoffs):
                    equip_dict[equip_dict.values().index(0)] = site
        
        # mark all equipment sets that end the day at a site as in use
        # (we've effectly taken superset of equipment sets starting day in use
        # and ending day in use as in both cases equipment sets are utilized that
        # full day for transportation)
        for key in equip_dict:
            if equip_dict[key] != 0:
                usage[key,day] = 1

    #usage_df = pd.DataFrame(data=usage, columns=demand_df.columns)
    #usage_df.to_csv('%s%s Equipment Usage.csv' % (directory_name, variation))

    return usage

def equipment_graph_maker(demand_df, directory_name, plotlist):
    """Makes bar graphs for proportion of time range equipment is utilized and
    proportion of demand that can be met with a given number of equipment sets

    Parameters
    ----------
    demand_df : DataFrame
        How many sets of equipment each site needs dropped-off or picked up
        each day

    directory_name : str
        The path for the directory where we'll save our graphs

    plotlist : list
        List of filepaths for previously made graphs in this variation

    Returns
    -------
    plotlist : list
        List of filepaths for previously made graphs in this variation

    """

    # find out on which days each set of equipment is used
    usage = equipment_usage_analysis(demand_df, directory_name)
    num_days = usage.shape[1]
    num_equip_used = sum(i > 0 for i in usage.sum(axis=1))

    # make graph showing what proportion of days an equipment set is used
    y = usage.sum(axis=1)[usage.sum(axis=1) > 0]/num_days
    x = range(num_equip_used)
    
    fig, ax = plt.subplots()
    ax.bar(x,y)
    plt.ylim([0,1])
    
    ax.set_xlabel('Equipment Set Number')
    ax.set_ylabel('Days Used in Year')
    fig.suptitle('Equipment Set Utilization')
    
    # save it and append to plot list
    image_name = 'Equipment_Set_Utilization.png'
    graph_location = directory_name + image_name

    plt.savefig(graph_location)
    plotlist.append(image_name)

    # make graph showing how much equipment demand is met by x equipment sets
    y = (usage.sum(axis=1)[usage.sum(axis=1) > 0]/usage.sum()).cumsum()
    x = range(num_equip_used)
    
    fig, ax = plt.subplots()
    ax.bar(x,y)
    plt.ylim([0,1])
    
    ax.set_xlabel('Equipment Set Number')
    ax.set_ylabel('Machine Demand Met')
    fig.suptitle('Cumulative Machine Utilization')

    # save it and append to plot list
    image_name = 'Cumulative_Equipment_Set_Utilization.png'
    graph_location = directory_name + image_name
   
    plt.savefig(graph_location)
    plotlist.append(image_name)

    return plotlist


def hauler_graph_maker(hours_df, index, plotlist, directory_name):
    """ Plots a bar graph detailing amount of hours an equipment hauler worked
    each day

    Parameters
    ----------
    hours_df : DataFrame
        How many minutes each hauler works each day

    index : int
        Which hauler we are currently plotting

    plotlist : list
        List of strings containing file names for all previously created
        hauler plots

    directory_name : str
        File path of our working directory

    Returns
    -------
    plotlist : list
        List of filepaths for previously made graphs in this variation
    """    

    # x is dates, y is minutes worked by that hauler that day
    x = np.arange(len(hours_df.columns)) + 1
    y = list(hours_df.iloc[[index-1]].values)[0]

    # convert y from minutes to hours
    y = [value/60. for value in y]

    fig, ax = plt.subplots()
    #ax.xaxis_date()
    ax.bar(x, y)
    
    # max set a little greater than max hours that can be worked in one day
    plt.ylim([0,24])

    # axes labels
    plt.ylabel('Hours')
    plt.xlabel('Day')

    #fig.autofmt_xdate()
    fig.suptitle('Truck %s Utilization by Day' % (index))

    image_name = 'Truck%s.png' % index
    graph_location = directory_name + image_name
  
    plt.savefig(graph_location)
    
    # add where we saved this plot to the list of plots to add to the report
    plotlist.append(image_name)

    return plotlist

def make_report(data, fixed_parameters):
    """Creates input for a report of truck and equipment usage over the time range

    Details miles traveled by the fleet of trucks, utilization rates for each
    equipment hauler, and utilization rates for each set of equipment.

    Parameters
    ----------
    data : dict
        A dictionary containing daily site demands, truck mileage totals, and
        hours worked by each hauler

    fixed_parameters : dict
        Parameters that are constant for any variation and region (as defined
        in the main function)
    """
    
    demand_df = data['demand_df']
    mileage_df = data['mileage_df']
    hours_df = data['hours_df']
    hauler_routes = data['hauler_routes']

    directory_name = fixed_parameters['directory_name']
    fleet_upper_bound = fixed_parameters['fleet_upper_bound']

    # compile summary statistics for how much each hauler works
    hauler_summary = summarize(hours_df)
    
    # find the total number of miles the fleet runs over the entire time range
    fleet_miles = mileage_df.values.sum(axis=1)[fleet_upper_bound]

    plotlist = []
    
    # make graphs detailing the usage for each set of equipment
    #plotlist = equipment_graph_maker(demand_df, directory_name, plotlist)

    # make graphs detailing how much each hauler works each day
    for index in hauler_summary.index:
        plotlist = hauler_graph_maker(hours_df, index, plotlist, directory_name)

    # variables to be passed back to views.end
    template_vars = {
        'truck_miles' : 'Total Miles Driven by All Trucks: %s' % fleet_miles,
        'table_intro' : 'Usage Statistics by Truck',
        'truck_table' : hauler_summary.to_html(),
        'pictures' : plotlist,
        'hauler_routes' : hauler_routes
        'demand_df' : demand_df
    }

    return template_vars
