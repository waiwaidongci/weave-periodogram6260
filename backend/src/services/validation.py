import numpy as np
from src.constants.numerics import LINEAR_TREND_ALGORITHM_VERSION

def validate_points(points):
 if not 4<=len(points)<=240 or len({p['reference'] for p in points})!=len(points):raise ValueError('需要4..240个唯一测点编号')
 if any(type(p['position']) is bool or type(p['thickness']) is bool for p in points):raise ValueError('数值不能是bool')
 x=np.asarray([p['position'] for p in points],dtype=float);y=np.asarray([p['thickness'] for p in points],dtype=float)
 if not np.isfinite(x).all() or not np.isfinite(y).all() or (x<0).any() or (x>1e12).any() or (y<0).any() or (y>1e6).any():raise ValueError('位置/厚度须有限且在允许范围')
 if len(set(x))!=len(x) or np.ptp(x)>10000:raise ValueError('位置不能重复，测线跨度≤10000mm')
 return sorted(points,key=lambda p:p['position'])

def validate_plan(plan):
 f=np.asarray(plan['frequencies'],dtype=float)
 if f.ndim!=1 or not 3<=len(f)<=401 or not np.isfinite(f).all() or (f<=0).any() or (f>1).any() or (np.diff(f)<=0).any():raise ValueError('频率须3..401个有限严格递增正值且≤1周期/mm')
 if type(plan['permutations']) is not int or not 199<=plan['permutations']<=499 or type(plan['seed']) is not int or not 0<=plan['seed']<=1000000000:raise ValueError('置换次数199..499与seed须合法整数')
 return f

def build_trend_plan(declaration):
 if not isinstance(declaration,str) or not declaration.strip():raise ValueError('趋势校正计划须包含非空声明')
 if len(declaration)>3000:raise ValueError('趋势校正计划声明过长')
 return {'model':'y = c0 + c1*(x - x0) + c0_cyclic + a*cos(2*pi*f*(x-x0)) + b*sin(2*pi*f*(x-x0))','trend_terms':['intercept','linear'],'trend_coordinate':'x - x0，x0为首个有序位置，与相位同用移动坐标以保持数值稳定','baseline_comparison':'同一冻结频率网格上比较含线性趋势的基线模型与叠加周期项后的模型，报告功率差','permutation':'固定x与线性趋势，按基线残差对y标签做置换，每次重新拟合趋势与全部纳入频率','declaration':declaration.strip(),'version':LINEAR_TREND_ALGORITHM_VERSION}
