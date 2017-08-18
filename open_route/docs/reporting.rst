.. _reporting:

Reporting Results
=================

Upon completion of the truck routing for every day in our data set, we are
left with three complete pieces of information as our results.

    * how much demand each site had each day (smoothed)

    * what routes the trucks took each day

    * how many hours each hauler worked each day

We saw earlier in the docs how to come up with the smoothed version of demand.
All that is left with demand is to put the input side by side with the smoothed
so the changes are easy to see, as is done exactly on the top of the return page of
Open-Route. We've yet to cover how we interpreted the hours each driver works
and routes each truck takes each day. I'd like to take a second to do that now.

Interpreting Daily Hours and Routes
-----------------------------------

Recall our variable for number of times a route from site :math:`i` to :math:`j`
was covered by truck :math:`k`, :math:`x_{i,j,k}`. Also remember :math:`t_{i,j}`
was our travel distance between two sites and :math:`r` was our travel rate. With those
three piece of information, the following gives us how long each truck driver
works each day:

.. math::

    \sum_{i} \sum_{j} x_{i,j,k}*t_{i,j}*r \text{ } \forall \text{ } k \in \text{trucks}

Recording the time each driver works each day, we can then plot those hours into
the "Truck Utilization" graphs seen in the middle of the response page. Worth
noting, the highest indexed truck driver is assigned the longest set of routes
to run each day, in order to have to use extra drivers as little as possible.
Once we've decided which truck drivers match up to which of our :math:`k`
drivers in our model, we then record the routes they ran for that day by which
:math:`x_{i,j,k}` > 0.

Lastly, summary stats on the utilization of each truck driver are printed out
to help add a little more detail to their workload throughout the week. With
that we now have all the data and graphs we need to generate the return page. That's
it for Open-Route's documentation, but I welcome you to read on to my comments
on the project or brief biography on myself.

Continue to :ref:`conclusion`



Documentation
-------------
Summary of driver mileage accumulated and routes taken on a given day:

.. autofunction:: recording.record_fleet_mileage

Summary of time truck driver work each day and the routes they take:

.. autofunction:: recording.record_hauler_hours

Bar graph for daily hours of truck driver
.. autofunction:: reporting.hauler_graph_maker

Report generator:

.. autofunction:: reporting.make_report

Summarization of truck driver utilization:

.. autofunction:: reporting.summarize

Continue to :ref:`conclusion`


