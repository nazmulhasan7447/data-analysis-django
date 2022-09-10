from datetime import datetime
from .jobs import monitorMembeshipStatus
from apscheduler.schedulers.background import BackgroundScheduler

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(monitorMembeshipStatus, 'interval', seconds=20)
    scheduler.start()


