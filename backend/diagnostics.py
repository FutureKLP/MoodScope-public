"""Local rotating diagnostics without provider payloads, credentials or lyrics."""
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import re
import uuid


def sanitize(value):
    text=str(value)
    text=re.sub(r'https?://\S+','[URL]',text)
    text=re.sub(r'(?i)(AIza\S+|\bsk-\S+|\bhf_\S+|\bgh[pousr]_\S+)', '[CREDENTIAL]',text)
    text=re.sub(r'(?i)(api[_-]?key|token|password|secret)\s*[=:]\s*\S+',r'\1=[REDACTED]',text)
    text=re.sub(r'(?i)[A-Z]:[\\/]+Users[\\/]+[^\s"\']+','[LOCAL_PATH]',text)
    text=re.sub(r'/(?:home|Users)/[^\s"\']+','[LOCAL_PATH]',text)
    return text[:300]


def logger_for(data):
    directory=Path(data)/'logs';directory.mkdir(parents=True,exist_ok=True)
    logger=logging.getLogger('moodscope.'+str(directory.resolve()))
    logger.setLevel(logging.INFO);logger.propagate=False
    if not logger.handlers:
        handler=RotatingFileHandler(directory/'moodscope.log',maxBytes=2_000_000,backupCount=3,encoding='utf-8')
        handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
        logger.addHandler(handler)
    return logger


def event(data,operation,message):
    logger_for(data).info('operation=%s %s',operation,sanitize(message))


def failure(data,operation,exception):
    reference=uuid.uuid4().hex[:12]
    logger=logger_for(data)
    # Log frame locations rather than exception messages/source lines, which may contain user data.
    frames=[];trace=exception.__traceback__
    while trace:
        frames.append(f'{Path(trace.tb_frame.f_code.co_filename).name}:{trace.tb_lineno}:{trace.tb_frame.f_code.co_name}')
        trace=trace.tb_next
    response=getattr(exception,'response',None)
    status=getattr(response,'status_code',None)
    code=getattr(exception,'winerror',None) or getattr(exception,'errno',None)
    logger.error('id=%s operation=%s exception=%s http_status=%s system_code=%s frames=%s',
        reference,operation,type(exception).__name__,status if isinstance(status,int) else '-',code if isinstance(code,int) else '-',' > '.join(frames))
    return reference


def user_error(data,operation,exception,message):
    reference=failure(data,operation,exception)
    return f'{message} Fehler-ID: {reference}. Details: data/logs/moodscope.log'
