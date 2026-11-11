"""Analysis helpers shared by notebooks, report and dashboard."""
import math
import pandas as pd


def validate(frame):
    frame = frame.copy()
    required = {'record_id', 'date', 'team', 'map', 'kills', 'deaths', 'rating', 'adr', 'rating_group', 'source', 'identity_confidence', 'result', 'game_version'}
    missing = required - set(frame)
    if missing:
        raise ValueError(f'Missing columns: {sorted(missing)}')
    for column in ['kills', 'deaths', 'rating', 'adr']:
        frame[column] = pd.to_numeric(frame[column], errors='coerce')
        if frame[column].dropna().map(lambda value: not math.isfinite(value)).any():
            raise ValueError(f'Non-finite {column}')
    for column in ['record_id', 'team', 'map', 'source', 'rating_group']:
        if frame[column].isna().any() or frame[column].astype(str).str.strip().eq('').any():
            raise ValueError(f'Missing {column}')
    if frame.empty or frame.record_id.duplicated().any():
        raise ValueError('Empty dataset or duplicate record IDs')
    if pd.to_datetime(frame.date, format='%Y-%m-%d', errors='coerce').isna().any():
        raise ValueError('Invalid dates')
    if (frame[['kills', 'deaths', 'rating', 'adr']] < 0).any().any():
        raise ValueError('Negative combat counts')
    if (frame[['kills','deaths']].dropna() % 1 != 0).any().any():
        raise ValueError('Non-integer combat counts')
    if not set(frame.result).issubset({'win', 'loss', 'draw', 'unknown'}):
        raise ValueError('Invalid map outcome')
    return frame


def wilson(wins, total):
    if total == 0:
        return (None, None)
    z = 1.959963984540054
    p = wins / total
    center = (p + z*z/(2*total))/(1+z*z/total)
    half = z*math.sqrt(p*(1-p)/total + z*z/(4*total*total))/(1+z*z/total)
    return center-half, center+half


def summarize(frame, keys):
    frame = frame.copy()
    for column in ['kills', 'deaths', 'rating', 'adr']:
        frame[column] = pd.to_numeric(frame[column], errors='coerce')
    output = []
    for values, g in frame.groupby(keys, dropna=False, sort=True):
        values = values if isinstance(values, tuple) else (values,)
        row = dict(zip(keys, values))
        wins = int(g.result.eq('win').sum())
        losses = int(g.result.eq('loss').sum())
        combat = g.dropna(subset=['kills', 'deaths'])
        deaths = combat.deaths.sum()
        low, high = wilson(wins, wins+losses)
        same_rating = g.loc[g.rating.notna(), 'rating_group'].nunique() <= 1
        row.update(maps=len(g), rated_maps=int(g.rating.count()), mean_rating=g.rating.mean() if same_rating else None,
                   rating_sd=g.rating.std() if same_rating else None, adr_maps=int(g.adr.count()), mean_adr=g.adr.mean(),
                   kd=combat.kills.sum()/deaths if deaths else None,
                   combat_maps=len(combat), wins=wins, losses=losses,
                   win_rate=wins/(wins+losses) if wins+losses else None,
                   win_ci_low=low, win_ci_high=high, first_date=g.date.min(), last_date=g.date.max())
        output.append(row)
    return pd.DataFrame(output)


def coverage(frame):
    return summarize(frame, ['source', 'team', 'game_version', 'rating_group'])
