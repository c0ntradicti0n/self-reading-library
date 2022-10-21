import json


def json_file_update(path, update={}):
    with open(path) as f:
        content = json.load(f)
    if update:
        content.update(update)
        with open(path, "w") as f:
            f.write(json.dumps(content))
    return content
