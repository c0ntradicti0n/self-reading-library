from typing import Dict


class Resource(dict):
    def __init__(
        self,
        title,
        type,
        path,
        route,
        access: Dict = {
            "fetch": True,
            "read": True,
            "correct": True,
            "upload": True,
            "delete": True,
            "add_id": False,
        },
    ):
        _access = {
            "fetch": True,
            "read": True,
            "correct": True,
            "upload": True,
            "delete": True,
            "add_id": False,
        }
        _access.update(access)
        self.access = {k: str(v).lower() for k, v in _access.items()}
        self.route = route
        self.path = path
        self.type = type
        self.Title = title.title()
        self.title = title.lower()

    def __getattr__(self, name):
        if name in self:
            return self[name]
        else:
            raise AttributeError("No such attribute: " + name)

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        if name in self:
            del self[name]
        else:
            raise AttributeError("No such attribute: " + name)
