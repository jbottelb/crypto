from BlockChain import DIFFICULTY


class Constants():
    # We use a large buffer size of 256 Kb so that
    # we can handle sending full blockchains
    BUF_SIZE = 262144
    CATALOG_UPDATE_INTERVAL = 60
    CATALOG_ENDPOINT = 'catalog.cse.nd.edu.'
    CATALOG_PORT = 9097
    PROJECT_NAME = "JBnetwork"
    DIFFICULTY = 4 # number of leading zeros on computed hash
    COINBASE = 10 # reward for mining bloack (we do not support depreciation of value for mining blocks)
    TPB = 5 # number of transactions per block