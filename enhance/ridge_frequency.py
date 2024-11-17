import numpy as np
from .frequency import frequency

def ridge_freq(im, mask, orient, blksze, windsze, minWaveLength, maxWaveLength):
    rows, cols = im.shape
    freq = np.zeros((rows, cols))

    # Percorrer a imagem em blocos, calculando a frequência em cada um
    for r in range(0, rows - blksze + 1, blksze):
        for c in range(0, cols - blksze + 1, blksze):
            blkim = im[r:r + blksze, c:c + blksze]
            blkor = orient[r:r + blksze, c:c + blksze]

            freq[r:r + blksze, c:c + blksze] = frequency(blkim, blkor, windsze, minWaveLength, maxWaveLength)

    # Aplicar a máscara à matriz de frequências
    freq = freq * mask

    # Converter a matriz 2D para 1D para encontrar os valores não-zero
    freq_1d = np.reshape(freq, (1, rows * cols))
    ind = np.where(freq_1d > 0)

    ind = np.array(ind)
    ind = ind[1, :]  # Índices de elementos não-zero

    non_zero_elems_in_freq = freq_1d[0][ind]

    # Calcular a média e a mediana das frequências não-zero
    meanfreq = np.mean(non_zero_elems_in_freq)
    medianfreq = np.median(non_zero_elems_in_freq)

    return freq, meanfreq
