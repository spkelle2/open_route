# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.utils import timezone
from .models import Run
import numpy as np
import pandas as pd

def index(request):
    template = loader.get_template('website/index.html')
    context = {
    }
    return HttpResponse(template.render(context, request))

def end(request):
    
    # pull POST data into proper data frames 
    demand = np.zeros((5,5))
    sites = np.zeros((5,2))
    for key in request.POST.keys():
        if key != 'csrfmiddlewaretoken':
            
            # assign values for demands here 
            if len(key) == 2:
                row = int(key[0])-1
                col = int(key[1])-1
                demand[row, col] = request.POST[key]
   
            # assign values for coordinates here 
            else:
                row = int(key[-1])-1
                if key[:3] == 'lat':
                    col = 0
                else:
                    col = 1
                sites[row, col] = request.POST[key]
    
    # create data frame resembling input matrix from index page
    indices = ['Site 1', 'Site 2', 'Site 3', 'Site 4', 'Site 5']
    dates = ['day_1', 'day_2', 'day_3', 'day_4', 'day_5']
    demand_df = pd.DataFrame(data=demand, index=indices, columns=dates)

    coords = ['latitude', 'longitude'] 
    site_df = pd.DataFrame(data=sites, index=indices, columns=coords)

    template = loader.get_template('website/end.html')
    context = {
        'demand_df' : demand_df.to_html(),
        'site_df' : site_df.to_html()
    }
    return HttpResponse(template.render(context, request))






