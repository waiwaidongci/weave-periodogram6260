import numpy as np
from src.constants.numerics import QR_RANK_TOL,POWER_TIE_TOL,LINEAR_TREND_REASON

def trend_basis(x):
 x=np.asarray(x,dtype=float)
 if x.ndim!=1 or len(x)<4 or not np.isfinite(x).all() or (np.diff(x)<=0).any():raise ValueError('线性趋势需要递增唯一有限位置')
 origin=float(x[0]);t=x-origin;design=np.column_stack((np.ones_like(t),t));Q,R=np.linalg.qr(design,mode='reduced')
 return origin,t,Q,R

def residualize(Q,columns): return columns-Q@(Q.T@columns)

def baseline_residual(Q,y): return y-Q@(Q.T@y)

def build_trend_cache(x,frequencies):
 x=np.asarray(x,dtype=float);f=np.asarray(frequencies,dtype=float)
 if f.ndim!=1 or not len(f) or not np.isfinite(f).all() or (f<=0).any() or (np.diff(f)<=0).any():raise ValueError('趋势QR需要递增正频率')
 origin,t,Q_t,R_t=trend_basis(x);entries=[];Q=[];valid=[]
 for index,frequency in enumerate(f):
  phase=2*np.pi*frequency*t;c=np.cos(phase);s=np.sin(phase);uv=residualize(Q_t,np.column_stack((c,s)));sv=np.linalg.svd(uv,compute_uv=False);threshold=QR_RANK_TOL*max(float(sv[0]),np.sqrt(len(x)));window=float(c.mean()**2+s.mean()**2);retained=float((uv[:,0]@uv[:,0]+uv[:,1]@uv[:,1])/len(x))
  common={'frequency':float(frequency),'singular_values':sv.tolist(),'window_power':window,'retained_after_trend':retained,'trend_rank_tolerance':float(threshold)}
  if sv[-1]<=threshold:entries.append({**common,'included':False,'reason':LINEAR_TREND_REASON,'retained_after_trend':None});continue
  q,R=np.linalg.qr(uv,mode='reduced');entries.append({**common,'included':True,'reason':None,'R':R,'Q':q,'cos':c,'sin':s,'residual_cos':uv[:,0],'residual_sin':uv[:,1]});Q.append(q.T);valid.append(index)
 if not Q:return {'origin':origin,'x':x,'t':t,'frequencies':f,'entries':entries,'Q_t':Q_t,'R_t':R_t,'Q':np.zeros((0,0)),'valid_indices':[],'cache_builds':1,'trend_terms':2}
 return {'origin':origin,'x':x,'t':t,'frequencies':f,'entries':entries,'Q_t':Q_t,'R_t':R_t,'Q':np.stack(Q),'valid_indices':valid,'cache_builds':1,'trend_terms':2}

def trend_powers(cache,residuals,rss_baseline):
 if rss_baseline<=0:return np.zeros(len(cache['valid_indices']))
 coefficients=np.einsum('fkn,n->fk',cache['Q'],residuals);return np.clip(np.sum(coefficients*coefficients,axis=1)/rss_baseline,0,1)

def observed_trend_spectrum(cache,y):
 y=np.asarray(y,dtype=float)
 if y.ndim!=1 or not np.isfinite(y).all():raise ValueError('厚度须有限一维')
 Q_t,R_t=cache['Q_t'],cache['R_t'];baseline_coefficients=np.linalg.solve(R_t,Q_t.T@y);baseline_fit=Q_t@(R_t@baseline_coefficients);rss_baseline=float(np.sum((y-baseline_fit)**2))
 if rss_baseline<=1e-12*max(1.0,float(y@y)):raise ValueError('恒定厚度或厚度完全由线性趋势解释，基线残差RSS0数值为零，趋势校正谱功率未定义')
 if not cache['valid_indices']:raise ValueError('全谱退化：全部预设频率的周期项与线性趋势不可区分，趋势校正谱无可用频率')
 residuals=baseline_residual(Q_t,y);scores=trend_powers(cache,residuals,rss_baseline);maximum=float(scores.max());choice=int(np.flatnonzero(scores>=maximum-POWER_TIE_TOL)[0]);grid_index=cache['valid_indices'][choice];entry=cache['entries'][grid_index];frequency=entry['frequency'];a,b=np.linalg.solve(entry['R'],entry['Q'].T@residuals);cyclic=a*entry['cos']+b*entry['sin'];intercept,slope=baseline_coefficients-np.linalg.solve(R_t,Q_t.T@cyclic);fitted=Q_t@(R_t@np.array([intercept,slope]))+cyclic;rss=float(np.sum((y-fitted)**2));amplitude=float(np.hypot(a,b));phase=float(np.arctan2(b,a))
 scoremap={idx:float(scores[i]) for i,idx in enumerate(cache['valid_indices'])}
 spectrum=[{'frequency':e['frequency'],'period':1/e['frequency'],'included':e['included'],'reason':e['reason'],'singular_values':e['singular_values'],'trend_rank_tolerance':e['trend_rank_tolerance'],'power':scoremap.get(i),'rss':rss_baseline*(1-scoremap[i]) if i in scoremap else None,'baseline_rss':rss_baseline,'window_power':e['window_power'],'retained_after_trend':e['retained_after_trend']} for i,e in enumerate(cache['entries'])]
 best={'frequency':frequency,'period':1/frequency,'power':float(scores[choice]),'intercept':float(intercept),'slope_per_mm':float(slope),'cos_coefficient':float(a),'sin_coefficient':float(b),'amplitude':amplitude,'phase_rad':phase,'phase_origin':cache['origin'],'phase_definition':'c0 + c1*(x-x0) + A*cos(2*pi*f*(x-x0)-phi), phi=atan2(sin_coefficient,cos_coefficient)','rss':rss,'baseline_rss':rss_baseline,'incremental_rss':float(rss_baseline-rss),'baseline_intercept':float(baseline_coefficients[0]),'baseline_slope_per_mm':float(baseline_coefficients[1])}
 fit=[{'position':float(x),'observed':float(v),'fitted':float(pred),'baseline_fitted':float(trend_pred),'residual':float(v-pred),'baseline_residual':float(v-trend_pred)} for x,v,pred,trend_pred in zip(cache['x'],y,fitted,baseline_fit)]
 return {'rss_baseline':rss_baseline,'observed_max_power':maximum,'spectrum':spectrum,'included_frequencies':len(scores),'excluded_frequencies':len(spectrum)-len(scores),'best':best,'fit':fit},residuals

def global_trend_permutation(cache,residuals,observed_max,B,seed,permutation_indices=None):
 rng=np.random.default_rng(seed);null=[]
 iterable=permutation_indices if permutation_indices is not None else (rng.permutation(len(residuals)) for _ in range(B))
 Q_t=cache['Q_t']
 for indices in iterable:
  permuted=np.asarray(residuals,dtype=float)[np.asarray(indices,dtype=int)];refit=baseline_residual(Q_t,permuted);rss_permuted=float(refit@refit)
  null.append(float(trend_powers(cache,refit,rss_permuted).max()) if rss_permuted>0 else 0.0)
 count=sum(v>=observed_max-POWER_TIE_TOL for v in null);p=(count+1)/(len(null)+1);hist,edges=np.histogram(null,bins=np.linspace(0,1,21))
 return {'permutations':len(null),'seed':seed,'null_maxima':null,'exceedances_with_ties':count,'global_p':p,'minimum_monte_carlo_p':1/(len(null)+1),'power_tie_tolerance':POWER_TIE_TOL,'histogram':{'counts':hist.tolist(),'edges':edges.tolist()},'definition':'Fixed x and predeclared linear trend; permute the baseline residuals of y, refit the trend least-squares to every permuted vector, and score each included frequency against its own permuted baseline RSS, then take the full-grid maximum. p=(1+#nullmax>=observedmax-tol)/(B+1).','assumptions':'iid exchangeable, homoscedastic baseline residuals under no spatial periodic signal; the linear trend is a nuisance baseline, not evidence. Not single-frequency p, period CI, process cause, or online diagnosis.'}
