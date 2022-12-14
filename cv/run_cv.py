import cv2 as cv
import numpy as np
import fitz
import sys
from cv.signature_detect.loader import Loader
from cv.signature_detect.extractor import Extractor
from cv.signature_detect.cropper import Cropper
from cv.signature_detect.judger import Judger
import time


def text_size_check(page, debug_mode: bool = True):

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

    # TODO: fix text size check

    main_child_idx = 0
    for i in range(len(contours)):
        if hierch[0][i][3] == max_cont_idx:
            main_child_idx = i

    lowest_text = 0
    max_y = 0
    for i in range(len(contours)):
        if hierch[0][i][3] == main_child_idx:
            if max_y < cv.boundingRect(contours[i])[1]:
                max_y = cv.boundingRect(contours[i])[1]
                lowest_text = i

    (_x, _y, _w, _h) = cv.boundingRect(contours[lowest_text])
    cv.rectangle(page, (_x, _y), (_x + _w, _y + _h), (0, 255, 0), 2)
    if debug_mode:
        cv.imshow("page", page)
        cv.waitKey(0)
        cv.destroyAllWindows()
        
    if (_y - y + _h) / h <= .7:
        return True
    else:
        return False


def check_signature(page, debug_mode : bool = True):
    
    # Маска, ярким частям присвоено - 255, остальным - 0
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
        for i in range(len(results)):
            
            if debug_mode:
                cv.imshow("sign", results[i]['cropped_mask'])
                cv.waitKey(0)
                cv.destroyAllWindows()
            
            if judger.judge(results[i]['cropped_mask']):
                return True
    return False

def check_printing(page, low_threshold=0.15, high_treshold=1.2, debug_mode : bool = True):

    # gray
    gray = cv.cvtColor(page, cv.COLOR_BGR2GRAY)

    # smooth
    bilateral = cv.bilateralFilter(gray, 10, 50, 50)

    # blur
    blur = cv.GaussianBlur(bilateral, (7, 7), 0)

    # поиск окружностей
    circles = cv.HoughCircles(blur, cv.HOUGH_GRADIENT_ALT, dp=2, minDist=page.shape[0] // 20, minRadius=20, maxRadius=100, param1=300, param2=0.9)
    
    if circles is not None:
        circles = np.round(circles[0, :]).astype("int")

        for (x, y, r) in circles:
            empty = np.zeros((gray.shape[0], gray.shape[1]), dtype="uint8")
            cv.circle(empty, (x, y), r, (255, 255, 255), -1)
            crop = gray * (empty.astype(gray.dtype))
            
            # uncomment for testing
            if debug_mode:
                cv.imshow("Circle square", empty)
                cv.imshow("Cropped image", crop)
                cv.waitKey(0)
                cv.destroyAllWindows()
            

            # площадь печати
            square_of_print = len(empty[empty > 200])
            # кол-во пикселей в печати
            print_pixels = len(crop[crop > 50])
            # кол-во пикселей в фоне в печати
            print_bg_pixels = square_of_print - print_pixels
            # Подсчет отношения
            print_pixel_ratio = print_pixels / print_bg_pixels
            print(f'pixels ratio: {print_pixel_ratio:.3f}')
            if print_pixel_ratio > high_treshold or print_pixel_ratio < low_threshold: 
                continue
            else: 
                return True
    return False

def main(doc_path: str, debug_mode: bool = True):


    # open pdf file
    doc = fitz.open(doc_path)

    if debug_mode: print('Файл открыт')

    '''
    page = doc.load_page(1)
    pix = page.get_pixmap()
    page = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)
    cv.imwrite('test_sign3.png', page)
    '''
    
    result = {
        'pages_with_text_size_failure': [] ,
        'signature_check': None,
        'printing_check': None,
    }

    for i in range(doc.page_count):

        if debug_mode: print(f"Страница: {i+1}")

        # get page
        page = doc.load_page(i)
        pix = page.get_pixmap()
        page = np.frombuffer(pix.samples, np.uint8).reshape(pix.height, pix.width, 3)

        if i == 1:
            # Проверка на печать
            result['printing_check'] = check_printing(page, debug_mode=debug_mode)
            
            # Проверка на подпись
            result['signature_check'] = check_signature(page, debug_mode=debug_mode)
            if debug_mode: print('Проверка на подпись и печать')

        # Альбомный лист проверку на заполненность не проходит
        if page.shape[0] > page.shape[1]:
            if text_size_check(page, debug_mode):
                result['pages_with_text_size_failure'].append(i+1)
    
    if debug_mode: print('Проверка закончена\n\n')

    if debug_mode: print(f'''Результат:\n
            Страницы с объемом меньше 70%:  {result['pages_with_text_size_failure']}\n
            Проверка подписи:               {result['signature_check']}\n
            Проверка печати:                {result['printing_check']}\n
            \n''')

    return result
    

if __name__ == '__main__':
    print('run_cv')