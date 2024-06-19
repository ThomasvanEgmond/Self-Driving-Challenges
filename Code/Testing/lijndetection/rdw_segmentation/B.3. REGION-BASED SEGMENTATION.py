import cv2
import numpy as np
from IPython.display import display, Image
from matplotlib import pyplot as plt

# load data
# img = cv2.imread("D:/SDC/SDC_codes/right_copyyy/16830097160279615.png")
img = cv2.imread("Afbeelding3.png")

# change to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# set up thresholds, cv2.thresh_binary_inv + cv2.thresh_otsu can be replaced with other methods
ret, bin_img = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

# kernel (3,3) can be smaller or bigger, try out whatever works best (need not be symmetric), it has to do with region that is being considered
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

# one can change amount of iterations for better results
bin_img = cv2.morphologyEx(bin_img, cv2.MORPH_OPEN, kernel, iterations=2)

# below we separate the image into background and foreground
sure_bg = cv2.dilate(bin_img, kernel, iterations=3)  # sure background
dist = cv2.distanceTransform(bin_img, cv2.DIST_L2, 5)  # distance transform
ret, sure_fg = cv2.threshold(dist, 0.5 * dist.max(), 255, cv2.THRESH_BINARY)  # sure foreground
sure_fg = sure_fg.astype(np.uint8)
unknown = cv2.subtract(sure_bg, sure_fg)  # unknown part

ret, markers = cv2.connectedComponents(sure_fg)
markers += 1
markers[unknown == 255] = 0

markers = cv2.watershed(img, markers)

# here we plot these
fig, ax = plt.subplots(figsize=(5, 5))
ax.imshow(markers, cmap="tab20b")
ax.axis('off')
plt.show()

labels = np.unique(markers)

coins = []
for label in labels[2:]:
    # Create a binary image in which only the area of the label is in the foreground and the rest of the image is in the background
    target = np.where(markers == label, 255, 0).astype(np.uint8)

    # Perform contour extraction on the created binary image
    contours, hierarchy = cv2.findContours(target, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    coins.append(contours[0])

# this gives final result on the original image
img = cv2.drawContours(img, coins, -1, color=(26, 189, 255), thickness=2)
cv2.imshow("region_seg", img)
# cv2.imwrite(
