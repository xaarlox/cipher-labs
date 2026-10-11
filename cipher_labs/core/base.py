from abc import ABC, abstractmethod


class BaseCipher(ABC):
    @abstractmethod
    def encrypt(self, data, key):
        pass

    @abstractmethod
    def decrypt(self, data, key):
        pass
