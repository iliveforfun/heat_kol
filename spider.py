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

    def login(self):
        login_url, name, password = 'https://accounts.douban.com/j/mobile/login/basic', \
                                    str(self.yml['name']), self.yml['password']
        data = {'name': name,
                'password': password,
                'remember': True}
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/86.0.4240.75 Safari/537.36',
            'Connection': 'keep-alive',
            'Referer': login_url
        }
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
        headers = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/86.0.4240.75 Safari/537.36',
            'Connection': 'keep-alive',
            'Referer': url
        }
        html = requests.get(url=url, headers=headers).text
        items = get_parse(html)
        for item in items:
            print(item['title'])

    def crawl(self, pages=5):  # todo 分析爬取到的评论
        start_url = 'https://www.douban.com/group/613560/discussion?start='
        header = {
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.8',
            'Cache-Control': 'max-age=0',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/86.0.4240.75 Safari/537.36',
            'Connection': 'keep-alive',
            'Referer': start_url
        }
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
        return pd.concat(frames).sort_values(by='heat', ascending=False)

    '''
    返回目标kol的热度值
    '''
    def analyze(self, result, key='pwz|彭王者'):
        df = result.loc[result['theme'].str.contains(key, flags=re.IGNORECASE)]
        return df['heat'].sum()
        # todo 词云分析， 再按列排序, 这里默认是拿彭王者的数据


if __name__ == '__main__':
    spider = Spider()
    result = spider.crawl()
    print(spider.analyze(result))
