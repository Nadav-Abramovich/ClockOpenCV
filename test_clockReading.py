import time

import numpy as np
import pytest

from clockGeneration import generate_clock_image
from clockReading import _find_angles_in_radius, _find_furthest_number_between_lists, read_the_time
from consts.image import CLK_BACKGROUND_COLOR
from exceptions import TooManyClockHandsDetectedException, \
    InvalidListLengthsException


def test_find_angles_in_radius_too_many_clock_hands():
    arr = np.ndarray((500, 500, 3), np.uint8)
    for x in range(500):
        for y in range(500):
            arr[y][x] = CLK_BACKGROUND_COLOR
    for x in range(0, 500, 10):
        for y in range(500):
            arr[y][x] = [255, 0, 0]
    with pytest.raises(TooManyClockHandsDetectedException):
        _find_angles_in_radius(30, arr)


def test_find_furthest_number_between_lists_invalid_lengths():
    with pytest.raises(InvalidListLengthsException):
        _find_furthest_number_between_lists([1.0], [2.0, 3.0])


def test_read_the_time_test_cases():
    """
    Edge case tests read_the_time.
    """
   # Note for the reviewer - in principle it would probably be better to also have
   # unit tests for clockReading (tests on a static input, that are not dependent on
   # the clockGenerator. We could use some kind of serialization and save its outputs
   # in a way we can load for these unit tests. Since there is a time constraint
   # and this is no long term / multi people I skip them though.
    t=read_the_time(generate_clock_image(time.strptime("05 05 05","%H %M %S")))
    img=generate_clock_image(time.strptime("10 52 58", "%H %M %S"))
    t = read_the_time(img)
    t.tm_min