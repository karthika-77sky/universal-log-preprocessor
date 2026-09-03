import json

data = '{"timestamp": "2026-09-03", "event": "login_success", "user": "karthika"}'

result = json.loads(data)

print(result)
print(type(result))
print(result["event"])