import math
import time
from math import pi, atan2
from time import struct_time

import cv2 as cv
import numpy as np
import numpy.typing as npt
from matplotlib import pyplot as plt

from consts.image import IMG_WIDTH, IMG_HEIGHT, CLK_BACKGROUND_COLOR, CLK_HAND_RADII, CLK_HAND_COLORS
from exceptions import FailedToReadTimeException, TooManyClockHandsDetectedException, InvalidListLengthsException


def _calc_dist(pt1,pt2):
    return math.sqrt(math.pow(pt1[0] - pt2[0], 2) + math.pow(pt1[1] - pt2[1], 2))

def _find_angles_in_radius(side_length: float, binary_image: npt.NDArray[np.int_]) -> list[float]:
    """
    Finds the angles of all the clock hands inside the given black-white image
    by going along its sides clockwise and finding consecutive blocks of non-white.
    :param side_length: the length of the side of the rectangle to look for clock hands,
                         around the center.
    :param binary_image: the black-white image.
    :return: A list of hours on the clock (in the range 0 to 60)
    """
    # sub_image = binary_image[
    #            int(IMG_WIDTH / 2) - side_length:int(IMG_WIDTH / 2) + side_length,
    #            int(IMG_HEIGHT / 2) - side_length:int(IMG_HEIGHT / 2) + side_length
    #            ]
    # make the clock hands white for the mask
    sub_image = cv.bitwise_not(binary_image)
    cntr = (int(IMG_WIDTH / 2), int(IMG_HEIGHT / 2))
    mask = np.zeros(sub_image.shape[:2], dtype="uint8")
    cv.circle(mask, cntr,
              int(CLK_HAND_RADII[0]),
              (255, 255, 255),
              1
              )
    cv.circle(mask, cntr,
              int(CLK_HAND_RADII[1]),
              (255, 255, 255),
              1
              )
    # cv.circle(mask, cntr,
    #           int(CLK_HAND_RADII[2]),
    #           (255, 255, 255),
    #           1
    #           )
    masked = cv.bitwise_and(sub_image, sub_image, mask=mask)
    #plt.imshow(masked)
    #plt.show()
    indices = np.where(masked == [255])
    coordinates = list(zip(indices[0], indices[1]))
    second = [math.sqrt(math.pow(cor[0] - cntr[0], 2) + math.pow(cor[1] - cntr[1], 2)) > CLK_HAND_RADII[0] - 10 for cor
              in coordinates]
    hour = [math.sqrt(math.pow(cor[0] - cntr[0], 2) + math.pow(cor[1] - cntr[1], 2)) < CLK_HAND_RADII[2] + 10 for cor in
            coordinates]

    fsecond = None
    pt_second = cntr
    for i in range(len(coordinates)):
        if second[i]:
            fsecond = (atan2(coordinates[i][0] - cntr[0], coordinates[i][1] - cntr[1]) + pi / 2) / 2 / pi * 60
            # in case our x,y is in the fourth quadrant of the xy plane (hours 9 - 12)
            # The above function doesn't work in this case as the atan returns a value
            # between -pi to -pi/2 and adding pi/2 to it still gives a negative value / hour.
            if fsecond < 0:
                fsecond = (atan2(coordinates[i][0] - cntr[0], coordinates[i][1] - cntr[1]) +
                           (3 * pi / 2)) / 2 / pi * 60 + 30
            fsecond = math.ceil(fsecond) % 60
            pt_second=coordinates[i]
    b_fmin = None
    b_pt = None
    for i in range(len(coordinates)):
        if not second[i] and not hour[i]:
            fmin = (atan2(coordinates[i][0] - cntr[0], coordinates[i][1] - cntr[1]) + pi / 2) / 2 / pi * 60
            # in case our x,y is in the fourth quadrant of the xy plane (hours 9 - 12)
            # The above function doesn't work in this case as the atan returns a value
            # between -pi to -pi/2 and adding pi/2 to it still gives a negative value / hour.
            if fmin < 0:
                fmin = (atan2(coordinates[i][0] - cntr[0], coordinates[i][1] - cntr[1]) +
                        (3 * pi / 2)) / 2 / pi * 60 + 30
            #fmin = math.ceil(fmin)%60
            if b_fmin is None:
                b_fmin = fmin
                b_pt = coordinates[i]
            elif _calc_dist(b_pt, pt_second) < _calc_dist(coordinates[i], pt_second):
                b_fmin = fmin
                b_pt = coordinates[i]

    # b_fhour = None
    # b_hourpt = None
    # for i in range(len(coordinates)):
    #     if hour[i]:
    #         fhour = (atan2(coordinates[i][0] - cntr[0], coordinates[i][1] - cntr[1]) + pi / 2) / 2 / pi * 60
    #         # in case our x,y is in the fourth quadrant of the xy plane (hours 9 - 12)
    #         # The above function doesn't work in this case as the atan returns a value
    #         # between -pi to -pi/2 and adding pi/2 to it still gives a negative value / hour.
    #         if fhour < 0:
    #             fhour = (atan2(coordinates[i][0] - cntr[0], coordinates[i][1] - cntr[1]) +
    #                     (3 * pi / 2)) / 2 / pi * 60 + 30
    #         #fhour = math.ceil(fhour)%60
    #         pt = coordinates[i]
    #         if b_fhour is None:
    #             b_fhour = fhour
    #             b_hourpt = coordinates[i]
    #         elif ((_calc_dist(b_pt, b_hourpt)**2+_calc_dist(pt_second, b_hourpt)**2) <
    #               (_calc_dist(b_pt, pt)**2+_calc_dist(pt_second, pt))**2):
    #             b_fhour = fhour
    #             b_hourpt = pt

    if(fsecond<30):
        b_fmin = math.ceil(b_fmin-0.5)%60
    else:
        b_fmin = math.floor(b_fmin-0.5) % 60

    # if (b_fmin < 30):
    #     b_fhour = math.ceil(b_fhour/5) % 12
    # else:
    #     b_fhour = math.floor(b_fhour/5) % 12


    return [0, b_fmin, fsecond]

def find_hour_red(binary_image: npt.NDArray[np.int_]) -> float:
    cntr = (int(IMG_WIDTH / 2), int(IMG_HEIGHT / 2))
    # plt.imshow(binary_image)
    # plt.show()
    X, Y = np.where(np.all(binary_image == CLK_HAND_COLORS[2], axis=2))
    avg_y = sum(Y) / len(Y)
    avg_x = sum(X) / len(X)
    fmin = (atan2(avg_x - cntr[0], avg_y - cntr[1]) + pi / 2) / 2 / pi * 60
    if fmin < 0:
        fmin = (atan2(avg_x - cntr[0], avg_y - cntr[1]) +
                (3 * pi / 2)) / 2 / pi * 60 + 30

    return fmin


def _find_angles_in_radius_bad(side_length: float, binary_image: npt.NDArray[np.int_]) -> list[float]:
    """
    Finds the angles of all the clock hands inside the given black-white image
    by going along its sides clockwise and finding consecutive blocks of non-white.
    :param side_length: the length of the side of the rectangle to look for clock hands,
                         around the center.
    :param binary_image: the black-white image.
    :return: A list of hours on the clock (in the range 0 to 60)
    """
    sub_image = binary_image[
                int(IMG_WIDTH / 2) - side_length:int(IMG_WIDTH / 2) + side_length,
                int(IMG_HEIGHT / 2) - side_length:int(IMG_HEIGHT / 2) + side_length
                ]
    # Scanning from top-left in clock-wise order
    relevant_coordinates = (
        # Top side
            [(i, 0) for i in range(0, int(2 * side_length - 1))] +
            # right side
            [(2 * side_length - 1, i) for i in range(0, int(2 * side_length - 1))] +
            # bottom side
            [(i, 2 * side_length - 1) for i in range(int(2 * side_length - 1), 0, -1)] +
            # left side
            [(0, i) for i in range(int(2 * side_length - 1), 0, -1)])

    found = False
    sum_x, sum_y = 0, 0
    amount = 0
    found_angles = []
    for x, y in relevant_coordinates:
        if list(sub_image[y, x]) != CLK_BACKGROUND_COLOR:
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
                # in case our x,y is in the fourth quadrant of the xy plane (hours 9 - 12)
                # The above function doesn't work in this case as the atan returns a value
                # between -pi to -pi/2 and adding pi/2 to it still gives a negative value / hour.
                if val < 0:
                    val = (atan2(y - side_length, x - side_length) +
                           (3 * pi / 2)) / 2 / pi * 60 + 30
                found_angles.append(val)
            found = False
            sum_x = 0
            sum_y = 0
            amount = 0

    if len(found_angles) > 3:
        raise TooManyClockHandsDetectedException(
            "Found {} (More than 3) angles".format(len(found_angles)))
    return found_angles


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


def read_the_time_2(img: npt.NDArray[np.int_]) -> struct_time:
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
    count = 3  # We expect 3 clock hands inside the first circle
    last_found = []
    hour, minute, sec = -1, -1, -1

    # NOTE: This is not a good for loop, as these are pretty random magic numbers.
    #       The problem is that the clock is round, and yet im scanning around
    #       in a rectangle, so a clock hand might fit or not fit inside a rectangle
    #       depending on the time. This range seems to work with the clock hand radii
    #       and clock size im using. A more precise and general
    #       formula for this range could be found.
    #       Also - We could use a sort of binary search for the values
    #       where there is a change of 1 in the found angles length,
    #       so we would only have to find the angles O(log n) times
    #       instead of this O(n) implementation. But I didn't bother.
    for i in range(50, 171):
        found = _find_angles_in_radius(i, bw_img)
        if len(found) < count:
            count = len(found)
            if count == 1:  # Only 1 clock hand in the rectangle side
                minute = _find_furthest_number_between_lists(last_found, found)
                sec = found[0]
                break
            hour = _find_furthest_number_between_lists(last_found, found)
            if hour is not None:  # None means two clock hands overlap...
                # hour is in range [0..60) like minutes and seconds.
                # this scales it to a [0,12) scale as it should be.
                hour /= 5
            else:
                raise FailedToReadTimeException()

        last_found = found
    return time.strptime("{} {} {}".format(int(hour), int(minute), int(sec)), "%H %M %S")


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
    # count = 3  # We expect 3 clock hands inside the first circle
    # last_found = []
    # hour, minute, sec = -1, -1, -1

    # NOTE: This is not a good for loop, as these are pretty random magic numbers.
    #       The problem is that the clock is round, and yet im scanning around
    #       in a rectangle, so a clock hand might fit or not fit inside a rectangle
    #       depending on the time. This range seems to work with the clock hand radii
    #       and clock size im using. A more precise and general
    #       formula for this range could be found.
    #       Also - We could use a sort of binary search for the values
    #       where there is a change of 1 in the found angles length,
    #       so we would only have to find the angles O(log n) times
    #       instead of this O(n) implementation. But I didn't bother.
    radii = [30, 100, 165]
    # found = {
    #    radii[0]: None,
    #    radii[1]: None,
    #    radii[2]: None
    # }
    # for i in radii:
    #    found[i] = _find_angles_in_radius(i, bw_img)
    found = _find_angles_in_radius(1, bw_img)
    found[0] = round((find_hour_red(img)-(found[1]/12))/5)
    """if len(found) < count:
            count = len(found)
            if count == 1:  # Only 1 clock hand in the rectangle side
                minute = _find_furthest_number_between_lists(last_found, found)
                sec = found[0]
                break
            hour = _find_furthest_number_between_lists(last_found, found)
            if hour is not None:  # None means two clock hands overlap...
                # hour is in range [0..60) like minutes and seconds.
                # this scales it to a [0,12) scale as it should be.
                hour /= 5
            else:
                raise FailedToReadTimeException()

        last_found = found"""
    return time.strptime("{} {} {}".format(int(found[0]), int(found[1]), int(found[2])), "%H %M %S")
    if len(found[radii[0]]) == 3:
        hour = _find_furthest_number_between_lists(found[radii[0]], found[radii[1]])
        minute = _find_furthest_number_between_lists(found[radii[1]], found[radii[2]])
        sec = found[radii[2]][0]
    # There are two distinct values
    elif len(found[radii[0]]) == 2:
        # Hours is over the seconds
        if len(found[radii[1]]) == 2:
            minute = _find_furthest_number_between_lists(found[radii[1]], found[radii[2]])
            hour = sec = found[radii[2]][0]
        # Hours is over the minutes
        else:
            try:
                hour = minute = _find_furthest_number_between_lists(found[radii[0]], found[radii[2]])
                sec = found[radii[2]][0]
            except Exception:
                side_length = radii[2]
                sub_image = bw_img[
                            int((IMG_WIDTH + 40) / 2) - side_length:int((IMG_WIDTH + 40) / 2) + side_length,
                            int(IMG_HEIGHT / 2) - side_length:int(IMG_HEIGHT / 2) + side_length
                            ]
                plt.imshow(sub_image)
                plt.show()
                raise
    elif len(found[radii[0]]) == 1:
        hour = minute = sec = found[radii[2]][0]
    else:
        raise Exception()
    hour = round(hour / 5) % 12
    return time.strptime("{} {} {}".format(int(hour), int(minute), int(sec)), "%H %M %S")
