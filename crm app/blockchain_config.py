import os
from dotenv import load_dotenv
from typing import Dict, List, Optional
import json
from datetime import datetime

load_dotenv()

class BlockchainConfig:
    # Network configuration
    NETWORK_ID = os.getenv("BLOCKCHAIN_NETWORK_ID")
    CONTRACT_ADDRESS = os.getenv("BLOCKCHAIN_CONTRACT_ADDRESS")
    PRIVATE_KEY = os.getenv("BLOCKCHAIN_PRIVATE_KEY")
    
    # Chaincode configuration
    CHAINCODE_NAME = "army_crm"
    CHANNEL_NAME = "mychannel"
    
    # Endpoints
    PEER_ENDPOINTS = [
        "grpc://localhost:7051",
        "grpc://localhost:7052"
    ]
    
    # Orderer configuration
    ORDERER_ENDPOINT = "grpc://localhost:7050"
    
    # Organization configuration
    ORG_NAME = "ArmyOrg"
    ORG_MSP = "ArmyOrgMSP"
    
    # User configuration
    USER_NAME = "admin"
    USER_AFFILIATION = "army"
    
    # Chaincode functions
    FUNCTIONS = {
        "create_personnel": "CreatePersonnel",
        "update_personnel": "UpdatePersonnel",
        "delete_personnel": "DeletePersonnel",
        "create_inventory": "CreateInventory",
        "update_inventory": "UpdateInventory",
        "delete_inventory": "DeleteInventory",
        "create_alert": "CreateAlert",
        "update_alert": "UpdateAlert",
        "create_audit_log": "CreateAuditLog"
    }
    
    @staticmethod
    def get_connection_profile() -> Dict:
        return {
            "name": "army-network",
            "version": "1.0.0",
            "client": {
                "organization": BlockchainConfig.ORG_NAME,
                "connection": {
                    "timeout": {
                        "peer": {
                            "endorser": "300"
                        }
                    }
                }
            },
            "organizations": {
                BlockchainConfig.ORG_NAME: {
                    "mspid": BlockchainConfig.ORG_MSP,
                    "peers": BlockchainConfig.PEER_ENDPOINTS,
                    "certificateAuthorities": ["ca.army.org"]
                }
            },
            "peers": {
                endpoint: {
                    "url": endpoint,
                    "tlsCACerts": {
                        "path": f"crypto-config/peerOrganizations/army.org/peers/{endpoint.split('//')[1]}/tls/ca.crt"
                    },
                    "grpcOptions": {
                        "ssl-target-name-override": endpoint.split('//')[1],
                        "hostnameOverride": endpoint.split('//')[1]
                    }
                }
                for endpoint in BlockchainConfig.PEER_ENDPOINTS
            },
            "certificateAuthorities": {
                "ca.army.org": {
                    "url": "https://localhost:7054",
                    "caName": "ca.army.org",
                    "tlsCACerts": {
                        "path": "crypto-config/peerOrganizations/army.org/ca/ca.army.org-cert.pem"
                    },
                    "httpOptions": {
                        "verify": False
                    }
                }
            }
        }
    
    @staticmethod
    def get_wallet_path() -> str:
        return os.path.join(os.path.dirname(__file__), "wallet")
    
    @staticmethod
    def get_network_config_path() -> str:
        return os.path.join(os.path.dirname(__file__), "network-config.yaml")
    
    @staticmethod
    def get_crypto_path() -> str:
        return os.path.join(os.path.dirname(__file__), "crypto-config") 