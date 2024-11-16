# Transparently import modules that are not available in micropython
try:
    from datetime import datetime as datetime_, date as date_
except ImportError:
    from micropython_alternatives import datetime as datetime_, date as date_


datetime = datetime_
date = date_
