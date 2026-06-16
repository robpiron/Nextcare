import traceback
import sys
import threading
import time

import server

original_handle = server.NextCareHandler.handle

def debug_handle(self):
    try:
        original_handle(self)
    except Exception as e:
        print("DEBUG: Exception in handle()!", file=sys.stderr)
        traceback.print_exc(file=sys.stderr)
        raise e

server.NextCareHandler.handle = debug_handle

def debug_log_message(self, format, *args):
    sys.stderr.write("%s - - [%s] %s\n" %
                     (self.address_string(),
                      self.log_date_time_string(),
                      format%args))

server.NextCareHandler.log_message = debug_log_message

print("Starting debug servers (8000 and 8001)...", file=sys.stderr)

try:
    # Start server on Port 8000
    t1 = threading.Thread(target=server.start_server, args=(server.PORT,), daemon=True)
    t1.start()

    # Start server on Port 8001
    t2 = threading.Thread(target=server.start_server, args=(server.PORT_LOCAL,), daemon=True)
    t2.start()

    # Start LIS background engine thread
    t_lis = threading.Thread(target=server.run_lis_engine, daemon=True)
    t_lis.start()

    # Start DICOM MWL background server
    t_mwl = threading.Thread(target=server.run_dicom_mwl_server, daemon=True)
    t_mwl.start()

    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\nArresto dei server in corso.", file=sys.stderr)
except Exception as e:
    traceback.print_exc(file=sys.stderr)
