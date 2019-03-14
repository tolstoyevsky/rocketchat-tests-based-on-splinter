import os

from xvfbwrapper import Xvfb


class XvfbWrap(Xvfb):
    def _get_next_unused_display(self):
        display = super()._get_next_unused_display()
        if 'XVFB_DISPLAY' in os.environ:
            try:
                return os.environ['XVFB_DISPLAY'].split(':')[1]
            except IndexError:
                raise OSError("Invalid XVFB_DISPLAY variable, "
                              "use :display_number format")
        else:
            return display
