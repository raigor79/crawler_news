import sys
import asyncio
import aiohttp
from loguru import logger


logger.add(
        sys.stderr, 
        format="{time} {level} {message}", 
        filter="my_module", 
        level="INFO"
        )


def main():
    pass

if __name__ == "__main__":
    logger.info('Start - >')
    try:    
        pass
    except KeyboardInterrupt:
        pass
    logger.info('< - Close')