from pandas import *

class ComputeRankings:
    def __init__(self, league_format, dfs):
        self.num_players = league_format['num_players']
        self.set_categories(league_format['scoring'])
        self.generate_datasets(dfs, league_format['league'])
        self.calc_sp_scores()
        self.calc_batter_scores()
        self.calc_rp_scores()
        self.clean_numbers()
                
    def set_categories(self, scoring):
        if scoring == '6x6':
            self.categories = {
                'sp': ['W','K/BB','ERA','WHIP','K/9'],
                'rp': ['SV','K/BB','ERA','WHIP','K/9'],
                'bat': ['HR','RBI','R','SB','SLG','OBP']
                }
        elif scoring == '5x5':
            self.categories = {
                'sp': ['W','ERA','WHIP','K/9'],
                'rp': ['SV','ERA','WHIP','K/9'],
                'bat': ['HR','RBI','R','SB','AVG']
                }
        
    def generate_datasets(self, dfs, league):
        self.batters = dfs['bat']
        pitchers = dfs['pit']
        if league.lower() in ['al','nl']:
            self.batters = self.batters[self.batters.League == league.upper()]
            pitchers = pitchers[pitchers.League == league.upper()]


        pitchers.loc[:, 'BB'] = pitchers.loc[:, 'BB/9'] * 9
        pitchers.loc[:, 'K/BB'] = pitchers.loc[:, 'K/9'] / pitchers.loc[:, 'BB/9']
        sp_threshold = 0.25
        self.sp = pitchers[pitchers.loc[:, 'SP%_DC'] > sp_threshold]
        self.rp = pitchers[pitchers.loc[:, 'SP%_DC'] <= sp_threshold]
        
    def compute_rate_scores(self, df, score_cat, weight_cat, direction, pos):
        df.loc[:, weight_cat] = df.loc[:, weight_cat].astype('float')
        
        avg = (df.iloc[:self.num_players[pos], :][score_cat].astype('float') * \
               df.iloc[:self.num_players[pos], :][weight_cat].astype('float')).sum()\
                / df.iloc[:self.num_players[pos], :][weight_cat].sum()

        df.loc[:, '{0}_X'.format(score_cat)] = (df.loc[:, score_cat] - avg) * df.loc[:, weight_cat]
        cat_mean = df.loc[:, '{0}_X'.format(score_cat)].mean()
        cat_sd = df.loc[:, '{0}_X'.format(score_cat)].std()

        df.loc[:, '{0}_Z'.format(score_cat)] = direction*(df.loc[:, '{0}_X'.format(score_cat)] \
                                                    - cat_mean) \
                                                    / cat_sd
        return df

    def compute_count_scores(self, df, score_cat, pos):
        cat_mean = df.iloc[:self.num_players[pos], :][score_cat].mean()
        cat_sd = df.iloc[:self.num_players[pos], :][score_cat].std()
        df.loc[:, '{0}_Z'.format(score_cat)] = (df.loc[:, score_cat] - cat_mean) / cat_sd
        return df
    
    def calc_sp_scores(self):
        while True:
            old = self.sp.copy()
            self.sp = self.compute_rate_scores(self.sp, 'ERA', 'IP_DC', -1, 'sp')
            self.sp = self.compute_rate_scores(self.sp, 'WHIP', 'IP_DC', -1, 'sp')
            self.sp = self.compute_rate_scores(self.sp, 'K/9', 'IP_DC', 1, 'sp')
            self.sp = self.compute_rate_scores(self.sp, 'K/BB', 'BB', 1, 'sp')
            self.sp = self.compute_count_scores(self.sp, 'W', 'sp')
            self.sp.loc[:, 'TOT'] = self.sp.loc[:, [c + '_Z' for c in self.categories['sp']]].mean(axis = 1)
            self.sp.sort_values(by = 'TOT', ascending = False, inplace = True)
            if self.sp.index.all(old.index):
                break

        self.sp = self.sp.drop([c for c in self.sp.columns if '_X' in c], axis = 1)
        
    def calc_batter_scores(self):
        while True:
            old = self.batters.copy()
            self.batters = self.compute_rate_scores(self.batters, 'AVG', 'AB_DC', 1, 'bat')
            self.batters = self.compute_rate_scores(self.batters, 'SLG', 'AB_DC', 1, 'bat')
            self.batters = self.compute_rate_scores(self.batters, 'OBP', 'PA_DC', 1, 'bat')
            self.batters = self.compute_count_scores(self.batters, 'HR', 'bat')
            self.batters = self.compute_count_scores(self.batters, 'SB', 'bat')
            self.batters = self.compute_count_scores(self.batters, 'RBI', 'bat')
            self.batters = self.compute_count_scores(self.batters, 'R', 'bat')
            self.batters.loc[:, 'TOT'] = self.batters.loc[:, [c + '_Z' for c in self.categories['bat']]].mean(axis = 1)
            self.batters = self.batters.sort_values(by = 'TOT', ascending = False)
            if self.batters.index.all(old.index):
                break
        self.batters = self.batters.drop([c for c in self.batters.columns if '_X' in c], axis = 1)

    def calc_rp_scores(self):
        while True:
            old = self.rp.copy()
            self.rp = self.compute_rate_scores(self.rp, 'ERA', 'IP_DC', -1, 'rp')
            self.rp = self.compute_rate_scores(self.rp, 'WHIP', 'IP_DC', -1, 'rp')
            self.rp = self.compute_rate_scores(self.rp, 'K/9', 'IP_DC', 1, 'rp')
            self.rp = self.compute_rate_scores(self.rp, 'K/BB', 'BB', 1, 'rp')
            self.rp = self.compute_count_scores(self.rp, 'SV', 'rp')
            self.rp.loc[:, 'TOT'] = self.rp.loc[:, [c + '_Z' for c in self.categories['rp']]].mean(axis = 1)
            self.rp.sort_values(by = 'TOT', ascending = False, inplace = True)
            if self.rp.index.all(old.index):
                break

        self.rp = self.rp.drop([c for c in self.rp.columns if '_X' in c], axis = 1)
        
    def clean_numbers(self):
        for df in [self.sp, self.batters, self.rp]:
            df.loc[:, 'Rank'] = range(1, df.shape[0] + 1)
            for c in df.columns:
                if df.loc[:, c].dtype == 'float64':
                    df.loc[:, c] = df.loc[:, c].apply(lambda x: '{:.2f}'.format(x) ).astype('float')