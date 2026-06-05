from lox_callable import LoxCallable
import time

# function for clock
class Clock (LoxCallable):
    def call(self, interpreter, arguments):
        return round(time.time() * 1000)
    
    def arity(self):
        return 0