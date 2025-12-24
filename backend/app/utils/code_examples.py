"""Code example generators for API documentation.

This module provides utilities to generate consistent code examples
in multiple languages (cURL, Python, JavaScript) for API endpoints.
"""

import json
from typing import Any


def generate_curl_example(
    method: str,
    endpoint: str,
    auth: bool = True,
    body: dict[str, Any] | None = None,
    query_params: dict[str, str] | None = None,
    base_url: str = "https://api.cutcosts.com"
) -> str:
    """Generate cURL example for an endpoint.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        endpoint: API endpoint path (e.g., "/api/v1/accounts")
        auth: Whether authentication is required
        body: Request body data
        query_params: URL query parameters
        base_url: Base URL for the API

    Returns:
        Formatted cURL command as string

    Example:
        >>> generate_curl_example("POST", "/api/v1/auth/login", auth=False,
        ...                       body={"username": "user@example.com", "password": "pass"})
    """
    # Build URL with query parameters
    url = f"{base_url}{endpoint}"
    if query_params:
        params_str = "&".join([f"{k}={v}" for k, v in query_params.items()])
        url = f"{url}?{params_str}"

    # Start building curl command
    curl_cmd = f"curl -X {method.upper()} {url}"

    # Add authorization header
    if auth:
        curl_cmd += " \\\n  -H \"Authorization: Bearer YOUR_ACCESS_TOKEN\""

    # Add content-type header
    curl_cmd += " \\\n  -H \"Content-Type: application/json\""

    # Add request body
    if body:
        body_json = json.dumps(body, indent=2)
        # Indent the JSON properly
        body_lines = body_json.split('\n')
        indented_body = '\n    '.join(body_lines)
        curl_cmd += f" \\\n  -d '{{\n    {indented_body[2:]}}'"  # Remove first { from indentation

    return curl_cmd


def generate_python_example(
    method: str,
    endpoint: str,
    auth: bool = True,
    body: dict[str, Any] | None = None,
    query_params: dict[str, str] | None = None,
    base_url: str = "https://api.cutcosts.com"
) -> str:
    """Generate Python (httpx) example for an endpoint.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        endpoint: API endpoint path
        auth: Whether authentication is required
        body: Request body data
        query_params: URL query parameters
        base_url: Base URL for the API

    Returns:
        Formatted Python code as string

    Example:
        >>> generate_python_example("GET", "/api/v1/accounts", auth=True)
    """
    example = "import httpx\n\n"

    if auth:
        example += "# Get access token from login endpoint first\n"
        example += "access_token = \"YOUR_ACCESS_TOKEN\"\n\n"

    example += f"url = \"{base_url}{endpoint}\"\n"

    # Add headers
    if auth or body:
        example += "headers = {\n"
        if auth:
            example += "    \"Authorization\": f\"Bearer {access_token}\",\n"
        if body:
            example += "    \"Content-Type\": \"application/json\"\n"
        example += "}\n\n"

    # Add query parameters
    if query_params:
        example += f"params = {json.dumps(query_params, indent=4)}\n\n"

    # Add request body
    if body:
        example += f"data = {json.dumps(body, indent=4)}\n\n"

    # Build request
    example += f"response = httpx.{method.lower()}(\n"
    example += "    url"

    if auth or body:
        example += ",\n    headers=headers"

    if query_params:
        example += ",\n    params=params"

    if body:
        example += ",\n    json=data"

    example += "\n)\n\n"
    example += "print(response.json())"

    return example


def generate_javascript_example(
    method: str,
    endpoint: str,
    auth: bool = True,
    body: dict[str, Any] | None = None,
    query_params: dict[str, str] | None = None,
    base_url: str = "https://api.cutcosts.com"
) -> str:
    """Generate JavaScript (fetch) example for an endpoint.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        endpoint: API endpoint path
        auth: Whether authentication is required
        body: Request body data
        query_params: URL query parameters
        base_url: Base URL for the API

    Returns:
        Formatted JavaScript code as string

    Example:
        >>> generate_javascript_example("POST", "/api/v1/accounts",
        ...                            body={"provider": "aws", "account_name": "Production"})
    """
    # Build URL with query parameters
    url = f"{base_url}{endpoint}"
    if query_params:
        params_str = "&".join([f"{k}={v}" for k, v in query_params.items()])
        url = f"{url}?{params_str}"

    example = "// Using fetch API\n"
    if auth:
        example += "// Get access token from login endpoint first\n"
        example += "const accessToken = 'YOUR_ACCESS_TOKEN';\n\n"

    example += f"const url = '{url}';\n"

    # Build options object
    example += "const options = {\n"
    example += f"  method: '{method.upper()}',\n"
    example += "  headers: {\n"

    if auth:
        example += "    'Authorization': `Bearer ${accessToken}`,\n"

    example += "    'Content-Type': 'application/json'\n"
    example += "  }"

    if body:
        body_json = json.dumps(body, indent=4)
        # Indent properly for JavaScript
        body_lines = body_json.split('\n')
        indented_body = '\n    '.join(body_lines)
        example += f",\n  body: JSON.stringify({indented_body})"

    example += "\n};\n\n"

    # Make request
    example += "fetch(url, options)\n"
    example += "  .then(response => response.json())\n"
    example += "  .then(data => console.log(data))\n"
    example += "  .catch(error => console.error('Error:', error));"

    return example


def generate_all_examples(
    method: str,
    endpoint: str,
    auth: bool = True,
    body: dict[str, Any] | None = None,
    query_params: dict[str, str] | None = None,
    base_url: str = "https://api.cutcosts.com"
) -> dict[str, str]:
    """Generate code examples in all supported languages.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        endpoint: API endpoint path
        auth: Whether authentication is required
        body: Request body data
        query_params: URL query parameters
        base_url: Base URL for the API

    Returns:
        Dictionary with keys 'curl', 'python', 'javascript' containing code examples

    Example:
        >>> examples = generate_all_examples("POST", "/api/v1/accounts",
        ...                                  body={"provider": "aws"})
        >>> print(examples['curl'])
        >>> print(examples['python'])
        >>> print(examples['javascript'])
    """
    return {
        "curl": generate_curl_example(method, endpoint, auth, body, query_params, base_url),
        "python": generate_python_example(method, endpoint, auth, body, query_params, base_url),
        "javascript": generate_javascript_example(method, endpoint, auth, body, query_params, base_url),
    }


def format_code_examples_for_openapi(
    method: str,
    endpoint: str,
    auth: bool = True,
    body: dict[str, Any] | None = None,
    query_params: dict[str, str] | None = None,
    base_url: str = "https://api.cutcosts.com"
) -> str:
    """Generate formatted code examples for OpenAPI description field.

    This generates a markdown-formatted section with code examples in all languages,
    ready to be included in an endpoint's description parameter.

    Args:
        method: HTTP method (GET, POST, PUT, PATCH, DELETE)
        endpoint: API endpoint path
        auth: Whether authentication is required
        body: Request body data
        query_params: URL query parameters
        base_url: Base URL for the API

    Returns:
        Markdown-formatted string with code examples

    Example:
        >>> examples_md = format_code_examples_for_openapi("POST", "/api/v1/auth/login",
        ...                                                auth=False,
        ...                                                body={"username": "user@example.com"})
        >>> print(examples_md)
    """
    examples = generate_all_examples(method, endpoint, auth, body, query_params, base_url)

    markdown = "## Code Examples\n\n"

    # cURL example
    markdown += "### cURL\n```bash\n"
    markdown += examples["curl"]
    markdown += "\n```\n\n"

    # Python example
    markdown += "### Python (httpx)\n```python\n"
    markdown += examples["python"]
    markdown += "\n```\n\n"

    # JavaScript example
    markdown += "### JavaScript (fetch)\n```javascript\n"
    markdown += examples["javascript"]
    markdown += "\n```\n"

    return markdown
