import os.path
from Scrapper.scrapper import LaTimes
from workitems import INPUT

if __name__ == "__main__":
    if not os.path.exists(f"{os.getcwd()}/images"):
        os.mkdir(f"{os.getcwd()}/images")
    la_time = LaTimes(search=INPUT.search, topics=INPUT.topics, month_range=INPUT.month_range)
    la_time.start()
