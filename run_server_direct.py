import server
try:
    server.start_server(8000)
except Exception as e:
    import traceback
    traceback.print_exc()
