from layouteagle.LayoutModel.layoutmodel import LayoutModeler
import logging
from layouteagle.pathant.Converter import converter


@converter("features", "keras")
class LayoutTrainer(LayoutModeler):
    def __init__(self,
                 *args,
                 model_path: str = '.layouteagle/layoutmodel',
                 debug: bool = True, **kwargs):
        super().__init__(*args, **kwargs)
        self.model_path = model_path + self.path_spec._to

        self.debug = debug

    def __call__(self, feature_path):
        if feature_path:
            self.feature_path, meta = next(feature_path)
        feature_df = self.load_pandas_file(self.feature_path)
        feature_columns, features_as_numpy = self.prepare_features(feature_df)
        history = self.train(feature_columns, self.train_kwargs)
        if self.debug:
            self.plot(history)
        self.validate()
        self.save()
        logging.info(f'made model, saved to {self.model_path}')
        yield self.model_path, meta


if __name__ == '__main__':
    pass
