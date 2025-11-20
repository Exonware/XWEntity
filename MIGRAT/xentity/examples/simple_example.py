#!/usr/bin/env python3
"""
🏢 Simple xEntity Example
Demonstrates basic integration of xEntity with xAction decoration and xSchema.

This example shows:
- Basic schema definition with xSchema
- Simple xAction decorators
- Entity data validation
- Action execution
"""

from typing import Dict, Any
from src.xlib.xentity import xEntity
from src.xlib.xdata import xSchema
from src.xlib.xaction import xAction


class ProductEntity(xEntity):
    """
    📦 Simple Product Entity Example
    
    Demonstrates:
    - Basic schema with xSchema
    - Simple xAction decorators
    - Data validation and transformation
    """
    
    def __init__(self, name: str, price: float, category: str):
        # Define product schema
        product_schema = xSchema(
            value="product_schema",
            data={
                "type": "object",
                "title": "Product Schema",
                "description": "Simple product with basic validation",
                "properties": {
                    "name": {
                        "type": "string",
                        "minLength": 1,
                        "maxLength": 100,
                        "description": "Product name"
                    },
                    "price": {
                        "type": "number",
                        "minimum": 0,
                        "description": "Product price"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["electronics", "clothing", "books", "food"],
                        "description": "Product category"
                    },
                    "description": {
                        "type": "string",
                        "maxLength": 500,
                        "description": "Product description"
                    },
                    "in_stock": {
                        "type": "boolean",
                        "default": True,
                        "description": "Product availability"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Product tags"
                    },
                    "rating": {
                        "type": "number",
                        "minimum": 0,
                        "maximum": 5,
                        "description": "Product rating"
                    }
                },
                "required": ["name", "price", "category"]
            }
        )
        
        # Initialize with data
        super().__init__(
            schema=product_schema,
            data={
                "name": name,
                "price": price,
                "category": category,
                "description": "",
                "in_stock": True,
                "tags": [],
                "rating": 0.0
            },
            entity_type="product"
        )
    
    @xAction(
        api_name="update-price",
        roles=["admin", "manager"],
        in_types={
            "new_price": xSchema("new_price", data={"type": "number", "minimum": 0})
        }
    )
    def update_price(self, new_price: float) -> Dict[str, Any]:
        """Update product price."""
        old_price = self.get("price")
        self.set("price", new_price)
        
        return {
            "success": True,
            "old_price": old_price,
            "new_price": new_price,
            "price_change": new_price - old_price
        }
    
    @xAction(
        api_name="add-tag",
        roles=["admin", "manager", "editor"],
        in_types={
            "tag": xSchema("tag", data={"type": "string", "minLength": 1, "maxLength": 20})
        }
    )
    def add_tag(self, tag: str) -> Dict[str, Any]:
        """Add a tag to the product."""
        tags = self.get("tags", [])
        
        if tag in tags:
            return {
                "success": False,
                "error": f"Tag '{tag}' already exists"
            }
        
        tags.append(tag)
        self.set("tags", tags)
        
        return {
            "success": True,
            "tag": tag,
            "total_tags": len(tags)
        }
    
    @xAction(
        api_name="remove-tag",
        roles=["admin", "manager", "editor"],
        in_types={
            "tag": xSchema("tag", data={"type": "string", "minLength": 1})
        }
    )
    def remove_tag(self, tag: str) -> Dict[str, Any]:
        """Remove a tag from the product."""
        tags = self.get("tags", [])
        
        if tag not in tags:
            return {
                "success": False,
                "error": f"Tag '{tag}' not found"
            }
        
        tags.remove(tag)
        self.set("tags", tags)
        
        return {
            "success": True,
            "removed_tag": tag,
            "total_tags": len(tags)
        }
    
    @xAction(
        api_name="set-rating",
        roles=["*"],  # Public action
        in_types={
            "rating": xSchema("rating", data={"type": "number", "minimum": 0, "maximum": 5})
        }
    )
    def set_rating(self, rating: float) -> Dict[str, Any]:
        """Set product rating."""
        self.set("rating", rating)
        
        return {
            "success": True,
            "rating": rating,
            "product_name": self.get("name")
        }
    
    @xAction(
        api_name="toggle-stock",
        roles=["admin", "manager"]
    )
    def toggle_stock(self) -> Dict[str, Any]:
        """Toggle product stock status."""
        current_stock = self.get("in_stock")
        new_stock = not current_stock
        
        self.set("in_stock", new_stock)
        
        return {
            "success": True,
            "old_status": current_stock,
            "new_status": new_stock,
            "message": f"Product is now {'in stock' if new_stock else 'out of stock'}"
        }
    
    @xAction(
        api_name="update-description",
        roles=["admin", "manager", "editor"],
        in_types={
            "description": xSchema("description", data={"type": "string", "maxLength": 500})
        }
    )
    def update_description(self, description: str) -> Dict[str, Any]:
        """Update product description."""
        old_description = self.get("description")
        self.set("description", description)
        
        return {
            "success": True,
            "old_description": old_description,
            "new_description": description
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """Get product summary."""
        return {
            "id": self.id,
            "name": self.get("name"),
            "price": self.get("price"),
            "category": self.get("category"),
            "in_stock": self.get("in_stock"),
            "rating": self.get("rating"),
            "tags_count": len(self.get("tags", []))
        }


def run_simple_example():
    """Run the simple xEntity example."""
    print("🏢 Simple xEntity Example with xAction and xSchema")
    print("=" * 50)
    
    # Create product entity
    print("\n1. Creating Product Entity...")
    product = ProductEntity(
        name="Wireless Headphones",
        price=99.99,
        category="electronics"
    )
    
    print(f"✅ Product created: {product.id}")
    print(f"📋 Schema validation: {product.validate()}")
    print(f"📦 Product: {product.get('name')} - ${product.get('price')}")
    
    # Update price
    print("\n2. Updating Price...")
    result = product.execute_action("update-price", new_price=89.99)
    print(f"✅ Price update result: {result.data if hasattr(result, 'data') else result}")
    
    # Add tags
    print("\n3. Adding Tags...")
    product.execute_action("add-tag", tag="wireless")
    product.execute_action("add-tag", tag="bluetooth")
    product.execute_action("add-tag", tag="noise-cancelling")
    
    # Try to add duplicate tag
    duplicate_result = product.execute_action("add-tag", tag="wireless")
    print(f"❌ Duplicate tag result: {duplicate_result.data if hasattr(duplicate_result, 'data') else duplicate_result}")
    
    # Set rating
    print("\n4. Setting Rating...")
    rating_result = product.execute_action("set-rating", rating=4.5)
    print(f"✅ Rating result: {rating_result.data if hasattr(rating_result, 'data') else rating_result}")
    
    # Update description
    print("\n5. Updating Description...")
    desc_result = product.execute_action("update-description", 
                                       description="High-quality wireless headphones with noise cancellation")
    print(f"✅ Description result: {desc_result.data if hasattr(desc_result, 'data') else desc_result}")
    
    # Show available actions
    print("\n6. Available Actions:")
    actions = product.list_actions()
    if isinstance(actions, dict):
        for action_name, action_info in actions.items():
            print(f"  🔧 {action_name}: {action_info.get('description', 'No description')}")
    else:
        print(f"  🔧 Available actions: {actions}")
    
    # Show product summary
    print("\n7. Product Summary:")
    summary = product.get_summary()
    print(f"📋 Summary: {summary}")
    
    # Test schema validation
    print("\n8. Schema Validation Test:")
    print(f"✅ Valid data: {product.validate()}")
    
    # Test invalid data
    print("\n9. Testing Invalid Data...")
    try:
        product.set("price", -10)  # Invalid: negative price
        print(f"❌ Should fail validation: {product.validate()}")
    except Exception as e:
        print(f"✅ Validation caught error: {e}")
    
    # Export entity
    print("\n10. Entity Export:")
    export_data = product.to_dict()
    print(f"📦 Exported keys: {list(export_data.keys())}")
    print(f"📊 Entity type: {export_data.get('_metadata', {}).get('type')}")
    print(f"🆔 Entity ID: {export_data.get('_metadata', {}).get('id')}")
    
    print("\n✅ Simple xEntity example completed successfully!")
    return product


if __name__ == "__main__":
    run_simple_example()
