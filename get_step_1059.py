import json

transcript_path = r"C:\Users\robpiron\.gemini\antigravity\brain\4e261f84-2c21-4fbb-8677-a352af49bbdc\.system_generated\logs\transcript.jsonl"

def extract(line_idx, filename):
    with open(transcript_path, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f):
            if idx == line_idx:
                step = json.loads(line)
                tcs = step.get('tool_calls', [])
                for tc in tcs:
                    args = tc.get('args', {})
                    content = args.get('ReplacementContent', '') or args.get('CodeContent', '')
                    with open(filename, 'w', encoding='utf-8') as outf:
                        outf.write(content.replace('\\n', '\n').replace('\\t', '\t').replace('\\"', '"'))
                print(f"Extracted line {line_idx} to {filename}")

extract(1050, 'step_1059.txt')
extract(1056, 'step_1065.txt')
