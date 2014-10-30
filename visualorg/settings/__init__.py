import os

#from visualorg.settings.local import *

if 'IS_RUNNING_ON_HEROKU' in os.environ:
    #print 'Heroku environ detected'

    from .production import *
else:
    from .local import*
