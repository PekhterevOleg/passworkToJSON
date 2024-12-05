import reprlib

from dataclasses import dataclass
from typing import Protocol
from typing import Generator
from abc import abstractmethod



@dataclass
class Folder:
    name: str
    parentId: str
    vaultId: str
    id: str


@dataclass
class Password:
    name: str
    login: str
    vaultId: str
    id: str
    password: str
    url: str
    description: str


class BasePasswork:
    def __len__(self):
        return len(self._passwords)

    def __getitem__(self, item):
        return self._passwords[item]

    def __repr__(self):
        return reprlib.repr(self._passwords)

    def __iter__(self):
        yield from self._passwords


class ProtPasswork(Protocol):
    @abstractmethod
    def decrypt_passwords(self) -> Generator:
        raise NotImplementedError


