# Note - choosing an IMG width to small compared to the hand radii will
#        result in the code not working, as we need to be able to have different
#        rectangles around the clock center in which different handles fit in,
#        without the clock itself (numbers etc) appearing in it.
from enum import Enum

IMG_WIDTH = 800
# I assume the clock is symmetric
IMG_HEIGHT = IMG_WIDTH

# Image shape is used by cv2 and is in the form (num_of_rows, num_of_columns, num_of_channels)
IMG_SHAPE = (IMG_HEIGHT, IMG_WIDTH, 3)  # 3 channels for RGB
CLOCK_IMG_PATH = "clk_470x470.jpg"

class ExtendedEnum(Enum):
    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


# Hour, Minute, Second
# Note for the reviewer: The clock hands are short because
# I do not want them to overlap with numbers on the clock.
class HandRadii(ExtendedEnum):
    SECONDS = 180
    MINS = 130
    HOURS = 80


#CLK_HAND_RADII = [180, 130, 80]
# NOTE for the reviewer:
# I initially tried having all the clock hands be black, as i believed it was
# more challenging and therefore more impressive. After some failures to read
# the time like that i realised my problem was that sometimes the shorter clock
# hand would be hidden under another longer clock hand, and in such cases
# it was impossible in some cases to tell the time accurately (you would
# have to guess under which hand the hidden hand is). This problem
# has many possible solutions, but given that I the task seemed to take longer
# than I had hoped I decided on the simpler solution. Had I understood this problem
# earlier I would have consulted you about this before choosing this (simpler) solution.
# If i were to make the longer clock hand the different color,
# I couldve made it overlap with the numbers, resulting in a more
# aesthetic clock.
CLK_HAND_COLORS = [(0, 0, 0),(0, 0, 0),(0, 0, 255)]
CLK_BACKGROUND_COLOR = [255, 255, 255]
CLK_HAND_THICKNESS = [10, 15, 15]