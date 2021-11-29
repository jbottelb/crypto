from enum import Enum

class MessageTypes(str, Enum):
    Get_Seed_Nodes = "Get_Seed_Nodes"
    Get_Neighbors = "Get_Neighbors"
    Get_Blockchain = "Get_Blockchain"
    Send_Transaction = "Send_Transaction"
    Send_Block = "Send_Block"
    Get_Seed_Nodes_Response = "Get_Seed_Nodes_Response"
    Get_Neighbors_Response = "Get_Neighbors_Response"

