import json,hashlib
from src.constants.numerics import ALGORITHM_VERSION,LINEAR_TREND_ALGORITHM_VERSION
def fingerprint(study,points,plan,trend_plan=None):
 payload={'version':ALGORITHM_VERSION,'study':study,'points':sorted(points,key=lambda p:p['position']),'plan':plan}
 if trend_plan is not None:payload={'version':LINEAR_TREND_ALGORITHM_VERSION,'study':study,'points':sorted(points,key=lambda p:p['position']),'plan':plan,'trend_plan':trend_plan}
 return hashlib.sha256(json.dumps(payload,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
