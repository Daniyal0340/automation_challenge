import os.path

from RPA.Robocorp.WorkItems import WorkItems
from Scrapper import logger
from Scrapper.scrapper import LaTimes

try:
    work_items = WorkItems()
    work_items.get_input_work_item()
    work_item = work_items.get_work_item_variables()
    logger.info(f"Work items data {work_item}")
    search = work_item.get('search', 'Imran Khan')
    month_range = work_item.get('months', 0)
    topics = work_item.get('topics', 'Sports')
except KeyError:
    search = "Imran Khan"
    month_range = 0
    topics = 'Sports'

if __name__ == "__main__":
    if os.path.exists(f"{os.getcwd()}/images"):
        os.mkdir(f"{os.getcwd()}/images")
    la_time = LaTimes(search=search, topics=topics, month_range=month_range)
    la_time.start()
