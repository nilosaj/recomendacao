import redis
import os
from dotenv import load_dotenv

load_dotenv()

def connectRedis():
    r = redis.Redis(
        host=os.getenv("REDIS_HOST"),
        port=os.getenv("REDIS_PORT"),
        password='',
        db=os.getenv("REDIS_DB"),
        decode_responses=True)
    return r



