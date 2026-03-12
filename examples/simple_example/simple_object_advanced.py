"""
XWEntity Example - Using XW Class Instances
Demonstrates using XWSchema, XWAction instances directly.
"""

from exonware.xwentity import XWEntity
from exonware.xwschema import XWSchema
from exonware.xwaction import XWAction


def main():
    # Option 1: Using XW class instances directly
    schema = XWSchema({
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "number"}
        }
    })
    # Create XWAction instances
    greet_action = XWAction.create(
        lambda obj, **kwargs: f"Hello {obj.get('name')}!",
        api_name="greet"
    )
    compute_action = XWAction.create(
        lambda obj, **kwargs: obj.get('age', 0) * 2,
        api_name="double_age"
    )
    # Create entity with XW class instances
    obj = XWEntity(
        schema=schema,  # XWSchema instance
        data={
            "name": "John Doe",
            "age": 30
        },
        actions=[greet_action, compute_action]  # List of XWAction instances
    )
    print("=== Using XW Class Instances ===")
    print(f"Object ID: {obj.id}")
    print(f"Data: {obj.get('name')}, Age: {obj.get('age')}")
    print(f"Schema type: {type(obj.schema).__name__}")
    print(f"Actions: {list(obj.actions.keys())}")
    # Test action execution
    if "greet" in obj.actions:
        result = obj.execute_action("greet")
        print(f"Greet action result: {result}")
    if "double_age" in obj.actions:
        result = obj.execute_action("double_age")
        print(f"Double age action result: {result}")
    print("\nSUCCESS: XWEntity works with XW class instances!")
if __name__ == "__main__":
    main()
