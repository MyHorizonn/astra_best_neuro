from typing import Any

import cv2
import numpy as np
import os


class Loader:
    """
    Load an image or a pdf file.

    Attributes
    ----------
    low_threshold: tuple
        The low threshold of cv2.inRange
    high_threshold: tuple
        The high threshold of cv2.inRange

    Methods
    -------
    get_masks(path: str) -> list
        It read an image or a pdf file page by page.
        It returns the masks that the bright parts are marked as 255, the rest as 0.
    """

    def __init__(self, low_threshold=(0, 0, 250), high_threshold=(255, 255, 255)):
        if self._is_valid(low_threshold):
            self.low_threshold = low_threshold
        if self._is_valid(high_threshold):
            self.high_threshold = high_threshold
    
    def __str__(self) -> str:
        s = "\nLoader\n==========\n"
        s += "low_threshold = {}\n".format(self.low_threshold)
        s += "high_threshold = {}\n".format(self.high_threshold)
        return s

    def _is_valid(self, threshold: tuple) -> bool:
        if type(threshold) is not tuple:
            raise Exception("The threshold must be a tuple.")
        if len(threshold) != 3:
            raise Exception("The threshold must have 3 item (h, s, v).")
        for item in threshold:
            if item not in range(0, 256):
                raise Exception("The threshold item must be in the range [0, 255].")
        return True

    def get_masks(self, img) -> list:
        '''
        basename = os.path.basename(path)
        dn, dext = os.path.splitext(basename)
        ext = dext[1:].lower()
        if ext == "pdf":
            self.document_type = "PDF"
        elif ext == "jpg" or ext == "jpeg" or ext == "png" or ext == "tif":
            self.document_type = "IMAGE"
        else:
            raise Exception("Document should be jpg/jpeg, png, tif or pdf.")
        '''
        loader = _ImageWorker(self.low_threshold, self.high_threshold)
        return loader.make_mask(img)

class _ImageWorker:
    def __init__(self, low_threshold: tuple, high_threshold: tuple) -> None:
        self.low_threshold = low_threshold
        self.high_threshold = high_threshold

    def make_mask(self, image) -> Any:
        """
        create a mask that the bright parts are marked as 255, the rest as 0.

        params
        ------
        image: numpy array

        return
        ------
        frame_threshold: numpy array
        """
        blur = cv2.GaussianBlur(image, (3, 3), 0)
        frame_HSV = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        frame_threshold = cv2.inRange(
            frame_HSV, self.low_threshold, self.high_threshold
        )
        return frame_threshold
