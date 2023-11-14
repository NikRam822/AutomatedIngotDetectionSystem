"""
The image preprocessing module.
It prepares the image for the AI.
"""
import os.path

import cv2
import numpy as np
import utlis

from decision import Decisions

def image_processing(path_image, save_dir):
    """Try to identify ingot on the image and transform it so the only ingot will be shown."""

    image_name = os.path.basename(path_image)
    img = cv2.imread(path_image)
    img_height, img_width, _ = img.shape

    try:
        img = cv2.resize(img, (img_width, img_height))  # RESIZE IMAGE
        # imgBlank = np.zeros((img_height, img_width, 3), np.uint8)  # CREATE A BLANK IMAGE FOR TESTING DEBUGING IF REQUIRED
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE
        img_blur = cv2.GaussianBlur(img_gray, (5, 5), 1)  # ADD GAUSSIAN BLUR
        # thres=utlis.valTrackbars() # GET TRACK BAR VALUES FOR THRESHOLDS

        img_threshold = cv2.Canny(img_blur, 180, 150)  # APPLY CANNY BLUR
        # imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        kernel = np.ones((5, 5))
        img_dial = cv2.dilate(img_threshold, kernel, iterations=2)  # APPLY DILATION
        img_threshold = cv2.erode(img_dial, kernel, iterations=1)  # APPLY EROSION

        ## FIND ALL COUNTOURS
        img_contours = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
        img_big_contour = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
        try:
            contours, _ = cv2.findContours(img_threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS
            cv2.drawContours(img_contours, contours, -1, (0, 255, 0), 10)  # DRAW ALL DETECTED CONTOURS

            # FIND THE BIGGEST COUNTOUR
            biggest, _ = utlis.biggest_contour(contours)  # FIND THE BIGGEST CONTOUR
            if biggest.size == 0:
                cv2.imwrite(save_dir + '/' + image_name, img)
                print("Blank images")
                return Decisions.no_ingot

            biggest = utlis.reorder(biggest)
            cv2.drawContours(img_big_contour, biggest, -1, (0, 255, 0), 20)  # DRAW THE BIGGEST CONTOUR
            img_big_contour = utlis.draw_rectangle(img_big_contour, biggest, 2)
            pts1 = np.float32(biggest)  # PREPARE POINTS FOR WARP
            pts2 = np.float32([[0, 0], [img_width, 0], [0, img_height], [img_width, img_height]])  # PREPARE POINTS FOR WARP
            matrix = cv2.getPerspectiveTransform(pts1, pts2)
            img_warp_colored = cv2.warpPerspective(img, matrix, (img_width, img_height))

            # REMOVE 20 PIXELS FORM EACH SIDE
            img_warp_colored = img_warp_colored[20:img_warp_colored.shape[0] - 20, 20:img_warp_colored.shape[1] - 20]
            img_warp_colored = cv2.resize(img_warp_colored, (img_width, img_height))

            # APPLY ADAPTIVE THRESHOLD
            img_warp_gray = cv2.cvtColor(img_warp_colored, cv2.COLOR_BGR2GRAY)
            img_adaptive_thre = cv2.adaptiveThreshold(img_warp_gray, 255, 1, 1, 7, 2)
            img_adaptive_thre = cv2.bitwise_not(img_adaptive_thre)
            img_adaptive_thre = cv2.medianBlur(img_adaptive_thre, 3)

            cv2.imwrite(save_dir + '/' + image_name, img_warp_colored)
            print("Image Saved")
            return Decisions.ok

        except Exception:
            cv2.imwrite(save_dir + '/' + image_name, img)
            print("Error during contour processing")
            return Decisions.bad_image

    except Exception:
        cv2.imwrite(save_dir + '/' + image_name, img)
        print("Error in image_processing function")
        return Decisions.bad_image
