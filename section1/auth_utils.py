"""
Authentication and Role-Based Access Control using .env configuration.
Allows dynamic modification of credentials in .env.
"""

import os
from pathlib import Path
from dotenv import dotenv_values

ENV_FILE_PATH = Path(__file__).resolve().parent.parent / '.env'

def get_env_credentials():
    """
    Reads credentials freshly from .env file so any modifications
    are immediately reflected without needing code changes.
    """
    if ENV_FILE_PATH.exists():
        config = dotenv_values(ENV_FILE_PATH)
    else:
        config = {}

    return {
        'FACULTY': {
            'username': config.get('FACULTY_USERNAME', 'faculty'),
            'password': config.get('FACULTY_PASSWORD', 'faculty123'),
            'name': config.get('FACULTY_NAME', 'Dr. Ramesh Kumar'),
            'department': config.get('FACULTY_DEPARTMENT', 'Computer Science & Engineering'),
            'employee_id': config.get('FACULTY_EMPLOYEE_ID', 'RNSIT-CS-1042')
        },
        'HOD': {
            'username': config.get('HOD_USERNAME', 'hod'),
            'password': config.get('HOD_PASSWORD', 'hod123'),
            'name': config.get('HOD_NAME', 'Dr. Kiran B. R. (HOD - CSE)'),
            'department': config.get('HOD_DEPARTMENT', 'Computer Science & Engineering')
        },
        'PRINCIPAL': {
            'username': config.get('PRINCIPAL_USERNAME', 'principal'),
            'password': config.get('PRINCIPAL_PASSWORD', 'principal123'),
            'name': config.get('PRINCIPAL_NAME', 'Dr. M. K. Venkatesha (Principal)'),
            'institution': config.get('PRINCIPAL_INSTITUTION', 'RNS Institute of Technology')
        }
    }


def authenticate_user(username, password, role=None):
    """
    Validates username and password against .env configuration.
    Returns (True, role, user_info) or (False, None, None).
    """
    creds = get_env_credentials()
    username = username.strip()
    password = password.strip()

    roles_to_check = [role.upper()] if role and role.upper() in creds else ['FACULTY', 'HOD', 'PRINCIPAL']

    for r in roles_to_check:
        user_data = creds[r]
        if user_data['username'] == username and user_data['password'] == password:
            return True, r, user_data

    return False, None, None
