from pandas import *

class AverageProjections:
    def __init__(self, proj):
        self.proj_avg = {'bat': {}, 'pit': {}}
        self.set_calculations()
        for pos in ['bat','pit']:
            self.average_projections(proj, pos)
            self.scale_back(pos)
        
    def set_calculations(self):
        self.categories = \
            {'bat': {
                'scale': ['RBI','HR','SB','R'], 
                'all': ['Name','Tooltip','Team','League','PA','AB',
                        'R','RBI','HR','SB','AVG','SLG','OBP'],
                'avg': ['PA','AB','R','RBI','HR','SB','AVG','SLG','OBP']
                 }, 
             'pit': {
                'scale': ['W','SV'],
                'all': ['Name','Tooltip','Team','League','GS','G','IP',
                        'W','SV','ERA','WHIP','K/9','BB/9','SP%'],
                'avg': ['GS','G','IP','W','SV','ERA','WHIP','K/9','BB/9','SP%']
                }
             }                

    def average_projections(self, proj, pos):
        if pos == 'bat':
            scale_stat = 'PA'
        else:
            scale_stat = 'IP'

        for p in proj.keys():
            tmp = proj[p].dfs[pos].copy()

            for stat in self.categories[pos]['scale']:
                tmp.loc[:, stat] = tmp.loc[:, stat].astype('float') / tmp.loc[:, scale_stat].astype('float')
            self.proj_avg[pos][p] = tmp.loc[:, self.categories[pos]['all']]

        s = self.proj_avg[pos]['steamer'].loc[:, self.categories[pos]['avg']].astype('float')
        z = self.proj_avg[pos]['zips'].loc[:, self.categories[pos]['avg']].astype('float')
        f = self.proj_avg[pos]['fan'].loc[:, self.categories[pos]['avg']].astype('float')
        combine = s.merge(z, how = 'outer', left_index = True, 
                              right_index = True, suffixes = ('_S','_Z'))\
                   .merge(f, how = 'outer', left_index = True, right_index = True)

        for c in self.categories[pos]['avg']:
            combine.loc[:, c] = combine[[c + '_S', c + '_Z', c]].mean(axis = 1)
        combine = combine.loc[:, self.categories[pos]['avg']]

        self.proj_avg[pos] = self.proj_avg[pos]['steamer'].loc[:, ['Name','Tooltip','Team','League']]\
                                .merge(combine, left_index = True, right_index = True)

        if pos == 'bat':
            self.proj_avg[pos] = self.proj_avg[pos].join(proj['fangraphsdc']\
                                        .dfs[pos].loc[:, ['PA','AB']], rsuffix = '_DC')
        else:
            self.proj_avg[pos] = self.proj_avg[pos].join(proj['fangraphsdc']\
                                        .dfs[pos].loc[:, ['G','GS','IP','SP%']], rsuffix = '_DC')

    def scale_back(self, pos):
        if pos == 'bat':
            scale_stat = self.proj_avg[pos].loc[:, 'PA_DC'].astype('float')
        else:
            scale_stat = self.proj_avg[pos].loc[:, 'IP_DC'].astype('float')

        for cat in self.categories[pos]['scale']:
            self.proj_avg[pos].loc[:, cat] = (self.proj_avg[pos].loc[:, cat] * scale_stat)\
                                                .apply(lambda x: 0 if np.isnan(x) else x)