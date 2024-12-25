IMG_WIDTH = 500
# I assume the clock is symmetric
IMG_HEIGHT = IMG_WIDTH

# Image shape is used by cv2 and is in the form (num_of_rows, num_of_columns, num_of_channels)
IMG_SHAPE = (IMG_HEIGHT, IMG_WIDTH, 3)  # 3 channels for RGB
CLOCK_IMG_PATH = "clk_470x470.jpg"

# Hour, Minute, Second
CLK_HAND_RADII = [200 / 2, 200 / 1.3, 200]
CLK_HAND_COLORS = [(0, 0, 0), (0, 0, 0), (255, 0, 0)]
CLK_HAND_THICKNESS = [10, 10, 5]
