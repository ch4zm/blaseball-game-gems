import sys
import json
from .parser import DataParser


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
        gems = self.parser.parse()

        # ---------------
        # game info
        print("")
        print("\n".join(self.text_info_header(gems)))
        print("")

        # ---------------
        # box score
        print("")
        print("\n".join(self.text_box_score(gems)))
        print("")

        # ---------------
        # gems
        print("")
        print("\n".join(self.text_gems(gems)))
        print("")

    def text_info_header(self, d):
        info_header = []
        info_header.append("Game ID: %s"%(d['info']['id']))
        info_header.append("Season %d Day %d:"%(d['info']['season'], d['info']['day']))
        info_header.append("%s @ %s"%(
            d['info']['awayTeamName'],
            d['info']['homeTeamName'],
        ))
        info_header.append(d['info']['stadium'])
        info_header.append("Weather: %s"%(d['info']['weather']))
        return info_header

    def text_box_score(self, d):
        """Make a box score for a text view"""
        box_score = []

        def _make_box_score_row_text(name, row):
            rowstr = ""
            rowstr += "| %-20s | "%(name)
            for i in range(3):
                rowstr += "%3d | "%(row[i])
            return rowstr

        def _make_box_header_row_text():
            header = "| %20s |  R  |  H  |  E  |"%(" ")
            return header

        box_score.append("-"*42)
        box_score.append(_make_box_header_row_text())
        box_score.append("-"*42)
        box_score.append(_make_box_score_row_text(d['info']['awayTeamNickname'], d['box_score']['away']))
        box_score.append("-"*42)
        box_score.append(_make_box_score_row_text(d['info']['homeTeamNickname'], d['box_score']['home']))
        box_score.append("-"*42)

        return box_score

    def text_gems(self, d):
        gem_list = []
        gem_list.append("Blaseball Game Gems:")
        gem_list.append("")
        for gem in d['gems']:
            gem_list.append("* "+gem['gem_description'])
        return gem_list


class MarkdownView(TextView):
    def show(self):
        gems = self.parser.parse()

        # ---------------
        # game info
        print("")
        print("\n\n".join(self.md_info_header(gems)))
        print("")

        # ---------------
        # box score
        print("")
        print("\n".join(self.md_box_score(gems)))
        print("")

        # ---------------
        # gems
        print("")
        print("\n".join(self.md_gems(gems)))
        print("")

    def md_info_header(self, d):
        return self.text_info_header(d)

    def md_box_score(self, d):
        box_score = []

        def _make_box_score_row_md(name, row):
            rowstr = ""
            rowstr += "| %s | "%(name)
            for i in range(3):
                rowstr += "%3d | "%(row[i])
            return rowstr

        def _make_box_header_row_md():
            header = "|  | R | H | E |"
            return header

        def _make_box_header_sep_md():
            sep = "| --- | --- | --- | --- |"
            return sep

        box_score.append(_make_box_header_row_md())
        box_score.append(_make_box_header_sep_md())
        box_score.append(_make_box_score_row_md(d['info']['awayTeamNickname'], d['box_score']['away']))
        box_score.append(_make_box_score_row_md(d['info']['homeTeamNickname'], d['box_score']['home']))

        return box_score

    def md_gems(self, d):
        return self.text_gems(d)
