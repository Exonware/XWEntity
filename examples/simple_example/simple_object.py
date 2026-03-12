"""
XWEntity Example - Simple JSON/Dict Definitions
Demonstrates using simple JSON/dict definitions without importing XWSchema, XWData, or XWAction.
XWEntity automatically converts them to the appropriate XW classes.
"""
# Disable xwlazy for this example to improve performance

import sys
import os
# Set environment variable to disable xwlazy
os.environ['XWLAZY_DISABLE'] = '1'
# Remove xwlazy from sys.meta_path if it's already installed
if 'exonware.xwlazy' in sys.modules:
    try:
        from exonware.xwlazy import _uninstall_global_import_hook
        _uninstall_global_import_hook()
    except (ImportError, AttributeError):
        # If xwlazy is not available or doesn't have uninstall function, try manual removal
        try:
            # Find and remove xwlazy from sys.meta_path
            for i, meta_path_item in enumerate(sys.meta_path):
                if hasattr(meta_path_item, '__class__') and 'xwlazy' in str(type(meta_path_item)).lower():
                    sys.meta_path.pop(i)
                    break
        except Exception:
            pass
from exonware.xwentity import XWEntity
from exonware.xwaction import XWAction


def perfect_age_handler(obj, **kwargs):
    """Calculate perfect age using xwqs."""
    result = XWAction.query("SELECT age - 5 AS perfect_age", obj.data, format="xwqs")
    # Extract the value from the result
    if hasattr(result, 'data'):
        if isinstance(result.data, list) and result.data:
            return result.data[0].get("perfect_age") if isinstance(result.data[0], dict) else result.data[0]
        elif isinstance(result.data, dict):
            return result.data.get("perfect_age")
        return result.data
    return result


def main():
    # Option 1: Simple JSON/dict definition - no need to import XWSchema, XWData, or XWAction
    obj = XWEntity(
        schema={
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        },
        data={
            "name": "John Doe",
            "age": 30
        },
        actions={
            # Actions can be simple handler functions or action definitions
            "greet": {
                "handler": lambda obj, **kwargs: f"Hello {obj.get('name')}!"
            },
            "perfect_age_of_female_mate": {
                "query": {
                    "format": "xwqs",
                    "query": "SELECT age - 5 AS perfect_age"
                }
            }
        }
    )
    # Actions accessed via obj.actions["action_name"] automatically have execute() method
    # that accepts arguments and passes them to XWAction.execute()
    age_female = obj.actions["perfect_age_of_female_mate"].execute()
    print(f"Perfect age of female mate: {age_female}")
if __name__ == "__main__":
    main()
