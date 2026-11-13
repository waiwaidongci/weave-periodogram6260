import {fmt} from '../utils/format';

export function SpectrumPlot({result,window=false,retained=false}:{result:any;window?:boolean;retained?:boolean}){
 const data=result.spectrum,W=1000,H=330,L=60,R=24,T=30,B=44;
 const min=data[0].frequency,max=data.at(-1).frequency;
 const key=window?'window_power':retained?'retained_after_trend':'power';
 const x=(f:number)=>L+(W-L-R)*(f-min)/(max-min);
 const y=(v:number)=>T+(H-T-B)*(1-v);
 const pathFor=(selector:(p:any)=>number|null|undefined)=>{let path='',start=true;for(const p of data){const v=selector(p);if(v===null||v===undefined){start=true;continue}path+=(start?'M':'L')+x(p.frequency)+','+y(Math.min(1,Math.max(0,v)))+' ';start=false}return path};
 const title=window?'采样窗口函数':retained?'线性趋势后周期项保留比例':'冻结频率网格 / 归一功率';
 const subtitle=window?'|mean(exp(iω(x−x₀)))|²':retained?'||(I−P_trend)[cos,sin]||² / N':'power = 1 − RSSf / RSS0';
 const caption=window?'采样位置本身的窗口结构；混叠和泄漏仍需核对。':retained?'逐频率展示线性趋势吸收后仍可用于周期项的方差比例；比例接近0说明周期项与趋势不可区分。':`cycles/mm · ${result.included_frequencies}纳入 / ${result.excluded_frequencies}退化排除；排除点不连线。`;
 return <figure className={window?'window-plot':retained?'retained-plot':'spectrum-plot'}>
  <figcaption><strong>{title}</strong><span>{subtitle}</span></figcaption>
  <svg viewBox={`0 0 ${W} ${H}`} role="img" aria-label={title}>
   {[0,.25,.5,.75,1].map(v=><g key={v}><line x1={L} y1={y(v)} x2={W-R} y2={y(v)} className="plot-grid"/><text x={L-12} y={y(v)+4} textAnchor="end">{v}</text></g>)}
   {Array.from({length:6},(_,i)=>{const f=min+(max-min)*i/5;return <g key={i}><line x1={x(f)} y1={T} x2={x(f)} y2={H-B} className="plot-tick"/><text x={x(f)} y={H-15} textAnchor="middle">{fmt(f,4)}</text></g>})}
   <path d={pathFor(p=>p[key])} className={window?'window-path':retained?'retained-path':'power-path'}/>
   {!window&&!retained&&<line x1={x(result.best.frequency)} y1={T} x2={x(result.best.frequency)} y2={H-B} className="peak-line"/>}
   {!window&&!retained&&<circle cx={x(result.best.frequency)} cy={y(result.best.power)} r="5" className="peak-dot"/>}
   {!window&&!retained&&data.filter((p:any)=>!p.included).map((p:any)=><path key={p.frequency} d={`M${x(p.frequency)-3},${H-B-5}l6,10m-6,0l6,-10`} className="excluded-mark"/>)}
  </svg>
  <div className="plot-caption">{caption}</div>
 </figure>
}
