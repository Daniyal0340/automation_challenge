from RPA.Robocorp.WorkItems import WorkItems

from Scrapper.scrapper import LaTimes

try:
    work_items = WorkItems()
    work_items.get_input_work_item()
    work_item = work_items.get_work_item_variables()
    latest_work_item = work_item.get("variables", dict())
    search = latest_work_item.get('search', 'Imran Khan')
    months = latest_work_item.get('months', 0)
    topics = latest_work_item.get('topics', 'Sports')
except Exception:
    search = "Imran Khan"
    months = 0
    topics = 'Sports'

if __name__ == "__main__":
    la_time = LaTimes(search=search)
    la_time.start()
