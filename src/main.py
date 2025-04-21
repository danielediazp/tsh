import logging

from rich.console import Console

from app import Menu

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
        m = Menu(csl)
        m.run()
    except KeyboardInterrupt:
        csl.clear()
        csl.print("[bold red]Program interrupted.[/bold red]")

    LOGGER.info("Program done executing!")


if __name__ == "__main__":
    main()
