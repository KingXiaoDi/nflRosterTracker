from logzero import logger, logfile
from bs4 import BeautifulSoup
import datetime
import requests
import pandas
import sys
import os

def create_folders():
    """Creates various folders used by the code"""
    for each in ['webPage', 'rosterData', 'logs']:
        if not os.path.isdir(each):
            logger.info(f"'{each}' folder does not exist. "
                                f"Making '{each}' folder.")
            os.mkdir(each)
            logger.info(f"'{each}' folder created.")
    return

def setup_Logfile(logFileName='log'):
    """Initiates a log file"""
    create_folders()
    logfile(f'./logs/{logFileName}.log', backupCount = 2, maxBytes = 1e6)
    logger.info(f"Logfile initiated for {__file__}")

def scrape_roster(team, URLpiece):
    """Tries to scrape an NFL team's roster page. If successful,
    saves the HTML to local storage and returns it"""

    fileName = f'webPage/{team}.html'
    logger.info(f'Scraping roster page for {team}')

    try:
        r = requests.get(f'http://www.{URLpiece}.com/team/players-roster/')
        if r.status_code != 200:
            logger.info(f"Scrape failed for {team}"
                        f"HTTP code {r.status_code}"
                        f"Check URL and try again")
            return

        with open(fileName, 'w', encoding='utf-8') as file:
            logger.info(f'Saving roster page for {team}')
            file.write(r.text)
            return (r.text)
    
    except Exception as e:
        logger.error(f'Failed to scrape roster page for {team}\n'
                     f'error: {e}')
        return

def soup_Roster(team, URLpiece):
    """Pull players on roster from scraped HTML. Indicate which roster each
    player is on. Save to local storage. If the roster is of sufficient
    length, delete the previously saved HTML."""

    sourceName = f'webPage/{team}.html'
    saveName = f'rosterData/{team} {datetime.date.today()}.csv'
    
    try:
        with open(sourceName, 'r', encoding='utf-8') as file:
            text = file.read()
    
    except FileNotFoundError:
        text = scrape_roster(team, URLpiece)
    
    except Exception as e:
        print (e)
        logger.error(f'Failed for {team}\n'
                     f'error: {e}')
        return 
    
    if not text is None:
        
        soup = BeautifulSoup(text, 'lxml')
        rosterTables = soup.find_all('table')
        roster = pandas.DataFrame()
        
        for each in rosterTables:
        
            label = each.find('caption')
            label = label.text.replace(' ', '').replace('\n', '')
            table = pandas.read_html(each.prettify(), flavor='bs4')[0]
            table['type'] = label
            roster = roster.append(table)
        
        logger.info(f'Saving roster for {team}')
        roster.to_csv(saveName, index=False)
        
        if len(roster) > 52:
            logger.info(f'Roster looks full,'
                        f' deleting saved roster page for {team}')
            os.remove(sourceName)
        else:
            logger.warning(f'Roster for {team} looks incomplete')
    
teams = {"49ers": "49ers",
        "bears": "chicagobears",
        "bengals": "bengals",
        "bills": "buffalobills",
        "broncos": "denverbroncos",
        "browns": "clevelandbrowns",
        "buccaneers": "buccaneers",
        "cardinals": "azcardinals",
        "chargers": "chargers",
        "chiefs": "chiefs",
        "colts": "colts",
        "cowboys": "dallascowboys",
        "dolphins": "miamidolphins",
        "eagles": "philadelphiaeagles",
        "falcons": "atlantafalcons",
        "giants": "giants",
        "jaguars": "jaguars",
        "jets": "newyorkjets",
        "lions": "detroitlions",
        "packers": "packers",
        "panthers": "panthers",
        "patriots": "patriots",
        "raiders": "raiders",
        "rams": "therams",
        "ravens": "baltimoreravens",
        "saints": "neworleanssaints",
        "seahawks": "seahawks",
        "steelers": "steelers",
        "texans": "houstontexans",
        "titans": "tennesseetitans",
        "vikings": "vikings",
        "washington": "washingtonfootball"}

setup_Logfile()
for team in teams:
    soup_Roster(team, teams[team])