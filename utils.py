import numpy as np
from PySide.QtGui import QImage

import exceptions as e
from numpy.fft import fft2, fftshift, ifft2, ifftshift
#from numpy.fft import rfft2, fftshift, irfft2, ifftshift
#from scipy.fftpack import fft2, ifft2, fftshift, ifftshift, rfft2, irfft2


def image_to_array(image, to_gray=False):
    """ :type image: QImage """
    if not image:
        return
    bits = image.constBits()
    w, h = image.width(), image.height()
    array = np.frombuffer(bits, dtype=np.uint8).copy()

    if image.format() == QImage.Format_Indexed8:
        return array.reshape(h, w)
    else:
        return array[0::4].reshape(h, w).copy()


def array_to_image(array, real=False):
    """ :type array: np.ndarray """
    if array.dtype != np.uint8:
        raise e.WrongArrayTypeException(array.dtype)
    h, w = array.shape

    array = array.astype(np.uint32)
    array = (array | array << 8 | array << 16)
    image = QImage(array.tostring(), w, h, QImage.Format_RGB32)
    return image


def rescale_array(array, scale_factor, max_value=255, dtype=np.uint8):
    scale_factor = scale_factor or np.max(array)
    return ((array/scale_factor) * max_value).astype(dtype)


def descale_array(array, scale_factor, max_value=255):
    array = array.astype(np.int32)
    return ((array/max_value) * scale_factor)


def fft_to_array(fft):
    return np.abs(ifft2(2**fft)).astype(np.uint8)


def array_to_fft(array):
    return np.log2(fftshift(fft2(array)))


def zeropad(x, shape):
    '''Pad a two-dimensional NumPy array with zeros along its borders
    to the specified shape.
    '''
    m, n = x.shape
    p, q = shape
    assert p > m
    assert q > n
    tb = (p - m) / 2
    lr = (q - n) / 2
    xpadded = np.zeros(shape, dtype=np.complex64)
    xpadded[tb:tb + m, lr:lr + n] = x
    return xpadded
