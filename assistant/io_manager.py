

class PrintAndSave(object):
    def __init__(self, file_path, also_print):
        self.file_path = file_path
        self.also_print = also_print
        self.outfile = open(self.file_path, 'w')

    def output(self, out_string, end=None):
        if self.also_print:
            print(out_string, flush=True, end=end)
        self.outfile.write(out_string)

    def close(self):
        self.outfile.close()
