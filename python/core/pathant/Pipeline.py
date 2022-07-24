import itertools
import logging

from helpers.time_tools import timeit_context
from core.pathant.parallel import paraloop

class Pipeline:
    def __init__(self, pipeline, source, target, extra_paths, via=None, **flags):
        self.extra_paths = extra_paths
        self.target = target
        self.source = source
        self.pipeline = pipeline
        self.flags = flags
        self.via = via
        self.dummy_generator = itertools.cycle([("dummy", {"meta": None})])

    def log_progress(self, gen, *args, name='unknown', logger=print, **kwargs):
        try:
            for x in gen:
                msg = f"Pipeline step {name} running on result: '''{str(x)[:100]}...'''"
                with timeit_context(msg, logger=logger):
                    yield x
        except TypeError as e:
            logger(f"{name} finished")

    def __call__(self, arg, **flags):
        intermediate_result = arg

        for functional_object in self.pipeline:
            self.flags.update(flags)
            functional_object.flags = self.flags if self.flags else flags

            name = functional_object.__class__.__name__
            start_message = f"Pipeline object '{name}' is started"
            logger = functional_object.logger.info if hasattr(functional_object, 'logger') else print
            logger(start_message)

            try:
                try:
                    if functional_object in self.extra_paths:
                        others = self.extra_paths[functional_object]
                        others = [other(self.dummy_generator) for other in others]


                        intermediate_result = functional_object(intermediate_result, *others)
                    elif intermediate_result != None:
                        intermediate_result = functional_object(intermediate_result)
                    else:
                        intermediate_result = functional_object()
                except Exception as e:
                    print(functional_object)
                    raise e
            except RuntimeError as e:
                logging.error(f"StopIteration {e} raised between {functional_object} and {intermediate_result}")
                raise e

            intermediate_result = intermediate_result

        return intermediate_result

    def __add__(self, other):

        new_pipe = Pipeline(
            pipeline=self.pipeline + other.pipeline,
            source=self.source,
            target=other.target,
            extra_paths={**self.extra_paths, **other.extra_paths}

        )
        new_pipe.flags = {**self.flags, **other.flags}
        return new_pipe

