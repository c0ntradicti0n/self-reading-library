import glob

from config import config
from helpers.model_tools import find_best_model

print(find_best_model(config.TEXT_BOX_MODEL_PATH)[0])
