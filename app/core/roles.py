from typing import List

# Role definitions
ROLES = {
    "user": [
        "manage-instagram-accounts",
        "view-conversations",
        "send-messages",
        "view-messages",
    ],
    "admin": [
        "manage-instagram-accounts",
        "view-conversations",
        "send-messages",
        "view-messages",
        "manage-users",
        "view-logs",
    ],
}


def get_permissions_for_role(role: str) -> List[str]:
    """Get permissions for a given role"""
    return ROLES.get(role, [])


def has_permission(user_permissions: List[str], required_permission: str) -> bool:
    """Check if user has required permission"""
    return required_permission in user_permissions

