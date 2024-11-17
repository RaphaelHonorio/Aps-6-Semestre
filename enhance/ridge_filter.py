import numpy as np
import scipy.ndimage

def ridge_filter(im, orient, freq, kx, ky):
    angleInc = 3
    im = np.double(im)
    rows, cols = im.shape
    newim = np.zeros((rows, cols))

    freq_1d = np.reshape(freq, (1, rows * cols))
    ind = np.where(freq_1d > 0)
    ind = np.array(ind)
    ind = ind[1, :]

    # Arredondar as frequências para o número mais próximo de 0.01
    non_zero_elems_in_freq = freq_1d[0][ind]
    non_zero_elems_in_freq = np.round(non_zero_elems_in_freq * 100) / 100
    unfreq = np.unique(non_zero_elems_in_freq)

    # Gerar filtros de Gabor para as frequências distintas e orientações
    sigmax = 1 / unfreq[0] * kx
    sigmay = 1 / unfreq[0] * ky

    sze = int(np.round(3 * np.max([sigmax, sigmay])))
    x, y = np.meshgrid(np.linspace(-sze, sze, (2 * sze + 1)),
                       np.linspace(-sze, sze, (2 * sze + 1)))

    # Filtro de Gabor original
    reffilter = np.exp(-(((x ** 2) / (sigmax ** 2) + (y ** 2) / (sigmay ** 2)))) * np.cos(2 * np.pi * unfreq[0] * x)

    filt_rows, filt_cols = reffilter.shape

    gabor_filter = np.zeros((int(180 / angleInc), filt_rows, filt_cols))

    for o in range(0, int(180 / angleInc)):
        # Rotacionar o filtro de Gabor
        rot_filt = scipy.ndimage.rotate(reffilter, -(o * angleInc + 90), reshape=False)
        gabor_filter[o] = rot_filt

    # Encontrar os pontos válidos na matriz que estão longe das bordas
    maxsze = sze
    validr, validc = np.where(freq > 0)
    valid_mask = (validr > maxsze) & (validr < rows - maxsze) & (validc > maxsze) & (validc < cols - maxsze)
    finalind = np.where(valid_mask)

    # Converter os valores de orientação de radianos para índices (graus/angleInc)
    maxorientindex = np.round(180 / angleInc)
    orientindex = np.round(orient / np.pi * 180 / angleInc) % maxorientindex

    # Executar a filtragem de Gabor
    sze = int(sze)
    for k in range(finalind[0].size):
        r = validr[finalind[0][k]]
        c = validc[finalind[0][k]]

        # Fatiamento correto da matriz
        img_block = im[r - sze:r + sze + 1, c - sze:c + sze + 1]

        newim[r, c] = np.sum(img_block * gabor_filter[int(orientindex[r, c])])

    return newim
