from core.pathant.PathSpec import PathSpec


class Filter(PathSpec):
    def __init__(self, f, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.f = f

    def __call__(self, x_ms, *args, **kwargs):
        for x_m in x_ms:
            if self.f(x_m):
                print(self.f(x_m))
                yield x_m
