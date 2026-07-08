from datetime import date
from pathlib import Path
from uuid import uuid4

import httpx
from fastapi import APIRouter, File, Form, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, EmailStr, ValidationError, field_validator

router = APIRouter(tags=['Работники'])
templates = Jinja2Templates(directory='app/templates')

API_BASE_URL = 'http://127.0.0.1:8000/api/v1/employees'
UPLOAD_DIR = Path('app/static/images/avatars')
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def calc_age(date_of_birth: str) -> int:
    dob = date.fromisoformat(date_of_birth)
    today = date.today()
    return today.year - dob.year - (
        (today.month, today.day) < (dob.month, dob.day)
    )


async def fetch_employees(page: int = 1, size: int = 10) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            API_BASE_URL, params={'page': page, 'size': size},
        )
        response.raise_for_status()
        return response.json()


async def fetch_employee(employee_id: int) -> dict:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f'{API_BASE_URL}/{employee_id}')
        response.raise_for_status()
        return response.json()


def build_page_numbers(page: int, pages: int) -> list[int]:
    if pages <= 1:
        return [1]
    start = max(1, page - 2)
    end = min(pages, page + 2)
    if end - start < 4:
        if start == 1:
            end = min(pages, 5)
        elif end == pages:
            start = max(1, pages - 4)
    return list(range(start, end + 1))


async def save_photo(photo: UploadFile | None) -> str | None:
    if not photo or not photo.filename:
        return None

    suffix = Path(photo.filename).suffix.lower()
    filename = f'{uuid4().hex}{suffix}'
    file_path = UPLOAD_DIR / filename

    content = await photo.read()
    file_path.write_bytes(content)

    return f'/static/images/avatars/{filename}'


class EmployeeForm(BaseModel):
    last_name: str
    first_name: str
    middle_name: str | None = ''
    date_of_birth: date
    sex: str
    phone_number: str
    email: EmailStr

    @field_validator('last_name', 'first_name')
    @classmethod
    def not_empty(cls, v):
        v = (v or '').strip()
        if not v:
            raise ValueError('Поле обязательно для заполнения')
        return v

    @field_validator('sex')
    @classmethod
    def sex_allowed(cls, v):
        if v not in ('Муж.', 'Жен.'):
            raise ValueError('Выберите пол')
        return v

    @field_validator('phone_number')
    @classmethod
    def phone_allowed(cls, v):
        v = (v or '').strip()
        digits = ''.join(ch for ch in v if ch.isdigit())
        if len(digits) < 10:
            raise ValueError('Введите корректный номер телефона')
        return v

    @field_validator('date_of_birth')
    @classmethod
    def dob_allowed(cls, v):
        if v >= date.today():
            raise ValueError('Дата рождения должна быть в прошлом')
        return v


def validation_errors_to_dict(exc: ValidationError) -> dict[str, str]:
    errors: dict[str, str] = {}
    for err in exc.errors():
        field = err['loc'][0]
        errors[field] = err['msg']
    return errors


def build_form_data(
    last_name: str = '',
    first_name: str = '',
    middle_name: str = '',
    date_of_birth: str = '',
    sex: str = '',
    phone_number: str = '',
    email: str = '',
) -> dict:
    return {
        'last_name': last_name,
        'first_name': first_name,
        'middle_name': middle_name,
        'date_of_birth': date_of_birth,
        'sex': sex,
        'phone_number': phone_number,
        'email': email,
    }


def make_employee_for_edit(employee_id: int, form_data: dict) -> dict:
    return {
        'id': employee_id,
        'last_name': form_data.get('last_name', ''),
        'first_name': form_data.get('first_name', ''),
        'middle_name': form_data.get('middle_name', ''),
        'date_of_birth': form_data.get('date_of_birth', ''),
        'sex': form_data.get('sex', ''),
        'phone_number': form_data.get('phone_number', ''),
        'email': form_data.get('email', ''),
        'age': '',
        'photo': None,
    }


@router.get('/employees', response_class=HTMLResponse, name='employees_roster')
async def employees_roster(
    request: Request,
    page: int = 1,
    size: int = 10,
):
    payload = await fetch_employees(page=page, size=size)
    items = payload.get('items', [])

    workers = []
    for item in items:
        workers.append(
            {
                'id': item['id'],
                'full_name': f'{item["last_name"]} {item["first_name"]} '
                '{item["middle_name"]}',
                'age': calc_age(item['date_of_birth']),
                'phone_number': item['phone_number'],
                'sex': item['sex'],
                'photo': item['photo'],
            },
        )

    pages = payload.get('pages', 1)
    return templates.TemplateResponse(
        request=request,
        name='employees/roster.html',
        context={
            'workers': workers,
            'page': page,
            'size': size,
            'total': payload.get('total', 0),
            'pages': pages,
            'page_numbers': build_page_numbers(page, pages),
        },
    )


@router.get(
    '/employees/add',
    response_class=HTMLResponse,
    name='employees_create',
)
async def employees_create(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='employees/add.html',
        context={'errors': {}, 'form_data': build_form_data()},
    )


@router.post('/employees/add', name='employees_store')
async def employees_store(
    request: Request,
    last_name: str = Form(''),
    first_name: str = Form(''),
    middle_name: str = Form(''),
    date_of_birth: str = Form(''),
    sex: str = Form(''),
    phone_number: str = Form(''),
    email: str = Form(''),
    photo: UploadFile | None = File(None),
):
    form_data = build_form_data(
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        date_of_birth=date_of_birth,
        sex=sex,
        phone_number=phone_number,
        email=email,
    )

    try:
        validated = EmployeeForm(**form_data)
    except ValidationError as e:
        errors = validation_errors_to_dict(e)
        return templates.TemplateResponse(
            request=request,
            name='employees/add.html',
            context={'errors': errors, 'form_data': form_data},
            status_code=422,
        )

    photo_path = await save_photo(photo)

    payload = {
        'last_name': validated.last_name,
        'first_name': validated.first_name,
        'middle_name': validated.middle_name or None,
        'date_of_birth': validated.date_of_birth.isoformat(),
        'sex': validated.sex,
        'phone_number': validated.phone_number,
        'email': validated.email,
        'photo': photo_path,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(API_BASE_URL, json=payload)
        response.raise_for_status()

    return RedirectResponse(
        url=request.url_for('employees_roster'),
        status_code=303,
    )


@router.get(
    '/employees/{employee_id}',
    response_class=HTMLResponse,
    name='employees_detail',
)
async def employees_detail(request: Request, employee_id: int):
    employee = await fetch_employee(employee_id)
    employee['age'] = calc_age(employee['date_of_birth'])

    return templates.TemplateResponse(
        request=request,
        name='employees/detail.html',
        context={'employee': employee},
    )


@router.get(
    '/employees/{employee_id}/edit',
    response_class=HTMLResponse,
    name='employees_edit',
)
async def employees_edit(request: Request, employee_id: int):
    employee = await fetch_employee(employee_id)
    employee['age'] = calc_age(employee['date_of_birth'])

    return templates.TemplateResponse(
        request=request,
        name='employees/edit.html',
        context={
            'employee': employee,
            'errors': {},
            'form_data': build_form_data(
                last_name=employee.get('last_name', ''),
                first_name=employee.get('first_name', ''),
                middle_name=employee.get('middle_name', ''),
                date_of_birth=employee.get('date_of_birth', ''),
                sex=employee.get('sex', ''),
                phone_number=employee.get('phone_number', ''),
                email=employee.get('email', ''),
            ),
        },
    )


@router.post('/employees/{employee_id}/edit', name='employees_update')
async def employees_update(
    request: Request,
    employee_id: int,
    last_name: str = Form(''),
    first_name: str = Form(''),
    middle_name: str = Form(''),
    date_of_birth: str = Form(''),
    sex: str = Form(''),
    phone_number: str = Form(''),
    email: str = Form(''),
    photo: UploadFile | None = File(None),
):
    form_data = build_form_data(
        last_name=last_name,
        first_name=first_name,
        middle_name=middle_name,
        date_of_birth=date_of_birth,
        sex=sex,
        phone_number=phone_number,
        email=email,
    )

    try:
        validated = EmployeeForm(**form_data)
    except ValidationError as e:
        errors = validation_errors_to_dict(e)
        employee = make_employee_for_edit(employee_id, form_data)
        return templates.TemplateResponse(
            request=request,
            name='employees/edit.html',
            context={
                'employee': employee,
                'errors': errors,
                'form_data': form_data,
            },
            status_code=422,
        )

    photo_path = await save_photo(photo)

    payload = {
        'last_name': validated.last_name,
        'first_name': validated.first_name,
        'middle_name': validated.middle_name or None,
        'date_of_birth': validated.date_of_birth.isoformat(),
        'sex': validated.sex,
        'phone_number': validated.phone_number,
        'email': validated.email,
    }

    if photo_path is not None:
        payload['photo'] = photo_path

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.patch(
            f'{API_BASE_URL}/{employee_id}', json=payload,
        )
        response.raise_for_status()

    return RedirectResponse(
        url=request.url_for('employees_detail', employee_id=employee_id),
        status_code=303,
    )


@router.post('/employees/{employee_id}/delete', name='employees_delete')
async def employees_delete(request: Request, employee_id: int):
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.delete(f'{API_BASE_URL}/{employee_id}')
        response.raise_for_status()

    return RedirectResponse(
        url=request.url_for('employees_roster'),
        status_code=303,
    )
