import json
import logging
import os
import sys

from src.utils.kinopoisk_parser import KinopoiskParser


logging.basicConfig(stream=sys.stdout, level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

secrets_path = os.path.join(os.path.dirname(__file__), "..", "secrets.json")

if os.path.exists(secrets_path):
    with open(secrets_path, "r") as f:
        secrets = json.load(f)
    kinopoisk_parser = KinopoiskParser(tokens=secrets["kinopoisk_tokens"], logger=logger)
else:
    kinopoisk_parser = None
