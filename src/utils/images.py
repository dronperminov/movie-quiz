import cv2


def resize_image(image_path: str, max_width: int) -> None:
    image = cv2.imread(image_path)
    if image is None:
        return

    height, width = image.shape[:2]
    if width <= max_width:
        return

    max_height = round(height * max_width / width)
    image = cv2.resize(image, (max_width, max_height), interpolation=cv2.INTER_AREA)
    cv2.imwrite(image_path, image, [cv2.IMWRITE_WEBP_QUALITY, 90])
