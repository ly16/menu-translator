import threading
import easyocr
from openai import OpenAI
from config import OPENAI_API_KEY

reader = None
reader_lock = threading.Lock()

def get_reader(source_language: str):
    global reader
    if reader is None:
        with reader_lock:
            if reader is None:
                reader = easyocr.Reader([source_language])
    return reader


openai_client = None
def get_openai_client():
    global openai_client
    if openai_client is None:
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
    return openai_client