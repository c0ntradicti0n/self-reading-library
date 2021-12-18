class Sampler:
    def __init__(self, sample_file):
        self.sample_file = sample_file
        self.read_library_f = self.start_reading_library()

    def add_to_library(self, text):
        with open(self.sample_file, 'a') as f:
            f.write(text)
            f.write('\n')

    def start_reading_library(self):
        with open(self.sample_file, 'r') as f:
            content = f.read()
            text = str(content).split(sep='\n')
            for line in text:
                yield line

    def deliver_sample(self):
        try:
            return next(self.read_library_f)
        except StopIteration:
            return next(self.read_library_f)

    def complicated_sample(self, text):
        with open("./server_complicated.txt", 'a+') as f:
            f.writelines([text]+['\n'])
