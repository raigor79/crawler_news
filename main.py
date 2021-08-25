import re
import os
import sys
import asyncio
from datetime import datetime, time, timedelta
from typing import Optional, Union
import aiohttp
from loguru import logger
import aiofiles
from aiofiles.threadpool import text
from bs4 import BeautifulSoup
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
from wordcloud import WordCloud


USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0'
parametrs_parser = {
    'key_word': 'Russia',
    'language': 'en',
    'period': '1y',
    'region': 'US'    
}
template_article = r'./articles/.+'


logger.add(
        sys.stderr, 
        format="{time} {level} {message}", 
        filter="my_module", 
        level="INFO"
        )


class ValidationError(Exception):...


def make_dir(path: str) -> None:
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except OSError:
            logger.error("Create directories {} failed".format(path))


async def save_page_news(path_dir: str, file_name: str, text_page: text) -> None:
    make_dir(path_dir)
    async with aiofiles.open(path_dir + '/' + file_name, 'wb') as file:
            await file.write(text_page)


def parsing_text_by_param(html_text: text, param: str='html.parser'):
    page = BeautifulSoup(str(html_text), param)
    return page


def check_date_publication(date: str, last_period: Union[int, str]=30, date_format: str="%Y-%m-%dT%H:%M:%SZ") -> True:
    """function to check date publication, it includes or not at last period in days.
    date - must be string in format date_format
    last_period - must be integer, number of days or str ['day', 'month', 'year'] 
    """
    period = {'year': 365, 'month': 30, 'day': 1}    
    date_now = datetime.now()
    try:
        date_pub = datetime.strptime(date, date_format)    
    except TypeError:
        raise ValidationError('Error transform date')  
    if isinstance(last_period, int):
        return True if 0 <= (date_now - date_pub).days <= last_period else False
    range_date = timedelta(days=period[last_period])
    date_boarder = date_now - range_date
    if last_period in ('year', 'month'):
        date_boarder.day = date_now.day
    return True if  date_boarder <= date_pub <= date_now else False


def parsing_page(text: str) -> set[str]:
    soup = parsing_text_by_param(text)
    refs = set()
    for link in soup.body.findAll('article'):
        date = r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z"
        url = r"(href=\"\.)(/[\S]*)(\" )"        
        string_date_publication = re.search(date, str(link))
        if check_date_publication(string_date_publication.group()):
            publication = re.search(url, str(link))
            refs.add(publication.groups()[1])

    return refs


async def fetch_page(client: aiohttp.ClientSession, url: text) -> text:
    data = b''
    try:
        async with client.get(url) as resp:
            buffer = b''
            async for dline, _ in resp.content.iter_chunks():
                buffer += dline
            data = buffer[:]
    except Exception:
        pass
    return data


def generate_name_file_from_url(url: str) -> str:
    simbs = [ '\\', '/', ':', '*', '?', '"', '<', '>', '|', '+', '!', '%', '@', '~', '-']
    for simb in simbs:
        if simb in url:
            url = url.replace(simb, '')
    len_name_file = 60  if len(url) > 60 else len(url)
    return url[:len_name_file]


async def load_news_pages(client, root_page: str, resl: set) -> None:
    tasks_load, tasks_reload = [], []
    html_texts, urls = [], []
    for index, value in tqdm(enumerate(resl)):
        tasks_load.append(
            asyncio.create_task(
                fetch_page(
                    client, 
                    root_page + str(value)
                    )
                )
            )
        html_texts.append(await tasks_load[index])       
    await asyncio.gather(*tasks_load)

    logger.info(f'Pre-Loaded {len(html_texts)} refs')

    for html_text in tqdm(html_texts):
        page = parsing_text_by_param(html_text.decode('utf-8'))
        urls.append(str(page.body.findAll('a')[-1].get('href')))
            
    html_texts = []
    for index, url in tqdm(enumerate(urls)):
        logger.info(url)
        tasks_reload.append(asyncio.create_task(fetch_page(client, url)))        
        html_texts.append(await tasks_reload[index])
        await save_page_news(
            './news', str(index) + generate_name_file_from_url(url) + '.html', 
            html_texts[index]
            )
    await asyncio.gather(*tasks_reload)
    
    logger.info(f'Loaded {len(html_texts)} news refs')

    titles = []
    for html_text in tqdm(html_texts):
        page = parsing_text_by_param(html_text.decode('utf-8'))
        if text := page.title:
            match = re.search(r'^.*(?=[-,|])', text.string)
            if match:
                titles.append(match[0])
    return '.\n'.join([string.rstrip() for string in titles])

               
def create_header_request(user_agent: str=USER_AGENT, language: str='en', region: str='US') -> dict:
    accept_language = language + '-' + region + ',' + language + ';q=0.9'
    return {'User-Agent': user_agent, 'Accept-Language': accept_language}


def generate_wordcloud(text_: text) -> None:
    x, y = np.ogrid[:300, :300]
    mask = (x - 150) ** 2 + (y - 150) ** 2 > 130 ** 2
    mask = 255 * mask.astype(int)
    wc = WordCloud(background_color="white", repeat=True, mask=mask, max_words=50, min_word_length=4)
    wc.generate(text_)
    plt.axis("off")
    plt.imshow(wc, interpolation="bilinear")
    plt.show() 


async def main(par: dict) -> None:
    timeout = aiohttp.ClientTimeout(total=1)
    conn = aiohttp.TCPConnector(limit_per_host=30)   
    header_request = create_header_request()
    async with aiohttp.ClientSession(
        timeout=timeout, 
        connector=conn,
        headers=header_request
        ) as client:
        url_news = 'https://news.google.com/search?q={}+when:{}&hl={}'.format(
            par['key_word'],
            par['period'],
            par['language']
        )
        text_page = await fetch_page(client, url_news)
        url_line_news = parsing_page(text_page.decode('utf-8'))

        text_ = await load_news_pages(client, 'https://news.google.com', url_line_news)
    generate_wordcloud(text_)
 

if __name__ == "__main__":
    logger.info('Start - >')
    try:    
        asyncio.run(main(parametrs_parser))
    except KeyboardInterrupt:
        pass
    logger.info('< - Close')