import os

from core.pathant.Converter import converter
from config import config
from layout.latex.LayoutModel.layoutmodel import LayoutModeler


@converter("features", "keras")
class LayoutTrainer(LayoutModeler):
    def __init__(self,
                 *args,
                 model_path: str = config.layout_model_path,
                 debug: bool = True, **kwargs):
        super().__init__(*args, **kwargs, model_path=model_path)
        self.debug = debug

    def __call__(self, feature_path):
        if not os.path.isdir(self.model_path) or not os.path.exists(self.model_path + "/saved_model.pb"):
            if feature_path:
                self.feature_path, meta = next(feature_path)
            feature_df = self.load_pandas_file(self.feature_path)
            self.prepare_features(feature_df, training=True)
            history = self.train(self.train_kwargs)
            if self.debug:
                self.plot(history)
            self.validate()
            self.logger.info(f'made model, saved to {self.model_path}')
            yield self.model_path, meta
        else:
            self.logger.info("skippped training, because model exists")


if __name__ == '__main__':
    pass
