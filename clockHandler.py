import time
from math import sin, cos, pi, atan2
from time import struct_time

import cv2 as cv
import numpy as np
import numpy.typing as npt

from consts.image import (IMG_WIDTH, IMG_HEIGHT, CLOCK_IMG_PATH,
                          CLK_HAND_RADII, CLK_HAND_COLORS, CLK_HAND_THICKNESS)


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
    angles = list(map(lambda val: val * 2 * pi / 60, [hr * 5, mn, sec]))

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
    clk_img = cv.imread(CLOCK_IMG_PATH)
    img = cv.resize(clk_img, (IMG_WIDTH, IMG_HEIGHT))
    img_center = (int(IMG_WIDTH / 2), int(IMG_HEIGHT / 2))
    hr_angle, mn_angle, sec_angle = _get_angles(clk_time)

    # NOTE for the reviewer: This zip is probably too big, and looks a lil bit ridiculous.
    #                        I considered making a clockHand class to hold these
    #                        values instead of this mess. BUT since unlike real code
    #                        this code will not be further expanded / maintained, and
    #                        since these values will have to be put inside
    #                        the objects manually anyway (as these are arbitrary consts that
    #                        are different to each clock hand) I decided against it in this
    #                        case
    for angle, radius, color, thickness in zip([hr_angle, mn_angle, sec_angle],
                                               CLK_HAND_RADII,
                                               CLK_HAND_COLORS,
                                               CLK_HAND_THICKNESS):
        cv.line(img,
                img_center,
                (int(img_center[0] + radius * cos(angle)),
                 int(img_center[1] + radius * sin(angle))),
                color,
                thickness)

    return img


def _find_angles_in_radius(side_length: float, bw_img: npt.NDArray[np.int_]) -> list[float]:
    """
    Finds the angles of all the clock hands inside the given black-white image
    by going along its sides clockwise and finding consecutive blocks of non-white.
    :param side_length: the length of the side of the rectangle to look for clock hands,
                         around the center.
    :param bw_img: the black-white image.
    :return: A list of hours on the clock (in the range 0 to 60)
    """
    sub_image = bw_img[
                int(IMG_WIDTH / 2) - side_length:int(IMG_WIDTH / 2) + side_length,
                int(IMG_HEIGHT / 2) - side_length:int(IMG_HEIGHT / 2) + side_length
                ]
    # Scanning from top-left in clock-wise order
    relevant_coordinates = (
            # Top side
            [(i,0) for i in range(0, 2 * side_length - 1)] +
            # right side
            [(2 * side_length - 1, i) for i in range(0, 2 * side_length - 1)] +
            # bottom side
            [(i, 2 * side_length - 1) for i in range(2 * side_length - 1, 0, -1)] +
            # left side
            [(0,i) for i in range(2 * side_length - 1, 0, -1)])
    found = False
    sum_x, sum_y = 0,0
    amount = 0

    found_angles = []
    for x,y in relevant_coordinates:
        if list(sub_image[y,x]) != [255, 255, 255]:
            if not found:
                found = True
            sum_x += x
            sum_y += y
            amount += 1
        else:
            if found:
                x = int(sum_x / amount)
                y = int(sum_y / amount)
                val = (atan2(y - side_length, x - side_length) + pi / 2) / 2 / pi * 60
                # Fourth quadrant of they xy plane (9 - 12)
                # The above function doesnt work in this case as the atan returns a value
                # between -pi to -pi/2 and adding pi/2 to it still gives a negative value / hour.
                if val < 0:
                    val = (atan2(y - side_length, x - side_length) + (3 * pi / 2)) / 2 / pi * 60 + 30
                found_angles.append(val)
            found = False
            sum_x = 0
            sum_y = 0
            amount = 0
    return found_angles

def read_the_time(img: npt.NDArray[np.int_]) -> struct_time:
    """
    Receives an image generated by generate_clock_image and returns the time
    shown by the clock.

    :param img: An image that was generated by generate_clock_image.
    :return: The time the clock in the image was displaying.
    """
    ret, bw_img = cv.threshold(img, 127, 255, cv.THRESH_BINARY)
    print(_find_angles_in_radius(30, bw_img))
    return bw_img