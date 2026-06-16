import re

def search_file(filepath, patterns):
    print(f"=== Searching in {filepath} ===")
    with open(filepath, 'r', encoding='utf-8') as f:
        for idx, line in enumerate(f, 1):
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    print(f"{idx}: {line.strip()[:120]}")
                    break

search_file('app.js', ['renderLisLogsAndSimulators', 'openAgendasCalendar', 'renderCalendarGrid', 'PRELEVA', 'prelevare', 'lis_interface_type', 'lis_connection_type'])
search_file('server.py', ['lis_interface_type', 'prelevare', 'preleva', 'run_lis_engine', 'lis_connection_type', 'lis_protocol'])
