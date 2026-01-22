"""
Rate limiting configuration loaded from environment variables.
All limits are configurable per role and endpoint
"""
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

def get_rate_limit_config()-> Dict[str,Dict[str,int]]:
    """
    Returns rate limit configuration from environment variables
    Format:{role:{endpoint:{period:limit}}}
    """
    return{
        "admin":{
            "chat":{
                "per_minute":int(os.getenv("RATE_LIMIT","20")),
                "per_hour":int(os.getenv("RATE_LIMIT","100")),
            },
            "upload":{
                "per_hour":int(os.getenv("RATE_LIMIT","5")),
                "per_day":int(os.getenv("RATE_LIMIT","20")),
            }
        },
        "employee":{
            "chat":{
                "per_minute":int(os.getenv("RATE_LIMIT","10")),
                "per_hour":int(os.getenv("RATE_LIMIT","50")),
            }
        },
        "intern":{
            "chat":{
                "per_minute":int(os.getenv("RATE_LIMIT","50")),
                "per_hour":int(os.getenv("RATE_LIMIT","30")), 
            }
        }
    }

def get_ip_rate_limit_config()-> Dict[str,int]:
    """
    Returns IP-based rate limit configuration
    Used for login endpoint and global protection
    """
    return{
        "login_per_15min":int(os.getenv("RATE_LIMIT_LOGIN_PER_15MIN","50")),
        "login_per_hour":int(os.getenv("RATE_LIMIT_LOGIN_PER_HOUR","100")),
        "global_per_hour":int(os.getenv("RATE_LIMIT_GLOBAL_PER_HOUR","1000")),
    }