import datetime
import math
import time

import pytest

from clockGeneration import generate_clock_image
from clockReading import _find_furthest_number_between_lists, read_the_time
from exceptions import InvalidListLengthsException


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
    # t=read_the_time(generate_clock_image(time.strptime("05 05 05","%H %M %S")))
    for h in range(12):
        for m in range(1, 60, 2):
            for s in range(0, 60, 12):
                org = time.strptime("{} {} {}".format(h, m, s), "%H %M %S")
                img = generate_clock_image(org)
                t = read_the_time(img)
                got = datetime.datetime(*t[:6])
                org = datetime.datetime(*org[:6])
                assert math.fabs(got.second - org.second) < 2
                assert math.fabs(got.minute - org.minute) < 2
                assert math.fabs(got.hour - org.hour) < 1
