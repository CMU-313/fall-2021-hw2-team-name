from __future__ import unicode_literals

import platform

if platform.system() == 'OpenBSD':
    DEFAULT_PDFTOTEXT_PATH = '/usr/local/bin/pdftotext'
else:
    DEFAULT_PDFTOTEXT_PATH = '/usr/bin/pdftotext'
