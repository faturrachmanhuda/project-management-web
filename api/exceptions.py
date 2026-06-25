from rest_framework.views import exception_handler
from rest_framework.response import Response


def custom_exception_handler(exc, context):
    """Custom exception handler untuk format response yang konsisten"""
    response = exception_handler(exc, context)

    if response is not None:
        # Tentukan pesan utama
        message = ''
        details = {}

        if isinstance(response.data, dict):
            if 'detail' in response.data:
                # Error otentikasi / permission (misal: "Token tidak valid")
                message = str(response.data['detail'])
            else:
                # Validation errors — kumpulkan field errors
                details = response.data
                message = 'Validasi gagal'
        elif isinstance(response.data, list):
            message = str(response.data[0]) if response.data else 'Terjadi kesalahan'
        else:
            message = str(response.data)

        response.data = {
            'success': False,
            'error': message,
            'details': details,
        }

    return response
