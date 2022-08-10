import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = True
    MEDIA_FOLDER = os.path.join(basedir, 'media')
