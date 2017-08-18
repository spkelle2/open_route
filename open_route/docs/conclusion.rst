.. _conclusion:

Conclusion
==========

Possible Improvements
---------------------

Looking back on the work I did creating Open-Route's software package with
the construction company, there were a couple avenues I wish I would have
had the time to explore that I think would have led to better results for
the construction company. At the time of making Open-Route, almost a year
later, the first two remain to be improved, as they're why I want to go to
graduate school, but I have made progress on the third.

The first had to do with the smoothing integer program. The goal of the model
was to minimize the variation amongst the days. Given that variation is a
second-order function, I would have liked to have had the time to research
approaches to smoothing demand with an Quadratic Program. If the
objective of our smoothing function could have been quadratic, I could have
been able to minimize the overall variation, resulting in a tighter smoothing
of all the days' demands.

I also would have liked to have cleaned up the routing integer program as
well. Constraints :math:`(8)-(9)` despite solving a key issue with the model,
were very computationally expensive as they grew exponentially relative to
the number of sites that had demand for a given day. Given how small the
problem size was for each day (only 5 locations), dealing with
exponential constraint growth was not an issue. However, finding a way to
model the problem to the same effect but without the exponential constraints
would be necessary for scaling the number of locations for which we could
solve at one time.

The one area for improvement for that project I had wanted
to make that Open-Route solved was another issue in scalability - scaling so
that more people can use it more easily. The last project read from fragile
excel files and had to be run from the command line. I think providing a
structured form and GUI via a web app makes the project much more user
friendly and useful to anyone who would want to try it out.

Biography
---------

A brief bit about me. At time of writing, I'm a studying Industrial Engineer
at the University of Illinois. My interest areas lie in Operations Research
and Computer Science. I really enjoy Operations Research for the art of
modeling mathematically the world around me and having a means of making a
decision on what to do with whatever I have modeled. I developed an interest
in computer science out of my endeavors to make operations research more
valuable by means of developing time saving heuristics and embedding models
into software that the average person can use. This work represents the
joining of both of my interests which I have been developing throughout my
education and serves as the capstone for my collegiate career.

Moving forward, I'd like to continue developing products, like this one, that
aid people in making decisions or automate them for networks of machines. I see
two bottlenecks in such products becoming reality, and they are the motivation
for my work and study plans over the next few years.

The first is being able to develop scalable software, related to my third area
of improvement highlighted above. In order for people or machines to be able
to use such a product, intelligent data transmission and user interface, as
well as cloud and parallelized computing are bodies of knowledge over which
I'll need a firm grasp. It is for that reason I took time between my undergrad
and graduate studies to build data pipelines for a software company and intend
to take time during my graduate studies to continue developing internet
technologies.

The second is being able to develop scalable models, those that as they grow can
still reach a good enough solution in a feasible amount of time. As noted in
my second area for improvement, this is what stands in the way of me being able
to build models, and therefore software, that can accomodate the future's
toughest problems. For that reason, I view attending a graduate operations
research program with a strong focus on algorithms as a necessity for my future.
I intend to learn how optimization algorithms work, as well as equip myself
with the abilty to come up with new methods for their approximations, so that
no matter the complexity of my environment, I can solve the model that I made
to describe it.

Thank you for taking the time to read my work.

Sean Kelley

217-722-2228

seanpkelley94@gmail.com
