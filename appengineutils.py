# -*- coding: utf-8 -*-

import os

def is_dev_server():
    if os.environ.get('SERVER_SOFTWARE','').startswith('Development'):
        return True
    else:
        return False
