import numpy as np
from PySide.QtGui import QImage

import exceptions as e
from numpy.fft import fft2, fftshift, ifft2, ifftshift


def image_to_array(image, to_gray=False):
    """ :type image: QImage """
    bits = image.constBits()
    w, h = image.width(), image.height()
    array = np.frombuffer(bits, dtype=np.uint8).copy()

    if image.format() == QImage.Format_Indexed8:
        return array.reshape(h, w)

    else:
        return array[2::4].reshape(h, w)


def array_to_image(array, real=False):
    """ :type array: np.ndarray """
    if array.dtype != np.uint8:
        raise e.WrongArrayTypeException(array.dtype)
    h, w = array.shape

    if real:
        array = array.astype(np.uint32)
        array = (array | array << 8 | array << 16)
        image = QImage(array.tostring(), w, h, QImage.Format_RGB32)
    else:
        image = QImage(array.tostring(), w, h, QImage.Format_Indexed8)
    return image


def rescale_array(array, scale_factor, max_value=255, dtype=np.uint8):
    scale_factor = scale_factor or np.max(array)
    return ((array/scale_factor) * max_value).astype(dtype)


def descale_array(array, scale_factor, max_value=255):
    array = array.astype(np.int32)
    return ((array/max_value) * scale_factor)


def fft_to_array(fft):
    return ifft2(ifftshift(2**fft)).astype(np.ubyte)


def array_to_fft(array):
    return np.log2(fftshift(fft2(array)))
