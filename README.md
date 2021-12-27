# Crypto
This was a repository for a dist sys project, but it has sense been removed of partners code
and cleaned up so I may continue to develop it on my own. 

### Documentation
[Link Final Report](https://docs.google.com/document/d/1uQHn7B0NYk4viWjS4KtepPNqXG3mw2oChBbH1RgqB5U/edit?usp=sharing)\
[Message protocol](https://docs.google.com/spreadsheets/d/1RhuirGA03p4ts3WLCBAwsItBj6iXmr9cp1WiCFSmgjw/edit?usp=sharing)

### Replication
To run the system to the farthest we got it,

Run a Full Node \
`python3 FullNode.py <portnum>`\
Then run a miner to connect to that Node \
`python3 Miner.py miner_publickey <Full Node Name> <Full Node Port Number>`\
Then run the LightWeightCLI \
`python3 LightweightCLI.py <Full Node Name> <Full Node Port Number>`


With the CLI You can then create and then load a wallet, or just use one of ours, and then send transactions to the full node.
For easier use, you can just send transactions to anythings as the public key
because public keys can technically be anything, and since no one will use the received money it does not matter.
Miner Public key can also be anything

### Testing
To run various testing scripts\
`python3 BlockChainTesting.py`\
`python3 RSA_Keys.py`\
`python3 Transcation.py`

Sample Input for the CLI: \
Loads Josh's Keys and sends Brad 10 Coin \
---> l Josh_Keys.json \
---> t 10 \
---> Brad


### Status
 - Rewriting flies to be in a professional setup. 
 - Moving the Full Node to be an object, as it prbably should have been all along
