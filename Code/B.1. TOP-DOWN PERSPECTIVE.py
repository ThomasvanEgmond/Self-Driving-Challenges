import cv2
import numpy as np

# load data
im = cv2.imread("C:/Users/.../WIN_20230720_16_43_09_Pro.jpg")
img = im.copy()  # creates a copy of the image
height, width, _ = img.shape  # size of the image

# extract some more information about test image
test = cv2.imread("D:/SDC/SDC_codes/front_copy/16830093117081308000.png")
heightt, widtht, _ = test.shape
resized_img = cv2.resize(test, (width, height), interpolation=cv2.INTER_LINEAR)  # resize image

# vertical lines
cv2.line(img, (int(3/8*width)-12, 0), (int(3/8*width)-12, height), (0, 255, 0), 3)
cv2.line(img, (int(width/2)+20, 0), (int(width/2)+20, height), (0, 255, 0), 3)
cv2.line(img, (int(5/8*width), 0), (int(5/8*width), height), (0, 255, 0), 3)
cv2.line(img, (int(11/16*width)-14, 0), (int(11/16*width)-14, height), (0, 255, 0), 3)
cv2.line(img, (int(6/8*width)-20, 0), (int(6/8*width)-20, height), (0, 255, 0), 3)

# horizontal lines
cv2.line(img, (0, int(height/2)+20), (width, int(height/2)+20), (255, 0, 0), 3)
cv2.line(img, (0, int(9*height/16)-6), (width, int(9*height/16)-6), (255, 0, 0), 3)
cv2.line(img, (0, int(19*height/32)+3), (width, int(19*height/32)+3), (255, 0, 0), 3)
cv2.line(img, (0, int(10*height/16)-10), (width, int(10*height/16)-10), (255, 0, 0), 3)
cv2.line(img, (0, int(3*height/4)-20), (width, int(3*height/4)-20), (255, 0, 0), 3)
cv2.line(img, (0, int(13*height/16)+5), (width, int(13*height/16)+5), (255, 0, 0), 3)

# final points
cv2.circle(img, (int(width/2)+20, int(height/2)+20), 2, (0, 0, 255), -1)  # A
cv2.circle(img, (int(6*width/8)-20, int(height/2)+20), 2, (0, 0, 255), -1)  # B
cv2.circle(img, (int(width/2)+20, int(9*height/16)-6), 2, (0, 0, 255), -1)  # C
cv2.circle(img, (int(3/8*width)-12, int(19*height/32)+3), 2, (0, 0, 255), -1)  # D
cv2.circle(img, (int(11*width/16)-14, int(10*height/16)-10), 2, (0, 0, 255), -1)  # E

cv2.imshow('img', img)  # shows the image on the screen
# cv2.imwrite('lines.png', img)  # saves the image in the current folder

# points to map; im: on the image, coordinates in pixels; re: in real life, coordinates in meters
p1_im = (int(width/2)+20, int(height/2)+20)
p2_im = (int(6*width/8)-20, int(height/2)+20)
p3_im = (int(width/2)+20, int(9*height/16)-6)
p4_im = (int(3/8*width)-12, int(19*height/32)+3)  # later is disregarded
p5_im = (int(11*width/16)-14, int(10*height/16)-10)

src_points = np.array([p1_im, p2_im, p3_im, p5_im], dtype=np.float32)  # collect 4 source points in an array

# desired size of the destination image
x_sh = 640
y_sh = 800

# see ~ 2 meters ahead and ~ 1 meter to each side
p1_re = (int(x_sh/2), 0)
p2_re = (int(x_sh), 0)
p3_re = (int(x_sh/2), int(y_sh/4))
p4_re = (int(x_sh/4), int(y_sh/2))  # disregarded point
p5_re = (int(3*x_sh/4), int(y_sh/2))

dst_points = np.array([p1_re, p2_re, p3_re, p5_re], dtype=np.float32)  # collect 4 destination points in an array

M1 = cv2.getPerspectiveTransform(src_points, dst_points)  # get the mapping from source to destination points
birds = cv2.warpPerspective(im, M1, (x_sh, y_sh))  # top-down perspective for image with tapes in front of kart
test_cl = cv2.warpPerspective(resized_img, M1, (x_sh, y_sh))  # top-down perspective for test image

cv2.imshow('close', birds)
# cv2.imwrite('close.png', birds)

cv2.imshow('close_t', test_cl)
# cv2.imwrite('close_t.png', test_cl)

# see ~3 meters ahead and ~1.5 meters to each side
p1_re = (int(x_sh/2), int(y_sh/2))
p2_re = (int(3/4*x_sh), int(y_sh/2))
p3_re = (int(x_sh/2), int(5*y_sh/8))
p4_re = (int(3/8*x_sh), int(3/4*y_sh))  # disregard
p5_re = (int(5*x_sh/8), int(3/4*y_sh))

dst_points = np.array([p1_re, p2_re, p3_re, p5_re], dtype=np.float32)

M2 = cv2.getPerspectiveTransform(src_points, dst_points)
birds2 = cv2.warpPerspective(im, M2, (x_sh, y_sh))
test_bf = cv2.warpPerspective(resized_img, M2, (x_sh, y_sh))

cv2.imshow('bit_further', birds2)
# cv2.imwrite('bit_further.png', birds2)

cv2.imshow('bit_further_t', test_bf)
# cv2.imwrite('bit_further_t.png', test_bf)

# with side lines visible
p1_re = (320, 700)
p2_re = (360, 700)
p3_re = (320, 725)
p4_re = (300, 750)  # disregard
p5_re = (340, 750)

dst_points = np.array([p1_re, p2_re, p3_re, p5_re], dtype=np.float32)

M2 = cv2.getPerspectiveTransform(src_points, dst_points)
birds2 = cv2.warpPerspective(im, M2, (x_sh, y_sh))

cv2.imshow('and_a_bit_further', birds2)
# cv2.imwrite('and_a_bit_further.png', birds2)

test_tr = cv2.warpPerspective(resized_img, M2, (x_sh, y_sh))

cv2.imshow('test', test_tr)
# cv2.imwrite('test.png', test_tr)

cv2.waitKey()  # the pictures that appear on the screen will not disappear until 'x' is clicked
