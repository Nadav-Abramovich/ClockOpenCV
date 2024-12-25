"""
This module will allow me to locally call functions as I develop
the program. It won't be a part of the program once it is done.
Perhaps I won't be very tidy in this module as it isnt part of the final program.
"""
import time

import matplotlib.pyplot as plt

from clockGeneration import generate_clock_image
from clockReading import read_the_time


def main():
    img = generate_clock_image(time.localtime(time.time()))
    read_time = read_the_time(img)
    print("read: {}".format(read_time))
    plt.imshow(img)
    plt.show()


if __name__ == "__main__":
    main()
