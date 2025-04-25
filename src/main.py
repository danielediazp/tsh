import logging

from rich.console import Console
import time

from app import Tsh
from utils import csl_str_factory, CslStrStyleAttribute, ColorIndex

logging.basicConfig(
    level=logging.DEBUG,
    format="(%(asctime)s) %(levelname)s [%(filename)s:%(lineno)d]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="logs.txt",
    filemode="w",
)
LOGGER = logging.getLogger(__name__)


def main():

    try:
        csl = Console()
        Tsh(csl=csl)
        time.sleep(100)
    except KeyboardInterrupt:
        csl.clear()
        csl.print(
            csl_str_factory(
                "Program interrupted.", CslStrStyleAttribute.BOLD, ColorIndex(1)
            )
        )

    LOGGER.info("Program done executing!")


if __name__ == "__main__":
    main()
