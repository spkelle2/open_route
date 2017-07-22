# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

# Create your models here.

class Run(models.Model):
    first_name = models.CharField(max_length=50, default='')
    last_name = models.CharField(max_length=50, default='')
    email = models.CharField(max_length=100, default='')
    data_location = models.CharField(max_length=200, default='')
    run_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.first_name
