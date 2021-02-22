
model_config = "elmo_multi_head_self_attention_crf_straight_fitter.config"
parse_pdf2htmlEX = True

recursive = True
max_len = 200
NORMAL_HEIGHT = 100
page_array_model = 100

doc_port        = 5180
app_port        = 5181
annotation_port = 5182
science_port    = 5183

hidden_folder = ".layouteagle/"
cache = hidden_folder + "cache/"
tex_data = hidden_folder + "tex_data/"
models = hidden_folder + "models/"



tex_source = "http://arxiv.org"

INDEX_WRAP_TAG_NAME = 'z'

log_files = {
    "ccapp": "./CorpusCookApp/log.log",
    "cc": "../CorpusCook/log.log",
    "dist": "../Distinctiopus4/log.log"
}

new_corpus_increment = "../CorpusCook/server/corpus/"
cc_corpus_collection_path = "../CorpusCook/manually_annotated/"
cc_corpus_working_path = "../CorpusCook/server/corpus/"
dist_corpus_path = "../Distinctiopus4/manual_corpus/"

appcorpuscook_docs_json_dir = "../CorpusCookApp/pdfs/"
appcorpuscook_docs_html_dir = "../pdfetc2txt/docs/htmls/"
appcorpuscook_docs_document_dir  = "../pdfetc2txt/docs/pdfs/"
appcorpuscook_docs_txt_dir  = "../pdfetc2txt/docs/txts/"

appcorpuscook_diff_json_dir = "../CorpusCookApp/htmls/"
appcorpuscook_diff_html_dir = "../pdfetc2txt/scraped_difference_between/htmls/"
appcorpuscook_diff_document_dir  = "../pdfetc2txt/scraped_difference_between/download/"
appcorpuscook_diff_txt_dir  = "../pdfetc2txt/scraped_difference_between/txts/"

apache_dir_document = "../apache-tomcat-9.0.30/webapps/corpuscow/document/"
apache_css_dir = "../apache-tomcat-9.0.30/webapps/corpuscow/resources/document_css/"

mixer_path = "../CorpusCook/manually_annotated/mix_corpus_from_manual_files.py"
mixer_working_dir =  "../CorpusCook/"
corpuscook_venv = "../CorpusCook/venv/bin/activate"

science_map_corpus_path="../ScienceMap/manual_corpus/"
science_map_working_dir="../ScienceMap/"
science_map="../ScienceMap/GUI.py"
science_map_venv="../ScienceMap/venv/bin/activate"
science_map_csv="../ScienceMap/manual_corpus/relations.csv"

ampligraph_working_dir="../KnowledgeScience/"
ampligraph_venv="../KnowledgeScience/venv/bin/activate"
ampligraph="../KnowledgeScience/csv_ampligraph.py"
ampligraph_coords="CONSTRASTSUBJECT"

train_venv_python = "../Distinctiopus4/venv/bin/activate"
train_path= "../Distinctiopus4"
train_script= "../Distinctiopus4/do/train_multi_corpus.py"
train_log = "train.log"
allennlp_config = f"../Distinctiopus4/experiment_configs/{model_config}"

dist_model_path_first = "../Distinctiopus4/output/first_./experiment_configs/{config}/model.tar.gz".format(config=allennlp_config)
cc_model_path_first   = "../CorpusCook/server/models/model_first.tar.gz"
dist_model_path_over  = "../Distinctiopus4/output/over_./experiment_configs/{config}/model.tar.gz".format(config=allennlp_config)
cc_model_path_over    = "../CorpusCook/server/models/model_over.tar.gz"

all_coordinates="../KnowledgeScience/knowledge_graph_coords/knowledge_graph_3d_choords.csv"
ke_path=  "../KnowledgeScience/knowledge_graph_coords/tsne_clusters_mean_points.csv"
ke_colors="../KnowledgeScience/knowledge_graph_coords/kn_clusters_mean_points.csv"
hal = '"../hal/target/hal-1-jar-with-dependencies.jar"'
video_dir = '../view_control_web/WebContent/resources/media/'

wordlist = '../pdfetc2txt/wordlist.txt'

reader_width = 700
import numpy
reader_height = numpy.sqrt(2) * reader_width

page_margin_bottom = 0.06
page_margin_top = 0.15

pdf_dir = "../test/"
topics_dump = "./topics.pickle"
markup_dir = pdf_dir
markup_suffix = "pdflayout.html"

pdf2htmlEX = "/home/finn/CLionProjects/pdf2htmlEX-1/pdf2htmlEX/build/pdf2htmlEX"

corpus_conll = '/home/stefan/PycharmProjects/LayoutEagle/data/first.conll3'
difference_model_train_output = hidden_folder + f"/first_{model_config}/"
difference_model_config = hidden_folder + f"/first_{model_config}/config.json"

wordninjalanguagemodel = "nlp/english.txt.gz"