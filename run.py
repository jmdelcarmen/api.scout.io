import os
from scout import create_app

scout = create_app(os.getenv('APP_SETTINGS'))

if __name__ == '__main__':
    scout.run(port=int(os.getenv('PORT')) or 3000, host='0.0.0.0')
