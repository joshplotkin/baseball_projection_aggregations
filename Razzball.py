import requests

class ScrapeRazzball:
    def __init__(self):


    def         
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
    razz_df.head()