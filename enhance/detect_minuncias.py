import numpy as np
import scipy.ndimage


# Codigo responsavel por detectar as minuncias da impressão digital
def detect_minutiae(binary_img):
    rows, cols = binary_img.shape
    minutiae_img = np.zeros((rows, cols), dtype=int)

    for r in range(1, rows - 1):
        for c in range(1, cols - 1):
            if binary_img[r, c] == 1:
                # Vizinhança 3x3 para contar pontos de crista
                neighbors = binary_img[r - 1:r + 2, c - 1:c + 2]
                crossing_number = np.sum(neighbors) - 1  # Subtraímos 1 para desconsiderar o próprio ponto central

                # Identificar minúcias
                if crossing_number == 1:
                    minutiae_img[r, c] = 1  # Terminação
                elif crossing_number == 3:
                    minutiae_img[r, c] = 2  # Bifurcação

                    print("Minuncias detectadas")
    return minutiae_img