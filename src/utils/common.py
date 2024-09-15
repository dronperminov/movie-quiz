import hashlib
import os


def __get_hash(filename: str) -> str:
    hash_md5 = hashlib.md5()

    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)

    return hash_md5.hexdigest()


def get_static_hash() -> str:
    hashes = []

    for directory in ["js", "styles"]:
        for path, _, files in os.walk(os.path.join(os.path.dirname(__file__), "..", "..", "web", directory)):
            for name in files:
                hashes.append(__get_hash(os.path.join(path, name)))

    static_hash = "_".join(hashes)
    hash_md5 = hashlib.md5()
    hash_md5.update(static_hash.encode("utf-8"))
    return hash_md5.hexdigest()
