from __future__ import division
from bs4 import BeautifulSoup
from pandas import *
import requests
import sys

from ScrapeProjections import *
from AverageProjections import *
from ComputeRankings import *

try:
    scoring_input = sys.argv[1]
    league_input = sys.argv[2]
    sp_rostered = int(sys.argv[3])
    batters_rostered = int(sys.argv[4])
    rp_rostered = int(sys.argv[5])
    output_file = sys.argv[6]
except:
    err_msg = 'Enter the following command line arguments: (1) scoring (5x5 or 6x6), '
    err_msg += '(2) League (AL, NL, Both), (3) # of SP rostered, (4) Batters rostered, '
    err_msg += '(5) RP rostered, (6) output excel file name'
    print err_msg
    sys.exit(1)
assert league_input.lower() in ['al', 'nl', 'both'], 'invalid league'

proj = {}
for p in ['steamer', 'fan', 'zips', 'fangraphsdc']:
    proj[p] = ScrapeProjection(p)

ap = AverageProjections(proj)
cr = ComputeRankings({'scoring': scoring_input, 
                      'num_players': {'sp': sp_rostered, 'bat': batters_rostered, 'rp': rp_rostered}, 
                      'league': league_input}, 
                      ap.proj_avg)

#### START RAZZBALL ##################################
r = requests.get('http://razzball.com/top-500-for-2016-fantasy-baseball/').text
soup = BeautifulSoup(r, 'lxml')
table = soup.findAll('table', {'id': 'neorazzstatstable'})[0]

razz_headers = []
for tr in table.findAll('thead')[0]:
    try:
        razz_headers.append(tr.text)
    except:
        pass
razz_headers = [r for r in razz_headers[0].split('\n') if r != '']

def player_exists(p):
    try:
        player = p.findAll('td')
        if len(player) == 0:
            return None
        else:
            return True
    except:
        return None

razz_players = {}
for i, player in enumerate([p for p in table.findAll('tbody')[0] if player_exists(p) == True]):
    razz_players[i] = []
    for td in player.findAll('td'):
        razz_players[i].append(td.text)
        
razz_df = DataFrame.from_dict(razz_players, orient = 'index')
razz_df.columns = razz_headers
razz_df.loc[:, '#'] = range(1, razz_df.shape[0] + 1)

def name_code(name):
    name = name.upper()
    first = name.split(' ')[0].replace('.','')
    last = ''.join(name.split(' ')[1:])
    return first[:3] + last
    
razz_df.loc[:, 'Code'] = razz_df.loc[:, 'Name'].apply(lambda x: name_code(x)) + razz_df.loc[:, 'Team']
razz_df.set_index('Code', inplace = True)

razz_df = razz_df.loc[:, ['#','YAHOO']]
razz_df.columns = 'RAZZ','POS'
#### END RAZZBALL ####################################


def rearrange_cols(df, col, new_idx):
    new_cols = []
    cols = df.columns
    for i, c in enumerate(cols):
        if i+1 == new_idx:
            new_cols.append(col)
            new_cols.append(c)
        elif c == col:
            pass
        else:
            new_cols.append(c)
    if len(new_cols) < len(cols):
        new_cols.append(col)
    return df.loc[:, new_cols]


def merge_rearrange_write(writer, df, razz_df, sheet_name, pos=None):
	df = razz_df.merge(df, left_index = True, right_index = True)\
	             .sort_values(by='TOT', inplace = False, ascending = False)


	df.loc[:, 'Cost'] = ''
	df = rearrange_cols(df, 'Team', len(df.columns))
	df = rearrange_cols(df, 'League', len(df.columns))
	df = rearrange_cols(df, 'Name', 1)
	df = rearrange_cols(df, 'POS', 2)
	df = rearrange_cols(df, 'TOT', 3)
	df = rearrange_cols(df, 'Rank', 4)
	df = rearrange_cols(df, 'Cost', 1)

	df.to_excel(writer, sheet_name)
	# for hitters, add binary position label and write individual sheets
	if pos:
		positions = ['C','1B','2B','3B','SS','OF']
		for pos in positions:
		    df.loc[:, pos] = df.loc[:, 'POS']\
		    						.apply(lambda x: pos in [p.strip() \
		    								for p in x.split(',')]).astype(int)
		df.loc[:, 'DH'] = df.loc[:, positions].sum(axis = 1).apply(lambda x: 1 if x == 0 else 0)

		for pos in positions:
		    df[df.loc[:, pos] == 1].to_excel(writer, pos)



writer = ExcelWriter(output_file.split('.')[0] + '.xlsx')

merge_rearrange_write(writer, cr.batters, razz_df.copy(), 'ALL_HITTERS', True)
merge_rearrange_write(writer, cr.sp, razz_df.copy(), 'ALL_SP')
merge_rearrange_write(writer, cr.rp, razz_df.copy(), 'ALL_RP')


writer.save()

