import json

transcript_path = r"C:\Users\robpiron\.gemini\antigravity\brain\4e261f84-2c21-4fbb-8677-a352af49bbdc\.system_generated\logs\transcript.jsonl"

found = []
with open(transcript_path, 'r', encoding='utf-8') as f:
    for idx, line in enumerate(f):
        if 'sendSimulatedEmail' in line:
            try:
                step = json.loads(line)
                found.append({
                    'line': idx,
                    'step': step.get('step_index'),
                    'type': step.get('type')
                })
            except Exception:
                found.append({
                    'line': idx,
                    'type': 'unparseable'
                })

print(f"Found {len(found)} occurrences in transcript:")
for f_info in found:
    print(f_info)
