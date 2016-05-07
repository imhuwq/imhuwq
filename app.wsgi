#! /usr/bin/python3

import sys
import logging

logging.basicConfig(stream=sys.stderr)
sys.path.insert(0, '/home/john/Labs/imhuwq/')

activate_this = '/home/john/Labs/imhuwq/env/bin/activate_this.py'
exec(open(activate_this).read())

from manage import app as application
