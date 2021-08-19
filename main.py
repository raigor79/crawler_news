import sys
import asyncio
import aiohttp
from loguru import logger


OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    OK: "Error have been not",
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}


parametrs_parser = {
    'key_word': 'Russia',
    'language': 'en',
    'period': '1y',
    'region': 'US'    
}


logger.add(
        sys.stderr, 
        format="{time} {level} {message}", 
        filter="my_module", 
        level="INFO"
        )


def parsing_page(text: str) -> list[str]:
    ...


async def fetch_page(client, url):
    try:
        async with client.get(url) as resp:
            if resp.status in (OK,):
                logger.info(
                    f'Page {url[:20]}... loaded, status response = {resp.status} : {ERRORS[resp.status]}'
                    )
                home_page_text = await resp.text()
            else:
                logger.info(
                    f'Page {url[:20]}... is not loaded, status error {resp.status} : {ERRORS[resp.status]}'
                    )
    except Exception:
        pass
    return home_page_text


async def main(par):
    timeout = aiohttp.ClientTimeout(total=30)
    conn = aiohttp.TCPConnector(limit_per_host=30)
    user_agent = 'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:64.0) Gecko/20100101 Firefox/64.0'
    accept_language= par['language'] + '-' + par['region'] + ',' + par['language'] + ';q=0.9'
    header_request = {'User-Agent': user_agent, 'Accept-Language': accept_language}
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


if __name__ == "__main__":
    logger.info('Start - >')
    try:    
        asyncio.run(main(parametrs_parser))
    except KeyboardInterrupt:
        pass
    logger.info('< - Close')