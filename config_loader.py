import yaml

with open('config.yaml', 'r') as file:
    config_data = yaml.safe_load(file)

# Other
COURSES_DIR = config_data.get('courses_dir')

# Google
google_config = config_data.get('google', {})

GOOGLE_CREDENTIALS_FILE = google_config.get('credentials_file')
GOOGLE_TOKEN_FILE = google_config.get('token_file')
LABS_SHEETS_RANGE = google_config.get('credentials_file')

# Github
github_config = config_data.get('github', {})

GITHUB_TOKEN = github_config.get('token')
