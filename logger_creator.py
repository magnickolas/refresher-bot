import logging
import sys
from typing import IO
from typing import Optional


def get_logger(
    *,
    logger_name: str,
    filename: Optional[str] = None,
    stream: Optional[IO[str]] = sys.stdout,
    add_to_all: bool = True,
):
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    if filename:
        filehandler = logging.FileHandler(filename=f"logs/{filename}")
        filehandler.setFormatter(formatter)
        logger.addHandler(filehandler)
    if stream:
        streamhandler = logging.StreamHandler(stream)
        streamhandler.setFormatter(formatter)
        logger.addHandler(streamhandler)
    if add_to_all:
        all_file_handler = logging.FileHandler(filename="logs/all_logs.log")
        all_file_handler.setFormatter(formatter)
        logger.addHandler(all_file_handler)

    return logger
