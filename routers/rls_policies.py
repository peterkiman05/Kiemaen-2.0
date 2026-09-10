from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List

router = APIRouter()

# Comprehensive 4-policy CRUD schema (SELECT, INSERT, UPDATE, DELETE) per table scoped to auth.uid()
USER_SCOPED_POLICIES: Dict[str, List[Dict[str, str]]] = {
    "evolution_memory": [
        {"policy_name": "Select own evolution memory", "operation": "SELECT", "definition": "auth.uid() = user_id"},
        {"policy_name": "Insert own evolution memory", "operation": "INSERT", "definition": "auth.uid() = user_id"},
        {"policy_name": "Update own evolution memory", "operation": "UPDATE", "definition": "auth.uid() = user_id"},
        {"policy_name": "Delete own evolution memory", "operation": "DELETE", "definition": "auth.uid() = user_id"}
    ],
    "user_subscriptions": [
        {"policy_name": "Select own subscription tier", "operation": "SELECT", "definition": "auth.uid() = user_id"},
        {"policy_name": "Insert own subscription tier", "operation": "INSERT", "definition": "auth.uid() = user_id"},
        {"policy_name": "Update own subscription tier", "operation": "UPDATE", "definition": "auth.uid() = user_id"},
        {"policy_name": "Delete own subscription tier", "operation": "DELETE", "definition": "auth.uid() = user_id"}
    ],
    "chat_sessions": [
        {"policy_name": "Select own chat sessions", "operation": "SELECT", "definition": "auth.uid() = session_owner"},
        {"policy_name": "Insert own chat sessions", "operation": "INSERT", "definition": "auth.uid() = session_owner"},
        {"policy_name": "Update own chat sessions", "operation": "UPDATE", "definition": "auth.uid() = session_owner"},
        {"policy_name": "Delete own chat sessions", "operation": "DELETE", "definition": "auth.uid() = session_owner"}
    ],
    "api_audit_logs": [
        {"policy_name": "Select own audit logs", "operation": "SELECT", "definition": "auth.uid() = user_id"},
        {"policy_name": "Insert own audit logs", "operation": "INSERT", "definition": "auth.uid() = user_id"},
        {"policy_name": "Deny audit log updates", "operation": "UPDATE", "definition": "false"},
        {"policy_name": "Deny audit log deletions", "operation": "DELETE", "definition": "false"}
    ],
    "freelance_deliverables": [
        {"policy_name": "Select own freelance deliverables", "operation": "SELECT", "definition": "auth.uid() = creator_id"},
        {"policy_name": "Insert own freelance deliverables", "operation": "INSERT", "definition": "auth.uid() = creator_id"},
        {"policy_name": "Update own freelance deliverables", "operation": "UPDATE", "definition": "auth.uid() = creator_id"},
        {"policy_name": "Delete own freelance deliverables", "operation": "DELETE", "definition": "auth.uid() = creator_id"}
    ]
}

class PolicyRegistryResponse(BaseModel):
    total_tables: int
    policies: Dict[str, List[Dict[str, str]]]

@router.get("/api/security/rls/policies", response_model=PolicyRegistryResponse)
async def get_user_scoped_policies():
    return {
        "total_tables": len(USER_SCOPED_POLICIES),
        "policies": USER_SCOPED_POLICIES
    }

@router.post("/api/security/rls/generate-sql")
async def generate_sql_migration_script():
    """
    Generates runnable PostgreSQL SQL DDL statements enabling RLS and creating 
    the four user-scoped CRUD policies for each table.
    """
    sql_statements = []
    for table_name, policies in USER_SCOPED_POLICIES.items():
        sql_statements.append(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;")
        for p in policies:
            cmd = f"""CREATE POLICY "{p['policy_name']}" ON {table_name} FOR {p['operation']} USING ({p['definition']});"""
            if p['operation'] == 'INSERT':
                cmd = f"""CREATE POLICY "{p['policy_name']}" ON {table_name} FOR INSERT WITH CHECK ({p['definition']});"""
            sql_statements.append(cmd)
            
    return {
        "status": "success",
        "migration_sql": "\n".join(sql_statements)
    }
