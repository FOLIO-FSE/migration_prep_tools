import logging
import logging.handlers
import time
import os


@staticmethod
def print_dict_to_md_table(my_dict, h1="", h2=""):
    d_sorted = {k: my_dict[k] for k in sorted(my_dict)}
    for k, v in d_sorted.items():
        logging.info(f"{k} | {v}")


def setup_logging(class_name="", log_file_path: str = None, time_stamp=None):
    if not time_stamp:
        time_stamp = time.strftime("%Y%m%d-%H%M%S")
    logger = logging.getLogger()
    logger.handlers = []
    formatter = logging.Formatter("%(levelname)s\t%(message)s\t%(asctime)s")
    stream_handler = logging.StreamHandler()
    logger.setLevel(logging.INFO)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)
    print(f"LFP:{log_file_path}")
    if log_file_path:
        log_file = os.path.join(
            log_file_path, f"service_task_log_{class_name}_{time_stamp}.log"
        )
        logging.info(f"Writing log file to {log_file}")
        file_formatter = logging.Formatter(
            "%(levelname)s\t%(message)s\t%(asctime)s"
        )
        file_handler = logging.FileHandler(
            filename=log_file,
        )
        # file_handler.addFilter(LevelFilter(0, 20))
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.INFO)
        logging.getLogger().addHandler(file_handler)
    else:
        logging.info("no path, no logfile")
    logger.info("Logging setup")

    if log_file_path:
        debug_log_file = os.path.join(
            log_file_path, f"service_task_debug_log_{class_name}_{time_stamp}.log"
        )
        logging.info(f"Writing DEBUG log files to {debug_log_file}")
        debug_file_formatter = logging.Formatter(
            "%(levelname)s\t%(message)s\t%(asctime)s"
        )
        debug_file_handler = logging.FileHandler(
            filename=debug_log_file,
        )
        # file_handler.addFilter(LevelFilter(0, 20))
        debug_file_handler.setFormatter(debug_file_formatter)
        debug_file_handler.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(debug_file_handler)
    else:
        logging.info("no path, no logfile")
    logger.info("Logging setup")
