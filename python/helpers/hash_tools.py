import base64
import hashlib


def bas64encode(id):
    return base64.b64encode(bytes(id, "utf-8")).decode("ascii")


def hashval(annotation):
    return hashlib.sha256(bytes(str(annotation), "utf-8")).hexdigest()
