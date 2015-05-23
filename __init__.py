
from . import gui, srv
from util.columns import *
from util.misc import app_devtypes, app_devdata

devdata = lambda: app_devdata('FIO', get_columns([c_ip_addr]), app_devtypes(gui))

