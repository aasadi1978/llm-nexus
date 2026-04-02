import logging
from linecache import checkcache, getline
from os import path as os_path
from sys import exc_info

def log_exception(message=None, **kwargs):

    remarks = kwargs.get('remarks', 'ERROR:')
    level = str(kwargs.get('level', 'error')).lower()

    if message is not None:
        remarks = f'{remarks} {message}'

    try:
        exc_type, exc_obj, tb = exc_info()

        if tb is None:
            return 'sys.exc_info() returned None, no traceback available'
        
        f = tb.tb_frame
        lineno = tb.tb_lineno
        filename = f.f_code.co_filename
        checkcache(filename)
        line = getline(filename, lineno, f.f_globals)

        # str_now = dt_datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f'{remarks}: ({os_path.basename(filename)}, LINE {lineno} "{line.strip()}")(|): {exc_obj}'

        logging.log(getattr(logging, level.upper(), logging.ERROR), message)

        return message.split('(|):')[1]

    except Exception as err:
        logging.error(f'Error in log_exception: {str(err)}')
        return str(err)

