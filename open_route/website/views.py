# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.utils import timezone

from .models import Run
from .smoothing import smooth_demand
from .iterate import solve_variation

import numpy as np
import pandas as pd

def index(request):
    template = loader.get_template('website/index.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

def post_to_df(post_data):

    # pull POST data into proper data frames 
    demand = np.zeros((5,5))
    sites = np.zeros((7,3))
    for key in post_data.keys():
        if key != 'csrfmiddlewaretoken':
            
            # assign values for demands here 
            if len(key) == 2:
                row = int(key[0])-1
                col = int(key[1])-1
                demand[row, col] = post_data[key]
   
            # assign values for coordinates here 
            elif 'long' == key[:4] or 'lat' == key[:3]:
                row = int(key[-1])
                if key[:3] == 'lat':
                    col = 1
                else:
                    col = 2

                # coordinate value
                sites[row, col] = post_data[key]

                # site number (for travel_matrix generator in parameters.py)
                sites[row, 0] = row

                # add entry for end location
                if row == 0:
                    row = len(sites) - 1
                    sites[row, col] = post_data[key]
                    sites[row, 0] = row

    return(demand, sites)
 


def end(request):
    
    # assign values for all fixed inputs
    # give arbitrary values to start and end to fit function inputs
    start_date = '2015-01-01'
    end_date = '2015-01-05'

    travel_rate = float(request.POST['travel_rate'])/60
    day_length = int(request.POST['day_length'])
    handle = int(request.POST['handle'])
    fleet_upper_bound = 12
    window = int(request.POST['window'])
    directory_name = '/Users/skelley/Documents/personal/senior_design/web_app/open_route/media/'
    
    # pull the demand data and site coordinates from post data
    demand, sites = post_to_df(request.POST)

    # create dataframe from input that can be put into smoothing function
    dates = ['2015-01-01', '2015-01-02', '2015-01-03', '2015-01-04', '2015-01-05']
    demand_df = pd.DataFrame(data=demand, columns=dates)

    # start indices at 1 as required by parameters.py
    demand_df.index = demand_df.index + 1

    # create data frame to record our coordinates for the problem
    cols = ['Project #', 'Lat', 'Long'] 
    site_df = pd.DataFrame(data=sites, columns=cols)

    fixed_parameters = {
        'start_date' : start_date,
        'end_date' : end_date,
        'travel_rate' : travel_rate,
        'day_length' : day_length,
        'handle' : handle,
        'fleet_upper_bound' : fleet_upper_bound,
        'window' : window,
        'directory_name' : directory_name,
        'site_df' : site_df
    }

    # smooth our demand as evenly as possible, pass nothing for variation
    # since we only have one variation to solve for
    demand_df = smooth_demand(demand_df, '', window, start_date, end_date)

    # run the vehicle routing module for each day and return a dictionary
    # detailing usage statistics
    output = solve_variation(fixed_parameters, demand_df)

    truck_table = output['truck_table']
    pictures = output['pictures']
    hauler_routes = output['hauler_routes']

    # change demand dataframe to match format from views.index
    indices = ['Site 1', 'Site 2', 'Site 3', 'Site 4', 'Site 5']
    days = ['day 1', 'day 2', 'day 3', 'day 4', 'day 5']
    demand_df = pd.DataFrame(data=demand_df.values, index=indices, columns=days)

    # repull post data bc smoothing function was changing the input as well
    demand, sites = post_to_df(request.POST) 

    # create data frame resembling input matrix from index page
    input_df = pd.DataFrame(data=demand, index=indices, columns=days)

    template = loader.get_template('website/end.html')
    context = {
        'input_df' : input_df.to_html(),
        'demand_df' : demand_df.to_html(),
        'truck_table' : truck_table,
        'pictures' : pictures,
        'hauler_routes' : hauler_routes
    }
    return HttpResponse(template.render(context, request))






