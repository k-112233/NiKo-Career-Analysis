"""Optional real-browser checks: pip install playwright; use installed Edge or Chromium."""
import argparse
import csv
import io
import json
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT=Path(__file__).resolve().parents[1]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--channel',default='msedge')
    args=parser.parse_args()
    errors=[]
    with sync_playwright() as playwright:
        browser=playwright.chromium.launch(channel=args.channel or None,headless=True)
        page=browser.new_page(viewport={'width':1440,'height':1100},accept_downloads=True)
        page.on('pageerror',lambda error:errors.append(str(error)))
        page.goto((ROOT/'dashboard/index.html').as_uri())
        page.locator('#count').wait_for()
        assert page.locator('#count').inner_text()=='381'
        assert page.locator('#chart circle').count()>0
        screenshots=ROOT/'docs/images';screenshots.mkdir(parents=True,exist_ok=True)
        page.screenshot(path=str(screenshots/'dashboard-desktop.png'),full_page=True)
        page.select_option('#team','G2')
        page.select_option('#game','CS2')
        assert page.locator('#count').inner_text()=='195'
        assert page.locator('#avg').inner_text()=='—'
        page.select_option('#metric','adr')
        assert page.locator('#chart circle').count()>0
        with page.expect_download() as event:page.click('#download')
        download=event.value
        rows=list(csv.DictReader(Path(download.path()).read_text(encoding='utf-8-sig').splitlines()))
        assert len(rows)==195
        assert {r['team'] for r in rows}=={'G2'}
        assert {r['game_version'] for r in rows}=={'CS2'}
        assert all(r['adr'] for r in rows)
        assert all(not r['rating'] for r in rows)
        page.fill('#start','2026-01-01');page.locator('#start').dispatch_event('change')
        assert page.locator('#count').inner_text()=='0'
        assert page.locator('#kd').inner_text()=='—'
        page.reload()
        page.select_option('#team','FaZe');page.select_option('#metric','rating')
        assert '请选择单一' in page.locator('#chart').text_content()
        page.select_option('#rating','legacy_date_inferred_2.0')
        assert page.locator('#chart circle').count()>0
        page.reload();page.set_viewport_size({'width':390,'height':844})
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
        page.screenshot(path=str(screenshots/'dashboard-mobile.png'),full_page=True)
        page.goto((ROOT/'reports/analysis.html').as_uri())
        assert page.locator('table').count()>=4
        assert page.locator('h1').inner_text().endswith('v1.0.0')
        assert page.evaluate('Array.from(document.images).every(image=>image.complete&&image.naturalWidth>0)')
        page.goto((ROOT/'index.html').as_uri())
        page.wait_for_url('**/dashboard/index.html')
        assert not errors,errors
        (ROOT/'.build').mkdir(exist_ok=True)
        (ROOT/'.build/browser-validation.json').write_text(json.dumps({'browser':browser.version,'channel':args.channel,'desktop':[1440,1100],'mobile':[390,844],'status':'passed','checks':['filters','ADR','missing Rating','empty state','mixed methodology','CSV download','mobile overflow','report images','entry redirect']},indent=2)+'\n',encoding='utf-8')
        browser.close()
    print('Browser checks passed: desktop, mobile, filters, missing Rating, ADR, empty state, mixed methodology, CSV download.')


if __name__=='__main__':main()
