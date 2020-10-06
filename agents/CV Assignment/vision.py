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

    #square: [[1959,279],[2030,301],[1945,2051],[1867,2046]]
    #rgb ranges: bmin = 186, gmin = 177, rmin = 164
    #tick_ranges_res = [[1988, 2029], [1841, 1880], [1707, 1741], [1542, 1571], [1370, 1398], [1180, 1224], [999, 1031],
                     #  [802, 838], [577, 606], [347, 372]]


    #create mask for measuring stick
    og_img = 255 - readImage('images/day02_test.jpg')

    if (foliage_mask.shape != og_img.shape):
        foliage_mask = cv2.resize(foliage_mask, (og_img.shape[1], og_img.shape[0]))

    stick_mask_bg = np.zeros(og_img.shape, np.uint8)
    stick_countour = np.array([[1965,279],[2030,301],[1945,2051],[1872,2046]])
    white_stick_black_bg_mask = cv2.drawContours(stick_mask_bg, [stick_countour], -1, (255,255,255), -1)
    writeImage('images/day02_white_stick_black_bg_mask.jpg', white_stick_black_bg_mask)
    # stick_black_bg = cv2.bitwise_and(og_img, white_stick_black_bg_mask, stick_mask_bg, None)
    # writeImage('images/day02_stick_black_bg.jpg', stick_black_bg)

    #extract lines
    # low_rgb = np.array([186, 177, 164])
    # high_rgb = np.array([255,255,255])
    # lines_mask = cv2.medianBlur(cv2.inRange(stick_black_bg, low_rgb, high_rgb), 7)
    # writeImage('images/day02_lines_mask.jpg', lines_mask)

    #getting line ranges
    # lines_mask1col = np.max(lines_mask, axis=1)
    # print("lines mask: ", np.sum(lines_mask1col), lines_mask1col.shape, np.max(lines_mask1col))
    # currTick = 0
    # tick_ranges = []
    # row = 0
    # while row < lines_mask1col.shape[0]:
    #     start_white = 0
    #     end_white = 0
    #     if lines_mask1col[row] == 255:
    #         print("hi")
    #         start_white = row
    #         while lines_mask1col[row] == 255:
    #             row +=1
    #         end_white = row
    #     if (end_white - start_white > 20):
    #         tick_ranges.append([start_white, end_white])
    #         currTick +=1
    #     row += 1

    # print(tick_ranges)

    tick_ranges_res = [[1988, 2029], [1841, 1880], [1707, 1741], [1542, 1571], [1370, 1398], [1180, 1224], [999, 1031],
                       [802, 838], [577, 606], [347, 372]]

    white_stick_black_bg_mask_2d = white_stick_black_bg_mask[:,:,0]
    #print((white_stick_black_bg_mask_2d).shape, foliage_mask.shape)
    and_img = np.zeros(foliage_mask.shape, np.uint8)
    res_and_img = cv2.bitwise_and(white_stick_black_bg_mask_2d, foliage_mask, and_img, None)
    writeImage('images/day02_lines_only.jpg', white_stick_black_bg_mask_2d)
    writeImage('images/day02_foliage_only.jpg', foliage_mask)
    writeImage('images/day02_lines_and_foliage.jpg', res_and_img)

    res_and_img_1col = np.max(res_and_img, axis=1)
    max_height_row = 0.0
    for row in range(res_and_img_1col.shape[0]):
        if res_and_img_1col[row] == 255:
            max_height_row = row
            break

    final_height = None
    for i in range(len(tick_ranges_res) - 1):
        currTick = tick_ranges_res[i]
        nextTick = tick_ranges_res[i+1]
        if max_height_row >= currTick[0] and max_height_row <= currTick[1]:
            final_height = i
            break
        elif max_height_row > nextTick[1] and max_height_row < currTick[0]:
            frac = (float)(max_height_row - nextTick[1]) / (currTick[0] - nextTick[1])
            final_height = i + frac
            break

    if max_height_row >= tick_ranges_res[9][0] and max_height_row <= tick_ranges_res[9][1]:
        final_height = 9

    print("max_height_row: ", max_height_row)

    return final_height

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
    blue_mask = cv2.rectangle(rectangle_mask, (10,10), (20,20), (255,255,255), -1)
    
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
