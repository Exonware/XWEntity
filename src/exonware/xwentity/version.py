#!/usr/bin/env python3
"""
#exonware/xwentity/src/exonware/xwentity/version.py
Version information for xwentity library.
Company: eXonware.com
Author: eXonware Backend Team
Email: connect@exonware.com
Version: 0.6.0.1
Generation Date: 08-Nov-2025
"""

from datetime import datetime

def _today_release_date() -> str:
    """Return today's date in DD-MMM-YYYY."""
    return datetime.now().strftime("%d-%b-%Y")
__version__ = "0.6.0.1"  # Unified XWEntity (merged XWObject + XWEntity)
# Release/update date (DD-MMM-YYYY). Evaluated at import time.
__date__ = _today_release_date()


def get_date() -> str:
    """Get the release/update date (DD-MMM-YYYY)."""
    return __date__
