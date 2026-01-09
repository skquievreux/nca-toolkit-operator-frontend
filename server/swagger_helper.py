
from endpoint_discovery import get_all_endpoints

def generate_swagger_spec():
    """
    Generates OpenAPI 3.0 spec from KNOWN_ENDPOINTS
    """
    endpoints = get_all_endpoints()
    
    paths = {}
    
    for path, info in endpoints.items():
        # Parse params
        properties = {}
        required = []
        
        for param_str in info.get('params', []):
            # parse "name (optional, default: x)"
            parts = param_str.split('(', 1)
            name = parts[0].strip()
            desc = ""
            if len(parts) > 1:
                desc = parts[1].rstrip(')')
            
            properties[name] = {
                "type": "string",
                "description": desc
            }
            if "optional" not in desc.lower():
                required.append(name)
        
        paths[path] = {
            info['method'].lower(): {
                "summary": info['description'],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": properties,
                                "required": required
                            }
                        }
                    }
                },
                "responses": {
                    "200": {
                        "description": "Successful operation",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            }
                        }
                    }
                }
            }
        }

    return {
        "openapi": "3.0.0",
        "info": {
            "title": "NCA Toolkit Middleware API",
            "version": "1.0.0",
            "description": "API wrapper for NCA Toolkit Container functionality"
        },
        "servers": [
            {
                "url": "http://localhost:5000",
                "description": "Local Backend"
            }
        ],
        "paths": paths
    }

SWAGGER_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>NCA Toolkit API</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css" />
</head>
<body>
<div id="swagger-ui"></div>
<script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js" crossorigin></script>
<script>
  window.onload = () => {
    window.ui = SwaggerUIBundle({
      url: '/swagger.json',
      dom_id: '#swagger-ui',
    });
  };
</script>
</body>
</html>
"""
