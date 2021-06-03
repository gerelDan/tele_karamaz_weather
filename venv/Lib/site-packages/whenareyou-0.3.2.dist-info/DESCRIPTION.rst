whenareyou
==========

Gets the timezone of any location in the world.

This uses google and caches the results so that you can hopefully stay outside
the free rate limit (which I have no idea how high it is).

This is how you use it:

::

    $ pip install whenareyou
    $ ipython

    In [1]: from whenareyou import whenareyou

    In [2]: tz = whenareyou('Hamburg')

    In [3]: tz
    Out[3]: <DstTzInfo 'Europe/Berlin' LMT+0:53:00 STD>

    In [4]: from datetime import datetime

    In [5]: tz.localize(datetime(2002, 10, 27, 6, 0, 0))
    Out[5]: datetime.datetime(2002, 10, 27, 6, 0, tzinfo=<DstTzInfo 'Europe/Berlin' CET+1:00:00 STD>)

    In [6]: tz.localize(datetime(2002, 10, 27, 6, 0, 0)).isoformat()
    Out[6]: '2002-10-27T06:00:00+01:00'


