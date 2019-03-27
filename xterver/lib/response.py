from typing import Optional, Any, Dict

def json_response(res_type: str="success",
                  msg: str="",
                  data: Optional[Dict[str, Any]]=None) -> Dict[str, Any]:
    content = {"result": res_type, "msg": msg}
    if data is not None:
        content.update(data)
    return content
