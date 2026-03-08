"""
Database Configuration Example

Copy this file to config.py and update with your database credentials.
DO NOT commit config.py to version control.
"""

# PostgreSQL connection settings
DATABASE_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'themed_animation',
    'user': 'your_username',
    'password': 'your_password',
}

# Connection pool settings
POOL_CONFIG = {
    'minconn': 1,
    'maxconn': 10,
}

# Alternative: Use connection string
DATABASE_URL = 'postgresql://your_username:your_password@localhost:5432/themed_animation'

# Environment-specific configurations
ENVIRONMENTS = {
    'development': {
        'host': 'localhost',
        'port': 5432,
        'database': 'themed_animation_dev',
        'user': 'dev_user',
        'password': 'dev_password',
    },
    'testing': {
        'host': 'localhost',
        'port': 5432,
        'database': 'themed_animation_test',
        'user': 'test_user',
        'password': 'test_password',
    },
    'production': {
        'host': 'db.production.example.com',
        'port': 5432,
        'database': 'themed_animation',
        'user': 'prod_user',
        'password': 'prod_password',
        'sslmode': 'require',
    },
}
