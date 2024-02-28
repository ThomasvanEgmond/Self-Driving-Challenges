import numpy as np
import cv2 as cv
from skimage import io, img_as_float

# load data
# frame = cv.imread(r"D:/SDC/SDC_codes/right_copy/16830097790672958.png")  # name picture
frame = cv.imread("equa_hist.png")

# blurr the image and then turn into greyscale
kernel_size = 7
blur = cv.GaussianBlur(frame, (kernel_size, kernel_size), 0)
grey = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)

# lower and upper bound for detecting white: play around with lower bound
lower_white = 190
upper_white = 255
white = cv.inRange(grey, lower_white, upper_white)  # filters only white
cv.imshow("only white", white)  # shows new file

# process edge detection, use Canny
low_threshold = 50
high_threshold = 400
edges = cv.Canny(white, low_threshold, high_threshold)

cv.imshow("edge_det", edges)  # show new file
cv.imwrite("edge_det.png", edges)  # creates new file

cv.waitKey()
