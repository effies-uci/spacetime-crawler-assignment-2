from datetime import date,time
from pathlib import Path
'''Print crawler data into a text file in reports/ directory'''

NUMFREQWORDS = 20
reportName = ""

def intialize_crawler_log():
    global reportName

    reportName = f"Crawler_Log_{date.today()}"
    f = open(f"reports/{reportName}.txt", "w", encoding="UTF-8")
    f.write(f"REPORT LOG FOR CRAWLER RUN===========\n")
    f.write(f"{reportName} \n")
    f.write("=====================================\n")
    f.close()

def write_page_report(tokenFreq:dict, pageName:str):
    """Write report to log for 1 crawled page"""
    with(open(f"reports/{reportName}.txt", 'a', encoding="UTF-8")) as file:
        file.write(f"{pageName}\n")
        for token, count in tokenFreq:
            file.write(f"-- {token}: {count}\n")
        file.write("\n")

def write_total_report(tokenFreq:dict, uniqueUrls:set, subdomains:dict, pageLens:dict):

    sort_dict = dict(sorted(tokenFreq.items(), key=lambda item: item[1]))


    with(open(f"reports/{reportName}.txt", 'a', encoding="UTF-8")) as file:

        file.write("CRAWLER END OF RUN REPORT===========\n")

        file.write(f"Number of unique pages visited: {len(uniqueUrls)} pages\n")

        file.write(f"{NUMFREQWORDS} Most Frequent Words:\n")
        for i in range(NUMFREQWORDS):
            file.write(f"\t{sort_dict.keys()[i]} - {sort_dict[sort_dict.keys()[i]]} occurences\n")

        file.write(f"Number of subdomains per url:\n")
        for url in subdomains.keys():
            file.write(f"\t{url}.uci.edu - {subdomains[url]} subdomains\n")
        
        file.write(f"Longest page: {getLongestPage(pageLens)}")

        file.write(f"End of Crawler Log.")



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

def getLongestPage(pageLens:dict) -> str:
    longest = 0
    longest_name = ""
    for url in pageLens.keys():
        if pageLens[url] > longest:
            longest = pageLens[url]
            longest_name = url
    return f"{longest_name} ({longest} tokens)"