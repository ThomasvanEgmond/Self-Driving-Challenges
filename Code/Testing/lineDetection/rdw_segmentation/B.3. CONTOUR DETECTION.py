import numpy as np
from scipy.signal import convolve2d
import cv2

# Load sample data
# image = cv2.imread(r"D:/SDC/SDC_codes/right_copy/16830097790672958.png")
image = cv2.imread("Afbeelding3.png")

# convert to grayscale
gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

# create a binary thresholded image
_, binary = cv2.threshold(gray, 225, 255, cv2.THRESH_BINARY_INV)

# find the contours from the thresholded image: try out different methods eg: retr_tree -> retr_external
contours, hierarchy = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# draw all contours: -1 signifies drawing all contours; (26,189,255) is a contour colour, change that if you wish
image = cv2.drawContours(image, contours, -1, (26, 189, 255), 2)

cv2.imshow("contour", image)  # show new file
# cv2.imwrite("contour_det.png", image)  # creates new file
cv2.waitKey()
