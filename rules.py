import re
from db import get_rules

ATTACK_PATTERNS = {
    'sql_injection': [
        r'\b(union|select|from|where|drop|alter|insert|delete)\b.*?\b(all|distinct|top|into|group|having)\b',
        r'[\'"]?\s*--',
        r'1\s*=\s*1',
        r'/\*.*?\*/'
    ],
    'xss': [
        r'<\s*script\b[^>]*>(.*?)<\s*/\s*script\s*>',
        r'\bon\w+\s*=\s*[\'"]?.*?[\'"]?',
        r'javascript\s*:\s*',
        r'<\s*(img|iframe|embed|object)\b[^>]*\bsrc\s*=\s*[\'"]?\s*javascript:'
    ],
    'path_traversal': [
        r'\.\./',
        r'\.\.%2f',
        r'etc/(passwd|shadow|hosts)',
        r'windows/.*?\.(ini|conf)'
    ]
}

def is_malicious(request_data):
    # Check hardcoded patterns
    for attack_type, patterns in ATTACK_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, request_data, re.IGNORECASE):
                return attack_type

    # Check custom rules
    custom_rules = get_rules()
    for rule in custom_rules:
        try:
            if re.search(rule['pattern'], request_data, re.IGNORECASE):
                return f"custom_rule_{rule['id']}"
        except re.error:
            continue
    return None