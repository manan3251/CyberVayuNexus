import os
from typing import Dict, List, Optional
import json
from datetime import datetime
from fabric_sdk import Client, Network, Contract, Gateway
from blockchain_config import BlockchainConfig
from models import Personnel, InventoryItem, Alert, AuditLog

class BlockchainService:
    def __init__(self):
        self.client = None
        self.network = None
        self.contract = None
        self.gateway = None
        self.connected = False
    
    async def connect(self):
        try:
            # Create a new client
            self.client = Client()
            
            # Create a new gateway
            self.gateway = Gateway()
            
            # Connect to the gateway
            await self.gateway.connect(
                BlockchainConfig.get_connection_profile(),
                {
                    "wallet": BlockchainConfig.get_wallet_path(),
                    "identity": BlockchainConfig.USER_NAME
                }
            )
            
            # Get the network
            self.network = await self.gateway.get_network(BlockchainConfig.CHANNEL_NAME)
            
            # Get the contract
            self.contract = await self.network.get_contract(BlockchainConfig.CHAINCODE_NAME)
            
            self.connected = True
            return True
        except Exception as e:
            print(f"Failed to connect to blockchain: {str(e)}")
            return False
    
    async def disconnect(self):
        if self.gateway:
            await self.gateway.disconnect()
            self.connected = False
    
    async def create_personnel(self, personnel: Personnel) -> str:
        if not self.connected:
            await self.connect()
        
        try:
            # Submit transaction
            result = await self.contract.submit_transaction(
                BlockchainConfig.FUNCTIONS["create_personnel"],
                json.dumps(personnel.dict())
            )
            return result
        except Exception as e:
            print(f"Failed to create personnel: {str(e)}")
            return None
    
    async def update_personnel(self, personnel_id: str, personnel: Personnel) -> bool:
        if not self.connected:
            await self.connect()
        
        try:
            # Submit transaction
            await self.contract.submit_transaction(
                BlockchainConfig.FUNCTIONS["update_personnel"],
                personnel_id,
                json.dumps(personnel.dict())
            )
            return True
        except Exception as e:
            print(f"Failed to update personnel: {str(e)}")
            return False
    
    async def delete_personnel(self, personnel_id: str) -> bool:
        if not self.connected:
            await self.connect()
        
        try:
            # Submit transaction
            await self.contract.submit_transaction(
                BlockchainConfig.FUNCTIONS["delete_personnel"],
                personnel_id
            )
            return True
        except Exception as e:
            print(f"Failed to delete personnel: {str(e)}")
            return False
    
    async def get_personnel(self, personnel_id: str) -> Optional[Personnel]:
        if not self.connected:
            await self.connect()
        
        try:
            # Evaluate transaction
            result = await self.contract.evaluate_transaction(
                "GetPersonnel",
                personnel_id
            )
            return Personnel.parse_raw(result)
        except Exception as e:
            print(f"Failed to get personnel: {str(e)}")
            return None
    
    async def create_inventory(self, item: InventoryItem) -> str:
        if not self.connected:
            await self.connect()
        
        try:
            # Submit transaction
            result = await self.contract.submit_transaction(
                BlockchainConfig.FUNCTIONS["create_inventory"],
                json.dumps(item.dict())
            )
            return result
        except Exception as e:
            print(f"Failed to create inventory item: {str(e)}")
            return None
    
    async def update_inventory(self, item_id: str, item: InventoryItem) -> bool:
        if not self.connected:
            await self.connect()
        
        try:
            # Submit transaction
            await self.contract.submit_transaction(
                BlockchainConfig.FUNCTIONS["update_inventory"],
                item_id,
                json.dumps(item.dict())
            )
            return True
        except Exception as e:
            print(f"Failed to update inventory item: {str(e)}")
            return False
    
    async def delete_inventory(self, item_id: str) -> bool:
        if not self.connected:
            await self.connect()
        
        try:
            # Submit transaction
            await self.contract.submit_transaction(
                BlockchainConfig.FUNCTIONS["delete_inventory"],
                item_id
            )
            return True
        except Exception as e:
            print(f"Failed to delete inventory item: {str(e)}")
            return False
    
    async def get_inventory(self, item_id: str) -> Optional[InventoryItem]:
        if not self.connected:
            await self.connect()
        
        try:
            # Evaluate transaction
            result = await self.contract.evaluate_transaction(
                "GetInventory",
                item_id
            )
            return InventoryItem.parse_raw(result)
        except Exception as e:
            print(f"Failed to get inventory item: {str(e)}")
            return None
    
    async def create_alert(self, alert: Alert) -> str:
        if not self.connected:
            await self.connect()
        
        try:
            # Submit transaction
            result = await self.contract.submit_transaction(
                BlockchainConfig.FUNCTIONS["create_alert"],
                json.dumps(alert.dict())
            )
            return result
        except Exception as e:
            print(f"Failed to create alert: {str(e)}")
            return None
    
    async def update_alert(self, alert_id: str, alert: Alert) -> bool:
        if not self.connected:
            await self.connect()
        
        try:
            # Submit transaction
            await self.contract.submit_transaction(
                BlockchainConfig.FUNCTIONS["update_alert"],
                alert_id,
                json.dumps(alert.dict())
            )
            return True
        except Exception as e:
            print(f"Failed to update alert: {str(e)}")
            return False
    
    async def create_audit_log(self, log: AuditLog) -> str:
        if not self.connected:
            await self.connect()
        
        try:
            # Submit transaction
            result = await self.contract.submit_transaction(
                BlockchainConfig.FUNCTIONS["create_audit_log"],
                json.dumps(log.dict())
            )
            return result
        except Exception as e:
            print(f"Failed to create audit log: {str(e)}")
            return None
    
    async def get_audit_logs(self, entity_type: str = None, entity_id: str = None) -> List[AuditLog]:
        if not self.connected:
            await self.connect()
        
        try:
            # Evaluate transaction
            result = await self.contract.evaluate_transaction(
                "GetAuditLogs",
                entity_type or "",
                entity_id or ""
            )
            return [AuditLog.parse_raw(log) for log in json.loads(result)]
        except Exception as e:
            print(f"Failed to get audit logs: {str(e)}")
            return [] 