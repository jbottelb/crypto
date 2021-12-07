
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
    NEIGHBOR_PING_INTERVAL = 30
    # if a side fork blockchain falls behind the main branch by this amount, it will be discarded
    SIDE_BLOCKCHAIN_DIFFERENCE_FOR_PRUNING = 3
    # how far back we allow new blocks to add onto a block in an existing fork and create a new fork
    MAX_NEW_BLOCK_INDEX_LAG = 3
