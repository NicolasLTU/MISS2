"""
This program checks if the sun is under -10 degrees below the horizon to get close to astronomical twilight conditions (-12 degrees and below) 
and returns a True Boolean response if it's nighttime at KHO (Kjell Henriksen Observatory). Nicolas Martinez (UNIS-LTU) 2024

"""

from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz
from astropy.coordinates import get_sun
import astropy.units as u

def it_is_nighttime():
    kho = EarthLocation(lat=78.148*u.deg, lon=16.043*u.deg, height=520*u.m)

    # Use the current UTC time - Time from astropy.time is in UTC per default
    now = Time.now()

    frame_now = AltAz(obstime=now, location=kho)

    sun_position = get_sun(now).transform_to(frame_now)

    # Check if the sun's altitude is greater than 0 degrees (above the horizon)
    return sun_position.alt < -10 * u.deg and sun_position # Sun position needs to be below -10 degrees to exclude dawn/twilight. 

if __name__ == "__main__":
    if it_is_nighttime():
        print("The sun is down, MISS2 is on.")
    else:
        print("The sun is up, MISS2 is asleep.")
