# Crypto
Repository for cryptocurrency for Distributed System projectby Brad Budden and Josh Bottelberghe

### Documentation
[Link Final Report](https://docs.google.com/document/d/1uQHn7B0NYk4viWjS4KtepPNqXG3mw2oChBbH1RgqB5U/edit?usp=sharing)\
[Message protocol](https://docs.google.com/spreadsheets/d/1RhuirGA03p4ts3WLCBAwsItBj6iXmr9cp1WiCFSmgjw/edit?usp=sharing)

### Replication
To run the system to the farthest we got it,

Run a Full Node \
`python3 FullNode.py <portnum>`\
Then run a miner to connect to that Node \
`python3 Miner.py <Full Node Name> <Full Node Port Number>`\
Then run the LightWeightCLI \
`python3 LightweightCLI.py <Full Node Name> <Full Node Port Number>`


With the CLI You can then create and then load a wallet, or just use one of ours, and then send transactions to the full node.
For easier use, you can just send transactions to anythings as the public key
because public keys can technically be anything, and since no one will use the received money it does not matter.

### Testing
To run various testing scripts\
`python3 BlockChainTesting.py`\
`python3 RSA_Keys.py`\
`python3 Transcation.py`
