import sys

def foo():
    return 42

sys.monitoring.use_tool_id(1, "test")
sys.monitoring.set_events(1, sys.monitoring.events.PY_START)

call_count = 0
def handler(code, offset):
    global call_count
    call_count += 1

sys.monitoring.register_callback(1, sys.monitoring.events.PY_START, handler)
foo()
print(call_count)  # expecting 1?
sys.monitoring.free_tool_id(1)
