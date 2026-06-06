#!/usr/bin/env python
import os
import sys
import django
from datetime import date, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from apps.users.models import User
from apps.packages.models import Package
from apps.exams.models import ExamRoom, ExamSchedule
from apps.students.models import Student


def init_users():
    print('Creating default users...')
    users_data = [
        {'username': 'admin', 'password': 'admin123', 'real_name': '系统管理员', 'phone': '13800138000', 'role': 'admin', 'is_superuser': True, 'is_staff': True},
        {'username': 'finance', 'password': 'finance123', 'real_name': '财务人员', 'phone': '13800138001', 'role': 'finance', 'is_staff': True},
        {'username': 'coach1', 'password': 'coach123', 'real_name': '李教练', 'phone': '13800138002', 'role': 'coach'},
        {'username': 'coach2', 'password': 'coach123', 'real_name': '王教练', 'phone': '13800138003', 'role': 'coach'},
    ]
    for data in users_data:
        if not User.objects.filter(username=data['username']).exists():
            password = data.pop('password')
            user = User(**data)
            user.set_password(password)
            user.save()
            print(f'  Created user: {data["username"]} / {password}')
        else:
            print(f'  User exists: {data["username"]}')


def init_packages():
    print('Creating default packages...')
    packages_data = [
        {'name': 'C1普通班', 'code': 'C1-NORMAL', 'type': 'normal', 'license_type': 'C1', 'base_price': 3800, 'total_hours': 40, 'payment_type': 'both', 'down_payment': 1000, 'installment_months': 6, 'installment_amount': 467, 'description': '包含C1驾照培训，手动挡，基础班服务'},
        {'name': 'C1精品班', 'code': 'C1-PREMIUM', 'type': 'premium', 'license_type': 'C1', 'base_price': 5800, 'total_hours': 60, 'payment_type': 'both', 'down_payment': 1500, 'installment_months': 6, 'installment_amount': 717, 'description': '包含C1驾照培训，手动挡，一对一教学，优先约考'},
        {'name': 'C1VIP班', 'code': 'C1-VIP', 'type': 'vip', 'license_type': 'C1', 'base_price': 8800, 'total_hours': 80, 'payment_type': 'both', 'down_payment': 2000, 'installment_months': 12, 'installment_amount': 567, 'description': '包含C1驾照培训，手动挡，VIP专属服务，不限学时，补考免费'},
        {'name': 'C2普通班', 'code': 'C2-NORMAL', 'type': 'normal', 'license_type': 'C2', 'base_price': 4200, 'total_hours': 40, 'payment_type': 'both', 'down_payment': 1200, 'installment_months': 6, 'installment_amount': 500, 'description': '包含C2驾照培训，自动挡，基础班服务'},
        {'name': 'C2精品班', 'code': 'C2-PREMIUM', 'type': 'premium', 'license_type': 'C2', 'base_price': 6200, 'total_hours': 60, 'payment_type': 'both', 'down_payment': 1800, 'installment_months': 6, 'installment_amount': 733, 'description': '包含C2驾照培训，自动挡，一对一教学，优先约考'},
        {'name': 'D证普通班', 'code': 'D-NORMAL', 'type': 'normal', 'license_type': 'D', 'base_price': 1500, 'total_hours': 10, 'payment_type': 'full', 'description': '包含D证摩托车驾照培训'},
    ]
    for data in packages_data:
        if not Package.objects.filter(code=data['code']).exists():
            Package.objects.create(**data)
            print(f'  Created package: {data["name"]}')
        else:
            print(f'  Package exists: {data["name"]}')


def init_exam_rooms():
    print('Creating exam rooms...')
    rooms_data = [
        {'name': '车管所第一考场', 'address': '市车管所A区1号考场', 'capacity': 100},
        {'name': '车管所第二考场', 'address': '市车管所A区2号考场', 'capacity': 80},
        {'name': '科目二训练场', 'address': '驾校北区科目二场地', 'capacity': 30},
        {'name': '科目三路线1', 'address': '东区开发区科目三路线', 'capacity': 20},
    ]
    for data in rooms_data:
        if not ExamRoom.objects.filter(name=data['name']).exists():
            ExamRoom.objects.create(**data)
            print(f'  Created room: {data["name"]}')
        else:
            print(f'  Room exists: {data["name"]}')


def init_exam_schedules():
    print('Creating exam schedules...')
    rooms = ExamRoom.objects.all()
    if not rooms:
        return
    today = date.today()
    schedules_data = []
    for i in range(4):
        exam_date = today + timedelta(days=7 + i * 3)
        schedules_data.append({
            'subject': 1, 'exam_room': rooms[0], 'exam_date': exam_date,
            'start_time': '09:00', 'end_time': '11:00', 'total_quota': 50, 'status': 'open'
        })
        schedules_data.append({
            'subject': 2, 'exam_room': rooms[2], 'exam_date': exam_date,
            'start_time': '08:00', 'end_time': '12:00', 'total_quota': 20, 'status': 'open'
        })
        schedules_data.append({
            'subject': 3, 'exam_room': rooms[3], 'exam_date': exam_date,
            'start_time': '07:30', 'end_time': '17:00', 'total_quota': 15, 'status': 'open'
        })
        schedules_data.append({
            'subject': 4, 'exam_room': rooms[1], 'exam_date': exam_date,
            'start_time': '14:00', 'end_time': '16:00', 'total_quota': 40, 'status': 'open'
        })
    count = 0
    for data in schedules_data:
        if not ExamSchedule.objects.filter(subject=data['subject'], exam_date=data['exam_date'], exam_room=data['exam_room']).exists():
            ExamSchedule.objects.create(**data)
            count += 1
    print(f'  Created {count} exam schedules')


def init_sample_students():
    print('Creating sample students...')
    coach1 = User.objects.filter(role='coach').first()
    package = Package.objects.filter(is_active=True).first()
    if not coach1 or not package:
        return
    students_data = [
        {'name': '张三', 'gender': 'male', 'phone': '13900139001', 'id_card': '110101199001011234', 'license_type': 'C1', 'birthday': '1990-01-01', 'address': '北京市朝阳区', 'status': 'studying', 'total_hours': package.total_hours},
        {'name': '李四', 'gender': 'female', 'phone': '13900139002', 'id_card': '110101199202021234', 'license_type': 'C2', 'birthday': '1992-02-02', 'address': '北京市海淀区', 'status': 'studying', 'total_hours': package.total_hours},
        {'name': '王五', 'gender': 'male', 'phone': '13900139003', 'id_card': '110101199503031234', 'license_type': 'C1', 'birthday': '1995-03-03', 'address': '北京市西城区', 'status': 'studying', 'total_hours': package.total_hours},
    ]
    for data in students_data:
        if not Student.objects.filter(id_card=data['id_card']).exists():
            Student.objects.create(coach=coach1, package=package, **data)
            print(f'  Created student: {data["name"]}')
        else:
            print(f'  Student exists: {data["name"]}')


if __name__ == '__main__':
    print('=' * 50)
    print('Initializing driving school system data...')
    print('=' * 50)
    init_users()
    init_packages()
    init_exam_rooms()
    init_exam_schedules()
    init_sample_students()
    print('=' * 50)
    print('Data initialization complete!')
    print('=' * 50)
