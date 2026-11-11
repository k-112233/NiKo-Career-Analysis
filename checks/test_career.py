import unittest
from pathlib import Path
import pandas as pd
from analysis.career import summarize, validate, wilson

ROOT=Path(__file__).resolve().parents[1]


class CareerTests(unittest.TestCase):
    def setUp(self):
        self.frame=pd.DataFrame([
            dict(record_id='a',date='2025-01-01',team='Falcons',map='Nuke',kills=20,deaths=10,rating=1.4,adr=90,rating_group='3',source='fixture',identity_confidence='test',result='win',game_version='CS2'),
            dict(record_id='b',date='2025-01-02',team='Falcons',map='Nuke',kills=10,deaths=20,rating=None,adr=None,rating_group='3',source='fixture',identity_confidence='test',result='draw',game_version='CS2')])

    def test_weighted_kd_and_missing_metrics(self):
        row=summarize(self.frame,['team']).iloc[0]
        self.assertEqual(row.kd,1)
        self.assertEqual(row.rated_maps,1)
        self.assertEqual(row.mean_rating,1.4)
        self.assertEqual(row.win_rate,1)

    def test_duplicate_and_bad_date_rejected(self):
        with self.assertRaises(ValueError): validate(pd.concat([self.frame,self.frame]))
        self.frame.loc[0,'date']='invalid'
        with self.assertRaises(ValueError): validate(self.frame)

    def test_wilson_boundaries(self):
        self.assertEqual(wilson(0,0),(None,None))
        lo,hi=wilson(5,10)
        self.assertAlmostEqual(lo,0.236593,places=5)
        self.assertAlmostEqual(hi,0.763407,places=5)

    def test_csv_numeric_strings(self):
        self.frame['adr']=['90','-']
        row=summarize(self.frame,['team']).iloc[0]
        self.assertEqual(row.adr_maps,1)
        self.assertEqual(row.mean_adr,90)

    def test_nonfinite_and_missing_identity_rejected(self):
        self.frame['kills']=self.frame.kills.astype(float)
        self.frame.loc[0,'kills']=float('inf')
        with self.assertRaises(ValueError):validate(self.frame)
        self.frame.loc[0,'kills']=20
        self.frame.loc[0,'record_id']=''
        with self.assertRaises(ValueError):validate(self.frame)

    def test_rating_versions_not_pooled(self):
        self.frame.loc[1,'rating']=2.0
        self.frame.loc[1,'rating_group']='different_methodology'
        row=summarize(self.frame,['team']).iloc[0]
        self.assertEqual(row.rated_maps,2)
        self.assertTrue(pd.isna(row.mean_rating))
        self.assertTrue(pd.isna(row.rating_sd))

    def test_snapshot_contract(self):
        frame=validate(pd.read_csv(ROOT/'data/processed/niko_maps.csv'))
        self.assertEqual(len(frame),2030)
        recent=frame[frame.source.eq('hltv_public_history_snapshot')]
        self.assertEqual(recent.date.max(),'2026-11-04')
        self.assertEqual(set(recent.team),{'Falcons'})
        self.assertTrue(recent.adr.isna().all())
        provider=frame[frame.source.eq('ektarr_cs2_v10')]
        self.assertEqual(len(provider),542)
        self.assertEqual(set(provider.team),{'Falcons','G2'})
        self.assertTrue(provider.adr.notna().all())
        self.assertTrue(frame.groupby(['team','game_version','rating_group']).size().sum()==len(frame))


if __name__=='__main__':unittest.main()
