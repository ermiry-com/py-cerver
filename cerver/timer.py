from ctypes import c_double

from .lib import lib

timer_sleep_for_seconds = lib.timer_sleep_for_seconds
timer_sleep_for_seconds.argtypes = [c_double]

timer_get_current_time = lib.timer_get_current_time
timer_get_current_time.restype = c_double
