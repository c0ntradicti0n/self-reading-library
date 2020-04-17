class Pipeline:
    def __init__(self, pipeline):
        self.pipeline = pipeline

    def __call__(self, arg):
        intermediate_result = arg
        for functional_object in self.pipeline:
            print(intermediate_result)
            if intermediate_result:
                intermediate_result = functional_object(intermediate_result)
            else:
                intermediate_result = functional_object()
        return intermediate_result
