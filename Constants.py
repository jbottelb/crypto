
class Constants():
    # We use a large buffer size of 256 Kb so that
    # we can handle sending full blockchains
    BUF_SIZE = 262144
    CATALOG_UPDATE_INTERVAL = 60
    CATALOG_ENDPOINT = 'catalog.cse.nd.edu.'
    CATALOG_PORT = 9097
    PROJECT_NAME = "JBnetwork"
    DIFFICULTY = 3 # number of leading zeros on computed hash
    COINBASE = 10 # reward for mining bloack (we do not support depreciation of value for mining blocks)
    TPB = 5 # number of transactions per block
    NEIGHBOR_PING_INTERVAL = 30
    BLOCKCHAIN_FORK_PRUNING_INTERVAL = 30 # how often we prune short forks
    # if a side fork blockchain falls behind the main branch by this amount, it will be
    # discarded the next time we run a pruning function
    SIDE_BLOCKCHAIN_DIFFERENCE_FOR_PRUNING = 3
    # The genesis hash should always be the same
    GENESIS_HASH = "12f44f7f30883cf7109451e7cfed935825644c1cc7d33653729d5dccaf03e51c"
