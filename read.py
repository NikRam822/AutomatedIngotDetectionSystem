import cv2 as cv
import os

def rescaleFrame(frame, scale=0.75):
    width = int(frame.shape[1] * scale)
    height = int(frame.shape[0] * scale)
    dimensions = (width,height)
    return cv.resize(frame,dimensions,interpolation=cv.INTER_AREA)

def cropImage(image,filename):
    height, width = image.shape[:2]

    # Calculate the coordinates for the center of the image and the dimensions of the rectangle
    center_x = width // 2
    center_y = height // 2
    rect_width = 900  # Adjust this to your desired width
    rect_height = 950  # Adjust this to your desired height

    # Calculate the coordinates of the top-left and bottom-right corners of the rectangle
    x1 = center_x - rect_width // 2
    y1 = (center_y - rect_height // 2) * 0.7
    x2 = center_x + rect_width // 2
    y2 = (center_y + rect_height // 2) - 50

    # Crop the rectangle from the image
    cropped_rectangle = image[int(y1):int(y2), int(x1):int(x2)]

    cv.imwrite('output/cropped_' + filename, cropped_rectangle)
    return cropped_rectangle

# img = cv.imread('photos/IMG-20221110-WA0028.jpg')
# _,filename = os.path.split('photos/IMG-20221110-WA0028.jpg')
# croppedImg = cropImage(img,filename)

# cv.imshow('Picture',img)
# cv.imshow('Resized ',croppedImg)
# cv.waitKey(0)



