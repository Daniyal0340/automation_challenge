from RPA.Robocorp.WorkItems import WorkItems

from Scrapper import logger

try:
    work_items = WorkItems()
    work_items.get_input_work_item()
    work_item = work_items.get_work_item_variables()
    logger.info(f"Work items data {work_item}")


    class INPUT:
        search = work_item.get('search', 'Imran Khan')
        month_range = work_item.get('months', 0)
        topics = work_item.get('topics', 'Sports')
except KeyError:
    class INPUT:
        search = "Pakistan"
        month_range = 1
        topics = 'Sport'
