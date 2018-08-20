import utils
import os
import cv2
from matplotlib import pyplot as plt

WORKING_DIR = os.path.realpath('training_data')
os.chdir(WORKING_DIR)

def plot_img(img, title, fmt=(1,1), index=1, cmap='gray'):
    plt.subplot(fmt[0], fmt[1], index)
    plt.imshow(img, cmap=cmap)
    plt.title(title), plt.xticks([]), plt.yticks([])

def plot_processed(imagepath):

    #get color and greyscale images
    imgRGB = cv2.imread(imagepath, -1)
    imgGrey = cv2.imread(imagepath, 0)

    #make hsv image
    imgHSV = cv2.cvtColor(imgRGB, cv2.COLOR_BGR2HSV)
    imgLAB = cv2.cvtColor(imgRGB, cv2.COLOR_BGR2LAB)

    r, g, b = cv2.split(imgRGB)
    h, s, v = cv2.split(imgHSV)
    l, a, bLAB = cv2.split(imgLAB)

    sigma = 0.5
    edge_img_color = utils.auto_canny(imgRGB, sigma)

    fmt = (3,4)

    plot_img(imgRGB, 'RGB', fmt, 1)
    plot_img(r, 'R', fmt, 2)
    plot_img(g, 'G', fmt, 3)
    plot_img(b, 'B', fmt, 4)

    plot_img(imgHSV, 'HSV', fmt, 5)
    plot_img(h, 'H', fmt, 6)
    plot_img(s, 'S', fmt, 7)
    plot_img(v, 'V', fmt, 8)

    plot_img(imgLAB, 'LAB', fmt, 9)
    plot_img(l, 'L', fmt, 10)
    plot_img(a, 'A', fmt, 11)
    plot_img(bLAB, 'B', fmt, 12)

    plt.show()

plot_processed('frame_000696.jpg')