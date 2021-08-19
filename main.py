import logging
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


URL_NEWS = 'https://news.google.com/search?q=Russia&hl=en-US&gl=US&ceid=US%3Aen'


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
                    f'Home page loaded, status response = {resp.status} : {ERRORS[resp.status]}'
                    )
                home_page_text = await resp.text()
            else:
                logger.info(
                    f'Home page is not loaded, status error {resp.status} : {ERRORS[resp.status]}'
                    )
    except Exception:
        pass


async def main():
    timeout = aiohttp.ClientTimeout(total=30)
    conn = aiohttp.TCPConnector(limit_per_host=30)
    async with aiohttp.ClientSession(
        timeout=timeout, 
        connector=conn
        ) as client:
        text_page = await fetch_page(client, URL_NEWS)


if __name__ == "__main__":
    logger.info('Start - >')
    try:    
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    logger.info('< - Close')