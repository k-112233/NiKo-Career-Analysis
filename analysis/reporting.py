"""Write a reviewer-facing report from the same summaries used by the dashboard."""
from html import escape
import re
import pandas as pd
from analysis.career import summarize


def number(value,digits=3):
    return f'{value:.{digits}f}' if pd.notna(value) else '未提供'


def write_report(root,frame,provider_summary,recent):
    stage=summarize(frame,['team','game_version','rating_group'])
    maps=summarize(recent,['map']).query('maps >= 20').sort_values('kd',ascending=False)
    outcomes=summarize(recent,['result'])
    f=provider_summary.set_index('team').loc['Falcons']
    g=provider_summary.set_index('team').loc['G2']
    lines=['# NiKo Career Analysis · v1.0.0','','快照核验日期：2026-11-10。统计单位为地图，非 BO3/BO5 系列赛。','',
        '## 主要发现','',
        f'1. **同来源 CS2 样本**：G2 的总 K/D 为 {g.kd:.3f}、平均 ADR 为 {g.mean_adr:.1f}（{int(g.maps)} 张）；Falcons 为 {f.kd:.3f} 和 {f.mean_adr:.1f}（{int(f.maps)} 张）。两个样本属于不同时间、对手和赛制构成，不能据此断言转会导致表现变化。',
        f'2. **地图表现**：在至少 20 张 Falcons 观察地图的组中，{maps.iloc[0]["map"]} 的总 K/D 最高，为 {maps.iloc[0].kd:.3f}（n={int(maps.iloc[0].maps)}）。这是描述性排序，样本量不平衡，不能解释为地图间显著差异。',
        '3. **赢图与输图**：下表展示 Falcons 样本内的同场表现关联。Rating 仅计算有记录的子样本，不用同场信息包装赛前预测。','',
        '## v1 研究范围','',
        f'共 {len(frame):,} 张已接受地图，日期为 {frame.date.min()} 至 {frame.date.max()}；Falcons {len(recent)} 张，G2 CS2 195 张。研究生涯阶段、地图、稳定性及胜负关联。',
        'v1 是固定、部分覆盖的可复现研究快照。排名、赛事阶段、角色和武器数据不足，留作后续版本；不生成这些维度的结论。','',
        '## CS2 同来源对比','',
        '|战队|日期范围|地图|总 K/D|平均 ADR|ADR 有效样本|', '|---|---|---:|---:|---:|---:|']
    for r in provider_summary.itertuples():
        lines.append(f'|{r.team}|{r.first_date} — {r.last_date}|{r.maps}|{r.kd:.3f}|{r.mean_adr:.1f}|{r.adr_maps}|')
    lines+=['','此表只使用 ektarr v10 的已接受地图，避免将缺失 ADR 的网页样本混入同来源对比。提供商未提供 Rating，G2 CS2 Rating 保持缺失。','',
        '## Falcons：地图表现','', '|地图|地图数|总 K/D|平均 ADR|ADR 有效样本|胜率|', '|---|---:|---:|---:|---:|---:|']
    for r in maps.itertuples():
        lines.append(f'|{r.map}|{r.maps}|{r.kd:.3f}|{number(r.mean_adr,1)}|{r.adr_maps}|{r.win_rate:.1%}|')
    lines+=['','![Falcons map profile](figures/falcons_maps.png)','','## Falcons：胜负关联与波动','',
        '|地图结果|地图数|总 K/D|平均 Rating|Rating 有效样本|Rating 标准差|', '|---|---:|---:|---:|---:|---:|']
    for r in outcomes.itertuples():
        lines.append(f'|{r.result}|{r.maps}|{number(r.kd)}|{number(r.mean_rating)}|{r.rated_maps}|{number(r.rating_sd)}|')
    lines+=['','标准差描述观察值的离散程度，不是跨时代的稳定性排名。Rating 的缺失机制可能影响子样本表现，不能假设有 Rating 的地图代表所有地图。','',
        '## 生涯阶段与统计口径','', '|战队|游戏|Rating 组|地图|Rating 有效样本|平均 Rating|总 K/D|','|---|---|---|---:|---:|---:|---:|']
    for r in stage.itertuples():
        lines.append(f'|{r.team}|{r.game_version}|{r.rating_group}|{r.maps}|{r.rated_maps}|{number(r.mean_rating)}|{number(r.kd)}|')
    lines+=['','![Monthly career performance](figures/career.png)','',
        '月度图按 Rating 口径分面，点大小表示有效 Rating 样本数；不连接缺失月份。旧版本标签由历史代码按日期推断，尚不能视为逐条核验的官方方法版本。CS:GO 与 CS2 的回合规则不同，跨游戏对比也需谨慎。','',
        '## 数据质量与合并决定','',
        '- 旧历史来源已通过三个原始 CSV 的 SHA-256 与重新下载的原始档案比对确认。',
        '- 提供商 ID 26 通过全名和国家识别为 Nikola Kovač，排除了 ID 153 的另一位 niko；不混用提供商 ID 和 HLTV ID。',
        '- 231 张地图在日期、队伍、对手、地图、K/D 和比分上匹配后补充网页 Rating。',
        '- 1 个同日地图指标冲突隔离；10 条日期歧义的旧网页观察移出分析，不重复计算，不猜测日期。',
        '- 所有决策见 [合并审计](cs2_reconciliation.csv)，各月样本量见 [覆盖日历](coverage_calendar.csv)。零表示没有载入观察值，不表示选手没有比赛。','',
        '## 指标定义与限制','',
        '- K/D = 有完整击杀和死亡记录的总击杀 / 总死亡；不是地图 K/D 的平均。总死亡为零时缺失。',
        '- Rating 和 ADR 为地图等权均值，各自排除缺失值并报告有效样本数；不是按回合加权的官方汇总。多种非缺失 Rating 口径混合时不计算均值。',
        '- 胜率仅对 win/loss 计算。看板和 CSV 给出 95% Wilson 区间作为描述参考；同系列地图相关，不能将其视为严格独立样本推断。',
        '- 2021–2023 补充层较稀疏，2023 年过渡期以及其他来源遗漏尚未补齐。日期跨度不等于完整覆盖。',
        '- 缺少对照选手、角色和历史排名，不能从本研究推断长期顶尖或转会影响的因果原因。','',
        '## 复现与来源','',
        '`python -m tools.build_portfolio` 离线重建本报告、CSV、图表、SQLite 与看板。输入是 `data/processed/niko_maps.csv`，输入哈希见 [快照清单](manifest.json)。',
        '来源详情见 [来源审计](../docs/sources.md)；许可与署名见 [DATA_LICENSES](../DATA_LICENSES.md)。未持续监控或定时采集。']
    markdown='\n'.join(lines)+'\n'
    (root/'reports/analysis.md').write_text(markdown,encoding='utf-8')
    (root/'reports/analysis.html').write_text(render_html(lines),encoding='utf-8')


def render_html(lines):
    """Render the small Markdown subset emitted above; escape all data first."""
    def inline(value):
        text=escape(value)
        text=re.sub(r'!\[([^]]*)\]\(([^)]+)\)',r'<img alt="\1" src="\2">',text)
        text=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'<a href="\2">\1</a>',text)
        text=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',text)
        return re.sub(r'`([^`]+)`',r'<code>\1</code>',text)
    body=[];table=False
    for line in lines:
        if line.startswith('|'):
            if re.fullmatch(r'[|:\s-]+',line):continue
            tag='td' if table else 'th'
            if not table:body.append('<div class="scroll"><table>');table=True
            body.append('<tr>'+''.join(f'<{tag}>{inline(cell.strip())}</{tag}>' for cell in line.strip('|').split('|'))+'</tr>')
            continue
        if table:body.append('</table></div>');table=False
        if not line:continue
        if line.startswith('# '):body.append('<h1>'+inline(line[2:])+'</h1>')
        elif line.startswith('## '):body.append('<h2>'+inline(line[3:])+'</h2>')
        else:body.append('<p>'+inline(line)+'</p>')
    if table:body.append('</table></div>')
    css='body{font:16px/1.9 system-ui,"Microsoft YaHei",sans-serif;background:#0b1120;color:#e2e8f0;max-width:1050px;margin:auto;padding:32px}h1{font-size:36px}h2{margin-top:42px;color:#5eead4}a{color:#5eead4}img{max-width:100%;height:auto}table{border-collapse:collapse;font-size:14px;white-space:nowrap}td,th{padding:10px 14px;border-bottom:1px solid #334155;text-align:left}.scroll{overflow:auto}code{background:#1e293b;padding:3px 6px}p{overflow-wrap:anywhere}'
    return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>NiKo v1 · Analysis</title><style>'+css+'</style><nav><a href="../dashboard/index.html">← 交互看板</a> · <a href="analysis.md">Markdown</a></nav>'+''.join(body)+'</html>'
