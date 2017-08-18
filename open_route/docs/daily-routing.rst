.. _daily-routing:

Daily Routing
=============

Knowing how many drop-offs and pick-ups are required each day at this point,
I tried to route all trucks throughout the time range in one integer program.
This proved quite unsuccessful, however, as the model was so large it could
not run in a feasible amount of time. After some trial and error, I discovered
that truck routing could be done very efficiently one day at a time, thus the
daily calculations.

Creating Parameters
-------------------

Before solving for the routes each truck will take each day, we
need to create a few parameters our routing integer program will need in
order to run. They are the following:

    * locations, :math:`i`
        A list of all :math:`n` sites with demand for drop-offs or pick-ups on
        a given day. Sites with no demand are excluded from this list.
        Prepended and appended to this list is the hub, where the
        trucks start and end their day. The hub has multiple indices, :math:`0`
        and :math:`n+1` but represents the same physical location.

    * demand, :math:`d_{i}`
        The number of drop-offs or pick-ups each location, :math:`i`, needs on a
        given day, ignoring the sites with no demand.

    * customers, :math:`i`
        A list of locations minus the hub. This list has length :math:`n`.

    * route constraints, :math:`D_{i,j}`
        A matrix of the number of times the route from site :math:`i` to
        site :math:`j` can be traveled, indexed in the same order as the
        locations parameter. Forces the model to adhere to these real world
        constraints:

        * A truck must alternate between dropping-off items and picking-up
          items. This prevents item pick-ups being satisfied by a truck that
          is already carrying an item and drop-offs being satisfied by a truck
          that is empty.

        * A truck can only use the demand from one site to satisfy an
          opposite demand at another as many times as is the minimum absolute
          value of demand between the two sites. This prevents sites of lesser
          demand from sourcing sites with greater demand more than they are
          capable, forcing trucks to return to the hub or less convenient
          sites for replenishment once the lesser demanded site has been
	  satisfied.

        This assignment is very particular. Please see the documentation below
        (make_route_constraints) and its definition in the parameters.py module
        in the github repository for more details.
      
    * travel, :math:`t_{i,j}`
        A matrix stating how many miles apart site :math:`i` is from
        site :math:`j` indexed in the same order as the locations list.
        The distances are calculated by converting the differences in
        geographical coordinates listed for each site.

    * subsets, :math:`S_{m}`
        A list of the even-sized subsets, :math:`m`, of sites with demand on a
        given day, necessary for forcing continuity in our trucks' routes.

    * M
        An arbitrarily large number.

    * trucks, :math:`k`
        A list of the trucks we have available.

Also recall a few parameters fixed upon input.

    * rate of travel, :math:`r`

    * length of working day, :math:`l`

    * average time to load/unload a truck (handling time), :math:`h`

Developing the Routing Model
----------------------------

Lastly, the problem makes use of two variables. The first variable is
:math:`x_{i,j,k}`, the number of times truck :math:`k` takes the
route from site :math:`i` to site :math:`j`. The other needed variable
is :math:`y_{m,k}`, whether or not a truck, :math:`k`, enters the
subset of points :math:`m`.

Now that we have declared all of our parameters we will need to solve our
truck routing for each day, we can define our model [#]_ .

.. math::

   \text{min} &\sum_{i} \sum_{j} \sum_{k} & &t_{i,j}x_{i,j,k} & & & & &(1)

   \text{s.t.:}

   &\sum_{j\backslash\{0\}} & &x_{0,j,k} & &\geq 1 & &\forall \text{ } k \in
   \text{trucks} &(2)

   &\sum_{i} x_{i,h,k} &-\sum_{j} &x_{h,j,k} & &= 0 & &\forall \text{ } h \in
   \text{customers}, k \in \text{trucks} &(3)

   &\sum_{i} & &x_{i,n+1,k} & &= 1 & &\forall \text{ } k \in \text{trucks}
   &(4)

   &\sum_{i} \sum_{j} & &x_{i,j,k}(h + \frac{t_{i,j}}{r}) & &\leq l + h &
   &\forall \text{ } k \in \text{trucks} &(5)

   &\sum_{j} \sum_{k} & &x_{i,j,k} & &= \mid d_{i} \mid & &\forall \text{ } i
   \in \text{customers} &(6)

   &\sum_{k} & &x_{i,j,k} & &\leq D_{i,j} & &\forall \text{ } i,j \in
   \text{locations} &(7)

   &\sum_{i' \in S_{m}} \sum_{j' \in S_{m}} & &x_{i',j',k} & &\leq M(y_{m,k}) &
   &\forall \text{ } k \in \text{trucks}, m \in \text{subsets} &(8)

   &\sum_{i' \in S_{m}} \sum_{j \backslash S_{m}} & &x_{i',j,k} & &\geq
   y_{m,k} & &\forall \text{ } k \in \text{trucks}, m \in \text{subsets} &(9)

   & & &x_{i,j,k} & &\in Z \geq 0 & &\forall \text{ } i,j \in \text{locations},
   k \in \text{trucks} &(10)

   & & &y_{m,k} & &\in \{0,1\} & &\forall \text{ } k \in \text{trucks}, m
   \in \text{subsets} &(11)
 
:math:`(1)` tells us our objective is to minimize the total amount of distance
that our fleet of trucks cover each day. :math:`(2)-(4)` add
constraints for modeling the travel from one site to the next. :math:`(2)`
says that each truck must leave the hub each day, even if just to return directly
to it at no cost (equivalent to not being used). If a truck arrives at a site
:math:`h` to make a drop-off or a pick-up, :math:`(3)` ensures that truck
also leaves that site for another. Once a truck has made all drop-offs and
pick-ups it needed to make for a day, :math:`(4)` requires that it returns to
the hub. :math:`(5)` brings our time constraints into play. We required that
all driving and unloading/loading (un/loading) of trucks must be less
than the length of the allowable work day. Time for an extra handle was added
under the assumption that each truck needed no adjustments at neither the
start nor end of its day by its driver. :math:`(6)` covers our demand
constraint, the requirement that each site, :math:`i`, must be visited exactly
as many times as it needs items dropped-off or picked-up each
day. To ensure that :math:`(6)` only counts the visits that correspond to the
type of demand the site has, :math:`(7)` applies the route constraints that
force a truck's visit to a site be one where it is able to
satisfy one unit of that site's demand. :math:`(8)-(9)` are additions to
:math:`(2)-(4)`, enforcing that trucks take routes that are only
possible in the real world. :math:`(8)` monitors whether or not a
truck enters a given subset of sites, while :math:`(9)` requires that a
truck leave that set if it entered it. These constraints remove
the possibility that the routes a truck takes in a day are disconnected.
Lastly, :math:`(10)-(11)` define the spaces for our variables, specifically
that trucks can take no partial routes and either enter or do not
enter any given set of sites.

Running the Routing Model
-------------------------

One final piece of information remains to fully define our integer program
for truck routing: how many trucks are needed on a given day. Trying to use
as few trucks as possible each day, I started by running the model with as
few trucks as possible, one, and rerun it, adding one truck per rerun, until
the program is feasible. Once feasible, the following is recorded:

    * how many hours each truck driver worked

    * what routes each truck covered

Once this process has been repeated for each day given in our range of time,
we can then summarize the data we've recorded to understand the capital
required to meet all sites' demands over the horizon.

Continue on to :ref:`reporting`



Documentation
-------------
Daily routing wrapper function:

.. autofunction:: iterate.solve_day

Creating parameters wrapper function:

.. autofunction:: parameters.make_parameters

Demand:

.. autofunction:: parameters.make_demand_list

Route constraints:

.. autofunction:: parameters.make_route_constraints

Travel:

.. autofunction:: parameters.make_travel_matrix

Subsets:

.. autofunction:: parameters.make_subsets

Model implementation:

.. autofunction:: hauler_routing.route_fleet

.. rubric:: Footnotes

.. [#] (2) - (4), as well as inspiration for the rest of the constraints,
    originate from the "Vehichle Routing Problem with Time Windows" chapter
    of *Column Generation* by Desaulniers, Desrosiers, and Solomon.

Continue on to :ref:`reporting`


