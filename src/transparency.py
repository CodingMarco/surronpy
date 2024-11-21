# Transparently import modules that are not available in micropython
try:
    from datetime import datetime as datetime_, date as date_
    import logging as logging_
except ImportError:
    from micropython_alternatives import (
        datetime as datetime_,
        date as date_,
        logging as logging_,
    )


datetime = datetime_
date = date_
logging = logging_
