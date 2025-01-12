import time
from math import sin, cos, pi
from time import struct_time

import cv2 as cv
import numpy as np
import numpy.typing as npt

from imageConsts import (IMG_WIDTH, IMG_HEIGHT, CLOCK_IMG_PATH,
                         CLK_HAND_THICKNESS, HandRadii, CLK_HAND_COLORS)
from exceptions import FailedToResizeException, FailedToLoadFileException


def _get_angles(clk_time) -> list[float]:
    """
    This function calculates the angles of each clock hand relative
    to the 00:00 hour, based on the given clk_time.
    :param clk_time: The time for the clock to display.
    :return: [hour_hand_angle, min_hand_angle, sec_hand_angle]
    """
    hr, mn, sec = map(int, time.strftime("%I %M %S", clk_time).split())
    # Allow the hour and minute hands to move non-whole values
    hr += mn / 60
    mn += sec / 60

    # hr*5 is for making hours the same scale [0..60) as mn, and sec.
    angles = list(map(lambda val: val * 2 * pi / 60, [sec, mn, hr * 5]))

    # We have a phase shift of +2pi because we start
    # our measurements from the 12th hour, but the unit circle
    # starts from the 3rd hour.  This should fix it
    # so our values will work well with sin & cos
    angles = [angle - pi / 2 for angle in angles]
    return angles


def generate_clock_image(clk_time: struct_time) -> npt.NDArray[np.int_]:
    """
    Generate a JPEG image of an analog clock,
    showing the given time. The image is of size IMG_WIDTH x IMG_HEIGHT.

    :param clk_time: The time the clock in the generated image will show.
    :return: The image, as a numpy array.
    """
    try:
        clk_img = cv.imread(CLOCK_IMG_PATH)
    except cv.error as e:
        raise FailedToLoadFileException(e)
    if clk_img is None:
        raise FailedToLoadFileException("Failed to load the clock image.")

    try:
        img = cv.resize(clk_img, (IMG_WIDTH, IMG_HEIGHT))
    except cv.error as e:
        raise FailedToResizeException(e)

    img_center = (int(IMG_WIDTH / 2), int(IMG_HEIGHT / 2))
    sec_angle, mn_angle, hr_angle = _get_angles(clk_time)

    # NOTE for the reviewer: This zip is probably too big, and looks a lil bit ridiculous.
    #                        I considered making a clockHand class to hold these
    #                        values instead of this mess. BUT since unlike real code
    #                        this code will not be further expanded / maintained, and
    #                        since these values will have to be put inside
    #                        the objects manually anyway (as these are arbitrary consts that
    #                        are different to each clock hand) I decided against it in this
    #                        case
    for angle, radius, color, thickness in zip([sec_angle, mn_angle, hr_angle],
                                               HandRadii.list(),
                                               CLK_HAND_COLORS,
                                               CLK_HAND_THICKNESS):
        # This white "halo" around the clock hand is added in order to
        # let my code handle cases where the clock hands overlap.
        # cv.line(img,
        #        img_center,
        #        (int(img_center[0] + radius * cos(angle)),
        #         int(img_center[1] + radius * sin(angle))),
        #       WHITE_HALO_COLOR,
        #       thickness + 45)
        # This is the actual clock hand
        cv.line(img,
                img_center,
                (int(img_center[0] + radius * cos(angle)),
                 int(img_center[1] + radius * sin(angle))),
                color,
                thickness)

    return img
