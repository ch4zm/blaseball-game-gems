import sys
import json
from parser import DataParser


class BaseView(object):
    """
    Loads the JSON the user points to,
    and then looks for gems
    """
    def __init__(self, options):
        self.parser = DataParser(options)

class JsonView(BaseView):
    def show(self):
        d = self.parser.parse()
        print(json.dumps(d, indent=4))

class TextView(BaseView):
    def show(self):
        pass

