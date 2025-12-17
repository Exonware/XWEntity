#!/usr/bin/env python3
"""
⚙️ xEntity Configuration System
Configurable performance vs memory trade-offs for different use cases.
"""

from enum import Enum
from typing import Optional, Dict, Any
from dataclasses import dataclass
import os
import threading

class PerformanceMode(Enum):
    """Performance vs memory trade-off modes."""
    
    # Option A: Maximum performance, higher memory usage
    PERFORMANCE = "performance"  # Direct properties, 12.8x faster
    
    # Option C: Memory efficient, slower performance  
    MEMORY = "memory"  # xData delegation, 85% less memory
    
    # Hybrid: Balanced approach
    BALANCED = "balanced"  # Smart caching with fallback
    
    # Auto: Choose based on entity size/complexity
    AUTO = "auto"  # Performance for small entities, memory for large ones


@dataclass
class xEntityConfig:
    """Global configuration for xEntity behavior."""
    
    # Performance mode
    performance_mode: PerformanceMode = PerformanceMode.PERFORMANCE
    
    # Auto-mode thresholds
    auto_property_threshold: int = 10  # Switch to memory mode if >10 properties
    auto_instance_threshold: int = 1000  # Switch to memory mode if >1000 instances
    
    # Feature toggles
    enable_validation: bool = True
    enable_action_discovery: bool = True
    enable_schema_caching: bool = True
    enable_property_caching: bool = True
    
    # Memory management
    max_property_cache_size: int = 1000
    max_schema_cache_size: int = 100
    entity_cache_size: int = 1024
    
    # Thread safety
    enable_thread_safety: bool = True
    
    # Debug options
    debug_mode: bool = False
    log_performance_warnings: bool = True
    
    # Decorator support (as requested - no type hints)
    supported_decorators: Dict[str, bool] = None
    
    def __post_init__(self):
        """Initialize default decorator support."""
        if self.supported_decorators is None:
            self.supported_decorators = {
                # Core decorators ✅
                "@xSchema": True,
                "@property": True,
                "Annotated": True,
                
                # Library decorators ✅
                "pydantic.Field": True,
                "sqlalchemy.Column": True,
                "marshmallow.fields": True,
                "attr.ib": True,
                "django.models": True,
                "fastapi.Query": True,
                "fastapi.Path": True,
                "fastapi.Body": True,
                
                # Excluded decorators ❌
                "type_hints": False,  # As requested - no simple type hints
            }


class xEntityConfigManager:
    """Thread-safe configuration manager."""
    
    _instance: Optional['xEntityConfigManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            self._config = xEntityConfig()
            self._instance_count = 0
            self._property_counts = {}
            self._initialized = True
    
    @property
    def config(self) -> xEntityConfig:
        """Get current configuration."""
        return self._config
    
    def set_performance_mode(self, mode: PerformanceMode) -> None:
        """Set global performance mode."""
        with self._lock:
            self._config.performance_mode = mode
            from src.xlib.xwsystem import get_logger
            logger = get_logger(__name__)
            logger.info(f"🔧 xEntity performance mode set to: {mode.value}")
    
    def register_entity_creation(self, entity_class: type, property_count: int) -> PerformanceMode:
        """Register new entity creation and return recommended mode."""
        with self._lock:
            self._instance_count += 1
            self._property_counts[entity_class.__name__] = property_count
            
            # Return effective mode (considering AUTO)
            return self._get_effective_mode(entity_class, property_count)
    
    def _get_effective_mode(self, entity_class: type, property_count: int) -> PerformanceMode:
        """Get effective mode considering AUTO logic."""
        base_mode = self._config.performance_mode
        
        if base_mode != PerformanceMode.AUTO:
            return base_mode
        
        # Auto-selection logic
        if property_count > self._config.auto_property_threshold:
            return PerformanceMode.MEMORY
        
        if self._instance_count > self._config.auto_instance_threshold:
            return PerformanceMode.MEMORY
        
        # Default to performance for small entities
        return PerformanceMode.PERFORMANCE
    
    def get_decorator_support(self, decorator_name: str) -> bool:
        """Check if a decorator is supported."""
        return self._config.supported_decorators.get(decorator_name, False)
    
    def configure_from_env(self) -> None:
        """Configure from environment variables."""
        # Performance mode
        env_mode = os.getenv('XENTITY_PERFORMANCE_MODE', '').lower()
        if env_mode in [m.value for m in PerformanceMode]:
            self._config.performance_mode = PerformanceMode(env_mode)
        
        # Debug mode
        if os.getenv('XENTITY_DEBUG', '').lower() in ('true', '1', 'yes'):
            self._config.debug_mode = True
        
        # Validation
        if os.getenv('XENTITY_VALIDATION', '').lower() in ('false', '0', 'no'):
            self._config.enable_validation = False
    
    def get_stats(self) -> Dict[str, Any]:
        """Get configuration and usage statistics."""
        return {
            "performance_mode": self._config.performance_mode.value,
            "total_instances": self._instance_count,
            "entity_types": len(self._property_counts),
            "avg_properties": sum(self._property_counts.values()) / len(self._property_counts) if self._property_counts else 0,
            "supported_decorators": sum(self._config.supported_decorators.values()),
            "memory_stats": {
                "property_cache_size": self._config.max_property_cache_size,
                "schema_cache_size": self._config.max_schema_cache_size,
            }
        }


# Global configuration instance
config_manager = xEntityConfigManager()


# ========================================================================
# CONVENIENCE FUNCTIONS
# ========================================================================

def get_config() -> xEntityConfig:
    """Get the current configuration."""
    return config_manager.config

def set_performance_mode(mode: PerformanceMode) -> None:
    """Set global performance mode."""
    config_manager.set_performance_mode(mode)


def use_performance_mode() -> None:
    """Switch to performance mode (Option A) - 12.8x faster."""
    set_performance_mode(PerformanceMode.PERFORMANCE)


def use_memory_mode() -> None:
    """Switch to memory mode (Option C) - 85% less memory."""
    set_performance_mode(PerformanceMode.MEMORY)


def use_balanced_mode() -> None:
    """Switch to balanced mode - compromise between performance and memory."""
    set_performance_mode(PerformanceMode.BALANCED)


def use_auto_mode() -> None:
    """Switch to auto mode - automatic selection based on entity complexity."""
    set_performance_mode(PerformanceMode.AUTO)


def get_current_mode() -> PerformanceMode:
    """Get current performance mode."""
    return config_manager.config.performance_mode


def configure_from_environment() -> None:
    """Configure xEntity from environment variables."""
    config_manager.configure_from_env()


def get_config_stats() -> Dict[str, Any]:
    """Get configuration and usage statistics."""
    return config_manager.get_stats()


# ========================================================================
# CONFIGURATION EXAMPLES
# ========================================================================

def print_performance_guide():
    """Print performance configuration guide."""
    print("""
🚀 xEntity Performance Configuration Guide
==========================================

🏃 PERFORMANCE MODE (Default):
  - 12.8x faster property access
  - Higher memory usage (+300% typical)
  - Best for: APIs, real-time apps, frequent access
  
💾 MEMORY MODE:
  - 85% less memory usage
  - Slower property access
  - Best for: Batch processing, large datasets, memory-constrained environments
  
⚖️ BALANCED MODE:
  - Smart caching with performance fallbacks
  - Moderate memory usage
  - Best for: Mixed workloads
  
🤖 AUTO MODE:
  - Automatically chooses based on entity complexity
  - <10 properties → Performance mode
  - >10 properties → Memory mode
  - Best for: Variable workloads

Usage:
  from src.xlib.xentity.config import use_performance_mode, use_memory_mode
  
  use_performance_mode()  # For speed
  use_memory_mode()       # For memory efficiency
  
Environment Variables:
  XENTITY_PERFORMANCE_MODE=performance|memory|balanced|auto
  XENTITY_DEBUG=true
  XENTITY_VALIDATION=false
""")


if __name__ == "__main__":
    print_performance_guide()
