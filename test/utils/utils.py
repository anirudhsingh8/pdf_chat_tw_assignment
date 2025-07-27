def file_to_bytes(path: str) -> bytes:
    with open(path, "rb") as file:
        return file.read()