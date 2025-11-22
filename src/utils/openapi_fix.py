def fix_openapi_spec(schema: dict):
    """
    Post-process OpenAPI schema to ensure 3.0.3 compatibility.
    Converts Pydantic v2 'anyOf' nullables to OpenAPI 3.0 'nullable: true'.
    """
    if isinstance(schema, dict):
        # Check for the specific anyOf pattern (Pydantic v2 nullable)
        if "anyOf" in schema:
            any_of = schema["anyOf"]
            if isinstance(any_of, list) and len(any_of) == 2:
                null_type = next((item for item in any_of if item.get("type") == "null"), None)
                non_null_type = next((item for item in any_of if item.get("type") != "null"), None)
                
                if null_type and non_null_type:
                    # Found a nullable field pattern
                    del schema["anyOf"]
                    
                    # If the non-null type is a reference, wrap in allOf for strict compliance
                    if "$ref" in non_null_type:
                        schema["allOf"] = [non_null_type]
                    else:
                        # Otherwise just merge properties
                        schema.update(non_null_type)
                    
                    schema["nullable"] = True

        # Recursively fix children
        for key, value in schema.items():
            fix_openapi_spec(value)
            
    elif isinstance(schema, list):
        for item in schema:
            fix_openapi_spec(item)
