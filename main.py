"""
This module will allow me to locally call functions as I develop
the program. It won't be a part of the program once it is done.
Perhaps I won't be very tidy in this module as it isnt part of the final program.
"""
import time

import cv2 as cv
import matplotlib.pyplot as plt

from clockHandler import generate_clock_image, read_the_time


def main():
    img = generate_clock_image(time.localtime(time.time()))
    img = read_the_time(img)
    #print("read: {}".format()
    #imshow(img)
    #plt.show()
    cv.imshow("Binary", img)
    cv.waitKey(0)


if __name__ == "__main__":
    main()
