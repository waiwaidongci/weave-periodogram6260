from datetime import datetime,date
from sqlalchemy import inspect
def row(obj):
 return {c.key:(getattr(obj,c.key).isoformat() if isinstance(getattr(obj,c.key),(datetime,date)) else getattr(obj,c.key)) for c in inspect(obj).mapper.column_attrs if c.key!='password_hash'}
def run_row(run):
 data=run if isinstance(run,dict) else row(run);data=dict(data);data['linear_trend_correction']=bool(data.get('trend_plan_snapshot'));return data
