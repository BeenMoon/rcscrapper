from collections import namedtuple
from concurrent.futures import ThreadPoolExecutor
import logging
import urllib.robotparser
import urllib.parse

from bs4 import BeautifulSoup
import requests



logging.basicConfig(level=logging.INFO, format="%(asctime)s:%(levelname)s:%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

class MyCrawler:
    def __init__(self, url, useragent='*'):
        self.urls = [url]
        self.useragent = useragent
        self.robot = namedtuple('Robot', ['can_fetch', 'crawl_delay', 'request_rate'])
        self.start = True
    
    def robot_check(self, url):
        o = urllib.parse.urlparse(url)
        base_url = f"{o.scheme}://{o.netloc}"
        robot_url = urllib.parse.urljoin(base_url, 'robots.txt')
        rp = urllib.robotparser.RobotFileParser(robot_url)
        rp.read()
        return self.robot(rp.can_fetch(self.useragent, url), rp.crawl_delay(self.useragent), rp.request_rate(self.useragent))
    
    def fetch_url(self, url):
        robot = self.robot_check(url)
        if not robot.can_fetch:
            logging.warning(f'{url}은 정책에 따라 크롤링할 수 없습니다.')
            return
        try:
            req = requests.get(url, timeout=10, allow_redirects=False)
            if req.status_code == 200:
                soup = BeautifulSoup(req.content, 'html.parser')
                if self.start:
                    for link in soup.find_all('a', href=True):
                        full_url = urllib.parse.urljoin(url, link['href'])
                        if full_url not in self.urls:
                            self.urls.append(full_url)
                    self.start = False
                return soup
            else:
                logging.error(f'{url}을 크롤링하는 중 상태 코드 {req.status_code}')
                logging.error(f'내용: {req.content}')
        except Exception as e:
            logging.error(f'{url}을 크롤링하는 중 오류 발생: {e}')
        return

    def crawl_urls(self, max_workers=10):
        result = []
        first = self.fetch_url(self.urls[0])
        if not first:
            return
        result.append(first)
        with ThreadPoolExecutor(max_workers) as executor:
            futures = {executor.submit(self.fetch_url, url): url for url in self.urls[1:]}
            for future in futures:
                try: 
                    res = future.result()
                    if res:
                        result.append(res)
                except Exception as e:
                    logging.error(f'URL 크롤링 중 오류 발생: {e}')
            return result



def main():
    crawler = MyCrawler('https://www.saramin.co.kr/zf_user/search?search_area=main&search_done=y&search_optional_item=n&searchType=recently&searchword=Airflow')
    pages = crawler.crawl_urls()
    if pages:
        for page in pages:
            logging.info(f"{page.find('title').get_text()}")

if __name__ == '__main__':
    main()
