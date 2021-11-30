from enum import Enum

class MessageTypes(str, Enum):
    Get_Seed_Nodes = "Get_Seed_Nodes"
    Get_Neighbors = "Get_Neighbors"
    Get_Blockchain = "Get_Blockchain"
    Send_Transaction = "Send_Transaction"
    Send_Block = "Send_Block"
    Get_Seed_Nodes_Response = "Get_Seed_Nodes_Response"
    Get_Neighbors_Response = "Get_Neighbors_Response"
    Get_Miner_Count = "Get_Miner_Count"
    Join_As_Miner = "Join_As_Miner"
    Get_Miner_Count_Response = "Get_Miner_Count_Response"
    Join_As_Miner_Response = "Join_As_Miner_Response"
    Start_New_Block = "Start_New_Block"
    Start_New_Block_Response = "Start_New_Block_Response"
