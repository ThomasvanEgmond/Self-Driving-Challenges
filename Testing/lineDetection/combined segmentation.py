import numpy as np
import cv2 as cv
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt

def histogramEqualization(img):
    # Convert the img to grayscale
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Apply histogram equalization
    equalized = cv.equalizeHist(gray)
    # Convert the equalized img back to BGR
    equalized_bgr = cv.cvtColor(equalized, cv.COLOR_GRAY2BGR)
    return equalized_bgr

def detectLines(frame):
    # Blurr the img and then turn it into greyscale
    kernel_size = 7
    blur = cv.GaussianBlur(frame, (kernel_size, kernel_size), 0)
    grey = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)
 
    # Lower and upper bound for detecting white
    lower_white = 190
    upper_white = 255
    white = cv.inRange(grey, lower_white, upper_white)  # filters only white
 
    # Process edge detection, use Canny
    low_threshold = 50
    high_threshold = 400
    edges = cv.Canny(white, low_threshold, high_threshold)
    return edges

def clusteringSegmentation(img):
    vectorized = img.reshape((-1, 3))

    # k-means part, change n_clusters for better results
    kmeans = KMeans(n_clusters=5, random_state=0, n_init=5).fit(vectorized)
    centers = np.uint8(kmeans.cluster_centers_)
    segmented_data = centers[kmeans.labels_.flatten()]

    return segmented_data.reshape(img.shape)

def graphSegmentation(img):
    # create a simple mask img similar to the loaded img, with the shape and return type
    mask = np.zeros(img.shape[:2], np.uint8)

    # specify the background and foreground model using numpy the array is constructed of 1 row and 65
    # columns, and all array elements are 0. Data type for the array is np.float64 (default)
    backgroundModel = np.zeros((1, 65), np.float64)
    foregroundModel = np.zeros((1, 65), np.float64)

    # define the Region of Interest (ROI) as the coordinates of the rectangle where the values are entered
    # as (startingPoint_x, startingPoint_y, width, height) these coordinates are according to the input
    # img it may vary for different imgs
    rectangle = (0, 100, 643, 263) # Afb3: (70, 0, 643, 200) (0, 100, 643, 263) Afb4: (100, 100, 760, 512)

    # apply the grabcut algorithm with appropriate values as parameters, number of iterations = 3
    # cv.GC_INIT_WITH_RECT is used because of the rectangle mode is used
    cv.grabCut(img, mask, rectangle, backgroundModel, foregroundModel, 3, cv.GC_INIT_WITH_RECT)

    # In the new mask img, pixels will be marked with four flags four flags denote the background /
    # foreground mask is changed, all the 0 and 2 pixels are converted to the background mask is changed,
    # all the 1 and 3 pixels are now the part of the foreground the return type is also mentioned, this
    # gives us the final mask
    mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')

    # The final mask is multiplied with the input img to give the segmented img.
    img = img * mask2[:, :, np.newaxis]

    # output segmented img with colorbar
    plt.imshow(cv.cvtColor(img, cv.COLOR_BGR2RGB))
    plt.colorbar()
    return img

def contourDetection(img):
    # convert to grayscale
    gray = cv.cvtColor(img, cv.COLOR_RGB2GRAY)

    # create a binary thresholded img
    _, binary = cv.threshold(gray, 225, 255, cv.THRESH_BINARY_INV)

    # find the contours from the thresholded img: try out different methods eg: retr_tree -> retr_external
    contours, hierarchy = cv.findContours(binary, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    # draw all contours: -1 signifies drawing all contours; (26,189,255) is a contour colour, change that if you wish
    img = cv.drawContours(img, contours, -1, (26, 189, 255), 2)
    return img

def main():
    frame = cv.imread("Afbeelding3.png")

    # Display frame
    # cv.imshow('clus_hist', histogram_equalization(clusteringSegmentation(frame)))
    # cv.imshow('hist_clus', clusteringSegmentation(histogram_equalization(frame)))
    # cv.imshow('clus_line', detect_lines(clusteringSegmentation(frame)))
    # cv.imshow('hist_line', detect_lines(histogram_equalization(frame)))
    # cv.imshow('line', detectLines(frame))
    # cv.imshow('graph', histogramEqualization(graphSegmentation(frame)))
    cv.imshow('clust', clusteringSegmentation(frame))
    cv.imshow('contour', contourDetection(frame))
    # cv.imshow('hist', histogramEqualization(frame))

    # cv.imwrite("newFrame.png", newFrame)  # creates new file
    
    cv.waitKey()
 
 
if __name__ == "__main__":
    main()
