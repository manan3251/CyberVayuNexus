from typing import List, Dict, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import json
from enum import Enum

class Rank(Enum):
    PRIVATE = "Private"
    CORPORAL = "Corporal"
    SERGEANT = "Sergeant"
    LIEUTENANT = "Lieutenant"
    CAPTAIN = "Captain"
    MAJOR = "Major"
    COLONEL = "Colonel"
    GENERAL = "General"

class DeploymentStatus(Enum):
    ACTIVE = "Active"
    DEPLOYED = "Deployed"
    ON_LEAVE = "On Leave"
    INJURED = "Injured"
    RETIRED = "Retired"

class MissionStatus(Enum):
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

class Personnel(BaseModel):
    id: str
    name: str
    rank: str
    unit: str
    deployment_history: List[Dict]
    medical_records: str  # Encrypted
    clearance_level: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class InventoryItem(BaseModel):
    id: str
    name: str
    category: str
    quantity: int
    threshold: int
    expiry_date: Optional[datetime]
    supplier: str
    origin: str
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

class Alert(BaseModel):
    id: str
    type: str  # 'inventory', 'personnel', 'system'
    severity: str  # 'low', 'medium', 'high'
    message: str
    created_at: datetime = Field(default_factory=datetime.now)
    resolved: bool = False

class AuditLog(BaseModel):
    id: str
    user_id: str
    action: str
    entity_type: str  # 'personnel', 'inventory', 'alert'
    entity_id: str
    details: Dict
    timestamp: datetime = Field(default_factory=datetime.now)

class BlockchainTransaction:
    def __init__(self, network_id: str, contract_address: str):
        self.network_id = network_id
        self.contract_address = contract_address
    
    def create_transaction(self, data: Dict, transaction_type: str) -> str:
        # TODO: Implement blockchain transaction creation
        return "transaction_hash"
    
    def verify_transaction(self, transaction_hash: str) -> bool:
        # TODO: Implement blockchain transaction verification
        return True
    
    def get_transaction_history(self, entity_id: str) -> List[Dict]:
        # TODO: Implement blockchain transaction history retrieval
        return []

class RoleBasedAccess:
    ROLES = {
        'admin': ['read', 'write', 'delete', 'manage_users'],
        'supply_officer': ['read', 'write_inventory', 'manage_alerts'],
        'viewer': ['read']
    }
    
    @staticmethod
    def has_permission(role: str, permission: str) -> bool:
        return permission in RoleBasedAccess.ROLES.get(role, [])

class Soldier:
    def __init__(
        self,
        id: str,
        name: str,
        rank: Rank,
        unit: str,
        skills: List[str],
        deployment_status: DeploymentStatus,
        health_records: Dict,
        emergency_contact: Dict,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.name = name
        self.rank = rank
        self.unit = unit
        self.skills = skills
        self.deployment_status = deployment_status
        self.health_records = health_records
        self.emergency_contact = emergency_contact
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

class InventoryItem:
    def __init__(
        self,
        id: str,
        name: str,
        category: str,
        quantity: int,
        location: str,
        threshold: int,
        rfid_tag: Optional[str] = None,
        qr_code: Optional[str] = None,
        lost_damaged_logs: List[Dict] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.name = name
        self.category = category
        self.quantity = quantity
        self.location = location
        self.threshold = threshold
        self.rfid_tag = rfid_tag
        self.qr_code = qr_code
        self.lost_damaged_logs = lost_damaged_logs or []
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

class Mission:
    def __init__(
        self,
        id: str,
        name: str,
        description: str,
        assigned_unit: str,
        status: MissionStatus,
        start_date: datetime,
        end_date: datetime,
        tasks: List[Dict],
        field_reports: List[Dict] = None,
        communication_logs: List[Dict] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None
    ):
        self.id = id
        self.name = name
        self.description = description
        self.assigned_unit = assigned_unit
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        self.tasks = tasks
        self.field_reports = field_reports or []
        self.communication_logs = communication_logs or []
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()

class FieldReport:
    def __init__(
        self,
        id: str,
        mission_id: str,
        reporter_id: str,
        content: str,
        location: str,
        attachments: List[str] = None,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.mission_id = mission_id
        self.reporter_id = reporter_id
        self.content = content
        self.location = location
        self.attachments = attachments or []
        self.created_at = created_at or datetime.now()

class CommunicationLog:
    def __init__(
        self,
        id: str,
        mission_id: str,
        sender_id: str,
        receiver_id: str,
        content: str,
        type: str,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.mission_id = mission_id
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.content = content
        self.type = type
        self.created_at = created_at or datetime.now()

class Alert:
    def __init__(
        self,
        id: str,
        type: str,
        severity: str,
        message: str,
        entity_id: Optional[str] = None,
        entity_type: Optional[str] = None,
        created_at: Optional[datetime] = None,
        resolved: bool = False,
        resolved_at: Optional[datetime] = None
    ):
        self.id = id
        self.type = type
        self.severity = severity
        self.message = message
        self.entity_id = entity_id
        self.entity_type = entity_type
        self.created_at = created_at or datetime.now()
        self.resolved = resolved
        self.resolved_at = resolved_at 