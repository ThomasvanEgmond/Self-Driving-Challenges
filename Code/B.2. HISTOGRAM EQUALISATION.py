import cv2
import matplotlib.pyplot as plt
import numpy as np

def to_gray(image):
    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray

def histogram_equalization(image):
    # Apply histogram equalization
    equalized = cv2.equalizeHist(image)
    return equalized

# image = cv2.imread("D:/Internship_RDW/16830097790672958.png")
image = cv2.imread("Afbeelding4.png")
print(image.shape)
gray = to_gray(image)
cv2.imshow('Grayscale Image', gray)
# cv2.imwrite('gray_hist.png', gray)

equalized = histogram_equalization(gray)
print(equalized.shape)
cv2.imshow('Equalized Image', equalized)
# cv2.imwrite('equa_hist.png', equalized)

# Calculate histograms
gray_hist, gray_bins = np.histogram(gray.ravel(), bins=16, range=[0, 256])
equalized_hist, equalized_bins = np.histogram(equalized.ravel(), bins=16, range=[0, 256])

# Plot histograms - for advice document
plt.figure(figsize=(5, 5))
plt.bar(gray_bins[:-1], gray_hist, width=np.diff(gray_bins), color='#FCBD1A', edgecolor='#F1AE04')
plt.title('Grayscale Histogram')
plt.xlabel('Pixel Value')
plt.ylabel('Frequency')
plt.xlim([0, 256])
plt.ylim([0, np.max([np.max(gray_hist), np.max(equalized_hist)])])

plt.figure(figsize=(5, 5))
plt.bar(equalized_bins[:-1], equalized_hist, width=np.diff(equalized_bins), color='#FCBD1A', edgecolor='#F1AE04')
plt.title('Equalized Histogram')
plt.xlabel('Pixel Value')
plt.ylabel('Frequency')
plt.xlim([0, 256])
plt.ylim([0, np.max([np.max(gray_hist), np.max(equalized_hist)])])

plt.show()

cv2.waitKey(0)
