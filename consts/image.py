# Note - choosing an IMG width to small compared to the hand radii will
#        result in the code not working, as we need to be able to have different
#        rectangles around the clock center in which different handles fit in,
#        without the clock itself (numbers etc) appearing in it.
IMG_WIDTH = 800
# I assume the clock is symmetric
IMG_HEIGHT = IMG_WIDTH

# Image shape is used by cv2 and is in the form (num_of_rows, num_of_columns, num_of_channels)
IMG_SHAPE = (IMG_HEIGHT, IMG_WIDTH, 3)  # 3 channels for RGB
CLOCK_IMG_PATH = "clk_470x470.jpg"

# Hour, Minute, Second
CLK_HAND_RADII = [180, 130, 80]
CLK_HAND_COLORS = [(0, 0, 0),(0, 0, 0),(0, 0, 255)]
CLK_BACKGROUND_COLOR = [255, 255, 255]
CLK_HAND_THICKNESS = [20, 30, 30]
CLK_HAND_THICKNESS = [10, 15, 15]

WHITE_HALO_COLOR = (255, 255, 255)
