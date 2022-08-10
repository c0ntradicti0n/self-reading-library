from core.rest.AnnotationPublisher import DifferenceAnnotationPublisher
from core.rest.DifferencePublisher import DifferencePublisher
from core.standard_converter import PATH2HTML
from config.config import PORT
from core.pathant.PathAnt import PathAnt
from core.pathant.AntPublisher import AntPublisher
from core.pathant.ConfigRest import ConfigRest
from core.layout_eagle import LayoutEagle
from core.standard_converter.Scraper import Scraper
from core.standard_converter.HTML2PDF import HTML2PDF
#from core.standard_converter.PDF2HTML import PDF2HTML
from helpers.list_tools import metaize, forget_except
from helpers.model_tools import TRAINING_RATE
from language.text2speech.AudioPublisher import AudioPublisher
from topics.TopicsPublisher import TopicsPublisher
from layout.annotator.annotation import Annotator, AnnotationQueueRest
from layout.upload_annotation.upload_annotation import UploadAnnotator
from layout.upload_annotation.upload_annotation import UploadAnnotator
from layout.annotation_thread import layout_annotate_train_model, UploadAnnotationQueueRest, sample_pipe, model_pipe, \
    upload_pipe, full_model_path
from language.PredictionAlignment2Css import PredictionAlignment2Css
from layout.Layout2ReadingOrder import Layout2ReadingOrder
from language.transformer.ElmoDifference import ElmoDifference, ElmoDifferenceQueueRest, elmo_difference_pipe, \
    elmo_difference_model_pipe, annotate_difference_elmo
from language.text2speech.Txt2Mp3 import Txt2Mp3

# from language.heuristic.heuristic_difference import HeurisiticalLogician
