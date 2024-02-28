import cv2
import numpy as np
from sklearn.cluster import KMeans

# load data
# img = cv2.imread(r"D:/SDC/SDC_codes/right_copy/16830097790672958.png")
img = cv2.imread("Afbeelding3.png")
vectorized = img.reshape((-1, 3))

# k-means part, change n_clusters for better results
kmeans = KMeans(n_clusters=5, random_state=0, n_init=5).fit(vectorized)
centers = np.uint8(kmeans.cluster_centers_)
segmented_data = centers[kmeans.labels_.flatten()]

segmented_image = segmented_data.reshape(img.shape)

cv2.imshow("cluster_seg", segmented_image)  # show new file
# cv2.imwrite("cluster_seg.png", segmented_image)  # creates a new file
cv2.waitKey()
