import numpy as np
import cv2
from cv_utils import *
from filterColor import createMask, transformFromBGR

def gamma_correction(image, g):
    invGamma = 1.0/g
    table = np.array([((i/255.0)**invGamma)*255 for i in np.arange(0,256)]).astype("uint8")
    return cv2.LUT(image, table)

# Detect the plants in the image. Return a mask (black/white mask, where 0
# indicates no plants and 255 indicates plants)
def classifyFoliage(image):
    foliage_mask = np.zeros(image.shape[0:2], np.uint8)
    # Your code goes here:
    # Create a mask that has 255 where there is part of a plant in the image
    #   and 0 everywhere else
    # 24 73  108 255 30 207
    low_hsv = np.array([24, 108, 30])
    high_hsv = np.array([73,255,207])
    smoothed = cv2.medianBlur(image, 7)
    hsv_smoothed = transformFromBGR(smoothed, "HSV")
    foliage_mask = cv2.inRange(hsv_smoothed, low_hsv, high_hsv)
    
    return cv2.medianBlur(foliage_mask,7)

# Given the foliage mask (as would be returned from classifyFoliage), 
#   return the height in cms the tallest plant that crosses in front 
#   of the measuring stick. Return None if no foliage overlaps the stick
def measureHeight(foliage_mask):
    height = None
    # Your code goes here:
    # Find the maximum height of plants that overlap the measuring stick
    #   in the foliage_mask
    return height

# Use the color calibration squares to find a transformation that will
#   color-correct the image such that the mean values of the calibration
#   squares are the given "goal" colors.
# Return the color-corrected image
def colorCorrect(image, blue_goal, green_goal, red_goal):
    # Your code goes here:
    # Find a transform c' = T c, c is the pixel value in the image,
    #   c' is the transformed pixel, and T is the 3x3 transformation matrix
    # Do this by solving d = A x, as per the lecture notes.
    # Note that while the lecture notes describe an affine (3x4) transform,
    #  here we have only 3 colors, so it has to be a Euclidean (3x3) tranform
    rectangle_mask = np.zeros(image.shape[0:2], np.uint8)
    
    A = np.zeros((9, 9), np.float)
    red_mask = cv2.rectangle(rectangle_mask, (5,5), (50,50), (255,255,255), -1)
    green_mask = cv2.rectangle(rectangle_mask, (10,10), (20,20), (255,255,255), -1)
    # Your code goes here:
    # Fill in the rows of the matrix, according to the notes
        
    
    d = np.zeros((1,9))
    # Your code goes here:
    # Fill in the d vector with the "goal" colors 

    x = np.matmul(np.matmul(np.linalg.pinv(np.matmul(A.T, A)), A.T), d.T)
    T = x.reshape((3,3))

    corrected_image = image.copy()
    # Your code goes here:
    # Apply the transform to the pixels of the image and return the new image

    return corrected_image

def classifyFoliageCorrected(image):
    # You can use these as "ground truth" or substitute your own
    blue_goal =  [150, 75, 75]
    green_goal = [75, 150, 75]
    red_goal =   [75, 75, 150]

    # colorCorrect the image and then use classifyFoliage to
    corrected_image = colorCorrect(image, blue_goal, green_goal, red_goal)
    # detect the plants in the image
    # note that you will probably need to change the filter values to
    #   work well for the color-corrected images
    foliage_mask = classifyFoliage(corrected_image)
    return foliage_mask
