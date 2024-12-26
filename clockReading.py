import math
import time
from math import pi, atan2
from time import struct_time

import cv2 as cv
import numpy as np
import numpy.typing as npt

from imageConsts import IMG_WIDTH, IMG_HEIGHT, CLK_HAND_COLORS, HandRadii
from exceptions import InvalidListLengthsException

# Subtracting this number seems to help when both clock hands are near 0,
# in order to not mistake 59 for 00
MAGIC_FIX = 0.5


def _calc_dist(pt1: list[float, float], pt2: list[float, float]) -> float:
    """
    Calculate the distance between two points.
    :return: The euclidian distance between two points.
    """
    return math.sqrt(math.pow(pt1[0] - pt2[0], 2) +
                     math.pow(pt1[1] - pt2[1], 2)
                     )


def _calc_angle(pt1: list[float, float], pt2: list[float, float]) -> float:
    """
    Calculate the angle between two points, where 0 o-clock is 0 degrees.
    :return: The degree in radians
    """
    deg = (atan2(pt1[0] - pt2[0], pt1[1] - pt2[1]) + pi / 2) / 2 / pi * 60
    # in case our x,y is in the fourth quadrant of the xy plane (hours 9 - 12)
    # The above function doesn't work in this case as the atan returns a value
    # between -pi to -pi/2 and adding pi/2 to it still gives a negative value / coordinates_outside_the_hour_radius.
    if deg < 0:
        deg = (atan2(pt1[0] - pt2[0], pt1[1] - pt2[1]) +
               (3 * pi / 2)) / 2 / pi * 60 + 30
    return deg


def _is_coordinate_outside_seconds_hand_radius(cor: tuple[float, float]) -> float:
    """
    Check if a coordinate is inside the given radius of the seconds hand.
    Meaning - if you were to draw a circle around the center of the clock
    at the radius of the seconds hand, this would check if given coordinate
    is inside it.
    """
    img_center = (int(IMG_WIDTH / 2), int(IMG_HEIGHT / 2))
    return _calc_dist(cor, img_center) > HandRadii.SECONDS.value - 10


def _find_angles_in_radius(binary_image: npt.NDArray[np.int_]) -> list[float]:
    """
    Finds the angles of all the clock hands inside the given black-white image.
    :param binary_image: the black-white image.
    :return: A list of hours on the clock (in the range 0 to 60)
    """
    # make the clock hands white for the mask
    sub_image = cv.bitwise_not(binary_image)
    center = (int(IMG_WIDTH / 2), int(IMG_HEIGHT / 2))
    mask = np.zeros(sub_image.shape[:2], dtype="uint8")
    for i in HandRadii.list()[0:2]:
        cv.circle(mask, center, int(i), (255, 255, 255), 1)
    masked_image = cv.bitwise_and(sub_image, sub_image, mask=mask)
    indices = np.where(masked_image == [255])
    coordinates = list(zip(indices[0], indices[1]))

    read_second = None
    cor_of_read_second = center
    for cord in coordinates:
        if _is_coordinate_outside_seconds_hand_radius(cord):
            read_second = _calc_angle(cord, center)
            cor_of_read_second = cord

    best_min_found_angle = None
    best_min_found_cor = None
    for cord in coordinates:
        if (not _is_coordinate_outside_seconds_hand_radius(cord)
                and not (_calc_dist(cord, center) < HandRadii.HOURS.value + 10)):
            fmin = _calc_angle(cord, center)
            if best_min_found_angle is None:
                best_min_found_angle = fmin
                best_min_found_cor = cord
            elif _calc_dist(best_min_found_cor, cor_of_read_second) < _calc_dist(cord, cor_of_read_second):
                best_min_found_angle = fmin
                best_min_found_cor = cord

    if read_second < 30:
        best_min_found_angle = math.ceil(best_min_found_angle - MAGIC_FIX) % 60
    else:
        best_min_found_angle = math.floor(best_min_found_angle - MAGIC_FIX) % 60

    return [0, best_min_found_angle, read_second]


def find_hour_red(image: npt.NDArray[np.int_]) -> float:
    """
    Find the hour displayed in the clock image, based on the fact
    the hour hand is red.
    :param image: A RGB color image.
    :return: The hour displayed by the clock.
    """
    cntr = (int(IMG_WIDTH / 2), int(IMG_HEIGHT / 2))
    X, Y = np.where(np.all(image == CLK_HAND_COLORS[2], axis=2))
    avg_y = sum(Y) / len(Y)
    avg_x = sum(X) / len(X)
    return _calc_angle((avg_x, avg_y), cntr)


def _find_furthest_number_between_lists(large_list: list[float], small_list: list[float]) -> float:
    """
    Receives angles of m (in large) and n (in small) clock hand angles,
    and guesses the one that is most likely unique to the large list.
    This is needed because the same clock hand has a little bit different
    of an angle depending on the radius you calculate it at.
    :param large_list: A list of m angles.
    :param small_list: A list of n<m angles.
    :return: The angles unique to the large list.
    """
    if len(large_list) <= len(small_list):
        raise InvalidListLengthsException("Invalid lengths. small={} large={}".format(
            len(small_list), len(large_list))
        )
    best_diff = -1
    best_value = None
    for angle in large_list:
        min_diff = -1
        for small in small_list:
            if min_diff == -1 or abs(small - angle) < min_diff:
                min_diff = abs(small - angle)
        if best_diff == -1 or min_diff > best_diff:
            best_diff = min_diff
            best_value = angle
    return best_value


def read_the_time(img: npt.NDArray[np.int_]) -> struct_time:
    """
    Receives an image generated by generate_clock_image and returns the time
    shown by the clock.

    :param img: An image that was generated by generate_clock_image.
    :return: The time the clock in the image was displaying.
    :remarks: There could be a problem of interference between
             the background of the clock and the clock hands.
             The solutions I thought of are to change the color
             of the clock (not the hands) to be less black,
             and so they'll be removed when changing into bw image.
             This seemed like a "cheat" solution,
             So didn't do this, I ended up needing at least
             2 of the clock hands to be smaller much than the numbers
             in radius so there exists a square around the center
             where only 1 clock hand appear but there is no numbers
             in it. This seems like a "cheat" solution also in hindsight.
    """
    ret, bw_img = cv.threshold(img, 127, 255, cv.THRESH_BINARY)
    found = _find_angles_in_radius(bw_img)
    found[0] = round((find_hour_red(img) - (found[1] / 12)) / 5)
    return time.strptime("{} {} {}".format(
        int(found[0]), int(found[1]), int(found[2])
    ), "%H %M %S")
