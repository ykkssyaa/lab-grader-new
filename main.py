import yaml
from fastapi import FastAPI
# from gateway import google_docs, github_api
import os

app = FastAPI()


@app.get('/courses/', response_model=list)
def get_courses():
    courses_dir = 'courses'
    courses_info = []

    if not os.path.exists(courses_dir) or not os.path.isdir(courses_dir):
        return []

    for filename in os.listdir(courses_dir):
        file_path = os.path.join(courses_dir, filename)
        if os.path.isfile(file_path) and filename.endswith('.yaml'):
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    course_config = yaml.safe_load(file)
                    course_info = {
                        'id': filename,
                        'name': course_config.get('course', {}).get('name', ''),
                        'semester': course_config.get('course', {}).get('semester', '')
                    }
                    courses_info.append(course_info)
                except Exception as e:
                    print(f"Error reading {filename}: {str(e)}")

    return courses_info
