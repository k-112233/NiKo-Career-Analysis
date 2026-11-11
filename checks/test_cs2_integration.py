import unittest
import pandas as pd
from tools.integrate_cs2 import extract_maps, reconcile


class CS2IntegrationTests(unittest.TestCase):
    def raw_fixture(self):
        row=dict(is_total=False,game_id=123,match_id=456,datetime='2025-01-15 10:00:00',
                 team1='Team Falcons',team2='G2 Esports',score1_game=13,score2_game=8,
                 map_name='Nuke',tournament='Fixture Cup')
        for side in (1,2):
            for slot in range(1,6):
                p=f'team{side}_player{slot}'
                row[p+'_id']=999;row[p]='Other'
                for stat,value in [('kills',20),('deaths',12),('assists',4),('adr',90),('kast',75)]:row[p+'_'+stat]=value
        row['team1_player1_id']=26;row['team1_player1']='NiKo (Nikola Kovač), BA'
        return row

    def extract_fixture(self):
        return extract_maps(pd.DataFrame([self.raw_fixture()]),pd.DataFrame([dict(player_id=26,player_name='NiKo (Nikola Kovač), BA')]))

    def test_series_totals_and_other_niko_excluded(self):
        row=self.raw_fixture();total=dict(row,is_total=True,game_id=-1)
        other=dict(row,team1_player1_id=153,team1_player1='niko (Nikolaj Kristensen), DK',game_id=124)
        result=extract_maps(pd.DataFrame([row,total,other]),pd.DataFrame([dict(player_id=26,player_name='NiKo (Nikola Kovač), BA')]))
        self.assertEqual(len(result),1)
        self.assertEqual(result.iloc[0].record_id,'ektarr:game:123:player:26')
        self.assertEqual(result.iloc[0].result,'win')
        self.assertIsNone(result.iloc[0].rating)

    def test_identity_mapping_must_match(self):
        with self.assertRaises(ValueError):
            extract_maps(pd.DataFrame([self.raw_fixture()]),pd.DataFrame([dict(player_id=26,player_name='Someone else')]))

    def test_rating_only_added_after_combat_and_score_match(self):
        incoming=self.extract_fixture();old=incoming.copy()
        old['rating']=1.2;old['rating_group']='HLTV_displayed_3.0';old['rating_version']='3.0_displayed';old['source_url']='https://example.test/history'
        result,audit=reconcile(old,incoming)
        self.assertEqual(len(result),1)
        self.assertEqual(result.iloc[0].rating,1.2)
        self.assertEqual(audit.iloc[0].status,'matched')
        old['kills']=99
        result,audit=reconcile(old,incoming)
        self.assertTrue(result.empty)
        self.assertEqual(audit.iloc[0].status,'quarantined_conflict')

    def test_near_date_duplicate_is_not_counted_twice(self):
        incoming=self.extract_fixture();old=incoming.copy();old['date']='2025-01-16'
        result,audit=reconcile(old,incoming)
        self.assertEqual(len(result),1)
        self.assertIn('quarantined_date_ambiguity',set(audit.status))

    def test_duplicate_map_join_rejected(self):
        incoming=self.extract_fixture()
        with self.assertRaises(ValueError):reconcile(incoming,pd.concat([incoming,incoming]))


if __name__=='__main__':unittest.main()
