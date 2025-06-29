import json
from datetime import datetime

# Predefined metadata records..

metadata_records = [
    {
        "config_id": "CFG001",
        "parameter_name": "max_user_connections",
        "parameter_value": "500",
        "description": "Maximum number of connections a user can have",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "config_id": "CFG002",
        "parameter_name": "cache_expiry_seconds",
        "parameter_value": "3600",
        "description": "Redis cache expiry time in seconds",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "config_id": "CFG003",
        "parameter_name": "default_profile_visibility",
        "parameter_value": "public",
        "description": "Visibility of profile if not set",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "config_id": "CFG004",
        "parameter_name": "data_retention_days",
        "parameter_value": "730",
        "description": "How many days to retain user activity logs",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "config_id": "CFG005",
        "parameter_name": "feature_toggle_recommendation",
        "parameter_value": "enabled",
        "description": "Feature flag for enabling/disabling recommendations",
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
]

# Save to JSON file..

with open("system_metadata.json", "w") as f:
    json.dump(metadata_records, f, indent=4)

print("Done! Saved system metadata to 'system_metadata.json'")