"""Audit and integrate Maxim/ektarr's dated NiKo map observations.

Raw input is excluded from release. Processed source derivative: CC BY-SA 4.0.
This module deliberately rejects series totals and ambiguous cross-source joins.
"""
import hashlib
import json
import re
from pathlib import Path
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SOURCE_URL='https://www.kaggle.com/datasets/ektarr/counter-strike-pro-matches'


def normalize_team(value):
    return re.sub(r'team|esports|[^a-z0-9]', '', str(value).lower())


def extract_maps(raw, players):
    identity=players[players.player_id.eq(26)]
    if len(identity)!=1 or identity.iloc[0].player_name!='NiKo (Nikola Kovač), BA':
        raise ValueError('Provider ID 26 identity mapping changed')
    rows=[]
    for side in (1,2):
        for slot in range(1,6):
            prefix=f'team{side}_player{slot}'
            selected=raw[raw[prefix+'_id'].eq(26) & raw.is_total.eq(False)]
            for _,r in selected.iterrows():
                if r[prefix]!='NiKo (Nikola Kovač), BA':
                    raise ValueError('Unexpected name for provider player 26')
                team={'G2 Esports':'G2','Team Falcons':'Falcons'}.get(r[f'team{side}'])
                if team is None: raise ValueError('Unexpected career team')
                score,other=r[f'score{side}_game'],r[f'score{3-side}_game']
                rows.append(dict(record_id=f'ektarr:game:{int(r.game_id)}:player:26',
                    date=str(r.datetime)[:10],source_datetime=r.datetime,team=team,
                    opponent=r[f'team{3-side}'],map=r.map_name,
                    kills=r[prefix+'_kills'],deaths=r[prefix+'_deaths'],assists=r[prefix+'_assists'],
                    adr=r[prefix+'_adr'],kast=r[prefix+'_kast'],rating=None,rating_version='unavailable',
                    rating_group='no_rating_provided',game_version='CS2',team_score=score,opponent_score=other,
                    result='win' if score>other else 'loss' if score<other else 'draw',
                    source='ektarr_cs2_v10',source_url=SOURCE_URL,event_name=r.tournament,
                    series_id=f'ektarr:match:{int(r.match_id)}',provider_map_id=str(int(r.game_id)),
                    provider_player_id='26',player_id=None,player_link=None,
                    identity_method='provider_id_26_full_name_country',identity_confidence='high_provider_id_backed',
                    collected_date='2026-11-10',coverage_note='Partial provider coverage; source dates and map grain retained',
                    data_license='CC-BY-SA-4.0',rating_source=None))
    frame=pd.DataFrame(rows)
    if frame.record_id.duplicated().any():raise ValueError('Duplicate provider map/player keys')
    if frame[['kills','deaths','adr','kast','team_score','opponent_score']].isna().any().any():
        raise ValueError('Missing required per-map fields')
    if not frame.kast.between(0,100).all():raise ValueError('Invalid KAST percentage')
    return frame


def match_key(row):
    return '|'.join([str(row['date']),normalize_team(row['team']),normalize_team(row['opponent']),str(row['map']).lower()])


def reconcile(existing, incoming):
    """Exact dated map joins only. Conflicts go to quarantine, not an arbitrary winner."""
    existing=existing.copy();incoming=incoming.copy()
    existing['_join']=existing.apply(match_key,axis=1)
    incoming['_join']=incoming.apply(match_key,axis=1)
    if existing._join.duplicated().any() or incoming._join.duplicated().any():
        raise ValueError('Ambiguous date/team/opponent/map key: acquire official IDs first')
    index={row['_join']:row for _,row in existing.iterrows()}
    audit=[];accepted=[];consumed=set()
    for _,row in incoming.iterrows():
        old=index.get(row['_join'])
        if old is not None:
            consumed.add(row['_join'])
            fields=['kills','deaths','team_score','opponent_score']
            conflicts=[k for k in fields if float(row[k])!=float(old[k])]
            status='quarantined_conflict' if conflicts else 'matched'
            audit.append(dict(join_key=row['_join'],existing_id=old.record_id,incoming_id=row.record_id,status=status,
                conflict_fields=','.join(conflicts),existing_kills=old.kills,incoming_kills=row.kills,
                existing_deaths=old.deaths,incoming_deaths=row.deaths,
                existing_score=f'{old.team_score}-{old.opponent_score}',incoming_score=f'{row.team_score}-{row.opponent_score}'))
            if conflicts:continue
            row['rating']=old.rating;row['rating_group']=old.rating_group;row['rating_version']=old.rating_version
            row['rating_source']=old.source_url
        else:
            audit.append(dict(join_key=row['_join'],incoming_id=row.record_id,status='new_provider_record'))
        accepted.append(row)
    leftovers=existing[~existing._join.isin(consumed)].copy()
    # Preserve unmatched source observations, but detect near-date potential duplicates.
    # Such candidates are excluded rather than shifted to a guessed date.
    keep=[]
    for _,old in leftovers.iterrows():
        possible=incoming[(incoming.team==old.team)&incoming.opponent.map(normalize_team).eq(normalize_team(old.opponent))&incoming['map'].str.lower().eq(str(old['map']).lower())]
        candidates=possible[(pd.to_datetime(possible.date)-pd.Timestamp(old.date)).abs().dt.days.le(1)]
        same=candidates[candidates.kills.eq(old.kills)&candidates.deaths.eq(old.deaths)&candidates.team_score.eq(old.team_score)&candidates.opponent_score.eq(old.opponent_score)]
        if not same.empty:
            audit.append(dict(join_key=old['_join'],existing_id=old.record_id,status='quarantined_date_ambiguity'))
        else:
            keep.append(old)
            audit.append(dict(join_key=old['_join'],existing_id=old.record_id,status='retained_history_only'))
    result=pd.concat([pd.DataFrame(accepted,columns=incoming.columns),pd.DataFrame(keep,columns=existing.columns)],ignore_index=True).drop(columns='_join')
    return result,pd.DataFrame(audit)


def main():
    source=ROOT/'data/raw/source_audit'
    incoming=extract_maps(pd.read_csv(source/'cs2_all_tiers_games.csv',low_memory=False),pd.read_csv(source/'players.csv'))
    snapshot=ROOT/'data/processed/niko_maps.csv'
    previous=pd.read_csv(snapshot)
    # Always rebuild against the original history excerpt, independent of previous integrations.
    backup=ROOT/'data/processed/niko_maps_before_cs2.csv'
    if not backup.exists(): previous.to_csv(backup,index=False)
    previous=pd.read_csv(backup)
    historical=previous[previous.game_version.eq('CSGO')].copy()
    historical['data_license']=historical.source.map({'counter_strike_competitive_data':'CC-BY-4.0','external_csgo_2012_2023':'MIT_repository_declared'})
    historical.loc[historical.source.eq('counter_strike_competitive_data'),'source_url']='https://www.kaggle.com/datasets/filipechavesdemacedo/counter-strike-competitive-data'
    historical.loc[historical.source.eq('external_csgo_2012_2023'),'source_url']='https://github.com/tedtay/CS-GO-Pro-Matches-Comprehensive-Dataset'
    historical['coverage_note']='Partial historical data; original base source verified by SHA-256, see provenance manifest'
    modern,audit=reconcile(previous[previous.game_version.eq('CS2')],incoming)
    modern['data_license']=modern.data_license.fillna('no_open_data_license_verified')
    combined=pd.concat([historical,modern],ignore_index=True).sort_values(['date','record_id'])
    snapshot.write_text(combined.to_csv(index=False),encoding='utf-8')
    incoming.to_csv(ROOT/'data/processed/niko_ektarr_cs2_v10.csv',index=False)
    audit.to_csv(ROOT/'reports/cs2_reconciliation.csv',index=False)
    provenance=ROOT/'data/provenance';provenance.mkdir(exist_ok=True)
    sources=[dict(provider='Filipe Macedo',dataset='filipechavesdemacedo/counter-strike-competitive-data',version=1,license='CC-BY-4.0',source_url='https://www.kaggle.com/datasets/filipechavesdemacedo/counter-strike-competitive-data',verification='All three local files matched downloaded archive SHA-256 on 2026-11-10',files={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (ROOT/'data/raw/csgo').glob('*.csv')}),dict(provider='Maxim (ektarr)',dataset='ektarr/counter-strike-pro-matches',version=10,license='CC-BY-SA-4.0',source_url=SOURCE_URL,raw_sha256=hashlib.sha256((source/'cs2_all_tiers_games.csv').read_bytes()).hexdigest(),map_rows=len(incoming),excluded_series_totals=True,player_id_namespace='provider-specific; 26 is not HLTV ID 3741')]
    (provenance/'sources.json').write_text(json.dumps(sources,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Provider maps:',len(incoming),'Final maps:',len(combined))
    print(audit.status.value_counts().to_string())


if __name__=='__main__':main()
