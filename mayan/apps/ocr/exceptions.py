from __future__ import unicode_literals


class OCRError(Exception):
    """
    Raised by the OCR backend for unexpected events that stop the
    OCR processing.
    """
