import yaml
from fastapi import FastAPI, Path, HTTPException, Request, Body
from fastapi.responses import JSONResponse
import google_docs
import github_api
from config_loader import COURSES_DIR
import os

app = FastAPI()


@app.get('/courses/', response_model=list)
def get_courses():
    courses_info = []

    if not os.path.exists(COURSES_DIR) or not os.path.isdir(COURSES_DIR):
        return []

    for filename in os.listdir(COURSES_DIR):
        file_path = os.path.join(COURSES_DIR, filename)
        if os.path.isfile(file_path) and filename.endswith('.yaml'):
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    course_config = yaml.safe_load(file)
                    course_info = {
                        'id': filename[:-5],  # Получение только название файла
                        'name': course_config.get('course', {}).get('name', ''),
                        'semester': course_config.get('course', {}).get('semester', '')
                    }
                    courses_info.append(course_info)
                except Exception as e:
                    print(f"Error reading {filename}: {str(e)}")

    return courses_info


@app.get('/courses/{course_id}/', response_model=dict)
def get_course(course_id: str = Path(..., description="Course ID")):
    course_file = os.path.join(COURSES_DIR, f'{course_id}.yaml')

    if not os.path.exists(course_file) or not os.path.isfile(course_file):
        raise HTTPException(status_code=404, detail="Course not found")

    with open(course_file, 'r', encoding='utf-8') as file:
        try:
            course_config = yaml.safe_load(file)
            course_info = {
                'id': course_id,
                'config': f'{course_id}.yaml',
                'name': course_config.get('course', {}).get('name', ''),
                'semester': course_config.get('course', {}).get('semester', ''),
                'email': course_config.get('course', {}).get('email', ''),
                'github-organization': course_config.get('course', {}).get('github', {}).get('organization', ''),
                'google-spreadsheet': course_config.get('course', {}).get('google', {}).get('spreadsheet', '')
            }
            return course_info
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.get('/courses/{course_id}/groups', response_model=list)
def get_course_groups(course_id: str = Path(..., description="Course ID")):
    course_file = os.path.join(COURSES_DIR, f'{course_id}.yaml')

    if not os.path.exists(course_file) or not os.path.isfile(course_file):
        raise HTTPException(status_code=404, detail="Course not found")

    with open(course_file, 'r', encoding='utf-8') as file:
        try:

            course_config = yaml.safe_load(file)
            google_spreadsheet_field = course_config.get('course', {}).get('google', {}).get('spreadsheet', '')

            if not google_spreadsheet_field:
                return []

            groups = google_docs.get_course_groups(google_spreadsheet_field)

            info_sheet_name = course_config.get('course', {}).get('google', {}).get('info-sheet', '')

            if info_sheet_name in groups:
                groups.remove(info_sheet_name)

            return groups

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.get('/courses/{course_id}/groups/{group_id}/labs', response_model=list)
def get_course_group_labs(
        course_id: str = Path(..., description="Course ID"),
        group_id: str = Path(..., description="Group ID")
):
    course_file = os.path.join(COURSES_DIR, f'{course_id}.yaml')

    if not os.path.exists(course_file) or not os.path.isfile(course_file):
        raise HTTPException(status_code=404, detail="Course not found")

    with open(course_file, 'r', encoding='utf-8') as file:
        try:
            course_config = yaml.safe_load(file)
            google_spreadsheet = course_config.get('course', {}).get('google', {}).get('spreadsheet', '')

            if not google_spreadsheet:
                return []

            lab_short_names = []

            # Извлекаем сокращенные названия лабораторных работ из конфигурационного файла
            lab_config = course_config.get('course', {}).get('labs', {})
            for lab_key in lab_config:
                short_name = lab_config[lab_key].get('short-name', '')
                if short_name:
                    lab_short_names.append(short_name)

            group_sheets_labs = google_docs.get_course_group_labs(google_spreadsheet, group_id)
            group_labs = []

            for group in lab_short_names:
                if group in group_sheets_labs:
                    group_labs.append(group)

            return group_labs
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))


@app.post("/courses/{course_id}/groups/{group_id}/register")
def register_student(
        data=Body(),
        course_id: str = Path(..., description="Course ID"),
        group_id: str = Path(..., description="Group ID")
):
    # Проверка наличия и длины полей
    required_fields = ["name", "surname", "github"]
    for field in required_fields:
        if field not in data or not isinstance(data[field], str) or len(data[field]) == 0:
            raise HTTPException(status_code=422, detail="Validation error")

    # Проверка patronymic
    if "patronymic" in data and not isinstance(data["patronymic"], str):
        raise HTTPException(status_code=422, detail="Validation error")

    # Чтение конфига курса
    course_file = os.path.join(COURSES_DIR, f'{course_id}.yaml')

    if not os.path.exists(course_file) or not os.path.isfile(course_file):
        raise HTTPException(status_code=404, detail="Course not found")

    with open(course_file, 'r', encoding='utf-8') as file:
        try:
            course_config = yaml.safe_load(file)
            google_spreadsheet = course_config.get('course', {}).get('google', {}).get('spreadsheet', '')

            if not google_spreadsheet:
                raise HTTPException(status_code=500, detail="Error with reading google spreadsheet field")

            groups = google_docs.get_course_groups(google_spreadsheet)
            if group_id not in groups:
                raise HTTPException(status_code=404, detail="Group not found in course")

            students = google_docs.get_students_of_group(google_spreadsheet, group_id)

            full_name = f"{data['surname']} {data['name']}"
            if data['patronymic']:
                full_name += f" {data['patronymic']}"

            if full_name not in students:
                raise HTTPException(status_code=404, detail="Студент не найден")

            if not github_api.is_user_exist(data['github']):
                raise HTTPException(status_code=404, detail="Пользователь GitHub не найден")

            github_column = google_docs.find_github_column(google_spreadsheet, group_id)

            if github_column is None:
                raise HTTPException(status_code=500, detail="Ошибка получения столбца GitHub")

            student_index = students.index(full_name) + 3

            google_docs.update_cell(
                google_spreadsheet,
                group_id,
                github_column[:-1], str(student_index),
                data['github'],
                check_null=True
            )

            return {"message": "Аккаунт GitHub успешно задан"}

        except ValueError as ve:
            raise HTTPException(status_code=422, detail=str(ve))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
