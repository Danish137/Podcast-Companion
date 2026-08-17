import httpx

# Test audio endpoint with GET
resp = httpx.get(
    'http://localhost:8000/episodes/ep01/audio',
    headers={'Range': 'bytes=0-1023'},
    timeout=10
)

print(f'Status: {resp.status_code}')
print(f'Content-Type: {resp.headers.get("content-type")}')
print(f'Content-Length: {resp.headers.get("content-length")}')
print(f'Accept-Ranges: {resp.headers.get("accept-ranges")}')
print(f'Content-Range: {resp.headers.get("content-range")}')
print(f'First 50 bytes type: {type(resp.content[:50])}')
print(f'First 50 bytes length: {len(resp.content[:50])}')

# Test invalid episode
try:
    resp_invalid = httpx.get('http://localhost:8000/episodes/ep99/audio', timeout=10)
    print(f'\nInvalid episode status: {resp_invalid.status_code}')
except httpx.HTTPStatusError as e:
    print(f'\nInvalid episode error: {e.response.status_code}')
