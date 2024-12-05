from email.mime import image
from pickle import GLOBAL
from tkinter import Image
import cv2
from re import L
import time
from PIL import Image
from matplotlib import pyplot as plt
import numpy as np
import pytesseract
import os
import asyncio
#pytesseract.pytesseract.tesseract_cmd = "C:/Users/mfouc/AppData/Local/Programs/Tesseract-OCR/tesseract"
pytesseract.pytesseract.tesseract_cmd = "/opt/local/bin/tesseract"
grid = [
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0],
        [0,0,0,0,0,0,0,0,0]
]
pst1 = []
image = cv2.imread("/Users/matthieufoucu/Documents/pics/skewed.png")
print('Original Dimensions : ', image.shape)

def resizeOG(image):
    while image.shape[0] > 1300 or image.shape[1] > 1300:
        scale_percent = 95 # percent of original size
        width = int(image.shape[1] * scale_percent / 100)
        height = int(image.shape[0] * scale_percent / 100)
        dim = (width, height)
        image = cv2.resize(image,dim, interpolation=cv2.INTER_AREA)
    return image
#---------------------------------------------------------------------------

#find the four corners. use contors or just drag over an area because on a phone app you can make it aline with sudoku. LOOK FOR LIEK SUDOKU FIND CONRER ON SELF
def transform(image, p):
    p = np.float32(p)
    pst2 = np.float32([[0,0], [900, 0], [0,900], [900, 900]])
    T = cv2.getPerspectiveTransform(p, pst2)
    image = cv2.warpPerspective(image, T, (900, 900))
    cv2.imshow("transformed", image)
    #------------------------might not needs these maybe after it goes grid by gri
    return image
def sliceandprint(image):
    for c in range(9):
        for r in range(9):
            sliced_image = image[int(10+(100*r)):int(90+(100*r)), int(10+(100*c)):int(90+(100*c))]
            
            #-------------fitlering
            sliced_image = cv2.resize(sliced_image, None, fx = 1, fy = 1)
            gray = cv2.cvtColor(sliced_image, cv2.COLOR_BGR2GRAY)
            noise = cv2.medianBlur(gray, 5)
            thresh = cv2.threshold(noise, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
            #change the psm if needed.
            #use custom this and that and check if lengh of numbers is same, if not then uh oh, or compare for greate amount
            custom_oem = r'--psm 6'
            # custom_oem = r'--psm 10 -c tessedit_char_whitelist=0123456789'

            num = pytesseract.image_to_string(Image.fromarray(cv2.cvtColor(thresh, cv2.COLOR_BGR2RGB)),config=custom_oem)
            num = num.replace("\n\x0c", "") 
            if num.isnumeric() and int(num) > 0:
                #print (str(r) + str(c) + " " + num)
                grid[r][c] = int(num)
            else:
                grid[r][c] = 0
    
    return grid
def just_print_for_all(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        temp = []
        cv2.circle(image, (x, y), 6, (255, 0, 0), -1)
        print("Corner at: ", x, ":", y)
        temp.append(x)
        temp.append(y)
        pst1.append(temp)
    if event == cv2.EVENT_RBUTTONDOWN:
        print(pst1)
        cv2.destroyWindow("window")
        directory = r"/Users/matthieufoucu/Documents/pics"
        os.chdir(directory)
        filename = 'warped2.png'
        cv2.imwrite(filename, transform(image, pst1))
        print('Successfully saved')
        sudoku = sliceandprint(transform(image, pst1))
        print(np.matrix(sudoku))
        Compsolve(sudoku)
        #===

def empty(board):
    empty_spot = []
    for row in range(9):
        for col in range(9):
            if board[row][col] == 0:
                empty_spot.append(row)
                empty_spot.append(col)
                return empty_spot
    if len(empty_spot) == 0:
        empty_spot.append(-1)
        empty_spot.append(-1)
        return empty_spot
#=====
def find_possible_solutions(board, x, y):
    possible = [1,2,3,4,5,6,7,8,9]
    place = y
    while place < 9:
        if board[x][place] == 0:
            place = place + 1
        elif board[x][place] != 0:
            taken = board[x][place]
            if taken in possible:
                possible.remove(taken)
            place = place + 1
    place = y
    while place > -1:
        if board[x][place] == 0:
            place = place - 1
        elif board[x][place] != 0:
            taken = board[x][place]
            if taken in possible:
                possible.remove(taken)
            place = place - 1
    place = x
    while place < 9:
        if board[place][y] == 0:
            place = place + 1
        elif board[place][y] !=0:
            taken = board[place][y]
            if taken in possible:
                possible.remove(taken)
            place = place + 1
    place = x
    while place > -1:
        if board[place][y] == 0:
            place = place - 1
        elif board[place][y] !=0:
            taken = board[place][y]
            if taken in possible:
                possible.remove(taken)
            place = place - 1
    top_x = x - x % 3
    top_y = y - y % 3
    possiblegrid = [1,2,3,4,5,6,7,8,9]
    for i in range(3):
        for j in range(3):
            if board[top_x+i][top_y+j] != 0:
                possiblegrid.remove(board[top_x+i][top_y+j])
    solutions = set(possible).intersection(possiblegrid)         
    return solutions
#=======
def Compsolve(board):
    possible_solution = []
    newempty = empty(board)
    x = newempty[0]
    y = newempty[1]
    if x == -1 or y == -1:
        print("solution below")
        print(np.matrix(board))
        wimage = cv2.imread("/Users/matthieufoucu/Documents/pics/warped2.png")
        drawit(board, wimage)
    possible_solution = find_possible_solutions(board, x, y)
    if len(possible_solution) == 0:
        return False
    else:
        for entry in possible_solution:
            board[x][y] = entry
            if (Compsolve(board)):
                return True
        board[x][y] = 0
        return False
#======
def drawit(board1, img):

    for c in range(9):
        for r in range(9):
            if board1[r][c] != 0:
              img = cv2.putText(img, str(board1[r][c]), (25+(100*int(c)), 75+(100*int(r))), cv2.FONT_HERSHEY_SIMPLEX,2.3, (255, 0, 0), 4, cv2.LINE_AA)
    cv2.imshow("With answers", img)
    print("Done!")


#-------------------Call functions here
image = resizeOG(image)
#-------------------
cv2.namedWindow("window")
cv2.setMouseCallback("window", just_print_for_all)
#---make a wait until
cv2.imshow("window", image)



#---------------------------
#---------------------------
cv2.waitKey(0)
cv2.destroyAllWindows()
#-------------------


#160, 206
#106, 807
#876, 783
#807, 177