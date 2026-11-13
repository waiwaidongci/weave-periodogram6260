from pydantic import BaseModel,Field,model_validator
class RunInput(BaseModel):
 study_id:int=Field(gt=0,strict=True)
 plan_id:int=Field(gt=0,strict=True)
 name:str=Field(min_length=2,max_length=180)
 trendy:bool=Field(default=False,strict=True)
 algorithm:str|None=Field(default=None,max_length=40)
 trend_declaration:str|None=Field(default=None,max_length=3000)
 @model_validator(mode='after')
 def frozen_trend_plan(self):
  if self.trendy:
   if self.algorithm!='linear-trend':raise ValueError('启用趋势校正时必须预先声明algorithm=linear-trend')
   if not self.trend_declaration or not self.trend_declaration.strip():raise ValueError('启用趋势校正时必须提交预先冻结的趋势校正声明')
  elif self.algorithm is not None or self.trend_declaration is not None:raise ValueError('未启用趋势校正时不得提交趋势字段')
  return self
