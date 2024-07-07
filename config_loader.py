import yaml

with open('config.yaml', 'r') as file:
    config_data = yaml.safe_load(file)


COURSES_DIR = config_data.get('courses_dir')

# Google
GOOGLE_CREDENTIALS_FILE = config_data.get('google', {}).get('credentials_file')


# Github
GITHUB_TOKEN = config_data.get('github', {}).get('token')
