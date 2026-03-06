"""
Client Singleton Caching System
Provides module-level client instance management with weak references and auth-profile scoping.
Reduces credential initialization overhead and connection overhead per CLI command.
"""

import weakref
from typing import Dict, Optional, Any, Type, Union
from threading import Lock


# Global client registry with profile scoping
_client_cache: Dict[str, Dict[str, weakref.ref]] = {}
_cache_lock = Lock()


def get_cached_client(
    client_class: Type, profile: Optional[str] = "default"
) -> Any:
    """
    Get or create a cached client instance scoped to an auth profile.
    
    Uses weak references to allow garbage collection while minimizing
    credential initialization and connection overhead.
    
    Args:
        client_class: The client class to instantiate (e.g., Entity, Glossary)
        profile: Auth profile name (default: "default"). Scopes cache to prevent cross-profile contamination.
    
    Returns:
        Cached or newly created client instance
        
    Example:
        from purviewcli.client import Entity
        from purviewcli.client.client_cache import get_cached_client
        
        entity_client = get_cached_client(Entity, profile="prod")
    """
    with _cache_lock:
        cache_key = f"{profile}:{client_class.__name__}"
        
        if cache_key not in _client_cache:
            _client_cache[cache_key] = {}
        
        profile_cache = _client_cache[cache_key]
        
        # Try to get existing cached instance
        if "instance" in profile_cache:
            ref = profile_cache["instance"]
            instance = ref()  # Dereference weak reference
            if instance is not None:
                return instance
        
        # Create new instance if not cached or garbage collected
        instance = client_class()
        profile_cache["instance"] = weakref.ref(instance)
        
        return instance


def clear_client_cache(profile: Optional[str] = None) -> None:
    """
    Clear cached client instances.
    
    Args:
        profile: Profile to clear (None = all profiles)
    """
    with _cache_lock:
        if profile is None:
            _client_cache.clear()
        else:
            keys_to_delete = [
                k for k in _client_cache.keys() if k.startswith(f"{profile}:")
            ]
            for key in keys_to_delete:
                del _client_cache[key]


def cache_stats() -> Dict[str, Any]:
    """Get cache statistics for diagnostics"""
    with _cache_lock:
        stats = {
            "total_profiles": len(set(k.split(":")[0] for k in _client_cache.keys())),
            "total_cache_entries": len(_client_cache),
            "active_instances": sum(
                1
                for profile_cache in _client_cache.values()
                if "instance" in profile_cache and profile_cache["instance"]() is not None
            ),
        }
        return stats
