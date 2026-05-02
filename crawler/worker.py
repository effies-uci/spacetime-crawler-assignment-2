from threading import Thread

from inspect import getsource

import reports
from utils.download import download
from utils import get_logger
import scraper
import time


class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        # basic check for requests in scraper
        assert {getsource(scraper).find(req) for req in {"from requests import", "import requests"}} == {-1}, "Do not use requests in scraper.py"
        assert {getsource(scraper).find(req) for req in {"from urllib.request import", "import urllib.request"}} == {-1}, "Do not use urllib.request in scraper.py"
        super().__init__(daemon=True)
        
    def run(self):
        self.logger.info("Starting thread")
        while True:
            tbd_url = self.frontier.get_tbd_url()
            if not tbd_url:
                self.logger.info("Frontier is empty. Stopping Crawler.")
                reports.write_total_report(scraper.word_freq, scraper.unique_urls,
                                           scraper.unique_subdomains, scraper.page_lens)
                break
            resp = download(tbd_url, self.config, self.logger, self.config.time_delay)

            if resp is None: # domain was too recently requested
                self.logger.info(f"Domain from {tbd_url} was requested too recently.")
                # put url back into frontier to try again later
                self.frontier.put_back_tbd_url(tbd_url)
                continue

            # if the domain is downloaded successfully:
            self.logger.info(
                f"Downloaded {tbd_url}, status <{resp.status}>, "
                f"using cache {self.config.cache_server}.")
            scraped_urls = scraper.scraper(tbd_url, resp, self.logger)
            for scraped_url in scraped_urls:
                self.frontier.add_url(scraped_url)
            self.frontier.mark_url_complete(tbd_url)

