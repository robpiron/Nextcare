import sys
import threading
import time
import urllib.request
import traceback

def sys_excepthook(exctype, value, tb):
    print("UNHANDLED EXCEPTION:")
    traceback.print_exception(exctype, value, tb)
sys.excepthook = sys_excepthook

# For python 3.8+
if hasattr(threading, 'excepthook'):
    def threading_excepthook(args):
        print("THREAD EXCEPTION:")
        traceback.print_exception(args.exc_type, args.exc_value, args.exc_traceback)
    threading.excepthook = threading_excepthook

import server

t = threading.Thread(target=server.start_server, args=(9090,), daemon=True)
t.start()
time.sleep(2)

print("Making GET request to port 9090...")
try:
    with urllib.request.urlopen("http://127.0.0.1:9090/") as resp:
        print("Response:", resp.getcode())
except Exception as e:
    print("Request failed:", e)
