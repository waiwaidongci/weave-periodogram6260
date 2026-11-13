from .validation import validate_points,validate_plan
from .qr_cache import build_cache
from .spectrum import observed_spectrum
from .permutation import global_permutation
from .trend import build_trend_cache,observed_trend_spectrum,global_trend_permutation
from .fingerprint import fingerprint
from src.constants.numerics import LINEAR_TREND_ALGORITHM_VERSION

def analyze(study,points,plan):
 points=validate_points(points);f=validate_plan(plan);x=[p['position'] for p in points];y=[p['thickness'] for p in points];cache=build_cache(x,f);result,centered=observed_spectrum(cache,y);test=global_permutation(cache,centered,result['rss0'],result['observed_max_power'],plan['permutations'],plan['seed'])
 return {**result,'global_test':test,'source_study':study,'plan':plan,'n':len(points),'coordinate_origin':cache['origin'],'qr_cache_builds':1,'fingerprint':fingerprint(study,points,plan),'tie_rule':'lowest frequency within absolute power tolerance 1e-12 of maximum; upper-tail null ties use same tolerance','interpretation':'Frozen predeclared frequency grid. Sampling window, aliasing, leakage and grid spacing limit interpretation; the selected period is not a confidence interval or a manufacturing cause. Independent homoscedastic exchangeable errors are required.'}

def uncorrected_reference(study,points,plan):
 try:
  reference=analyze(study,points,plan)
 except Exception as error:
  return {'status':'failed','error':str(error)[:1000],'reason':'同一快照的未校正谱未定义，校正前后不可对照'}
 return {'status':'completed','observed_max_power':reference['observed_max_power'],'best':reference['best'],'global_test':reference['global_test'],'spectrum':[{'frequency':s['frequency'],'period':s['period'],'included':s['included'],'reason':s['reason'],'power':s['power'],'window_power':s['window_power']} for s in reference['spectrum']],'rss0':reference['rss0'],'included_frequencies':reference['included_frequencies'],'excluded_frequencies':reference['excluded_frequencies'],'fingerprint':reference['fingerprint']}

def analyze_trend(study,points,plan,trend_plan):
 points=validate_points(points);f=validate_plan(plan);x=[p['position'] for p in points];y=[p['thickness'] for p in points];cache=build_trend_cache(x,f);result,residuals=observed_trend_spectrum(cache,y);test=global_trend_permutation(cache,residuals,result['observed_max_power'],plan['permutations'],plan['seed']);before=uncorrected_reference(study,points,plan)
 return {**result,'global_test':test,'comparison':{'same_snapshot':True,'snapshot_fingerprint':fingerprint(study,points,plan),'before':before,'after':{'status':'completed','observed_max_power':result['observed_max_power'],'best':result['best'],'global_test':test,'rss_baseline':result['rss_baseline'],'included_frequencies':result['included_frequencies'],'excluded_frequencies':result['excluded_frequencies']}},'source_study':study,'plan':plan,'trend_plan':trend_plan,'n':len(points),'coordinate_origin':cache['origin'],'trend_terms':cache['trend_terms'],'qr_cache_builds':1,'trend_qr_cache_builds':1,'fingerprint':fingerprint(study,points,plan,trend_plan),'algorithm_version':LINEAR_TREND_ALGORITHM_VERSION,'tie_rule':'最大峰频率在同tol并列时取较低频率；上尾null并列按同一tol保守计入','interpretation':'预先冻结的线性趋势校正计划：基线模型含截距与线性趋势，周期项叠加后比较相对基线残差的增量功率。全谱、最大功率零分布与全局p只对冻结搜索范围、iid可交换同方差基线残差的无周期null解释；不是制造原因、在线诊断或观测峰后改范围的单频p。'}
