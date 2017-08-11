# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils import timezone

# Create your models here.

class Run(models.Model):
    name = models.CharField(max_length=50, default='')
    run_date = models.DateTimeField(default=timezone.now)
    affiliation = models.CharField(max_length=50, default='')
    fun_fact = models.CharField(max_length=200, default='')

    def __str__(self):
        return self.name
