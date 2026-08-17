import httpx
import json

# Test chat endpoint with structured sources
resp = httpx.post(
    'http://localhost:8000/chat',
    json={'session_id': 'test', 'message': 'Explain special relativity simply'},
    timeout=30
)

print(f'Status: {resp.status_code}')
data = resp.json()
print(f'Intent: {data["intent_used"]}')
print(f'Sources count: {len(data["sources"])}')

if data["sources"]:
    print('\nFirst source:')
    print(json.dumps(data['sources'][0], indent=2))
    
print('\nResponse preview:')
print(data['response'][:200] + '...')
