import itertools

class Pipeline:
    def __init__(self, pipeline, source, target, extra_paths, **flags):
        self.extra_paths = extra_paths
        self.target = target
        self.source = source
        self.pipeline = pipeline
        self.flags = flags
        self.dummy_generator = itertools.cycle([("dummy", {"meta": None})])

    def __call__(self, arg, **flags):
        intermediate_result = arg
        for functional_object in self.pipeline:
            functional_object.flags = self.flags if self.flags else flags

            if functional_object in self.extra_paths:
                others = self.extra_paths[functional_object]
                others = [other(self.dummy_generator) for other in others]
                intermediate_result = functional_object(intermediate_result, *others)
            elif intermediate_result:
                intermediate_result = functional_object(intermediate_result)
            else:
                intermediate_result = functional_object()

        return intermediate_result
