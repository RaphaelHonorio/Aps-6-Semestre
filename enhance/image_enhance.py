# Assegure-se de que as importações estejam corretas para o seu ambiente
from .detect_minuncias import detect_minutiae
from .ridge_segmentation import ridge_segment
from .ridge_orientation import ridge_orient
from .ridge_frequency import ridge_freq
from .ridge_filter import ridge_filter


# import cv2  # Certifique-se de que o OpenCV esteja instalado se for utilizar

def image_enhance(img, blksze=16, thresh=0.1, gradientsigma=1, blocksigma=7, orientsmoothsigma=7, windsze=5,
                  minWaveLength=5, maxWaveLength=15, kx=0.65, ky=0.65):
    # Normaliza a imagem e encontra a ROI (Região de Interesse)
    normim, mask = ridge_segment(img, blksze, thresh)

    # Encontra a orientação de cada pixel
    orientim = ridge_orient(normim, gradientsigma, blocksigma, orientsmoothsigma)

    # Define o tamanho do bloco para a frequência e parâmetros de filtro
    blksze = 38
    freq, medfreq = ridge_freq(normim, mask, orientim, blksze, windsze, minWaveLength, maxWaveLength)

    freq = medfreq * mask  # Aplica a frequência calculada à máscara
    # Cria um filtro Gabor e realiza a filtragem
    newim = ridge_filter(normim, orientim, freq, kx, ky)

    # Se você quiser retornar uma imagem binária, descomente a linha abaixo:
    # th, bin_im = cv2.threshold(np.uint8(newim), 0, 255, cv2.THRESH_BINARY)
    # return bin_im

    # Identificação de Minúcias
    minutiae_img = detect_minutiae(newim)

    print(minutiae_img)

    # Retorna a imagem filtrada com um corte em -3 (ajustável conforme necessário)
    return newim < -3