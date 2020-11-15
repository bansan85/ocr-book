from typing import Any, List, Tuple, Optional

import cv2
import numpy as np

import compute

if np.__version__.startswith("1.2"):
    # Add typing for numpy :
    # from numpy.typing import ArrayLike.
    # For the moment, they are all Any.
    raise Exception("numpy now support ArrayLike with numpy.typing")


def charge_image(fichier: str) -> Any:
    return cv2.imread(fichier, flags=cv2.IMREAD_ANYDEPTH)


def convertion_en_niveau_de_gris(image: Any) -> Any:
    # Already a 8 bit image.
    if image.ndim == 2:
        return image
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def get_polygon_from_contour(contour: Any, number_of_vertices: int) -> Any:
    min_e = 0
    max_e = 1
    max_stagnation = 10

    arc_length_contour = cv2.arcLength(contour, True)

    epsilon = (min_e + max_e) / 2
    epislon_step_dichotomy = (max_e - min_e) / 2
    n_stagnation = 0
    contour_max: List[Any] = []
    last_contour_size = 0

    while True:
        contour_i = cv2.approxPolyDP(
            contour, epsilon * arc_length_contour, True
        )
        if len(contour_i) == number_of_vertices:
            return contour_i
        epislon_step_dichotomy = epislon_step_dichotomy / 2
        if len(contour_i) > number_of_vertices:
            epsilon = epsilon + epislon_step_dichotomy
            n_stagnation = max(n_stagnation + 1, 1)
            if len(contour_max) < number_of_vertices or len(contour_i) < len(
                contour_max
            ):
                contour_max = contour_i
        elif len(contour_i) < number_of_vertices:
            epsilon = epsilon - epislon_step_dichotomy
            n_stagnation = min(n_stagnation - 1, -1)
            # On garde le contour le plus grand au cas où on ne trouve
            # pas un contour de taille suffisant.
            if len(contour_max) < len(contour_i):
                contour_max = contour_i
        if np.abs(n_stagnation) > max_stagnation:
            return contour_max
        # Si la taille du contour change, on réinitialise le compteur.
        if last_contour_size != len(contour_i):
            n_stagnation = 0
        last_contour_size = len(contour_i)


def rotate_image(image: Any, angle_deg: float) -> Any:
    image_center = tuple(np.array(image.shape[1::-1]) / 2)
    rot_mat = cv2.getRotationMatrix2D(image_center, angle_deg, 1.0)
    result = cv2.warpAffine(
        image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR
    )
    return result


def crop_rectangle(image: Any, crop: Tuple[int, int, int, int]) -> Any:
    return image[crop[2] : crop[3], crop[0] : crop[1]]


def number_channels(image: Any) -> int:
    if image.ndim == 2:
        return 1
    if image.ndim == 3:
        return image.shape[-1]
    raise Exception("Failed to found the number of channels.")


def is_black_white(image: Any) -> bool:
    if number_channels(image) != 1:
        return False
    hist = cv2.calcHist([image], [0], None, [256], [0, 256])
    return sum(hist[1:255]) < 1


def force_image_to_be_grayscale(
    image: Any, blur_kernel_size: Tuple[int, int], force_blur: bool
) -> Any:
    if number_channels(image) == 1:
        one_channel_image = image.copy()
    else:
        one_channel_image = convertion_en_niveau_de_gris(image)

    if force_blur or is_black_white(one_channel_image):
        return cv2.blur(one_channel_image, blur_kernel_size)
    return one_channel_image


def draw_lines_from_hough_lines(
    image: Any, lines: Any, color: Any, width: int
) -> Any:
    image_with_lines = convertion_en_couleur(image)
    for line in lines:
        for point1_x, point1_y, point2_x, point2_y in line:
            cv2.line(
                image_with_lines,
                (point1_x, point1_y),
                (point2_x, point2_y),
                color,
                width,
            )
    return image_with_lines


def get_area(image: Any) -> int:
    return image.shape[0] * image.shape[1]


def get_hw(image: Any) -> Tuple[int, int]:
    return (image.shape[0], image.shape[1])


def remove_border_in_contours(
    contours: Any, border_size: int, image: Any
) -> None:
    height, width = get_hw(image)
    for cnt in contours:
        for contour in cnt:
            contour[0, 0] = compute.clamp(
                contour[0, 0] - border_size, 0, width - 1
            )
            contour[0, 1] = compute.clamp(
                contour[0, 1] - border_size, 0, height - 1
            )


def split_image(image: Any, angle: float, posx: int) -> Tuple[Any, Any]:
    height, width = get_hw(image)

    toppoint = (posx, 0)
    bottompoint = compute.get_bottom_point_from_alpha_posx(angle, posx, height)

    # On défini le masque pour séparer la page droite et gauche
    mask = np.zeros((height, width), np.uint8)
    pts = np.array(
        [
            [0, 0],
            [toppoint[0], 0],
            [toppoint[0], toppoint[1]],
            [bottompoint[0], bottompoint[1]],
            [bottompoint[0], height - 1],
            [0, height - 1],
        ]
    )
    mask2 = cv2.drawContours(mask, np.int32([pts]), 0, 255, -1)
    page_gauche = image.copy()
    page_droite = image.copy()
    # On applique le masque
    page_gauche[mask2 == 0] = 0
    page_droite[mask2 > 0] = 0
    # On crop les images.
    page_gauche_0 = crop_rectangle(
        page_gauche,
        (0, np.maximum(toppoint[0], bottompoint[0]) - 1, 0, height - 1),
    )
    page_droite_0 = crop_rectangle(
        page_droite,
        (np.minimum(toppoint[0], bottompoint[0]), width, 0, height - 1),
    )

    # On renvoie les images cropées.
    return page_gauche_0, page_droite_0


def convertion_en_couleur(image: Any) -> Any:
    # Already a 8 bit image.
    if image.ndim == 2:
        return cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    return image.copy()


def add_border_to_match_size(
    image: Any,
    paper_size_wh_cm: Tuple[float, float],
    crop: Tuple[int, int, int, int],
    shape_wh: Tuple[int, int],
    dpi: int,
) -> Any:
    height, width = get_hw(image)

    marge_haute_px = crop[2]
    marge_basse_px = shape_wh[1] - 1 - crop[3]
    marge_gauche_px = crop[0]
    marge_droite_px = shape_wh[0] - 1 - crop[1]
    if (
        marge_gauche_px + width + marge_droite_px
        < paper_size_wh_cm[0] / 2.54 * dpi
    ):
        pixels_manquant = paper_size_wh_cm[0] / 2.54 * dpi - width
        left = int(pixels_manquant / 2.0)
        right = int(pixels_manquant / 2.0)
    else:
        raise Exception("marge", "marge_gauche_px")
    if (
        marge_haute_px + height + marge_basse_px
        < paper_size_wh_cm[1] / 2.54 * dpi
    ):
        pixels_manquant = paper_size_wh_cm[1] / 2.54 * dpi - height
        # If no crop at the previous operation, add the same value to the
        # top and the bottom
        if marge_haute_px == 0 and marge_basse_px == 0:
            marge_haute_px = 1
            marge_basse_px = 1
        pourcenthaut = marge_haute_px / (marge_haute_px + marge_basse_px)
        top = int(pixels_manquant * pourcenthaut)
        pourcentbas = marge_basse_px / (marge_haute_px + marge_basse_px)
        bottom = int(pixels_manquant * pourcentbas)
    else:
        raise Exception("marge", "marge_gauche_px")
    return (top, bottom, left, right)


def write_image_if(
    image: Any, enable_debug: Optional[str], filename: str
) -> None:
    if enable_debug is not None:
        cv2.imwrite(enable_debug + filename, image)


def __find_longest_lines_in_border(
    shape: Tuple[int, int], epsilon: int, cnt: Any
) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
    height, width = shape
    left_top = height
    left_bottom = 0
    right_top = height
    right_bottom = 0
    top_left = width
    top_right = 0
    bottom_left = width
    bottom_right = 0
    for pt1, pt2 in compute.iterator_zip_n_n_1(cnt):
        point1_x, point1_y = pt1[0]
        point2_x, point2_y = pt2[0]
        if point1_x <= epsilon and point2_x <= epsilon:
            left_top = min(left_top, point1_y, point2_y)
            left_bottom = max(left_bottom, point1_y, point2_y)
        if point1_y <= epsilon and point2_y <= epsilon:
            top_left = min(top_left, point1_x, point2_x)
            top_right = max(top_right, point1_x, point2_x)
        if point1_x >= width - 1 - epsilon and point2_x >= width - 1 - epsilon:
            right_top = min(right_top, point1_y, point2_y)
            right_bottom = max(right_bottom, point1_y, point2_y)
        if (
            point1_y >= height - 1 - epsilon
            and point2_y >= height - 1 - epsilon
        ):
            bottom_left = min(bottom_left, point1_x, point2_x)
            bottom_right = max(bottom_right, point1_x, point2_x)
    return (
        (left_top, left_bottom),
        (right_top, right_bottom),
        (top_left, top_right),
        (bottom_left, bottom_right),
    )


def __insert_border_in_mask(
    cnt: Any,
    threshold2: Any,
    mask_border_only: Any,
    epsilon: Tuple[int, float],
    page_angle: float,
) -> None:
    __pourcentage_white_allowed__ = 0.01
    epsilon_border, epsilon_angle = epsilon
    height, width = get_hw(threshold2)
    cnt2 = cnt[cnt[:, 0, 0] > epsilon_border]
    cnt3 = cnt2[cnt2[:, 0, 0] < width - 1 - epsilon_border]
    cnt4 = cnt3[cnt3[:, 0, 1] > epsilon_border]
    cnt5 = cnt4[cnt4[:, 0, 1] < height - 1 - epsilon_border]
    if len(cnt5) == 0:
        return
    contour_approximate = cv2.approxPolyDP(cnt5, epsilon_border, True)
    all_pair = list(compute.iterator_zip_n_n_1(contour_approximate))
    all_pair_no_single_pixel = list(
        filter(
            lambda x: x[0][0][0] != x[1][0][0] or x[0][0][1] != x[1][0][1],
            all_pair,
        )
    )
    all_angles = list(
        map(
            lambda x: (
                (x[0][0], x[1][0]),
                compute.get_angle_0_180(x[0][0], x[1][0]),
                np.linalg.norm(x[0][0] - x[1][0]),
            ),
            all_pair_no_single_pixel,
        )
    )
    vertical_lines = list(
        filter(
            lambda x: compute.is_angle_closed_to(
                x[1], page_angle + 90.0, epsilon_angle, 180
            ),
            all_angles,
        )
    )
    horizontal_lines = list(
        filter(
            lambda x: compute.is_angle_closed_to(
                x[1], page_angle, epsilon_angle, 180
            ),
            all_angles,
        )
    )
    vertical_lines_pos = list(
        map(
            lambda x: (
                compute.get_angle_0_180_posx_safe(x[0][0], x[0][1])[1],
                x[1],
            ),
            vertical_lines,
        )
    )
    horizontal_lines_pos = list(
        map(
            lambda x: (
                compute.get_angle_0_180_posy_safe(x[0][0], x[0][1])[1],
                x[1],
            ),
            horizontal_lines,
        )
    )
    vertical_lines_pos.sort(key=lambda x: x[0])
    horizontal_lines_pos.sort(key=lambda x: x[0])
    for posx, angle in vertical_lines_pos:
        mask = np.zeros((height, width), np.uint8)
        bottom_point = compute.get_bottom_point_from_alpha_posx(
            angle, posx, height
        )
        if posx < width / 2:
            pts = np.array(
                [
                    [-1, 0],
                    [posx - 1, 0],
                    [bottom_point[0] - 1, bottom_point[1]],
                    [-1, height - 1],
                ]
            )
        else:
            pts = np.array(
                [
                    [width, 0],
                    [posx + 1, 0],
                    [bottom_point[0] + 1, bottom_point[1]],
                    [width, height - 1],
                ]
            )
        mask = cv2.drawContours(mask, [pts], 0, 255, -1)
        histogram = cv2.calcHist([threshold2], [0], mask, [2], [0, 256])
        if __pourcentage_white_allowed__ * histogram[0] > sum(
            histogram[1:]
        ) or __pourcentage_white_allowed__ * histogram[-1] > sum(
            histogram[:-1]
        ):
            mask_border_only = cv2.drawContours(
                mask_border_only, [pts], 0, (0), -1
            )
    for posy, angle in horizontal_lines_pos:
        mask = np.zeros((height, width), np.uint8)
        bottom_point = compute.get_right_point_from_alpha_posy(
            angle, posy, width
        )
        if posy < height / 2:
            pts = np.array(
                [
                    [0, -1],
                    [0, posy - 1],
                    [bottom_point[0], bottom_point[1] - 1],
                    [width - 1, -1],
                ]
            )
        else:
            pts = np.array(
                [
                    [0, height],
                    [0, posy + 1],
                    [bottom_point[0], bottom_point[1] + 1],
                    [width - 1, height],
                ]
            )
        mask = cv2.drawContours(mask, [pts], 0, 255, -1)
        histogram = cv2.calcHist([threshold2], [0], mask, [2], [0, 256])
        if __pourcentage_white_allowed__ * histogram[0] > sum(
            histogram[1:]
        ) or __pourcentage_white_allowed__ * histogram[-1] > sum(
            histogram[:-1]
        ):
            mask_border_only = cv2.drawContours(
                mask_border_only, [pts], 0, (0), -1
            )


def remove_black_border_in_image(
    gray_bordered: Any, page_angle: float, enable_debug: Optional[str]
) -> Any:
    thresholdi = threshold_from_gaussian_histogram_black(gray_bordered)
    _, threshold = cv2.threshold(
        gray_bordered, thresholdi, 255, cv2.THRESH_BINARY_INV
    )
    write_image_if(threshold, enable_debug, "_2b2.png")
    contours, _ = cv2.findContours(
        threshold, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
    )
    if enable_debug is not None:
        image_contours = cv2.drawContours(
            convertion_en_couleur(gray_bordered), contours, -1, (0, 0, 255), 3
        )
        write_image_if(image_contours, enable_debug, "_2b3.png")
    __epsilon__ = 5
    mask_border_only = 255 * np.ones(shape=gray_bordered.shape, dtype=np.uint8)
    height, width = get_hw(gray_bordered)
    __angle_tolerance__ = 3.0
    for cnt in contours:
        (
            (left_top, left_bottom),
            (right_top, right_bottom),
            (top_left, top_right),
            (bottom_left, bottom_right),
        ) = __find_longest_lines_in_border((height, width), __epsilon__, cnt)

        if (
            left_bottom - left_top > 0
            or top_right - top_left > 0
            or right_bottom - right_top > 0
            or bottom_right - bottom_left > 0
        ):
            __insert_border_in_mask(
                cnt,
                threshold,
                mask_border_only,
                (__epsilon__, __angle_tolerance__),
                page_angle,
            )

    # Borders are in black in mask.
    write_image_if(mask_border_only, enable_debug, "_2c.png")
    return mask_border_only


def apply_mask(image: Any, mask: Any) -> Any:
    gray_bordered2 = cv2.bitwise_not(image)
    gray_bordered3 = cv2.bitwise_and(
        gray_bordered2, gray_bordered2, mask=mask
    )
    gray_bordered4 = cv2.bitwise_not(gray_bordered3)
    # Borders are in white in original image.
    return gray_bordered4


def erode_and_dilate(
    image: Any, size: Tuple[int, int], iterations: int, reverse: bool = False
) -> Any:
    start = int(reverse)
    img = image
    for i in range(2):
        if (i + start) % 2 == 0:
            img = cv2.erode(
                img,
                cv2.getStructuringElement(cv2.MORPH_ELLIPSE, size),
                iterations=iterations,
            )
        else:
            img = cv2.dilate(
                img,
                cv2.getStructuringElement(cv2.MORPH_ELLIPSE, size),
                iterations=iterations,
            )
    return img


def threshold_from_gaussian_histogram_white(
    image: Any, pourcentage: float = 0.2, blur_kernel_size: int = 31
) -> int:
    histogram = cv2.calcHist([image], [0], None, [256], [0, 256])
    histogram_blur = cv2.GaussianBlur(
        histogram,
        (1, blur_kernel_size),
        blur_kernel_size,
        borderType=cv2.BORDER_REPLICATE,
    )
    i = 255
    extreme_min = histogram_blur[255][0]
    for j in range(254, 0, -1):
        if histogram_blur[j][0] < extreme_min:
            extreme_min = histogram_blur[j][0]
        else:
            i = j
            break
    limit = extreme_min * (1 + pourcentage)
    for j in range(i, 0, -1):
        if histogram_blur[j][0] > limit:
            i = j
            break
    return i


def threshold_from_gaussian_histogram_black(
    image: Any, blur_kernel_size: int = 31
) -> int:
    histogram = cv2.calcHist([image], [0], None, [256], [0, 256])
    histogram_blur = cv2.GaussianBlur(
        histogram,
        (1, blur_kernel_size),
        blur_kernel_size,
        borderType=cv2.BORDER_REPLICATE,
    )
    for i in range(1, 256):
        if histogram_blur[i][0] < histogram_blur[i + 1][0]:
            return i
    return 255


def gaussian_blur_wrap(histogram: Any, kernel_size: int) -> Any:
    histogram_wrap = np.concatenate(
        [
            histogram[-kernel_size:],
            histogram,
            histogram[:kernel_size],
        ]
    )
    histogram_wrap_blur = cv2.GaussianBlur(
        histogram_wrap,
        (1, kernel_size),
        kernel_size,
        borderType=cv2.BORDER_REPLICATE,
    )
    return histogram_wrap_blur[kernel_size:-kernel_size]


def apply_brightness_contrast(
    input_img: Any, brightness: int = 0, contrast: int = 0
) -> Any:
    if brightness != 0:
        if brightness > 0:
            shadow = brightness
            highlight = 255
        else:
            shadow = 0
            highlight = 255 + brightness
        alpha_b = (highlight - shadow) / 255
        gamma_b = shadow
        buf = cv2.addWeighted(input_img, alpha_b, input_img, 0, gamma_b)
    else:
        buf = input_img.copy()

    if contrast != 0:
        alpha_c = 131 * (contrast + 127) / (127 * (131 - contrast))
        gamma_c = 127 * (1 - alpha_c)
        buf = cv2.addWeighted(buf, alpha_c, buf, 0, gamma_c)

    return buf


# return cv2ext.bounding_rectangle(
#     cv2ext.get_hw(images_mask),
#     (lines_vertical_angle, lines_horizontal_angle),
#     (flag_v_min, flag_v_max, flag_h_min, flag_h_max),
# )
def bounding_rectangle(
    shape: Tuple[int, int],
    lines: Tuple[
        List[Tuple[Tuple[int, int], Tuple[int, int]]],
        List[Tuple[Tuple[int, int], Tuple[int, int]]],
    ],
    flags: Tuple[List[bool], List[bool], List[bool], List[bool]],
) -> Any:
    mask = 255 * np.ones(shape, dtype=np.uint8)
    lines_vertical_angle, lines_horizontal_angle = lines

    for line, flag in zip(lines_vertical_angle, flags[0]):
        if not flag:
            continue
        pt1, pt2 = line
        angle, posx = compute.get_angle_0_180_posx_safe(pt1, pt2)

        pts = np.array(
            [
                [0, 0],
                [posx, 0],
                compute.get_bottom_point_from_alpha_posx(
                    angle, posx, shape[0]
                ),
                [0, shape[0] - 1],
            ]
        )
        mask = cv2.drawContours(mask, np.int32([pts]), 0, (0), -1)

    for line, flag in zip(lines_vertical_angle, flags[1]):
        if not flag:
            continue
        pt1, pt2 = line
        angle, posx = compute.get_angle_0_180_posx_safe(pt1, pt2)

        pts = np.array(
            [
                [shape[1] - 1, 0],
                [posx, 0],
                compute.get_bottom_point_from_alpha_posx(
                    angle, posx, shape[0]
                ),
                [shape[1] - 1, shape[0] - 1],
            ]
        )
        mask = cv2.drawContours(mask, np.int32([pts]), 0, (0), -1)

    for line, flag in zip(lines_horizontal_angle, flags[2]):
        if not flag:
            continue
        pt1, pt2 = line
        angle, posy = compute.get_angle_0_180_posy_safe(pt1, pt2)

        pts = np.array(
            [
                [0, 0],
                [0, posy],
                compute.get_right_point_from_alpha_posy(angle, posy, shape[1]),
                [shape[1] - 1, 0],
            ]
        )
        mask = cv2.drawContours(mask, np.int32([pts]), 0, (0), -1)

    for line, flag in zip(lines_horizontal_angle, flags[3]):
        if not flag:
            continue
        pt1, pt2 = line
        angle, posy = compute.get_angle_0_180_posy_safe(pt1, pt2)

        pts = np.array(
            [
                [0, shape[0] - 1],
                [0, posy],
                compute.get_right_point_from_alpha_posy(angle, posy, shape[1]),
                [shape[1] - 1, shape[0] - 1],
            ]
        )
        mask = cv2.drawContours(mask, np.int32([pts]), 0, (0), -1)

    rectangle = cv2.boundingRect(mask)

    return np.array(
        [
            [[rectangle[0], rectangle[1]]],
            [[rectangle[0], rectangle[1] + rectangle[3]]],
            [[rectangle[0] + rectangle[2], rectangle[1] + rectangle[3]]],
            [[rectangle[0] + rectangle[2], rectangle[1]]],
        ]
    )


def is_line_not_cross_images(
    line: Tuple[int, int, int, int], images_mask: Any
) -> bool:
    line_x1, line_y1, line_x2, line_y2 = line
    image_line = np.zeros(images_mask.shape, np.uint8)
    cv2.line(
        image_line,
        (line_x1, line_y1),
        (line_x2, line_y2),
        (255, 255, 255),
        1,
    )
    image_line = cv2.bitwise_and(images_mask, image_line)
    return cv2.countNonZero(image_line) == 0
