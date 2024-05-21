import json


class PrintAndSave(object):
    def __init__(self, file_path, also_print):
        self.file_path = file_path
        self.also_print = also_print
        self.outfile = open(self.file_path, 'w')

    def output(self, out_string, end=None):
        if self.also_print:
            print(out_string, flush=True, end=end)
        self.outfile.write(out_string)

    def output_json(self, out_string, header=None, end=None):
        json_object = json.loads(out_string)
        json_formatted_str = json.dumps(json_object, indent=2)
        if header:
            self.output(f"\n\n{header}\n")
        self.output(json_formatted_str, end=end)
    def close(self):
        self.outfile.close()
