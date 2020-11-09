from bs4 import BeautifulSoup
import requests
import yaml
import os
import re
import pandas as pd
from lib.url_helper import get_page_url
from lib.logger import *


class Spider:
    def __init__(self, path=os.path.join('config', 'config.yml')):
        with open(path, 'r+') as f:
            ctt = f.read()
            self.yml = yaml.load(ctt)
        self.session = requests.session()
        # 当列名含中文名无法对齐的问题
        # pd.set_option('display.unicode.ambiguous_as_wide', True)
        # pd.set_option('display.unicode.east_asian_width', True)

    def get_header(self, url):
        header = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/86.0.4240.75 Safari/537.36',
            'Connection': 'keep-alive',
            'Referer': url
        }
        return header

    def login(self):
        login_url, name, password = 'https://accounts.douban.com/j/mobile/login/basic', \
                                    str(self.yml['name']), self.yml['password']
        data = {'name': name,
                'password': password,
                'remember': True}

        headers = self.get_header(login_url)
        try:
            r = self.session.post(login_url, data=data, headers=headers)
            print(r.status_code)
            r.raise_for_status()
        except:
            print('登录失败')

    def get_top25(self):
        def get_parse(html):  # 进行解析
            parse = re.compile('<li.*?div.*?"item".*?<a.*?img.*?src="(.*?)"'
                               '.*?div.*?"info".*?span.*?"title">(.*?)</span>'
                               '.*?div.*?"bd".*?p.*?>(.*?)<br>', re.S)
            parse_over = re.findall(parse, html)
            for item in parse_over:
                yield {
                    "jpg": item[0].strip(),
                    "title": item[1].strip(),
                    "director": item[2].strip()
                }

        url = "https://movie.douban.com/top250?start=1"
        header = self.get_header(url)

        html = requests.get(url=url, headers=header).text
        items = get_parse(html)
        for item in items:
            print(item['title'])

    def crawl_and_analyze(self, pages=5, key='pwz|彭王者'):  # todo 分析爬取到的评论
        start_url = 'https://www.douban.com/group/613560/discussion?start='
        header = self.get_header(start_url)

        frames = []
        for i in range(1, pages):
            url = get_page_url(start_url, page=i)
            text = self.session.get(url=url, headers=header).text
            soup = BeautifulSoup(text, 'lxml')
            ans = soup.select('#content > div > div.article > div:nth-child(2) > table')
            if len(ans):
                content = ans[0]
                df = pd.read_html(str(content), header=0)[0]
                '''
                print('*' * 7 + str(i) + '*' * 7)
                print(df[['讨论', '回应']])
                print('*' * 7 + str(i) + '*' * 7)
                '''
                df = df.rename(columns={'讨论': 'theme', '回应': 'heat'})
                frames.append(df[['theme', 'heat']])

        result = pd.concat(frames).sort_values(by='heat', ascending=False)
        df = result.loc[result['theme'].str.contains(key, flags=re.IGNORECASE)]
        return df['heat'].sum()

    '''
    选取某一个讨论的评论
    '''

    def discuss_analyze(self):
        # 爬取某一帖子评论
        url = 'https://www.douban.com/group/topic/185741459/'
        header = self.get_header(url)
        text = self.session.get(url=url, headers=header).text
        soup = BeautifulSoup(text, 'lxml')
        comments = soup.select('#comments li ')
        for comment in comments:
            print(comment.find(class_='reply-doc content').find('p').get_text())
            print('*' * 10)

    def analyze_kol_discuss(self):
        url = 'https://www.douban.com/group/topic/199639514/'
        header = self.get_header(url)
        text = self.session.get(url, headers=header).text
        soup = BeautifulSoup(text, 'lxml')
        comments = soup.find('ul', id='comments').find_all('li')
        for comment in comments:
            ctx = comment.find('p').get_text()
            print(ctx)

        # print(hrefs)
        # for href in hrefs:
        #     print(href)

    def click_then_analyze(self):
        def contains(content, keys):
            import re
            for key in keys:
                if not bool(re.search(content, key, re.IGNORECASE)):
                    return False
            return True

        url = 'https://www.douban.com/group/613560/discussion?start=50'
        header = self.get_header(url=url)
        text = self.session.get(url, headers=header).text
        soup = BeautifulSoup(text, 'lxml')
        # todo 查找对应评论id，然后点击url，然后统计评论
        links = []
        trs = soup.find('table', attrs={'class': 'olt'}).find_all('tr')
        for tr in trs:
            if tr.td.a and contains(tr.td.a.string, ['pwz', '彭王者']):
                print(tr.td.a.string)
                links.append(tr.td.a.attrs['href'])


if __name__ == '__main__':
    '''
    分析彭王者
    spider = Spider()
    result = spider.crawl()
    print(spider.analyze(result))
    '''
    # Spider().discuss_analyze()
    # Spider().analyze_kol_discuss()

    Spider().click_then_analyze()
