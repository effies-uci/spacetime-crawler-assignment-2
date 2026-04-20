from datetime import date,time
from pathlib import Path
'''Print crawler data into a text file in reports/ directory'''

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

