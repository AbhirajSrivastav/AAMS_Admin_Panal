"""
app/config.py
=============
Centralized configuration for the Attendance Management System.

This file defines different config classes for development, testing,
and production environments. Values are read from environment variables
(with sensible defaults) so the app is 12-factor compliant and SaaS-ready.
"""

import os
from dotenv import load_dotenv

# Load .env file variables into environment
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(os.path.dirname(basedir), '.env'))


class Config:
    """
    Base configuration shared across all environments.
    """
    # Flask core settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-me')
    FLASK_APP = os.getenv('FLASK_APP', 'run.py')

    # PostgreSQL database settings
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'attendance_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_PORT = int(os.getenv('DB_PORT', '5432'))

    # Face recognition settings
    FACE_TOLERANCE = float(os.getenv('FACE_TOLERANCE', '0.55'))
    IMAGE_DATA_DIR = os.getenv('IMAGE_DATA_DIR', 'app/image_data')

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        """
        Helper property to build a standard PostgreSQL URI.
        Useful if you later migrate to SQLAlchemy ORM.
        """
        return (
            f"postgresql://{self.DB_USER}:{self.DB_PASSWORD}"
            f"@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        )


class DevelopmentConfig(Config):
    """
    Development environment: debug enabled, verbose logging.
    """
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """
    Production environment: debug disabled, strict settings.
    """
    DEBUG = False
    TESTING = False
    # In production, always enforce a strong SECRET_KEY from env var
    SECRET_KEY = os.getenv('SECRET_KEY')


class TestingConfig(Config):
    """
    Testing environment: separate test database, debug enabled for tracebacks.
    """
    DEBUG = True
    TESTING = True
    DB_NAME = os.getenv('DB_TEST_NAME', 'attendance_db_test')


# Dictionary to easily select config by string name
config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig,
}

