import os.path

import cv2
import numpy as np
import utlis

from decision import Decisions

def image_processing(pathImage, saveDir):
    imageName = os.path.basename(pathImage)
    img = cv2.imread(pathImage)
    heightImg, widthImg, _ = img.shape

    try:
        img = cv2.resize(img, (widthImg, heightImg))  # RESIZE IMAGE
        imgBlank = np.zeros((heightImg, widthImg, 3), np.uint8)  # CREATE A BLANK IMAGE FOR TESTING DEBUGING IF REQUIRED
        imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # CONVERT IMAGE TO GRAY SCALE
        imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)  # ADD GAUSSIAN BLUR
        # thres=utlis.valTrackbars() # GET TRACK BAR VALUES FOR THRESHOLDS

        imgThreshold = cv2.Canny(imgBlur, 180, 150)  # APPLY CANNY BLUR
        # imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 11, 2)
        kernel = np.ones((5, 5))
        imgDial = cv2.dilate(imgThreshold, kernel, iterations=2)  # APPLY DILATION
        imgThreshold = cv2.erode(imgDial, kernel, iterations=1)  # APPLY EROSION

        ## FIND ALL COUNTOURS
        imgContours = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
        imgBigContour = img.copy()  # COPY IMAGE FOR DISPLAY PURPOSES
        try:
            contours, hierarchy = cv2.findContours(imgThreshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)  # FIND ALL CONTOURS
            cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 10)  # DRAW ALL DETECTED CONTOURS

            # FIND THE BIGGEST COUNTOUR
            biggest, maxArea = utlis.biggestContour(contours)  # FIND THE BIGGEST CONTOUR
            if biggest.size != 0:
                biggest = utlis.reorder(biggest)
                cv2.drawContours(imgBigContour, biggest, -1, (0, 255, 0), 20)  # DRAW THE BIGGEST CONTOUR
                imgBigContour = utlis.drawRectangle(imgBigContour, biggest, 2)
                pts1 = np.float32(biggest)  # PREPARE POINTS FOR WARP
                pts2 = np.float32([[0, 0], [widthImg, 0], [0, heightImg], [widthImg, heightImg]])  # PREPARE POINTS FOR WARP
                matrix = cv2.getPerspectiveTransform(pts1, pts2)
                imgWarpColored = cv2.warpPerspective(img, matrix, (widthImg, heightImg))

                # REMOVE 20 PIXELS FORM EACH SIDE
                imgWarpColored = imgWarpColored[20:imgWarpColored.shape[0] - 20, 20:imgWarpColored.shape[1] - 20]
                imgWarpColored = cv2.resize(imgWarpColored, (widthImg, heightImg))

                # APPLY ADAPTIVE THRESHOLD
                imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
                imgAdaptiveThre = cv2.adaptiveThreshold(imgWarpGray, 255, 1, 1, 7, 2)
                imgAdaptiveThre = cv2.bitwise_not(imgAdaptiveThre)
                imgAdaptiveThre = cv2.medianBlur(imgAdaptiveThre, 3)

                cv2.imwrite(saveDir + "/"+imageName, imgWarpColored)
                print("Image Saved")
                return Decisions.ok

            else:
                cv2.imwrite(saveDir + "/"+imageName, img)
                print("Blank images")
                return Decisions.no_ingot

        except Exception:
                cv2.imwrite(saveDir + "/" + imageName, img)
                print("Error during contour processing")
                return Decisions.bad_image

    except Exception:
            cv2.imwrite(saveDir + "/" + imageName, img)
            print("Error in image_processing function")
            return Decisions.bad_image

