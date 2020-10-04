#!/usr/bin/env python
import sys
import cv2
import numpy as np
from cv_utils import readImage, readMask
from vision import classifyFoliage, measureHeight, colorCorrect, classifyFoliageCorrected

test_days = ["day02", "day04", "day05", "day08", "day10"]
height_ranges = {"day02": None, "day04": None, "day05": [2.3, 2.8],
                 "day08": [3.7, 4.0], "day10": [5.0, 5.3]}
blue_goal = [150, 75, 75]
green_goal = [75, 150, 75]
red_goal = [75, 75, 150]

def checkFoliage(test, foliage_mask, groundtruth):
    if (foliage_mask.shape != groundtruth.shape):
        print("Foliage mask wrong shape: Is %s, should be %s" 
              %(foliage_mask.shape, groundtruth.shape))
        return 0

    pixels = groundtruth.shape[0]*groundtruth.shape[1]
    positives = cv2.countNonZero(groundtruth)
    negatives = pixels - positives
    selected = cv2.countNonZero(foliage_mask)
    
    TP = float(cv2.countNonZero(cv2.bitwise_and(groundtruth, foliage_mask)))
    FP = selected - TP
    TN = negatives - FP
    FN = positives - TP

    precision = (0 if selected == 0 else TP/selected)
    recall = TP/positives
    bal_accuracy = ((TP/positives) + (TN/negatives))/2
    b_sq = 1
    F1 = (1 + b_sq)*TP/(((1+b_sq)*TP) + (b_sq*FN) + FP)
    print("%s: Recall: %d%%, Precision: %d%%, Balanced Accuracy: %d%%, F1: %.2f"
          %(test, int(recall*100), int(precision*100), int(bal_accuracy*100), F1))
    return bal_accuracy

def checkHeight(test, height):
    global height_ranges

    groundtruth = height_ranges[test]
    print("%s: Detected height: %s; Measured range: %s"
          %(test, ("no overlap detected" if height == None else height),
            ("no overlap" if groundtruth == None else groundtruth)))
    return (height == None if (groundtruth == None) else
            groundtruth[0] <= height and height <= groundtruth[1])

# Compare two BGR colors.  First tried using cosine similarity, but it
#  did not differentiate colors by enough, so ended up using the ratio
#  of corrected to goal colors
def comp_colors(color, goal):
    comp = np.sum([v if v < 1 else 2-v for v in np.divide(color, goal)])/3
    return comp

def inta(l): return [int(v) for v in l]

def checkCorrection(test, image, blue_goal, green_goal, red_goal,
                    blue_mask, green_mask, red_mask):
    blue_calib = cv2.mean(image, blue_mask)[:-1]
    green_calib = cv2.mean(image, green_mask)[:-1]
    red_calib = cv2.mean(image, red_mask)[:-1]

    blue_comp = comp_colors(blue_calib, blue_goal)
    green_comp = comp_colors(green_calib, green_goal)
    red_comp = comp_colors(red_calib, red_goal)

    print("%s: B: %s (%.2f); G: %s (%.2f); R: %s (%.2f)"
          %(test, inta(blue_calib), blue_comp, inta(green_calib), green_comp,
            inta(red_calib), red_comp))
    return (blue_comp + green_comp + red_comp)/3


if (len(sys.argv) == 1 or '-p1' == sys.argv[1]):
    print("Part 1: Classify Foliage")
    numTests = 0; grade = 0.
    for test in test_days:
        if (len(sys.argv) < 3 or sys.argv[2] == test):
            image = readImage("images/"+test+".jpg")
            mask = classifyFoliage(image)
            groundtruth = readMask("autograder_files/mask_"+test+".jpg")
            grade += checkFoliage(test, mask, groundtruth)
            numTests += 1
    grade = 100*grade/numTests
    # Curve grade so that 80% => 100% and 50% (doing nothing) => 50%
    curved = (5*grade - 100)/3.
    print("Part 1 Score: %.1f%% (raw: %.1f%%)" %(curved, grade))

if (len(sys.argv) == 1 or '-p2' == sys.argv[1]):
    print("Part 2: Measure Plants")
    numTests = 0; grade = 0.
    for test in test_days:
        if (len(sys.argv) < 3 or sys.argv[2] == test):
            foliage_mask = readMask("autograder_files/mask_"+test+".jpg")
            height = measureHeight(foliage_mask)
            grade += checkHeight(test, height)
            numTests += 1
    print("Part 2 Score: %.1f%%" %(100*grade/numTests))

if (len(sys.argv) == 1 or '-p3' == sys.argv[1]):
    print("Part 3: Correct Color")
    
    print("  Goal colors: B: %s; G: %s; R: %s"
          %(inta(blue_goal), inta(green_goal), inta(red_goal)))

    numTests = 0; grade = 0.
    blue_mask = readMask("autograder_files/blue_mask.jpg")
    green_mask = readMask("autograder_files/green_mask.jpg")
    red_mask = readMask("autograder_files/red_mask.jpg")
    for test in test_days:
        if (len(sys.argv) < 3 or sys.argv[2] == test):
            # Check whether the means of the color calibration squares
            #   are approximately equal to the goal colors
            image = readImage("images/"+test+".jpg")
            corrected_image = colorCorrect(image, blue_goal, green_goal,
                                           red_goal)
            grade += checkCorrection(test, corrected_image,
                                     blue_goal, green_goal, red_goal,
                                     blue_mask, green_mask, red_mask)
            numTests += 1
    print("Part 3 Score: %.1f%%" %(100*grade/numTests))

if (len(sys.argv) == 1 or '-p4' == sys.argv[1]):
    print("Part 4: Classify Plants using Color-Corrected Images")
    numTests = 0; grade = 0.
    for test in test_days:
        if (len(sys.argv) < 3 or sys.argv[2] == test):
            image = readImage("images/"+test+".jpg")
            mask = classifyFoliageCorrected(image)
            groundtruth = readMask("autograder_files/mask_"+test+".jpg")
            grade += checkFoliage(test, mask, groundtruth)
            numTests += 1
    grade = 100*grade/numTests
    # Curve grade so that 85% => 100% and 50% (doing nothing) => 50%
    curved = (10*grade - 150)/7.
    print("Part 4 Score: %.1f%% (raw: %.1f%%)" %(curved, grade))
