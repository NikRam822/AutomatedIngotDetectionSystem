"""
A set of utility functions that helps to preprocess image.
Looks like it should be moved to the image_analysis module.
"""
import cv2
import numpy as np

## TO STACK ALL THE IMAGES IN ONE WINDOW
def stack_images(img_array, scale, lables):
    """Stack images."""
    rows = len(img_array)
    cols = len(img_array[0])
    available_rows = isinstance(img_array[0], list)
    width = img_array[0][0].shape[1]
    height = img_array[0][0].shape[0]
    print("row available: "+str(available_rows))
    if available_rows:
        for x in range (0, rows):
            cols = len(img_array[x])
            for y in range(0, cols):
                print('x='+str(x)+'y='+str(y))
                img_array[x][y] = cv2.resize(img_array[x][y], (0, 0), None, scale, scale)
                if len(img_array[x][y].shape) == 2:
                    img_array[x][y] = cv2.cvtColor(img_array[x][y], cv2.COLOR_GRAY2BGR)

        image_blank = np.zeros((height, width, 3), np.uint8)
        hor = [image_blank] * rows
        hor_con = [image_blank] * rows

        for x in range(0, rows):
            hor[x] = np.hstack(img_array[x])
            hor_con[x] = np.concatenate(img_array[x])

            for image in img_array[x]:
                height, width, channels = image.shape
                print(f"Image {x}: Width = {width}, Height = {height}, Channels = {channels}")

        ver = np.vstack(hor)
        # ver_con = np.concatenate(hor)

    else:
        for x in range(0, rows):
            img_array[x] = cv2.resize(img_array[x], (0, 0), None, scale, scale)
            if len(img_array[x].shape) == 2:
                img_array[x] = cv2.cvtColor(img_array[x], cv2.COLOR_GRAY2BGR)

        hor= np.hstack(img_array)
        hor_con= np.concatenate(img_array)
        ver = hor

    if len(lables) != 0:
        each_img_width= int(ver.shape[1] / cols)
        each_img_height = int(ver.shape[0] / rows)
       # print(eachImgHeight)
        for d in range(0, rows):
            for c in range (0, cols):
                cv2.rectangle(
                    ver,
                    (c * each_img_width, each_img_height * d),
                    (c * each_img_width + len(lables[d][c]) * 13 + 27, 30 + each_img_height * d),
                    (255, 255, 255),
                    cv2.FILLED
                )
                cv2.putText(
                    ver,
                    lables[d][c],
                    (each_img_width * c + 10, each_img_height * d + 20),
                    cv2.FONT_HERSHEY_COMPLEX,
                    0.7,
                    (255, 0, 255),
                    2
                )
    return ver

def reorder(points):
    """Reorder points."""
    points = points.reshape((4, 2))
    new_points = np.zeros((4, 1, 2), dtype=np.int32)
    add = points.sum(1)

    new_points[0] = points[np.argmin(add)]
    new_points[3] = points[np.argmax(add)]
    diff = np.diff(points, axis=1)
    new_points[1] = points[np.argmin(diff)]
    new_points[2] = points[np.argmax(diff)]

    return new_points

def biggest_contour(contours):
    """Find the biggest contour"""
    biggest = np.array([])
    max_area = 0
    for i in contours:
        area = cv2.contourArea(i)
        if area > 5000:
            peri = cv2.arcLength(i, True)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True)
            if area > max_area and len(approx) == 4:
                biggest = approx
                max_area = area
    return biggest,max_area

def draw_rectangle(img, biggest, thickness):
    """Draw a rectangle over the biggest area"""
    cv2.line(img, (biggest[0][0][0], biggest[0][0][1]), (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[0][0][0], biggest[0][0][1]), (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[3][0][0], biggest[3][0][1]), (biggest[2][0][0], biggest[2][0][1]), (0, 255, 0), thickness)
    cv2.line(img, (biggest[3][0][0], biggest[3][0][1]), (biggest[1][0][0], biggest[1][0][1]), (0, 255, 0), thickness)
    return img

def _nothing(_):
    """Do nothing."""

def initialize_trackbars():
    """Initialize trackbars."""
    cv2.namedWindow("Trackbars")
    cv2.resizeWindow("Trackbars", 360, 240)
    cv2.createTrackbar("Threshold1", "Trackbars", 200, 255, _nothing)
    cv2.createTrackbar("Threshold2", "Trackbars", 200, 255, _nothing)

def val_trackbars():
    """Get trackbars"""
    threshold_1 = cv2.getTrackbarPos("Threshold1", "Trackbars")
    threshold_2 = cv2.getTrackbarPos("Threshold2", "Trackbars")
    src = threshold_1, threshold_2
    return src
