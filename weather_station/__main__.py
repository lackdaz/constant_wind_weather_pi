import logging
from logging.handlers import RotatingFileHandler
from logging import StreamHandler
import sys

from weather_station.data_handler import poll

logger = logging.getLogger(__name__)


def main(sleep):
    # create any necessary instances
    try:
        pass
    except FileNotFoundError as e:
        if True:
            logger.error(e)
            try:
                pass
            except FileNotFoundError:
                pass
        else:
            raise
    # Add blocking process here
    poll(sleep=sleep)


def cli_main() -> int:
    """command line entrypoint"""
    import argparse

    ap = argparse.ArgumentParser(
        description="",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    ap.add_argument(
        "sleep",
        type=int,
        help="how often to send data?",
    )

    # configure logging
    ap.add_argument(
        "-v",
        "--verbose",
        help="print DEBUG log level",
        action="store_true",
    )

    args = ap.parse_args()
    # configure logging
    logging.basicConfig(
        handlers=[
            RotatingFileHandler(
                filename="event.log",  # TODO: hardcoded
                mode="w",
                maxBytes=512000,
                backupCount=4,
            ),
            StreamHandler(sys.stdout),
        ],
        level=logging.DEBUG if args.verbose else logging.INFO,
        datefmt="%Y-%m-%d %H:%M:%S",
        format="%(asctime)s.%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d] %(message)s",  # noqa
    )
    del args.verbose

    return main(**vars(args))


if __name__ == "__main__":
    weather_station = cli_main()
    sys.exit()
