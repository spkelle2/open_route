.. _main:

Set-Up Horizon
==============

Each request that Open-Route processes follows three steps: collecting data
that will be fixed for each day, making calculations specific
to each day, and reporting the results of all calculations
made. This section covers capturing the fixed data - the set-up that is
required for being able to solve for all days.

Fixed Inputs
------------

Regardless of which day the process is routing trucks, there are a few inputs
that remain constant from the time the user sets them. They are as follows:

    * the average rate of travel of the trucks
    * the length of a working day for a truck driver
    * the average time it takes an item to be unloaded from or loaded onto the
      truck
    * the number of days (time window) in which a site is elgible to have
      items dropped-off or picked-up for each instance of demand
    * the geographical coordinates of each site in our network - sites having
      items picked-up/dropped-off and the hub where trucks start/end their days

Demands - how many items are requested for drop-off or pick-up on a day at a
site - will also remain fixed throughout the request, with the exception of the
smoothing operation that may adjust those days prior to the daily calculations.
The rest of this section will be devoted to explaining that.

Importance of Time Windows
--------------------------

In order to make sure the dates items are dropped-off/picked-up are feasible,
we need a sufficient number of trucks and items available in our network. To
give a preference to having more items or more trucks in our network, I
implemented time windows into the calculations. For example, prescribing that
site must have its items dropped-off and picked-up the day they're demanded
will result in a couple extremes. It will minimize the number of items needed
to meet all sites' demands (as it minimizes the amount of items sitting unused
at sites prior to/after being needed) but will maximize the number of trucks
needed to satify the network as some days may require many more item
movements than others. Adding just a day to the time window (increasing it
from 1 day to 2) can dramatically decrease the number of trucks required
without having much effect on the number items. Having (hopefully) assigned
the time window as optimally as possible, let's move on to smoothing the
demand in the item network.

Demand Smoothing Model
----------------------

I approached demand smoothing by formulating an integer program. It's parameters
are sites, :math:`i`, days, :math:`l`, and sets, :math:`S_{i,l}`, of
alternative days that drop-offs/pick-ups can be made for site :math:`i`
with original demand on day :math:`l`. Each site, :math:`i`, for each day,
:math:`l`, has a demand, :math:`d_{i,l}`, stating how many drop-offs or pick-ups
are required, with :math:`d_{i,l}` < 0 for drop-offs and :math:`d_{i,l}` > 0
for pick-ups. A set, :math:`S_{i,l}`, is empty unless :math:`d_{i,l} \neq` 0. In
that case :math:`S_{i,l}` is the set of the :math:`n` days before and including
the drop-off date or the :math:`n` days after and including the pick-up date,
where :math:`n` is the number of days in our time window. (If there are fewer
than :math:`n` days until the start or the end of our days, the set is
just the remaining days.)

I used two variables in this problem. The first, :math:`w_{i,l}`, represents
the number of items going to or from site :math:`i` on day :math:`l`. The second,
:math:`z`, is the largest sum of items going to or from all sites on any
single day, :math:`l`. We can now form the following integer program:

.. math::

    &\text{minimize } &z & & & &(1)

    &\text{s.t.:} & & & &

    & \sum_{l' \in S_{i,l}} & w_{i,l'} & = |d_{i,l}| \text{ } & \forall
    & \text{ } i,l : S_{i,l} \neq \{\} &(2)

    & \sum_{i} & w_{i,l} & \leq z \text{ } & \forall & \text{ } l &(3)

    & & w_{i,l}, z & \in Z \geq 0 \text{ } & \forall & \text{ } i,l & (4)

:math:`(1)` tells us that we are minimizing :math:`z`, the maximum number of
pick-ups and drop-offs to be done on any single day. This is enforced by
:math:`(3)`, stating that our objective, :math:`z`, must be greater than or
equal to any single day's sum of drop-offs and pick-ups.
:math:`(2)` adds that for any site, :math:`i`, on any day, :math:`l`, with a
demand for drop-offs or pick-ups, the number of items going to or from
that site within the time window must equal the number of items
originally demanded by site :math:`i` on day :math:`l`. Our last
constraint, :math:`(4)`, ensures all our variables are non-negative integers.

Put in plain English, :math:`(2)` allows us to assign pick-ups and drop-offs
to different days as long as its sufficiently close to the original day they
were requested, and :math:`(1)` and :math:`(3)` ensure the number of trips being
made each day are as few as possible. :math:`(4)` simply prevents any half-
drop-offs or half-pick-ups from being made.

With the number of drop-offs and pick-ups to be made to each site each day
now smoothed, the inputs for each day are fixed and ready to be passed to
day-specific calculations

Continue to :ref:`daily-routing`



Documentation
-------------

Adjusting/gathering fixed input:

.. autofunction:: iterate.solve_horizon

Creating the set, :math:`S`, and calling the smoothing integer program:

.. autofunction:: smoothing.iterate

Demand smoothing integer program:

.. autofunction:: smoothing.smoothing_model

Wrapper for demand smoothing functions:

.. autofunction:: smoothing.smooth_demand

Continue to :ref:`daily-routing`








