import time

from main.Tools.TimeTools import TimeTools


class OutputFormater:
    @staticmethod
    def get_format_output(output_type, content):
        return "[{0}|{1}]:{2}".format(TimeTools.getLocalTime(), output_type, content)