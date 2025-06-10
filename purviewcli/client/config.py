"""
Configuration Management for  Purview CLI
Handles environment configuration, profiles, and settings
"""

import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

@dataclass
class PurviewProfile:
    """Purview connection profile"""
    name: str
    account_name: str
    tenant_id: Optional[str] = None
    client_id: Optional[str] = None
    azure_region: Optional[str] = None
    batch_size: int = 100
    max_retries: int = 3
    timeout: int = 30
    default_collection: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PurviewProfile':
        return cls(**data)

class ConfigManager:
    """Manages CLI configuration and profiles"""
    
    def __init__(self, config_dir: Optional[str] = None):
        self.config_dir = Path(config_dir) if config_dir else self._get_default_config_dir()
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.config_file = self.config_dir / 'config.yaml'
        self.profiles_file = self.config_dir / 'profiles.yaml'
        
        self._config = self._load_config()
        self._profiles = self._load_profiles()
    
    def _get_default_config_dir(self) -> Path:
        """Get default configuration directory"""
        if os.name == 'nt':  # Windows
            config_dir = Path.home() / 'AppData' / 'Local' / 'purviewcli'
        else:  # Unix-like
            config_dir = Path.home() / '.config' / 'purviewcli'
        return config_dir
    
    def _load_config(self) -> Dict[str, Any]:
        """Load main configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")
        
        return {
            'default_profile': None,
            'debug': False,
            'output_format': 'json',
            'auto_update_check': True
        }
    
    def _load_profiles(self) -> Dict[str, PurviewProfile]:
        """Load connection profiles"""
        profiles = {}
        
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r') as f:
                    data = yaml.safe_load(f) or {}
                    for name, profile_data in data.items():
                        profiles[name] = PurviewProfile.from_dict(profile_data)
            except Exception as e:
                logger.warning(f"Failed to load profiles: {e}")
        
        return profiles
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                yaml.dump(self._config, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")
    
    def save_profiles(self):
        """Save profiles to file"""
        try:
            profiles_data = {name: profile.to_dict() for name, profile in self._profiles.items()}
            with open(self.profiles_file, 'w') as f:
                yaml.dump(profiles_data, f, default_flow_style=False)
        except Exception as e:
            logger.error(f"Failed to save profiles: {e}")
    
    def add_profile(self, profile: PurviewProfile) -> bool:
        """Add or update a profile"""
        try:
            self._profiles[profile.name] = profile
            self.save_profiles()
            
            # Set as default if it's the first profile
            if len(self._profiles) == 1:
                self.set_default_profile(profile.name)
            
            return True
        except Exception as e:
            logger.error(f"Failed to add profile: {e}")
            return False
    
    def remove_profile(self, name: str) -> bool:
        """Remove a profile"""
        if name in self._profiles:
            del self._profiles[name]
            self.save_profiles()
            
            # Clear default if this was the default profile
            if self._config.get('default_profile') == name:
                self._config['default_profile'] = None
                self.save_config()
            
            return True
        return False
    
    def get_profile(self, name: Optional[str] = None) -> Optional[PurviewProfile]:
        """Get a profile by name or default profile"""
        if name is None:
            name = self._config.get('default_profile')
        
        if name and name in self._profiles:
            return self._profiles[name]
        
        return None
    
    def list_profiles(self) -> Dict[str, PurviewProfile]:
        """List all profiles"""
        return self._profiles.copy()
    
    def set_default_profile(self, name: str) -> bool:
        """Set default profile"""
        if name in self._profiles:
            self._config['default_profile'] = name
            self.save_config()
            return True
        return False
    
    def get_config(self, key: str, default=None):
        """Get configuration value"""
        return self._config.get(key, default)
    
    def set_config(self, key: str, value: Any):
        """Set configuration value"""
        self._config[key] = value
        self.save_config()
    
    def resolve_account_name(self, account_name: Optional[str] = None, profile_name: Optional[str] = None) -> Optional[str]:
        """Resolve account name from various sources"""
        # 1. Explicit parameter
        if account_name:
            return account_name
        
        # 2. Profile
        profile = self.get_profile(profile_name)
        if profile:
            return profile.account_name
        
        # 3. Environment variable
        env_account = os.environ.get('PURVIEW_ACCOUNT_NAME')
        if env_account:
            return env_account
        
        return None
    
    def create_profile_from_env(self, name: str = 'default') -> Optional[PurviewProfile]:
        """Create profile from environment variables"""
        account_name = os.environ.get('PURVIEW_ACCOUNT_NAME')
        if not account_name:
            return None
        
        profile = PurviewProfile(
            name=name,
            account_name=account_name,
            tenant_id=os.environ.get('AZURE_TENANT_ID'),
            client_id=os.environ.get('AZURE_CLIENT_ID'),
            azure_region=os.environ.get('AZURE_REGION'),
            batch_size=int(os.environ.get('PURVIEW_BATCH_SIZE', '100')),
            max_retries=int(os.environ.get('PURVIEW_MAX_RETRIES', '3')),
            timeout=int(os.environ.get('PURVIEW_TIMEOUT', '30'))
        )
        
        return profile

class EnvironmentHelper:
    """Helper for environment variable management"""
    
    @staticmethod
    def setup_environment(profile: PurviewProfile):
        """Setup environment variables from profile"""
        os.environ['PURVIEW_ACCOUNT_NAME'] = profile.account_name
        
        if profile.tenant_id:
            os.environ['AZURE_TENANT_ID'] = profile.tenant_id
        
        if profile.client_id:
            os.environ['AZURE_CLIENT_ID'] = profile.client_id
        
        if profile.azure_region:
            os.environ['AZURE_REGION'] = profile.azure_region
    
    @staticmethod
    def get_auth_info() -> Dict[str, str]:
        """Get authentication information"""
        return {
            'tenant_id': os.environ.get('AZURE_TENANT_ID', 'Not set'),
            'client_id': os.environ.get('AZURE_CLIENT_ID', 'Not set'),
            'region': os.environ.get('AZURE_REGION', 'public'),
            'purview_account': os.environ.get('PURVIEW_ACCOUNT_NAME', 'Not set')
        }

# Global config manager instance
config_manager = ConfigManager()
