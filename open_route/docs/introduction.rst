.. _introduction:

Introduction
============

This documentation explains the code base and mathematical models powering
Open-Route. If you haven't checked out the website yet, I welcome you to
go to http://www.open-route.website and
take a look. Clicking through the website takes less than a minute and will
make the following documentation much more coherent!

Originally a package that I created for modeling the movement of identical
sets of large construction equipment ('thus identical items that fill the
truck's capacity exactly' on the website), the software behind Open-Route has been
repurposed for a general application of scheduling and vehicle routing in a
delivery network. Open-Route hopes to benefit anyone moving large and identical
items through a network by providing the following solutions:

    * What days should items be dropped-off/picked-up

    * How many trucks are needed each day

    * What routes does each truck take each day

Github
------

If you'd like to follow along in the code for which this documentation was
created, I invite you to check out `the github repository
<https://github.com/spkelle2/open_route/tree/master/open_route/website/>`_.
The remaining chapters have a "Documentation" section detailing where
specifically in the code base you can find what is explained here.

Topics
------

I'll cover a few different topics throughout this documentation in order to
describe the entire approach to the solutions Open-Route provides.

    * :ref:`main` covers handling input data and adjusting drop-off/pick-up dates.
      This part is where everything is set up that will remain constant for
      the daily routing calculations.

    * :ref:`daily-routing` explains how the daily routing calculations are
      made - how many trucks are needed and what routes does each take.

    * :ref:`reporting` outlines how the graphs are generated for returned
      requests from the web app.

    * In :ref:`conclusion`, I'll give my closing remarks on the project and
      a brief bit about myself.

I hope you enjoy reading, and thank you for taking the time to check out my
work!

Sean Kelley

Operations Research Analyst and Software Developer



