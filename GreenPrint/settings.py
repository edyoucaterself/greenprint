#Import Custom Settings
import sys
sys.path.insert(0,"/etc/default")
import pp_settings

#Load settings dependent on enviroment
if pp_settings.ENVIRONMENT == 'PROD':
    from .settings_prod import *
else:
    from .settings_dev import *
