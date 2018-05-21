import time
import schedule
from scout.models import Recommendation

def refresh_recommendations_daily():
    Recommendation.create_recommendations_for_today()

def init():
    # TODO: every day
    schedule.every(10).seconds.do(refresh_recommendations_daily)

    while True:
        schedule.run_pending()
        time.sleep(1)
