from rest_framework import permissions


class PemilikHanya(permissions.BasePermission):
    """
    Permission kustom untuk hanya mengizinkan pemilik objek mengaksesnya.
    """

    def has_object_permission(self, request, view, obj):
        # Periksa apakah objek memiliki atribut user
        if hasattr(obj, 'user'):
            return obj.user == request.user
        # Untuk objek Pekerjaan, periksa melalui proyek
        elif hasattr(obj, 'proyek'):
            return obj.proyek.user == request.user
        # Untuk objek Aktivitas, periksa melalui pekerjaan.proyek
        elif hasattr(obj, 'pekerjaan'):
            return obj.pekerjaan.proyek.user == request.user
        # Untuk objek BuktiAktivitas, periksa melalui aktivitas.pekerjaan.proyek
        elif hasattr(obj, 'aktivitas'):
            return obj.aktivitas.pekerjaan.proyek.user == request.user
        return False
