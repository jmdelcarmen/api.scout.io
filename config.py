import os

class Config:
    DEBUG = False
    SECRET_KEY = os.getenv('JWT_SECRET')
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI_LOCAL')
    SQLALCHEMY_TRACK_MODIFICATIONS = True

class TestingConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI_TEST') or super().SQLALCHEMY_DATABASE_URI

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI_DEV') or super().SQLALCHEMY_DATABASE_URI

class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.getenv('DB_URI_PROD') or super().SQLALCHEMY_DATABASE_URI

app_config = {
    'testing': TestingConfig,
    'development': DevelopmentConfig,
    'production': ProductionConfig,
}