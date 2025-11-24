import time
import json
from functools import wraps

TRACES = {}


def trace(op_name: str):
    def deco(fn):
        @wraps(fn)
        def inner(*a, **kw):
            tid = f"{op_name}_{int(time.time()*1000)}"
            start = time.time()
            try:
                res = fn(*a, **kw)
                status = "ok"
            except Exception as e:
                res = {"error": str(e)}
                status = "error"
            TRACES[tid] = {
                "op": op_name,
                "status": status,
                "ms": int((time.time()-start)*1000),
            }
            return res
        return inner
    return deco


def export_traces() -> str:
    return json.dumps(TRACES, ensure_ascii=False, indent=2)
