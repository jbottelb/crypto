from enum import Enum

class Constants(str, Enum):
    # We use a large buffer size of 256 Kb so that
    # we can handle sending full blockchains
    BUF_SIZE = 262144