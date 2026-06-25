from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# pyrefly: ignore [missing-import]
from .models import User, Proyek, Pekerjaan, Aktivitas, BuktiAktivitas


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'nama', 'nim', 'is_active', 'is_staff', 'created_at']
    search_fields = ['email', 'nama', 'nim']
    list_filter = ['is_active', 'is_staff', 'created_at']
    ordering = ['email']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Profil', {'fields': ('nama', 'nim', 'profile_picture')}),
        ('Hak Akses', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Riwayat', {'fields': ('created_at', 'updated_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nama', 'nim', 'password1', 'password2'),
        }),
    )


@admin.register(Proyek)
class ProyekAdmin(admin.ModelAdmin):
    list_display = ['nama', 'user', 'status', 'sudah_selesai', 'tanggal_mulai', 'tanggal_selesai']
    search_fields = ['nama', 'deskripsi', 'user__email']
    list_filter = ['status', 'sudah_selesai', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Pekerjaan)
class PekerjaanAdmin(admin.ModelAdmin):
    list_display = ['nama', 'proyek', 'tanggal_mulai', 'tanggal_selesai']
    search_fields = ['nama', 'deskripsi', 'proyek__nama']
    list_filter = ['created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Aktivitas)
class AktivitasAdmin(admin.ModelAdmin):
    list_display = ['nama', 'pekerjaan', 'pelaksana', 'selesai', 'waktu_pelaksanaan']
    search_fields = ['nama', 'pekerjaan__nama', 'pelaksana']
    list_filter = ['selesai', 'created_at']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(BuktiAktivitas)
class BuktiAktivitasAdmin(admin.ModelAdmin):
    list_display = ['aktivitas', 'file', 'diunggah_pada']
    search_fields = ['aktivitas__nama']
    list_filter = ['diunggah_pada']
