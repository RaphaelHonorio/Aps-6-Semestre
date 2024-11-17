import numpy as np

def normalize(img, mean, std):
    normed = (img - np.mean(img)) / np.std(img)
    return normed

def ridge_segment(im, blksze, thresh):
    rows, cols = im.shape

    # Normalizar para obter média zero e desvio padrão unitário
    im = normalize(im, 0, 1)\

    # Substituir np.int e np.float por int e float
    new_rows = int(blksze * np.ceil(float(rows) / float(blksze)))
    new_cols = int(blksze * np.ceil(float(cols) / float(blksze)))

    padded_img = np.zeros((new_rows, new_cols))
    stddevim = np.zeros((new_rows, new_cols))

    padded_img[0:rows, 0:cols] = im

    # Calcular o desvio padrão em blocos
    for i in range(0, new_rows, blksze):
        for j in range(0, new_cols, blksze):
            block = padded_img[i:i + blksze, j:j + blksze]
            stddevim[i:i + blksze, j:j + blksze] = np.std(block) * np.ones(block.shape)

    stddevim = stddevim[0:rows, 0:cols]

    # Criar a máscara com base no limite do desvio padrão
    mask = stddevim > thresh

    mean_val = np.mean(im[mask])
    std_val = np.std(im[mask])

    # Normalizar a imagem dentro da região de interesse
    normim = (im - mean_val) / std_val

    return normim, mask