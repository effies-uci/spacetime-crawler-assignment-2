from datetime import date,time
from pathlib import Path
'''Print crawler data into a text file in reports/ directory'''

NUMFREQWORDS = 20
reportName = ""

def intialize():
    reportName = f"Crawler_Log_{date.today()}"
    f = open(f"reports/{reportName}.txt", "w", encoding="UTF-8")
    f.write(f"REPORT LOG FOR CRAWLER RUN===========\n")
    f.write(f"{reportName} \n")
    f.write("=====================================\n")
    f.close()

def pageReport(tokenFreq:dict, pageName:str):
    with(open(f"reports/{reportName}.txt", 'a', encoding="UTF-8")) as file:
        file.write(f"{pageName}\n")
        file.write(f"{tokenFreq}")
        file.write("\n")

def finalReport(tokenFreq:dict, numPagesVisited:int):
    sortDict = dict(sorted(tokenFreq.items(), key=lambda item: item[1]))
    with(open(f"reports/{reportName}.txt", 'a', encoding="UTF-8")) as file:
        file.write("END REPORT==================\n")
        file.write(f"Number of pages visited: {int} pages\n")
        file.write(f"{NUMFREQWORDS} Most Frequent Words:\n")
        for i in range(NUMFREQWORDS):
            file.write(f"{sortDict.keys()[i]}: {sortDict[sortDict.keys()[i]]} occurences\n")


def write_final_report(
        report_path: Path,
        unique_urls: set,
        word_freq: dict,
        longest_dict: dict,
        subdomain_pages: dict
):
    # Unique Pages
    # Longest Page
    # Top 20 most common words
    # Subdomains in uci.edu
    pass