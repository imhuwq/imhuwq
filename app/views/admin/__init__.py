from flask import Blueprint

admin = Blueprint('admin', __name__)

from .main import *
from .blog import *
