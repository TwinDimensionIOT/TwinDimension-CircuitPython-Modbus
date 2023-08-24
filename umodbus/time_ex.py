import time

def sleep_us(us : int):
    time.sleep(us / 1000000)
    
def sleep_ms(ms : int):
    time.sleep(ms / 1000)
    
def ticks_us():
    return time.monotonic_ns() / 1000

def ticks_ms():
    return time.monotonic_ns() / 1000000

def ticks_diff(start : int, end : int) -> int:
    return start - end