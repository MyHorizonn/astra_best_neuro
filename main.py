#import tensorflow as tf
import cv2 as cv
import numpy as np
import fitz


def text_size_check(page):

    # gray
    gray = cv.cvtColor(page, cv.COLOR_BGR2GRAY)

    # blur
    blur = cv.GaussianBlur(gray, (7, 7), 0)

    # canny
    canny = cv.Canny(blur, 127, 200, apertureSize=3, L2gradient=True)

    # threshold
    _, threshold = cv.threshold(canny, 127, 200, cv.THRESH_BINARY)

    # contours
    contours, hierch = cv.findContours(threshold, cv.RETR_TREE, cv.CHAIN_APPROX_SIMPLE)

    max_cont_idx = -1
    max_cont_area = 0
    for i in range(len(contours)):
            if (hierch[0][i][1] >= 0) and (hierch[0][i][2] >= 0) and (hierch[0][i][3] >= 0):
                if max_cont_area < cv.contourArea(contours[i]):
                    max_cont_area = cv.contourArea(contours[i])
                    max_cont_idx = i
                    
    (x, y, w, h) = cv.boundingRect(contours[max_cont_idx])
    cv.rectangle(page, (x, y), (x + w, y + h), (0, 0, 250), 1)

    main_child_idx = 0
    for i in range(len(contours)):
        if hierch[0][i][3] == max_cont_idx:
            temp_idx = i

    temp_kek = 0
    max_y = 0
    for i in range(len(contours)):
        if hierch[0][i][3] == temp_idx:
            if max_y < cv.boundingRect(contours[i])[1]:
                max_y = cv.boundingRect(contours[i])[1]
                temp_kek = i

    (_x, _y, _w, _h) = cv.boundingRect(contours[temp_kek])
    cv.rectangle(page, (_x, _y), (_x + _w, _y + _h), (0, 255, 0), 2)

    if (_y + _h - y) / h <= .7:
        print("Warning")
    else:
        print("OK")


if __name__ == '__main__':

    # load pdf file
    doc = fitz.open('./data/ЭПЦ-180701-СП.pdf')
    
    for i in range(doc.page_count):

        if cv.waitKey(0) & 0xFF==ord('d'):
            break
        
        # get page
        page = doc.load_page(i)
        pix = page.get_pixmap()
        page = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)
        text_size_check(page)

    #cv.waitKey(0)
    cv.destroyAllWindows()