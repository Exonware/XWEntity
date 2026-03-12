from exonware.xwentity import XWEntity

def main():
    entity = XWEntity(
        schema={
            "name": "bluesmyth.character",
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "number"}
            }
        },
        actions={
            "greet": {
                "handler": lambda instance, **kwargs: f"Hello {instance.get('name')}!"
            },
            "perfect_age_of_female_mate": {
                "query": {
                    "format": "xwqs",
                    "query": "SELECT age - 5 AS perfect_age"
                }
            }
        },
        data={
            "name": "John Doe",
            "age": 30
        }
    )
    print("Greeting:")
    print(entity.execute_action("greet"))
    print("Perfect age of female mate:")
    result = entity.execute_action("perfect_age_of_female_mate")
    if isinstance(result, dict) and "results" in result:
        print(result["results"])
    else:
        print(result)


if __name__ == "__main__":
    main()
