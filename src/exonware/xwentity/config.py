#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/config.py

XWEntity Configuration

This module provides configuration classes for the xwentity library following
GUIDE_DEV.md standards. Integrates with xwsystem config system.

Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1.2
Generation Date: 08-Nov-2025
"""

from typing import Any, Optional
from dataclasses import dataclass, field

from exonware.xwsystem import get_logger
from .defs import (
    EntityState,
    DEFAULT_ENTITY_TYPE,
    DEFAULT_STATE,
    DEFAULT_VERSION,
    DEFAULT_CACHE_SIZE,
    DEFAULT_THREAD_SAFETY,
)

logger = get_logger(__name__)


# ==============================================================================
# ENTITY CONFIGURATION
# ==============================================================================

@dataclass
class XWEntityConfig:
    """
    Configuration for XWEntity instances.
    
    Provides default values and configuration options for entity behavior,
    including node/edge strategies, graph manager settings, and performance
    optimization options.
    """
    
    # Entity defaults
    default_entity_type: str = DEFAULT_ENTITY_TYPE
    """Default entity type name."""
    
    default_state: EntityState = DEFAULT_STATE
    """Default entity state."""
    
    default_version: int = DEFAULT_VERSION
    """Default entity version number."""
    
    # XWNode configuration (for XWData)
    node_mode: str = "AUTO"
    """Node strategy mode for XWNode (AUTO, HASH_MAP, ORDERED_MAP, etc.)."""
    
    edge_mode: str = "AUTO"
    """Edge strategy mode for XWNode (AUTO, ADJ_LIST, ADJ_MATRIX, etc.)."""
    
    graph_manager_enabled: bool = False
    """Whether to enable graph manager for XWNode."""
    
    node_options: dict[str, Any] = field(default_factory=dict)
    """Additional options for XWNode initialization."""
    
    # Performance configuration
    cache_size: int = DEFAULT_CACHE_SIZE
    """Cache size for entity operations."""
    
    enable_thread_safety: bool = DEFAULT_THREAD_SAFETY
    """Enable thread safety for entity operations."""
    
    # Validation configuration
    strict_validation: bool = True
    """Enable strict validation mode."""
    
    auto_validate: bool = False
    """Automatically validate on data changes."""
    
    # Action configuration
    auto_register_actions: bool = True
    """Automatically register actions from entity methods."""
    
    # Serialization configuration
    default_serialization_format: str = "json"
    """Default format for serialization."""
    
    @classmethod
    def default(cls) -> "XWEntityConfig":
        """Get default configuration instance."""
        return cls()
    
    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "XWEntityConfig":
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Dictionary with configuration values
            
        Returns:
            XWEntityConfig instance
        """
        # Extract known fields
        known_fields = {
            "default_entity_type",
            "default_state",
            "default_version",
            "node_mode",
            "edge_mode",
            "graph_manager_enabled",
            "node_options",
            "cache_size",
            "enable_thread_safety",
            "strict_validation",
            "auto_validate",
            "auto_register_actions",
            "default_serialization_format",
        }
        
        # Filter to known fields and convert state if needed
        filtered = {}
        for key, value in config_dict.items():
            if key in known_fields:
                if key == "default_state" and isinstance(value, str):
                    filtered[key] = EntityState(value)
                else:
                    filtered[key] = value
        
        return cls(**filtered)
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dictionary representation of configuration
        """
        return {
            "default_entity_type": self.default_entity_type,
            "default_state": str(self.default_state),
            "default_version": self.default_version,
            "node_mode": self.node_mode,
            "edge_mode": self.edge_mode,
            "graph_manager_enabled": self.graph_manager_enabled,
            "node_options": self.node_options.copy(),
            "cache_size": self.cache_size,
            "enable_thread_safety": self.enable_thread_safety,
            "strict_validation": self.strict_validation,
            "auto_validate": self.auto_validate,
            "auto_register_actions": self.auto_register_actions,
            "default_serialization_format": self.default_serialization_format,
        }
    
    def get_node_config(self) -> dict[str, Any]:
        """
        Get XWNode configuration dictionary.
        
        Returns:
            Configuration dictionary for XWNode initialization
        """
        config = {
            "mode": self.node_mode,
            **self.node_options,
        }
        
        # Add edge mode if graph manager is enabled
        if self.graph_manager_enabled:
            config["edge_mode"] = self.edge_mode
        
        return config


# ==============================================================================
# GLOBAL CONFIGURATION
# ==============================================================================

_global_config: Optional[XWEntityConfig] = None


def get_config() -> XWEntityConfig:
    """
    Get global entity configuration.
    
    Returns:
        Global XWEntityConfig instance
    """
    global _global_config
    if _global_config is None:
        _global_config = XWEntityConfig.default()
    return _global_config


def set_config(config: XWEntityConfig) -> None:
    """
    Set global entity configuration.
    
    Args:
        config: Configuration instance to set as global
    """
    global _global_config
    _global_config = config
    logger.debug(f"Global entity configuration updated: {config}")


# ==============================================================================
# EXPORTS
# ==============================================================================

__all__ = [
    "XWEntityConfig",
    "get_config",
    "set_config",
]
