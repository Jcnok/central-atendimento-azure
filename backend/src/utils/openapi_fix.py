def fix_openapi_spec(schema: dict):
    """
    Post-process OpenAPI schema to ensure 3.0.3 compatibility.
    Converts Pydantic v2 'anyOf' nullables to OpenAPI 3.0 'nullable: true'.
    Also simplifies 'anyOf' with mixed primitive types (like string/int in ValidationError)
    to a single type to satisfy strict OpenAPI 3.0 validators.
    """
    if isinstance(schema, dict):
        # Check for anyOf patterns
        if "anyOf" in schema:
            any_of = schema["anyOf"]
            if isinstance(any_of, list):
                # Case 1: Nullable handling (type + null)
                null_type = next((item for item in any_of if item.get("type") == "null"), None)
                non_null_type = next((item for item in any_of if item.get("type") != "null"), None)
                
                if len(any_of) == 2 and null_type and non_null_type:
                    del schema["anyOf"]
                    if "$ref" in non_null_type:
                        schema["allOf"] = [non_null_type]
                    else:
                        schema.update(non_null_type)
                    schema["nullable"] = True
                
                # Case 2: Mixed primitive types (e.g., string | integer in ValidationError loc)
                # Azure and some Swagger tools dislike anyOf with simple types.
                # We simplify this to just "string" (or "integer") and add a note.
                else:
                    types = [item.get("type") for item in any_of if "type" in item]
                    if set(types) == {"string", "integer"}:
                        del schema["anyOf"]
                        schema["type"] = "string"
                        schema["description"] = "Can be string or integer"
                        # preserve title if it exists, usually doesn't conflict
        
        # Recursively fix children
        for key, value in schema.items():
            fix_openapi_spec(value)
            
    elif isinstance(schema, list):
        for item in schema:
            fix_openapi_spec(item)
