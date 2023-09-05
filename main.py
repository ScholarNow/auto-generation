import argparse
from config import PATH, CRON
import schedule
import time
from croniter import croniter
from datetime import datetime, timedelta
import os
import concurrent.futures
from job_helper import main

def job(path):
    # get current date
    current_date = datetime.now()

    # get previous date
    previous_date = current_date - timedelta(days=1)

    # format date
    formatted_date = previous_date.strftime("%y%m%d")

    print(f">>>>>>>>>>>>>>>processing {formatted_date}...")

    if os.path.exists(os.path.join(path, formatted_date)) and os.path.isdir(os.path.join(path, formatted_date)) == False:
        print("No files to process")
        return
    
    # get all json files in directory

    json_files = [pos_json for pos_json in os.listdir(os.path.join(path, formatted_date)) if pos_json.endswith('.json')]

    threads = []
    # check if json file has a corresponding pdf file, if not remove it from the list
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        for json_file in json_files:
            if os.path.exists(os.path.join(path, formatted_date, json_file.replace(".json", ".pdf"))) == False:
                json_files.remove(json_file)
                continue
            threads.append(executor.submit(main, path, os.path.basename(json_file).replace(".json",""), formatted_date))

    for thread in threads:
        thread.result()


    

    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="base path of scheduled tasks", default=PATH)
    parser.add_argument("--cron", help="cron expression", default=CRON)
    cfg = parser.parse_args()

    job(cfg.path)
    # parse cron expression
    # iter = croniter(cfg.parse)
    # schedule job
    # schedule.every().day.at(iter.get_next()).do(job, cfg.path)
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)