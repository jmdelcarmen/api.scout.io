import os

from scout import create_app
from scout.lib import schedules
from multiprocessing import Process


scout = create_app(os.getenv('APP_SETTINGS'))

if __name__ == '__main__':
    with scout.app_context():
        p1 = Process(target=schedules.init)
        p1.start()

        scout.run(port=int(os.getenv('PORT')) or 3000, host='0.0.0.0')

        p1.join()