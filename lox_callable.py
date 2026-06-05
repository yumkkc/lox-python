from abc import ABC, abstractmethod

class LoxCallable(ABC):
    @abstractmethod
    def call(self, interpteter, arguments):
        pass

    @abstractmethod
    def arity(self):
        pass
    