import logging
import sys

def setup_logging(log_file='data.log', level=logging.DEBUG):
    logger = logging.getLogger()
    logger.setLevel(level)

    # Replace only our own handlers when setup is called again.
    for handler in logger.handlers[:]:
        if getattr(handler, "_scanner_handler", False):
            logger.removeHandler(handler)
            handler.close()

    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
    #s is setting as a string rather than not
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    #Calling the handler's setFormatter method to assign the formatter we created

    for handler in (file_handler, console_handler):
        handler._scanner_handler = True
        logger.addHandler(handler)
