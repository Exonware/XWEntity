#!/usr/bin/env python3
"""
#exonware/xwentity/src/xwentity.py
XWEntity Re-export Module
This module re-exports XWEntity (unified class) for easy import.
XWEntity merges features from both XWObject and XWEntity.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.6.0.1
Generation Date: 28-Jan-2026
"""

from exonware.xwentity import XWEntity

XWObject = XWEntity
__all__ = ["XWEntity", "XWObject"]
