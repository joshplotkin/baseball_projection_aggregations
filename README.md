### Scraping Baseball Projections for Fantasy Baseball
This was written prior to the 2016 season. It requires BeautifulSoup and pandas for python2.7.

#### This utility does the following:
* Scrapes Steamer, ZiPS, Fans projections from fangraphs.com
* Scrapes rankings from razzball.com
* Scrapes expected plate appearances (or innings pitched for pitchers) from fangraphs.com depth charts
* Averages projections by per-PA/IP rates, and prorates to the projected PA/IP
* Generates fantasy baseball rankings for 5x5 or 6x6 systems, given user-defined roster sizes and league
* Rankings are based on z-scores for each category, and a weighted z-score by PA/IP (e.g. a pitcher with 2.50 ERA over 220 IP is more valuable than a pitcher with a 2.25 ERA over 80 IP)
* Writes the following tabs to an Excel file: all hitters, each hitter position, SP, RP


#### Run `python combine_rankings.py` with the following 6 command-line arguments:
* 1. Scoring: 5x5 (AVG/HR/RBI/SB/R, W/SV/ERA/WHIP/K) or 6x6 (OBP/SLG/HR/RBI/SB/R, W/SV/ERA/WHIP/K) scoring
* 2. League: AL, NL, or BOTH
* 3. Estimated number of SP rostered
* 4. Estimated number of Batters rostered
* 5. Estimated number of RP rostered
* 6. Name of output Excel file

#### Sample usage: python combine_rankings.py 5x5 AL 51 120 24 test_output

See test_output.xlsx for sample output.
