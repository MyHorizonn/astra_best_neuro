#import tensorflow as tf
from tabnanny import check
import cv2 as cv
import numpy as np
import fitz
import sys
from signature_detect.loader import Loader
from signature_detect.extractor import Extractor
from signature_detect.cropper import Cropper
from signature_detect.judger import Judger


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
            main_child_idx = i

    temp_kek = 0
    max_y = 0
    for i in range(len(contours)):
        if hierch[0][i][3] == main_child_idx:
            if max_y < cv.boundingRect(contours[i])[1]:
                max_y = cv.boundingRect(contours[i])[1]
                temp_kek = i

    (_x, _y, _w, _h) = cv.boundingRect(contours[temp_kek])
    cv.rectangle(page, (_x, _y), (_x + _w, _y + _h), (0, 255, 0), 2)

    if (_y + _h - y) / h <= .7:
        return False
    else:
        return True


def check_signature(page):
    
    # Маска ярким частям присвоено - 255, остальным - 0 
    loader = Loader()
    img = loader.get_masks(page)
    
    # Находит области, убирает слишком большие и слишком маленькие регионы
    extractor = Extractor(outlier_weight=1, outlier_bias=50, amplfier=15, min_area_size=10)
    labeled_mask = extractor.extract(img)
    
    # Находит контуры областей
    cropper = Cropper(min_region_size=2000, border_ratio=0.1)
    results = cropper.run(labeled_mask)
    if results != {}:

        # Определяет является ли контур подписью
        judger = Judger(size_ratio=[1, 4], pixel_ratio=[0.1, 0.7])
        flag = False
        for i in range(len(results)):
            res = judger.judge(results[i]['cropped_mask'])
            if res:
                flag = True
                break
        return flag
    else:
        return False


def main(doc_path: str):

    # open pdf file
    doc = fitz.open(doc_path)

    '''
    page = doc.load_page(1)
    pix = page.get_pixmap()
    page = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)
    cv.imwrite('test_sign3.png', page)
    '''
    
    result = {
        'pages_with_text_size_failure': [] ,
        'signature_check': None,
    }

    for i in range(doc.page_count):

        if cv.waitKey(0) & 0xFF==ord('d'):
            break
        
        # get page
        page = doc.load_page(i)
        pix = page.get_pixmap()
        page = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)

        if i == 1:
            result['signature_check'] = check_signature(page)
        if ~text_size_check(page): result['pages_with_text_size_failure'].append(i+1)
        
    print(result)
    

if __name__ == '__main__':

    doc_path = None
    for i in range(len(sys.argv)):
        if sys.argv[i] == '--file':
            doc_path = sys.argv[i + 1]
    if doc_path is None:
        print('Error: enter doc path\npython main.py --file myfile.pdf')
    else:
        main(doc_path)

