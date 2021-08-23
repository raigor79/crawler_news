from asyncio.tasks import sleep
from datetime import time
import re
import os
import sys
import asyncio
from aiofiles.threadpool import text
import aiohttp
from loguru import logger
import aiofiles
from bs4 import BeautifulSoup


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


def make_dir(path: str) -> None:
    """ Directories creation function
    arguments:
    path - full path make directory
    """
    if not os.path.isdir(path):
        try:
            os.makedirs(path)
        except OSError:
            logger.error("Create directories {} failed".format(path))


async def save_page_news(path_dir: str, file_name: str, text_page: text) -> None:
    make_dir(path_dir)
    async with aiofiles.open(path_dir + '/' + file_name, 'wb') as file:
            await file.write(text_page)


def parsing_page(text: str) -> set[str]:
    soup = BeautifulSoup(text, 'html.parser')
    refs = set()
    for link in soup.find_all('a'):
        ref = link.get('href')       
        if re.match(template_article, str(ref)):
            refs.add(ref)
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


def generate_name_file(url):
    simbs = [ '\\', '/', ':', '*', '?', '"', '<', '>', '|', '+', '!', '%', '@', '~', '-']
    for simb in simbs:
        if simb in url:
            url = url.replace(simb, '')
    len_name_file = 60  if len(url) > 60 else len(url)
    return url[:len_name_file]


async def load_news_pages(client, root_page: str, resl: set) -> None:
    tasks_load = []
    tasks_reload = []
    for index, value in enumerate(resl):
        tasks_load.append(asyncio.create_task(fetch_page(client, root_page + str(value[1:]))))
        html_text = await tasks_load[index]
        
        page = BeautifulSoup(str(html_text), 'html.parser')
        url = str(page.body.findAll('a')[-1].get('href'))
        tasks_reload.append(asyncio.create_task(fetch_page(client, url)))
        logger.info(f'{index} - {url}')
        html_text = await tasks_reload[index]
        await save_page_news('./new', str(index) + generate_name_file(url) +'.html', html_text)
    await asyncio.gather(*tasks_load, *tasks_reload)

        
def create_header_request(user_agent: str=USER_AGENT, language: str='en', region: str='US') -> dict:
    accept_language = language + '-' + region + ',' + language + ';q=0.9'
    return {'User-Agent': user_agent, 'Accept-Language': accept_language}


async def main(par: dict) -> None:
    timeout = aiohttp.ClientTimeout(total=15)
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
        url_line_news = parsing_page(str(text_page))
        
        await load_news_pages(client, 'https://news.google.com', url_line_news)        


if __name__ == "__main__":
    logger.info('Start - >')
    try:    
        asyncio.run(main(parametrs_parser))
    except KeyboardInterrupt:
        pass
    logger.info('< - Close')