<<<<<<< HEAD
from .settings_prod import *
=======
#Import Custom Settings
import sys
sys.path.insert(0,"/etc/default")
import pp_settings

#Load settings dependent on enviroment
if pp_settings.ENVIRONMENT == 'PROD':
    from .settings_prod import *
else:
    from .settings_dev import *
>>>>>>> 5fb675af9ef2d6eb72456b19e1b0e5a97400f039
