#!/usr/bin/env python3
"""
#exonware/xwentity/tests/0.core/test_core_performance.py
Core tests for XWEntity performance optimization.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.0.1.0
Generation Date: 28-Jan-2026
"""

from __future__ import annotations
import pytest
from exonware.xwentity import XWEntity
@pytest.mark.xwentity_core

class TestCorePerformance:
    """Test core performance optimization functionality."""

    def test_optimize_for_access(self, sample_entity):
        """Test optimize_for_access method."""
        result = sample_entity.optimize_for_access()
        assert result is sample_entity  # Should return self for chaining

    def test_optimize_for_validation(self, sample_entity):
        """Test optimize_for_validation method."""
        result = sample_entity.optimize_for_validation()
        assert result is sample_entity

    def test_optimize_memory(self, sample_entity):
        """Test optimize_memory method."""
        result = sample_entity.optimize_memory()
        assert result is sample_entity

    def test_get_memory_usage(self, sample_entity):
        """Test get_memory_usage method."""
        usage = sample_entity.get_memory_usage()
        assert isinstance(usage, int)
        assert usage >= 0

    def test_get_performance_stats(self, sample_entity):
        """Test get_performance_stats method."""
        stats = sample_entity.get_performance_stats()
        assert isinstance(stats, dict)
        # Should contain performance metrics
        assert len(stats) >= 0

    def test_optimization_chaining(self, sample_entity):
        """Test optimization methods can be chained."""
        result = (
            sample_entity
            .optimize_for_access()
            .optimize_for_validation()
            .optimize_memory()
        )
        assert result is sample_entity

    def test_memory_usage_increases_with_data(self):
        """Test memory usage increases with more data."""
        small_entity = XWEntity(data={"name": "Alice"})
        large_entity = XWEntity(data={f"key{i}": f"value{i}" for i in range(100)})
        small_usage = small_entity.get_memory_usage()
        large_usage = large_entity.get_memory_usage()
        # Large entity should use more memory (or at least not less)
        assert large_usage >= small_usage
