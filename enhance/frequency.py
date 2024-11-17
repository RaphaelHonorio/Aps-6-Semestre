import numpy as np
import math
import scipy.ndimage
# import cv2


def frequency(im, orientim, windsze, minWaveLength, maxWaveLength):
    rows, cols = np.shape(im)

    # Encontrar a orientação média dentro do bloco
    cosorient = np.mean(np.cos(2 * orientim))
    sinorient = np.mean(np.sin(2 * orientim))
    orient = math.atan2(sinorient, cosorient) / 2

    # Rotacionar o bloco de imagem para que as cristas fiquem verticais
    rotim = scipy.ndimage.rotate(
        im,
        orient / np.pi * 180 + 90,
        axes=(1, 0),reshape=False,
        order=3, mode='nearest')

    # Cortar a imagem para evitar regiões inválidas
    cropsze = int(np.fix(rows / np.sqrt(2)))
    offset = int(np.fix((rows - cropsze) / 2))
    rotim = rotim[offset:offset + cropsze, offset:offset + cropsze]

    # Somar ao longo das colunas para obter uma projeção dos valores de cinza
    proj = np.sum(rotim, axis=0)
    dilation = scipy.ndimage.grey_dilation(proj, windsze, structure=np.ones(windsze))
    temp = np.abs(dilation - proj)
    peak_thresh = 2
    maxpts = (temp < peak_thresh) & (proj > np.mean(proj))
    maxind = np.where(maxpts)

    # Obter o número de picos encontrados
    rows_maxind, cols_maxind = np.shape(maxind)
    # Determinar a frequência espacial das cristas
    if cols_maxind < 2:
        freqim = np.zeros(im.shape)
    else:
        NoOfPeaks = cols_maxind
        waveLength = (maxind[0][cols_maxind - 1] - maxind[0][0]) / (NoOfPeaks - 1)
        if minWaveLength <= waveLength <= maxWaveLength:
            freqim = 1 / np.double(waveLength) * np.ones(im.shape)
        else:
            freqim = np.zeros(im.shape)
    return freqim
