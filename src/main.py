import logging

from rich.console import Console
import time

from app.app import TshStates
from utils.csl_str_factory import csl_str_factory, CslStrStyleAttribute, ColorIndex
from app.menu import MainMenu
from utils.models import Task

logging.basicConfig(
    level=logging.DEBUG,
    format="(%(asctime)s) %(levelname)s [%(filename)s:%(lineno)d]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename="logs.txt",
    filemode="w",
)
LOGGER = logging.getLogger(__name__)


# TODO: Get rid of this, this is a func for UI testing purposes.
def fetch_task_data():
    from datetime import datetime

    """
    A sample function that fetches data from the database and returns a list of Task objects.
    """
    tasks = [
        Task(id=i, title=f"Task {i}", description="some", created_at=datetime.now())
        for i in range(25)
    ]
    return tasks


def main():

    try:
        csl = Console()
        m_menu = MainMenu(
            csl=csl,
            fetch_data=fetch_task_data,
        )
        TshStates.add_new_state(m_menu)
        
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
