import time
import microcontroller
import supervisor
from micropython import const

def sleep_us(us : int):
    microcontroller.delay_us(us)
    
def sleep_ms(ms : int):
    microcontroller.delay_us(ms * 1000)

def ticks_us():
    if time.monotonic_ns:
        return time.monotonic_ns() // 1000
    else:
        raise OSError('time.monotonic_ns not found: microseconds ticks cannot be ensured')

def ticks_ms():
    if time.monotonic_ns:
        return time.monotonic_ns() // 1000000
    else:
        return supervisor.ticks_ms()

_TICKS_PERIOD = const(1<<29)
_TICKS_MAX = const(_TICKS_PERIOD-1)
_TICKS_HALFPERIOD = const(_TICKS_PERIOD//2)

def ticks_diff(ticks1, ticks2):
    "Compute the signed difference between two ticks values, assuming that they are within 2**28 ticks"
    diff = (ticks1 - ticks2) & _TICKS_MAX
    diff = ((diff + _TICKS_HALFPERIOD) & _TICKS_MAX) - _TICKS_HALFPERIOD
    return diff