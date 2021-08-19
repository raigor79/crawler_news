import logging
import sys
import asyncio
import aiohttp
from loguru import logger


URL_NEWS = 'https://news.google.com/search?q=Russia&hl=en-US&gl=US&ceid=US%3Aen'


logger.add(
        sys.stderr, 
        format="{time} {level} {message}", 
        filter="my_module", 
        level="INFO"
        )


async def main():
    timeout = aiohttp.ClientTimeout(total=30)
    conn = aiohttp.TCPConnector(limit_per_host=30)
    async with aiohttp.ClientSession(timeout=timeout, connector=conn) as client:
        async with client.get(URL_NEWS) as resp:
            print(resp.status)
            print(await resp.text())


if __name__ == "__main__":
    logger.info('Start - >')
    try:    
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    logger.info('< - Close')