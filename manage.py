from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from scout import db
from run import scout

migrate = Migrate(scout, db)

manager = Manager(scout)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
