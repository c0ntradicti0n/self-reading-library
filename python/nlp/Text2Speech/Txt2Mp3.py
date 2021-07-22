import os
from pprint import pprint

from ant import Ant
from layouteagle.pathant.Converter import converter
from layouteagle.pathant.PathAnt import PathAnt
from layouteagle.pathant.PathSpec import cache_flow


@converter('txt', 'mp3')
class Txt2Mp3(Ant):
    def __init__(self, debug=True, *args, n=15, **kwargs):
        super().__init__(*args, cached=cache_flow.iterate, **kwargs)
        self.n = n
        self.debug = debug

    def __call__(self, iterator, *args, **kwargs):
        for txt, meta in iterator:
            meta['mp3_path'] = meta['txt_path'] + 'mp3'
            os.popen(f"text2wave -eval  '(voice_cmu_us_slt_arctic_hts)'  {meta['txt_path']} -o out.wave").read()
            os.popen(f"lame {meta['txt_path']} {meta['mp3_path']}").read()
            yield txt, meta


if __name__ == "__main__":
    ant = PathAnt()
    print (ant.graph())
    pipe = ant("pdf", "mp3")
    res = list(pipe("test/glue.pdf"))
    pprint(res)
    os.popen(f"mplayer {res['mp3_path']}").read()




