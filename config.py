import os

class Config:
    DEBUG = True
    SECRET_KEY = os.getenv('JWT_SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI_LOCAL')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class TestingConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI_TEST') or Config.SQLALCHEMY_DATABASE_URI

class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI_DEV') or Config.SQLALCHEMY_DATABASE_URI

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI_PROD') or Config.SQLALCHEMY_DATABASE_URI

app_config = {
    'local': Config,
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}