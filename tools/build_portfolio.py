"""Build offline report, figures and dashboard from a portable CSV snapshot."""
import hashlib
import json
from pathlib import Path
import os
import sqlite3
import pandas as pd
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault('MPLCONFIGDIR',str(ROOT/'.build/matplotlib'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analysis.career import validate, summarize, coverage

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT = ROOT / 'data/processed/niko_maps.csv'
def build():
    frame=validate(pd.read_csv(SNAPSHOT,keep_default_na=True))
    reports=ROOT/'reports'; figures=reports/'figures'; figures.mkdir(parents=True,exist_ok=True)
    for name,keys in [('team_summary',['team','game_version','rating_group']),('map_summary',['team','game_version','rating_group','map']),('annual_summary',['year','game_version','rating_group']),('outcome_summary',['team','rating_group','result'])]:
        frame['year']=pd.to_datetime(frame.date).dt.year
        summarize(frame,keys).to_csv(reports/f'{name}.csv',index=False)
    cov=coverage(frame);cov.to_csv(reports/'coverage.csv',index=False)
    plt.rcParams.update({'figure.facecolor':'#0e1726','axes.facecolor':'#0e1726','text.color':'#e2e8f0','axes.labelcolor':'#e2e8f0','xtick.color':'#cbd5e1','ytick.color':'#cbd5e1','axes.edgecolor':'#475569','font.size':10})
    groups=list(frame[frame.rating.notna()].groupby('rating_group'))
    fig,axs=plt.subplots(len(groups),1,figsize=(11,3.2*len(groups)),squeeze=False)
    for ax,(name,g) in zip(axs[:,0],groups):
        g=g.copy();g['month']=g.date.str[:7]
        monthly=g.groupby('month').rating.agg(['mean','count'])
        ax.scatter(pd.to_datetime(monthly.index),monthly['mean'],s=monthly['count']*3+10,color='#5eead4')
        ax.set_title(name,loc='left');ax.set_ylabel('Mean map rating');ax.grid(alpha=.12)
    fig.suptitle('NiKo | Observed monthly performance — rating groups kept separate',fontsize=15)
    fig.tight_layout();fig.savefig(figures/'career.png',dpi=160);plt.close(fig)
    recent=frame[frame.team.eq('Falcons') & frame.game_version.eq('CS2')]
    modern=frame[frame.game_version.eq('CS2')]
    summarize(modern,['team']).to_csv(reports/'cs2_combat_comparison.csv',index=False)
    fig,ax=plt.subplots(figsize=(10,5))
    maps=summarize(recent,['map']).query('maps >= 10').sort_values('kd')
    ax.barh(maps['map'],maps.kd,color='#5eead4');ax.set_xlabel('Total kills / total deaths (observed maps)')
    for i,row in enumerate(maps.itertuples()): ax.text(row.kd+.01,i,f'n={row.maps}',va='center',fontsize=9)
    ax.set_title('Falcons | Observed map profile (partial sample, n >= 10)',loc='left');fig.tight_layout();fig.savefig(figures/'falcons_maps.png',dpi=160);plt.close(fig)
    provider=modern[modern.source.eq('ektarr_cs2_v10')]
    provider_summary=summarize(provider,['team'])
    provider_summary.to_csv(reports/'cs2_same_source_comparison.csv',index=False)
    calendar=frame.assign(month=frame.date.str[:7]).groupby(['month','team']).size().unstack(fill_value=0)
    months=pd.date_range(frame.date.min()[:7]+'-01',frame.date.max()[:7]+'-01',freq='MS').strftime('%Y-%m')
    calendar.reindex(months,fill_value=0).rename_axis('month').to_csv(reports/'coverage_calendar.csv')
    from analysis.reporting import write_report
    write_report(ROOT,frame,provider_summary,recent)
    summarize(frame,['team','rating_group','identity_confidence']).to_csv(reports/'identity_sensitivity.csv',index=False)
    # pandas float columns retain NaN after where; normalize through JSON's null form.
    payload=json.loads(frame.to_json(orient='records',date_format='iso'))
    template=(ROOT/'dashboard/template.html').read_text(encoding='utf-8')
    (ROOT/'dashboard/index.html').write_text(template.replace('__DATA__',json.dumps(payload,ensure_ascii=False).replace('</','<\\/')),encoding='utf-8')
    db=ROOT/'database/portfolio.sqlite'
    db.parent.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(db) as conn: frame.to_sql('observed_maps',conn,if_exists='replace',index=False)
    manifest={'version':'1.0.0','snapshot_date':'2026-11-10','rows':len(frame),'date_min':frame.date.min(),'date_max':frame.date.max(),'latest_verified_date':recent.date.max(),'snapshot_sha256':hashlib.sha256(SNAPSHOT.read_bytes()).hexdigest(),'complete_career':False,'known_gaps':['sparse 2021–2023 secondary coverage; late CS:GO 2023 after June 10','early G2 CS2 before 2023-11-30 and provider omissions','provider omissions and 11 quarantined history observations'],'excluded_candidate':'Kaggle griffindesroches: historical rows contain scrape-time roster/player averages; not per-match NiKo data'}
    manifest['team_map_counts']=frame.groupby('team').size().to_dict()
    manifest['cs2_map_counts']=modern.groupby('team').size().to_dict()
    manifest['rated_cs2_maps']=int(modern.rating.notna().sum())
    manifest['source_audit']='data/provenance/sources.json'
    (reports/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False,indent=2))


if __name__=='__main__':
    build()
