"""
Configuration for MPSI Dashboard
Centralized settings for Flask app, models, and data paths
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'  # Points to /Users/kddv/py_works/mpsi_dash/data

class Config:
    """Base configuration - shared across all environments"""
    
    # ============================================
    # FLASK SETTINGS
    # ============================================
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'mpsi-dev-secret-key-change-in-production-2026'
    DEBUG = False
    TESTING = False
    
    # Server settings
    HOST = '0.0.0.0'  # Accept connections from any IP
    PORT = 5000
    
    # ============================================
    # FILE UPLOAD SETTINGS
    # ============================================
    UPLOAD_FOLDER = BASE_DIR / 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'doc', 'docx'}
    
    # Create upload folder if it doesn't exist
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    
    # ============================================
    # MPSI MODEL SETTINGS
    # ============================================
    
    # Model weights (70% keywords + 30% FinBERT)
    KEYWORD_WEIGHT = 0.70
    FINBERT_WEIGHT = 0.30
    
    # FinBERT model
    MODEL_NAME = "ProsusAI/finbert"
    MODEL_CACHE_DIR = BASE_DIR / 'models' / 'cache'
    
    # MPSI thresholds for stance classification
    HAWKISH_THRESHOLD = 10      # MPSI > 10 = Hawkish
    DOVISH_THRESHOLD = -10      # MPSI < -10 = Dovish
    # Between -10 and 10 = Neutral
    
    # Confidence levels
    HIGH_CONFIDENCE_THRESHOLD = 20    # |MPSI| > 20 = High confidence
    MEDIUM_CONFIDENCE_THRESHOLD = 10  # |MPSI| > 10 = Medium confidence
    # |MPSI| <= 10 = Low confidence
    
    # Text processing
    MIN_WORD_COUNT = 50         # Minimum words in document
    MAX_CHUNKS = 10             # Max chunks for FinBERT analysis
    CHUNK_SIZE = 400            # Words per chunk
    CHUNK_OVERLAP = 200         # Overlap between chunks
    
    # ============================================
    # DATA PATHS
    # ============================================
    
    # Historical data (your existing results)
    HISTORICAL_DATA_PATH = DATA_DIR / 'processed' / 'mpsi_hybrid_scores.csv'
    
    # Runtime directories
    DATABASE_DIR = BASE_DIR / 'data' / 'database'

    # Fed documents (for examples)
    FED_DATA_DIR = DATA_DIR / 'us_fed'
    FOMC_STATEMENTS_DIR = FED_DATA_DIR / 'fomc_statements'
    FOMC_MINUTES_DIR = FED_DATA_DIR / 'fomc_minutes'
    FED_SPEECHES_DIR = FED_DATA_DIR / 'fed_chair_speeches'
    
    
    # ============================================
    # DASHBOARD SETTINGS
    # ============================================
    
    # Pagination
    RESULTS_PER_PAGE = 20
    RECENT_RESULTS_COUNT = 5    # Show 5 most recent on home page
    
    # Chart colors (matching Bootstrap theme)
    CHART_COLORS = {
        'hawkish': '#dc3545',      # Red
        'neutral': '#6c757d',      # Gray
        'dovish': '#0d6efd',       # Blue
        'positive': '#198754',     # Green
        'negative': '#dc3545',     # Red
        'warning': '#ffc107'       # Yellow
    }
    
    # Date format
    DATE_FORMAT = '%Y-%m-%d'
    DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
    
    # ============================================
    # API SETTINGS
    # ============================================
    
    # Rate limiting (for production)
    API_RATE_LIMIT = '100 per hour'  # Max 100 requests per hour per IP
    
    # CORS settings (allow cross-origin requests)
    CORS_ENABLED = True
    CORS_ORIGINS = ['http://localhost:3000', 'https://fedmpsi.com']
    
    # ============================================
    # LOGGING
    # ============================================
    
    LOG_DIR = BASE_DIR / 'logs'
    LOG_DIR.mkdir(exist_ok=True)
    
    LOG_FILE = LOG_DIR / 'mpsi_dashboard.log'
    LOG_LEVEL = 'INFO'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # ============================================
    # EXAMPLE DOCUMENTS (for demo)
    # ============================================
    
    EXAMPLE_DOCS = {
        'hawkish_2022': {
            'path': FOMC_STATEMENTS_DIR / '20220316_statement.txt',
            'description': 'March 2022 FOMC Statement - First rate hike',
            'expected_mpsi': 23.5,
            'expected_stance': 'Hawkish'
        },
        'dovish_2020': {
            'path': FOMC_STATEMENTS_DIR / '20200315_statement.txt',
            'description': 'March 2020 Emergency Statement - COVID response',
            'expected_mpsi': -44.2,
            'expected_stance': 'Dovish'
        },
        'neutral_2021': {
            'path': FOMC_STATEMENTS_DIR / '20210728_statement.txt',
            'description': 'July 2021 Statement - Patient stance',
            'expected_mpsi': -5.3,
            'expected_stance': 'Neutral'
        }
    }
    
    # ============================================
    # VALIDATION STATS (from your research)
    # ============================================
    
    VALIDATION_STATS = {
        'correlation_with_fed_funds': 0.689,
        'p_value': 0.001,
        'r_squared': 0.475,
        'sample_size': 119,
        'date_range': '2020-2026',
        'lead_correlation_3m': 0.78,
        'lead_correlation_6m': 0.85
    }
    
    # ============================================
    # FEATURE FLAGS
    # ============================================
    
    ENABLE_FILE_UPLOAD = True
    ENABLE_API = True
    ENABLE_HISTORICAL_DATA = True
    ENABLE_ANALYTICS = True          # Google Analytics tracking
    ENABLE_EXAMPLE_DOCS = True
    ENABLE_DOWNLOAD = True           # Allow CSV/JSON downloads


class DevelopmentConfig(Config):
    """Development environment settings"""
    DEBUG = True
    TESTING = False
    
    # Use simpler logging in dev
    LOG_LEVEL = 'DEBUG'
    
    # No rate limiting in dev
    API_RATE_LIMIT = '1000 per hour'


class ProductionConfig(Config):
    """Production environment settings"""
    DEBUG = False
    TESTING = False
    
    # Secret key must be set via environment variable in production
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY environment variable must be set in production")
    
    # Stricter rate limiting
    API_RATE_LIMIT = '50 per hour'
    
    # Production logging
    LOG_LEVEL = 'WARNING'
    
    # Only allow HTTPS in production
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True


class TestingConfig(Config):
    """Testing environment settings"""
    DEBUG = False
    TESTING = True
    
    # Use in-memory database for testing
    DATABASE_PATH = ':memory:'
    
    # Disable rate limiting for tests
    API_RATE_LIMIT = None


# ============================================
# CONFIGURATION SELECTOR
# ============================================

config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name=None):
    """Get configuration object based on environment"""
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    return config_by_name.get(config_name, DevelopmentConfig)


# ============================================
# HELPER FUNCTIONS
# ============================================

def validate_config():
    """Validate that all required paths exist"""
    config = Config()
    
    issues = []
    
    # Check historical data
    if not config.HISTORICAL_DATA_PATH.exists():
        issues.append(f"Historical data not found: {config.HISTORICAL_DATA_PATH}")
    
    # Check Fed data directories
    if not config.FED_DATA_DIR.exists():
        issues.append(f"Fed data directory not found: {config.FED_DATA_DIR}")
    
    # Check example documents
    for name, info in config.EXAMPLE_DOCS.items():
        if not info['path'].exists():
            issues.append(f"Example document not found: {name} at {info['path']}")
    
    if issues:
        print("\n⚠️  Configuration Issues Found:")
        for issue in issues:
            print(f"   - {issue}")
        print("\n💡 These are warnings - app will still run but some features may be limited.\n")
    else:
        print("\n✅ Configuration validated successfully!\n")
    
    return len(issues) == 0


if __name__ == "__main__":
    """Test configuration"""
    print("="*70)
    print("MPSI DASHBOARD - CONFIGURATION TEST")
    print("="*70)
    
    # Test configuration loading
    dev_config = get_config('development')
    print(f"\n📝 Development Config:")
    print(f"   DEBUG: {dev_config.DEBUG}")
    print(f"   SECRET_KEY: {dev_config.SECRET_KEY[:20]}...")
    print(f"   KEYWORD_WEIGHT: {dev_config.KEYWORD_WEIGHT}")
    print(f"   FINBERT_WEIGHT: {dev_config.FINBERT_WEIGHT}")
    print(f"   HAWKISH_THRESHOLD: {dev_config.HAWKISH_THRESHOLD}")
    print(f"   DATABASE_PATH: {dev_config.DATABASE_PATH}")
    
    # Test paths
    print(f"\n📁 Data Paths:")
    print(f"   Historical Data: {dev_config.HISTORICAL_DATA_PATH}")
    print(f"   Fed Data Dir: {dev_config.FED_DATA_DIR}")
    print(f"   Upload Folder: {dev_config.UPLOAD_FOLDER}")
    
    # Test validation stats
    print(f"\n📊 Validation Statistics:")
    for key, value in dev_config.VALIDATION_STATS.items():
        print(f"   {key}: {value}")
    
    # Validate configuration
    print(f"\n🔍 Validating Configuration...")
    validate_config()
    
    print("="*70)