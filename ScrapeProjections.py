from __future__ import division
import requests
from bs4 import BeautifulSoup
from pandas import *


class ScrapeProjection:
    def __init__(self, proj):
        self.proj = proj
        self.dfs = {}        
        
        for pos in ['bat', 'pit']:
            self.all_players = {}
            self.i = 0
            
            for team in range(1,31):
                table = self.scrape_raw_table(pos, team)
                if team == 1:
                    self.make_headers(table)
                self.add_players(table)
                
            self.dfs[pos] = self.create_df(pos)
            self.transform_team(pos)
            self.player_code(pos)
        
        if proj == 'zips':
            self.dfs['pit'].loc[:, 'SV'] = np.float('nan')

    def scrape_raw_table(self, pos, team):
        url = 'http://www.fangraphs.com/projections.aspx?'
        url += 'pos=all&stats={0}&type={1}&team={2}&'\
                    .format(pos, self.proj, team)
        url += 'lg=all&players=0'
        if pos == 'pit':
            url += '&sort=9,d'
        else:
            url += '&sort=3,d'
                        
        r = requests.get(url, stream=True).text
        soup = BeautifulSoup(r, 'lxml')
        return soup.findAll('table', {'class': 'rgMasterTable'})[0]
 
    def make_headers(self, table):
        headers = table.findAll('thead')[0].findAll('tr')[-1]
        self.headers = [str(h.text) if h.text != '' 
                        else 'Tooltip' for h in headers.findAll('th') ]

    def add_players(self, table):
        players = table.findAll('tbody')[-1]
        for tr in players.findAll('tr'):
            self.all_players[self.i] = []
            for td in tr.findAll('td'):
                if td.text == '':
                    self.all_players[self.i].append(td.a['tooltip'])
                else:
                    self.all_players[self.i].append(td.text)
            self.i += 1

    def create_df(self, pos):
        df = DataFrame.from_dict(self.all_players, orient = 'index')
        df.columns = self.headers
        if pos == 'bat':
            df = df[df.loc[:, 'PA'] > 10]
        else:
            df = df[df.loc[:, 'G'] > 1]
            df.loc[:, 'SP%'] = df.loc[:, 'GS'].astype('float') / df.loc[:, 'G'].astype('float')
            
        return df
    
    def transform_team(self, pos):
        abbrev = {
            'Angels': {'Team': 'LAA', 'League': 'AL'},
            'Astros': {'Team': 'HOU', 'League': 'AL'},
            'Athletics': {'Team': 'OAK', 'League': 'AL'},
            'Blue Jays': {'Team': 'TOR', 'League': 'AL'},
            'Braves': {'Team': 'ATL', 'League': 'NL'},
            'Brewers': {'Team': 'MIL', 'League': 'NL'},
            'Cardinals': {'Team': 'STL', 'League': 'NL'},
            'Cubs': {'Team': 'CHN', 'League': 'NL'},
            'Diamondbacks': {'Team': 'ARI', 'League': 'NL'},
            'Dodgers': {'Team': 'LAN', 'League': 'NL'},
            'Giants': {'Team': 'SF', 'League': 'NL'},
            'Indians': {'Team': 'CLE', 'League': 'AL'},
            'Mariners': {'Team': 'SEA', 'League': 'AL'},
            'Marlins': {'Team': 'MIA', 'League': 'NL'},
            'Mets': {'Team': 'NYN', 'League': 'NL'},
            'Nationals': {'Team': 'WAS', 'League': 'NL'},
            'Orioles': {'Team': 'BAL', 'League': 'AL'},
            'Padres': {'Team': 'SD', 'League': 'NL'},
            'Phillies': {'Team': 'PHI', 'League': 'NL'},
            'Pirates': {'Team': 'PIT', 'League': 'NL'},
            'Rangers': {'Team': 'TEX', 'League': 'AL'},
            'Rays': {'Team': 'TB', 'League': 'AL'},
            'Red Sox': {'Team': 'BOS', 'League': 'AL'},
            'Reds': {'Team': 'CIN', 'League': 'NL'},
            'Rockies': {'Team': 'COL', 'League': 'NL'},
            'Royals': {'Team': 'KC', 'League': 'AL'},
            'Tigers': {'Team': 'DET', 'League': 'AL'},
            'Twins': {'Team': 'MIN', 'League': 'AL'},
            'White Sox': {'Team': 'CHA', 'League': 'AL'},
            'Yankees': {'Team': 'NYA', 'League': 'AL'} 
        }
        
        self.dfs[pos].loc[:, 'League'] = self.dfs[pos].loc[:, 'Team']\
                                        .apply(lambda x: abbrev[x]['League'])

        self.dfs[pos].loc[:, 'Team'] = self.dfs[pos].loc[:, 'Team']\
                                        .apply(lambda x: abbrev[x]['Team'])
    
    def player_code(self, pos):
        def name_code(name):
            name = name.upper()
            first = name.split(' ')[0].replace('.','')
            last = ''.join(name.split(' ')[1:])
            return first[:3] + last
            
        name = self.dfs[pos].loc[:, 'Name'].apply(lambda x: name_code(x))
        team = self.dfs[pos].loc[:, 'Team']
        self.dfs[pos].loc[:, 'Code'] = name + team        
        self.dfs[pos].set_index('Code', inplace = True)