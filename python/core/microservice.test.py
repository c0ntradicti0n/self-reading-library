
import unittest
from core.pathant.Converter import converter
from core.pathant.PathSpec import PathSpec


@microservice
@converter("a", "b")
class C(PathSpec):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        print("load model")

    def __call__(self, d_m, **kwargs):
        for d, m in d_m:
            print(d, m)
            n = 1
            o= 2
            res = self.predict(m, n, o)
            yield d, res


    def predict(self, m, n, o):
        print(f"predicting on {m}")
        m["predicting"] = "LOL"
        return {"some": "object", "list": ["hahah"]}

    def load(self):
        print("load model")


class T(unittest.TestCase):
    def test_check(self):
        result = list(C(metaize(["1", "3"])))
        self.assertEqual(
            [
                ("1", {"list": ["hahah"], "some": "object"}),
                ("3", {"list": ["hahah"], "some": "object"}),
            ],
            result,
        )


if __name__ == "__main__":
    from core.pathant.Converter import converter
