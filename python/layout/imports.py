import os
import shutil
from pprint import pprint, pformat
import pandas
import torch
from matplotlib import colors
from torch.utils.data import DataLoader
from datasets import load_metric
from GPUtil import showUtilization as gpu_usage
from sklearn.preprocessing import MinMaxScaler
from datasets import Dataset
from PIL import Image, ImageFilter
from transformers import LayoutLMv2Processor
from datasets import Features, Sequence, ClassLabel, Value, Array2D, Array3D
from transformers import LayoutLMv2ForTokenClassification, AdamW
import torch
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageFont

font = ImageFont.load_default()
