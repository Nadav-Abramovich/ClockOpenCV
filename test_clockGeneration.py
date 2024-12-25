import time
from unittest import mock
from unittest.mock import patch

import cv2 as cv
import pytest

from clockGeneration import _get_angles, generate_clock_image
from exceptions import FailedToResizeException, FailedToLoadFileException


def test_get_angles__handles_24_hour_format():
    """
    This test verifies that we handle correctly cases where the hours
    given are in the 13-24 range (as an analog clock only has 12 hours)
    """
    assert (_get_angles(time.strptime("1:00:00", "%H:%M:%S")) ==
            _get_angles(time.strptime("13:00:00", "%H:%M:%S")))

def test_generate_clock_image__raises_FailedToResizeException():
    with patch('cv2.resize', side_effect=cv.error('mocked error')):
        with pytest.raises(FailedToResizeException):
            generate_clock_image(time.time())

def imread():
    return None

def test_generate_clock_image__raises_FailedToLoadException():
    with patch('cv2.imread', side_effect=cv.error('mocked error')):
        with pytest.raises(FailedToLoadFileException):
            generate_clock_image(time.time())


@mock.patch('cv2.imread')
def test_generate_clock_image__raises_FailedToLoadException_on_fail_to_load(mock):
    mock.return_value = None
    with pytest.raises(FailedToLoadFileException):
        generate_clock_image(time.time())
