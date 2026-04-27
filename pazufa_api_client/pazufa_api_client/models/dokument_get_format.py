from enum import Enum

class DokumentGetFormat(str, Enum):
    FTM = "ftm"
    PAZUFA = "pazufa"

    def __str__(self) -> str:
        return str(self.value)
