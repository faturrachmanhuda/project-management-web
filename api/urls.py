from django.urls import path, include
from django.views.generic import RedirectView
from rest_framework.routers import DefaultRouter
# pyrefly: ignore [missing-import]
from .views import (
    RegisterView, LoginView, LogoutView, UserViewSet,
    ProyekViewSet, PekerjaanViewSet, AktivitasViewSet, BuktiAktivitasViewSet,
    TaskSubmissionViewSet,
    health_check,
    home_view, AboutView, projects_view, profile_view,
    project_detail_view, work_detail_view, task_report_view, submissions_page,
    sync_integration_status
)
# pyrefly: ignore [missing-import]
from .views_export import (
    export_project_excel, export_project_pdf,
    export_all_excel, export_all_pdf
)


router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'proyek', ProyekViewSet, basename='proyek')
router.register(r'pekerjaan', PekerjaanViewSet, basename='pekerjaan')
router.register(r'aktivitas', AktivitasViewSet, basename='aktivitas')
router.register(r'bukti-aktivitas', BuktiAktivitasViewSet, basename='bukti-aktivitas')
router.register(r'task-submissions', TaskSubmissionViewSet, basename='task-submission')

urlpatterns = [
    # Template Views (HTML Pages)
    path('', home_view, name='home'),
    path('about/', AboutView.as_view(), name='about'),
    path('proyek/', projects_view, name='projects'),
    path('profil/', profile_view, name='profile'),
    path('laporan-tugas/', task_report_view, name='task_report'),
    path('task-report/', RedirectView.as_view(pattern_name='task_report', permanent=False)),
    path('submissions/', submissions_page, name='submissions'),
    path('proyek/<str:project_id>/', project_detail_view, name='project_detail'),
    path('pekerjaan/<str:work_id>/', work_detail_view, name='work_detail'),
    
    # Redirects for backward compatibility
    path('projects/', RedirectView.as_view(pattern_name='projects', permanent=True)),
    path('profile/', RedirectView.as_view(pattern_name='profile', permanent=True)),
    path('projects/<str:project_id>/', RedirectView.as_view(pattern_name='project_detail', permanent=True)),

    # API endpoints
    path('api/auth/register/', RegisterView.as_view(), name='register'),
    path('api/auth/login/', LoginView.as_view(), name='login'),
    path('api/auth/logout/', LogoutView.as_view(), name='logout'),
    path('api/health/', health_check, name='health'),
    path('api/integration/sync/', sync_integration_status, name='sync_integration_status'),

    # Export Endpoints (Isolated from Router)
    path('api/reports/all/pdf/', export_all_pdf, name='export_all_pdf'),
    path('api/reports/all/excel/', export_all_excel, name='export_all_excel'),
    path('api/reports/project/<str:project_id>/excel/', export_project_excel, name='export_project_excel'),
    path('api/reports/project/<str:project_id>/pdf/', export_project_pdf, name='export_pdf'),

    # Router URLs (API)
    path('api/', include(router.urls)),
]
