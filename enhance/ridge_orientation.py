import numpy as np
import cv2
from scipy import ndimage
from scipy import signal

def ridge_orient(im, gradientsigma, blocksigma, orientsmoothsigma):
    rows, cols = im.shape
    # Calcular os gradientes da imagem
    sze = np.fix(6 * gradientsigma)
    if np.remainder(sze, 2) == 0:
        sze = sze + 1

    gauss = cv2.getGaussianKernel(int(sze), gradientsigma)
    f = gauss * gauss.T

    # Calcular o gradiente do filtro Gaussiano
    fy, fx = np.gradient(f)

    # Aplicar a convolução para calcular os gradientes na imagem
    Gx = signal.convolve2d(im, fx, mode='same')
    Gy = signal.convolve2d(im, fy, mode='same')

    Gxx = np.power(Gx, 2)
    Gyy = np.power(Gy, 2)
    Gxy = Gx * Gy

    # Suavizar os dados de covariância para realizar uma soma ponderada
    sze = np.fix(6 * blocksigma)
    if np.remainder(sze, 2) == 0:
        sze = sze + 1

    gauss = cv2.getGaussianKernel(int(sze), blocksigma)
    f = gauss * gauss.T

    Gxx = ndimage.convolve(Gxx, f)
    Gyy = ndimage.convolve(Gyy, f)
    Gxy = 2 * ndimage.convolve(Gxy, f)

    # Solução analítica para encontrar a direção principal
    denom = np.sqrt(np.power(Gxy, 2) + np.power((Gxx - Gyy), 2)) + np.finfo(float).eps

    sin2theta = Gxy / denom  # Seno dos ângulos dobrados
    cos2theta = (Gxx - Gyy) / denom  # Cosseno dos ângulos dobrados

    # Suavizar os valores do seno e cosseno se o parâmetro for fornecido
    if orientsmoothsigma:
        sze = np.fix(6 * orientsmoothsigma)
        if np.remainder(sze, 2) == 0:
            sze = sze + 1
        gauss = cv2.getGaussianKernel(int(sze), orientsmoothsigma)
        f = gauss * gauss.T
        cos2theta = ndimage.convolve(cos2theta, f)
        sin2theta = ndimage.convolve(sin2theta, f)

    # Calcular a imagem de orientação
    orientim = np.pi / 2 + np.arctan2(sin2theta, cos2theta) / 2
    return orientim
