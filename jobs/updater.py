# job schedular for monitoring our paid and trial members. After the the duration, it will automatically made the user free user(while time is up)
from datetime import datetime
from .jobs import monitorMembeshipStatus
from apscheduler.schedulers.background import BackgroundScheduler

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(monitorMembeshipStatus, 'interval', seconds=20)
    scheduler.start()


