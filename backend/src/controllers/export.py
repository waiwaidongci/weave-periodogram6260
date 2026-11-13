from fastapi import HTTPException
from src.models import WeaveNote
from src.services.audit import record
from src.utils.csv_export import csv_response

def export_note(db,id,actor):
 note=db.get(WeaveNote,id)
 if not note:raise HTTPException(404,'说明不存在')
 if note.status!='approved':raise HTTPException(409,'仅批准说明可导出')
 r=note.result_snapshot;trend=r.get('trend_plan')
 if trend:rows=[[note.name,r['source_study']['name'],r['fingerprint'],s['frequency'],s['period'],s['power'] if s['included'] else '',s['included'],s['reason'] or '',s['window_power'],s['retained_after_trend'],r['rss_baseline'],r['best']['slope_per_mm'],r['best']['baseline_slope_per_mm'],r['global_test']['global_p'],r['comparison']['before']['global_test']['global_p'],r['global_test']['permutations'],trend['declaration'],note.interpretation,note.next_step,note.review_note] for s in r['spectrum']]
 else:rows=[[note.name,r['source_study']['name'],r['fingerprint'],s['frequency'],s['period'],s['power'] if s['included'] else '',s['included'],s['reason'] or '',s['window_power'],r['global_test']['global_p'],r['global_test']['permutations'],note.interpretation,note.next_step,note.review_note] for s in r['spectrum']]
 record(db,actor,'note.exported',{'note_id':id,'linear_trend_correction':bool(trend)})
 if trend:return csv_response(f'weave-note-{id}.csv',rows,['补测说明','研究','指纹','频率cycles/mm','周期mm','校正后功率','纳入','排除理由','采样窗口功率','趋势后保留比例','基线残差RSS0','校正后线性斜率/mm','基线线性斜率/mm','校正后全网格全局p','校正前全网格全局p','置换B','冻结趋势校正声明','人工解释','下一步','审核意见'])
 return csv_response(f'weave-note-{id}.csv',rows,['补测说明','研究','指纹','频率cycles/mm','周期mm','功率','纳入','排除理由','采样窗口功率','全网格全局p','置换B','人工解释','下一步','审核意见'])
