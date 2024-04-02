"""
This program checks if the sun is over the horizon and returns a True Boolean response if it's daytime at KHO (Kjell Henriksen Observatory). Nicolas Martinez (UNIS-LTU) 2024

"""

import numpy as np
import datetime as dt
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz
from astropy.coordinates import get_sun
import astropy.units as u

def is_it_daytime():
    kho = EarthLocation(lat=78.148*u.deg, lon=16.043*u.deg, height=520*u.m)

    # Use the current UTC time
    now = Time.now()

    frame_now = AltAz(obstime=now, location=kho)

    sun_position = get_sun(now).transform_to(frame_now)

    # Check if the sun's altitude is greater than 0 degrees (above the horizon)
    return sun_position.alt > 0 * u.deg

if __name__ == "__main__":
    if is_it_daytime():
        print("The sun is up, MISS2 is asleep.")
    else:
        print("The sun is down, MISS2 is on.")