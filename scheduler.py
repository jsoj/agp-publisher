import os
import time
import datetime
from zoneinfo import ZoneInfo
from autonomous_publisher import main as run_publisher

TARGET_TIME = datetime.time(8, 0, 0)
TZ = ZoneInfo("America/Sao_Paulo")

def get_next_run():
    now = datetime.datetime.now(TZ)
    target_today = datetime.datetime.combine(now.date(), TARGET_TIME, tzinfo=TZ)
    if now < target_today:
        return target_today
    else:
        return target_today + datetime.timedelta(days=1)

def run_job():
    print(f"[{datetime.datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S %Z')}] Starting daily publisher execution...")
    try:
        run_publisher()
        print(f"[{datetime.datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S %Z')}] Daily publisher executed successfully.")
    except Exception as e:
        print(f"[{datetime.datetime.now(TZ).strftime('%Y-%m-%d %H:%M:%S %Z')}] Error running publisher: {e}")

def main_loop():
    print(f"Scheduler started. Target daily run time: {TARGET_TIME} ({TZ})")
    
    # Optional execution on startup for testing deployment
    run_on_startup = os.environ.get("RUN_ON_STARTUP", "false").lower() == "true"
    if run_on_startup:
        print("RUN_ON_STARTUP is enabled. Executing job immediately...")
        run_job()
        
    while True:
        next_run = get_next_run()
        now = datetime.datetime.now(TZ)
        sleep_seconds = (next_run - now).total_seconds()
        print(f"Next run scheduled at: {next_run.strftime('%Y-%m-%d %H:%M:%S %Z')}. Sleeping for {sleep_seconds:.1f} seconds...")
        
        # Sleep in intervals of 1 hour to keep container responsive and logs streaming
        while sleep_seconds > 0:
            to_sleep = min(sleep_seconds, 3600)
            time.sleep(to_sleep)
            now = datetime.datetime.now(TZ)
            sleep_seconds = (next_run - now).total_seconds()
            
        run_job()

if __name__ == "__main__":
    main_loop()
