import hashlib
import os
import re
import shutil
from datetime import datetime
from typing import List

import cv2
from fastapi import UploadFile

from src import constants


def escape_query(query: str) -> str:
    if re.fullmatch(r"/[^/]+/", query):
        return query[1:-1]

    alternatives = [re.escape(alternative) for alternative in query.split("|") if alternative]
    return "|".join(alternatives)


def get_default_question_years() -> List[List[int]]:
    years = []

    for i, year in enumerate(constants.QUESTION_YEARS[1:]):
        years.append([constants.QUESTION_YEARS[i], year - 1])

    years.append([constants.QUESTION_YEARS[-1], datetime.now().year])
    return years


def get_word_form(questions: int, word_forms: List[str]) -> str:
    if questions % 10 in {0, 5, 6, 7, 8, 9} or questions % 100 in {10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20}:
        return word_forms[0]

    if questions % 10 in {2, 3, 4}:
        return word_forms[1]

    return word_forms[2]


def crop_image(path: str) -> None:
    image = cv2.imread(path)
    height, width = image.shape[:2]
    size = min(height, width)
    x, y = (width - size) // 2, (height - size) // 2
    image = image[y:y + size, x:x + size]
    image = cv2.resize(image, (constants.CROP_IMAGE_SIZE, constants.CROP_IMAGE_SIZE), interpolation=cv2.INTER_AREA)
    cv2.imwrite(path, image)


def save_image(image: UploadFile, output_dir: str) -> str:
    file_name = image.filename.split("/")[-1]
    file_path = os.path.join(output_dir, file_name)

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
    finally:
        image.file.close()

    crop_image(file_path)
    return file_path


def get_hash(filename: str) -> str:
    hash_md5 = hashlib.md5()

    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def get_static_hash() -> str:
    hashes = []
    styles_dir = os.path.join(os.path.dirname(__file__), "..", "..", "web", "styles")
    js_dir = os.path.join(os.path.dirname(__file__), "..", "..", "web", "js")

    for filename in os.listdir(styles_dir):
        hashes.append(get_hash(os.path.join(styles_dir, filename)))

    for filename in os.listdir(js_dir):
        hashes.append(get_hash(os.path.join(js_dir, filename)))

    statis_hash = "_".join(hashes)
    hash_md5 = hashlib.md5()
    hash_md5.update(statis_hash.encode("utf-8"))

    return hash_md5.hexdigest()


def resize_preview(image_path: str, target_width: int = 500, target_height: int = 281) -> dict:
    image = cv2.imread(image_path)

    if image is None:
        return {"success": False, "message": "Не удалось открыть скачанной изображение"}

    height, width, _ = image.shape
    aspect_ratio = width / height

    if target_height != 0:
        resized_width, resized_height = round(aspect_ratio * target_height), target_height
    else:
        resized_width, resized_height = target_width, round(target_width / aspect_ratio)

    image = cv2.resize(image, (resized_width, resized_height), interpolation=cv2.INTER_AREA)

    if resized_width < target_width - 10:
        return {"success": False, "message": "Изображение слишком мало по ширине"}

    x = (resized_width - target_width) // 2
    image = image[:, x:x + target_width]

    if image_path.endswith(".webp"):
        cv2.imwrite(image_path, image, [cv2.IMWRITE_WEBP_QUALITY, 80])
    else:
        cv2.imwrite(image_path, image)

    return {"success": True}
