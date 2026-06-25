from rest_framework import viewsets, status, generics, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.utils import timezone
# pyrefly: ignore [missing-import]
from .models import User, Proyek, Pekerjaan, Aktivitas, BuktiAktivitas, TaskSubmission
# pyrefly: ignore [missing-import]
from .serializers import (
    UserSerializer, RegisterSerializer, LoginSerializer,
    ProyekSerializer, ProyekCreateSerializer,
    PekerjaanSerializer, PekerjaanCreateSerializer,
    AktivitasSerializer, BuktiAktivitasSerializer,
    TaskSubmissionSerializer
)
# pyrefly: ignore [missing-import]
from .authentication import build_auth_response, verify_user_password
# pyrefly: ignore [missing-import]
import threading


# ==================== TEMPLATE VIEWS ====================

def home_view(request):
    """Render home page"""
    return render(request, 'home.html')


class AboutView(TemplateView):
    """Class-based view untuk halaman Tentang Kami"""
    template_name = 'about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context['team_members'] = [
            {
                'name': 'Dwi Arbi Nugroho',
                'role': 'Project Concept and System Planning',
                'image': 'https://images.unsplash.com/photo-1629507208649-70919ca33793?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixlib=rb-4.1.0&q=80&w=400',
            },
            {
                'name': 'Muhammad Rizki',
                'role': 'System Development and Feature Design',
                'image': 'https://images.unsplash.com/photo-1621388730896-b0e6b1ba5c51?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixlib=rb-4.1.0&q=80&w=400',
            },
            {
                'name': 'Robin Felix Hama',
                'role': 'UI and Interface Design',
                'image': 'https://images.unsplash.com/photo-1695712551846-4dc15433fbd4?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixlib=rb-4.1.0&q=80&w=400',
            },
            {
                'name': 'George',
                'role': 'System Testing and Evaluation',
                'image': 'https://images.unsplash.com/photo-1564518534518-e79657852a1a?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixlib=rb-4.1.0&q=80&w=400',
            },
        ]

        context['initiatives'] = [
            {'icon': 'folder-kanban', 'title': 'Project Management', 'color': 'bg-blue-500'},
            {'icon': 'check-square', 'title': 'Task Management', 'color': 'bg-green-500'},
            {'icon': 'calendar', 'title': 'Activity Planning', 'color': 'bg-purple-500'},
            {'icon': 'bar-chart-3', 'title': 'Project Monitoring', 'color': 'bg-orange-500'},
            {'icon': 'clipboard-check', 'title': 'Project Evaluation', 'color': 'bg-pink-500'},
            {'icon': 'lock', 'title': 'Project Closure', 'color': 'bg-red-500'},
        ]

        context['vision'] = (
            'Become an innovative platform that supports effective and transparent '
            'project management, empowering teams to achieve their goals with '
            'confidence and clarity.'
        )

        context['missions'] = [
            'Provide tools to manage projects and tasks clearly',
            'Support collaboration between team members',
            'Help monitor project progress efficiently',
            'Improve productivity through a simple digital system',
        ]

        context['methodology_steps'] = [
            {'step': '01', 'title': 'User Research', 'desc': 'Understanding user needs'},
            {'step': '02', 'title': 'Wireframing', 'desc': 'Sketching layouts'},
            {'step': '03', 'title': 'Prototyping', 'desc': 'Creating interactive models'},
            {'step': '04', 'title': 'Usability Testing', 'desc': 'Gathering feedback'},
            {'step': '05', 'title': 'Improvement', 'desc': 'Iterative refinement'},
        ]

        context['impact_stats'] = [
            {'value': '85%', 'label': 'Improved Project Organization'},
            {'value': '92%', 'label': 'Enhanced Team Collaboration'},
            {'value': '78%', 'label': 'Increased Monitoring Efficiency'},
        ]

        context['contact_info'] = [
            {'bg': 'from-blue-50 to-blue-100', 'icon': 'mail', 'icon_bg': 'bg-blue-600', 'title': 'Email', 'value': 'contact@promanage.com'},
            {'bg': 'from-green-50 to-green-100', 'icon': 'phone', 'icon_bg': 'bg-green-600', 'title': 'Phone', 'value': '+62 812 3456 7890'},
            {'bg': 'from-purple-50 to-purple-100', 'icon': 'map-pin', 'icon_bg': 'bg-purple-600', 'title': 'Location', 'value': 'Jakarta, Indonesia'},
        ]

        context['social_links'] = [
            {'icon': 'facebook', 'url': '#'},
            {'icon': 'twitter', 'url': '#'},
            {'icon': 'linkedin', 'url': '#'},
            {'icon': 'instagram', 'url': '#'},
        ]

        return context


def projects_view(request):
    """Render projects page"""
    return render(request, 'projects.html')


def project_detail_view(request, project_id):
    """Render project detail page"""
    return render(request, 'project_detail.html', {'project_id': project_id})


def work_detail_view(request, work_id):
    """Render work detail page"""
    return render(request, 'work_detail.html', {'work_id': work_id})


def profile_view(request):
    """Render profile page"""
    return render(request, 'profile.html')


def task_report_view(request):
    """Render task report page"""
    context = {
        'submission_categories': [
            {
                'slug': 'implementation',
                'title': 'Implementation',
                'description': 'Tempat pengumpulan untuk hasil implementasi, penerapan fitur, atau bukti pengerjaan teknis.',
                'icon': 'code-2',
                'accent_class': 'bg-blue-600',
                'badge_class': 'bg-blue-50 text-blue-700 border border-blue-100',
                'panel_class': 'border-blue-100 bg-blue-50/60',
            },
            {
                'slug': 'creation',
                'title': 'Creation',
                'description': 'Tempat pengumpulan untuk karya baru, dokumen perancangan, atau hasil pembuatan awal.',
                'icon': 'pen-tool',
                'accent_class': 'bg-amber-600',
                'badge_class': 'bg-amber-50 text-amber-700 border border-amber-100',
                'panel_class': 'border-amber-100 bg-amber-50/60',
            },
            {
                'slug': 'engineering',
                'title': 'Engineering',
                'description': 'Tempat pengumpulan untuk tugas rekayasa, analisis sistem, dan pekerjaan teknis lanjutan.',
                'icon': 'settings-2',
                'accent_class': 'bg-emerald-600',
                'badge_class': 'bg-emerald-50 text-emerald-700 border border-emerald-100',
                'panel_class': 'border-emerald-100 bg-emerald-50/60',
            },
        ]
    }
    return render(request, 'task_report.html', context)


# ==================== API VIEWS ====================


class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            return Response(
                build_auth_response(user, request),
                status=status.HTTP_201_CREATED,
            )

        errors = serializer.errors
        message = 'Pendaftaran gagal'

        if 'email' in errors:
            message = 'Email sudah terdaftar.'
        elif 'nim' in errors:
            message = 'NIM sudah terdaftar.'

        return Response({
            'success': False,
            'error': message
        }, status=status.HTTP_400_BAD_REQUEST)


class LoginView(generics.GenericAPIView):
    """User login endpoint"""
    permission_classes = [AllowAny]
    authentication_classes = []
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            first_error = next(iter(serializer.errors.values()))[0]
            return Response({
                'success': False,
                'error': str(first_error),
            }, status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email'].strip().lower()
        password = serializer.validated_data['password']

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Email atau kata sandi tidak sesuai.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                'success': False,
                'error': 'Akun tidak aktif. Hubungi administrator.'
            }, status=status.HTTP_403_FORBIDDEN)

        if not verify_user_password(user, password):
            return Response({
                'success': False,
                'error': 'Email atau kata sandi tidak sesuai.'
            }, status=status.HTTP_401_UNAUTHORIZED)

        return Response(build_auth_response(user, request))


class LogoutView(generics.GenericAPIView):
    """Logout endpoint (JWT stateless — client clears tokens)"""
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        return Response({
            'success': True,
            'message': 'Logout berhasil.'
        })


class UserViewSet(viewsets.GenericViewSet):
    """User viewset — me + update_profile only (no list/detail of other users)"""
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user info"""
        serializer = self.get_serializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['patch', 'put'])
    def update_profile(self, request):
        """Update current user profile and picture"""
        user = request.user
        serializer = self.get_serializer(
            user, data=request.data, partial=True, context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            # Kembalikan data terbaru dengan context request agar URL foto absolut
            return Response(
                UserSerializer(user, context={'request': request}).data
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProyekViewSet(viewsets.ModelViewSet):
    """Proyek CRUD endpoints - Global Access with Optimizations"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nama', 'deskripsi', 'lokasi', 'pelaksana', 'pengawas']
    ordering_fields = ['created_at', 'tanggal_mulai', 'tanggal_selesai', 'nama']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return ProyekCreateSerializer
        return ProyekSerializer

    def get_queryset(self):
        """
        Optimized queryset with prefetch_related for nested data.
        Using global access pattern - all users can see all projects.
        """
        try:
            queryset = Proyek.objects.prefetch_related(
                'pekerjaan__aktivitas__bukti'
            ).select_related('user').all()
            return queryset
        except Exception as e:
            # Fallback to basic query if optimization fails
            return Proyek.objects.all()

    def list(self, request, *args, **kwargs):
        """Override list to add proper error handling"""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal mengambil data proyek',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to add proper error handling"""
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Proyek tidak ditemukan',
                'detail': str(e)
            }, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                proyek = serializer.save()
                # Refresh dengan prefetch untuk response yang lengkap
                proyek = Proyek.objects.prefetch_related('pekerjaan__aktivitas__bukti').get(id=proyek.id)
                # Broadcast ke IE, IC, dan Implementation (non-blocking)
                try:
                    import json as json_lib
                    from urllib.request import urlopen, Request

                    broadcast_payload = json_lib.dumps({
                        "pm_project_id": str(proyek.id),
                        "nama_proyek": proyek.nama,
                        "deskripsi": proyek.deskripsi,
                        "pelaksana": proyek.pelaksana,
                        "pengawas": proyek.pengawas,
                        "tanggal_mulai": str(proyek.tanggal_mulai) if proyek.tanggal_mulai else "",
                        "tanggal_selesai": str(proyek.tanggal_selesai) if proyek.tanggal_selesai else "",
                        "lokasi": proyek.lokasi,
                        "status": proyek.status,
                    }).encode('utf-8')
                    print(f"[PM] Broadcasting project '{proyek.nama}' (id={proyek.id}) to subsystems...")

                    def broadcast_to_subsystems(data_bytes):
                        targets = [
                            ("IE", "http://nginx/tif2/engineering/api/receive-pm-project/"),
                            ("IC", "http://nginx/tif2/creation/api/receive-pm-project/"),
                            ("Implementation", "http://nginx/tif2/implementation/api/receive-pm-project/"),
                        ]
                        for name, url in targets:
                            try:
                                req = Request(url, data=data_bytes, headers={'Content-Type': 'application/json'})
                                resp = urlopen(req, timeout=5)
                                print(f"[PM] Broadcast ke {name}: {resp.status} OK")
                            except Exception as e:
                                print(f"[PM] Gagal broadcast ke {name}: {e}")

                    thread = threading.Thread(target=broadcast_to_subsystems, args=(broadcast_payload,))
                    thread.daemon = True
                    thread.start()
                except Exception as broadcast_err:
                    print(f"[PM] Broadcast error (non-fatal): {broadcast_err}")

                return Response(
                    ProyekSerializer(proyek, context={'request': request}).data,
                    status=status.HTTP_201_CREATED
                )
            return Response({
                'success': False,
                'error': 'Validasi gagal',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response({
                'success': False,
                'error': 'Gagal membuat proyek',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'])
    def tutup(self, request, pk=None):
        """Close a project"""
        try:
            proyek = self.get_object()
            proyek.sudah_selesai = True
            proyek.status = 'Selesai'  # sinkronkan field status agar konsisten
            proyek.save()
            # Refresh dengan prefetch untuk response yang lengkap
            proyek = Proyek.objects.prefetch_related('pekerjaan__aktivitas__bukti').get(id=proyek.id)
            return Response(ProyekSerializer(proyek, context={'request': request}).data)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal menutup proyek',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'])
    def ubah_nama(self, request, pk=None):
        """Rename a project"""
        try:
            proyek = self.get_object()
            nama = request.data.get('nama', '').strip()
            if not nama:
                return Response({
                    'success': False,
                    'error': 'Nama diperlukan'
                }, status=status.HTTP_400_BAD_REQUEST)

            proyek.nama = nama
            proyek.save()
            # Refresh dengan prefetch untuk response yang lengkap
            proyek = Proyek.objects.prefetch_related('pekerjaan__aktivitas__bukti').get(id=proyek.id)
            return Response(ProyekSerializer(proyek, context={'request': request}).data)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal mengubah nama proyek',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def ringkasan(self, request):
        """Get summary statistics for projects, works, and activities"""
        try:
            daftar_proyek = self.get_queryset()
            total_proyek = daftar_proyek.count()
            proyek_selesai = daftar_proyek.filter(sudah_selesai=True).count()
            proyek_aktif = total_proyek - proyek_selesai

            daftar_pekerjaan = Pekerjaan.objects.all()
            total_pekerjaan = daftar_pekerjaan.count()

            daftar_aktivitas = Aktivitas.objects.all()
            total_aktivitas = daftar_aktivitas.count()
            aktivitas_selesai = daftar_aktivitas.filter(selesai=True).count()

            progres = 0
            if total_aktivitas > 0:
                progres = round((aktivitas_selesai / total_aktivitas) * 100, 2)

            return Response({
                'success': True,
                'total_proyek': total_proyek,
                'proyek_aktif': proyek_aktif,
                'proyek_selesai': proyek_selesai,
                'total_pekerjaan': total_pekerjaan,
                'total_aktivitas': total_aktivitas,
                'aktivitas_selesai': aktivitas_selesai,
                'progres_keseluruhan': progres
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal mengambil ringkasan',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def dashboard_stats(self, request):
        """Get comprehensive analytics for project management dashboard"""
        from django.db.models import Count
        try:
            daftar_proyek = Proyek.objects.prefetch_related('pekerjaan__aktivitas').all()
            daftar_pekerjaan = Pekerjaan.objects.all()
            daftar_aktivitas = Aktivitas.objects.all()

            # 1. Project Status Distribution
            status_counts = daftar_proyek.values('status').annotate(count=Count('id'))
            status_map = {item['status']: item['count'] for item in status_counts}

            # 2. Activity Completion (The "Real" Progress)
            total_activities = daftar_aktivitas.count()
            done_activities = daftar_aktivitas.filter(selesai=True).count()
            progress_percent = round((done_activities / total_activities * 100) if total_activities > 0 else 0, 1)

            # 3. Work Category Distribution (Kategori removed)
            work_counts = daftar_pekerjaan.values('proyek__nama').annotate(count=Count('id'))
            works_per_project = {item['proyek__nama']: item['count'] for item in work_counts}

            # 4. Individual Project Progress (Deep Dive)
            project_details = []
            for p in daftar_proyek:
                p_activities = daftar_aktivitas.filter(pekerjaan__proyek=p)
                p_total = p_activities.count()
                p_done = p_activities.filter(selesai=True).count()
                p_progress = round((p_done / p_total * 100) if p_total > 0 else 0)
                
                project_details.append({
                    'id': p.id,
                    'nama': p.nama,
                    'status': p.status,
                    'progres': p_progress,
                    'total_activities': p_total,
                })

            return Response({
                'success': True,
                'summary': {
                    'total_projects': daftar_proyek.count(),
                    'total_works': daftar_pekerjaan.count(),
                    'total_activities': total_activities,
                },
                'portfolio': {
                    'status': status_map,
                    'works_per_project': works_per_project,
                },
                'activities': {
                    'percent': progress_percent,
                    'done': done_activities,
                    'total': total_activities
                },
                'project_breakdown': project_details
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal mengambil statistik dashboard',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['get'])
    def timeline(self, request, pk=None):
        """Get timeline/gantt chart data for a specific project"""
        try:
            proyek = self.get_object()
            timeline_data = []
            
            for pekerjaan in proyek.pekerjaan.prefetch_related('aktivitas').all():
                timeline_data.append({
                    'id': pekerjaan.id,
                    'nama': pekerjaan.nama,
                    'kategori': pekerjaan.kategori,
                    'tanggal_mulai': pekerjaan.tanggal_mulai.isoformat() if pekerjaan.tanggal_mulai else None,
                    'tanggal_selesai': pekerjaan.tanggal_selesai.isoformat() if pekerjaan.tanggal_selesai else None,
                    'pelaksana': pekerjaan.pelaksana,
                    'lokasi': pekerjaan.lokasi,
                    'progres': self._calculate_work_progress(pekerjaan)
                })
            
            return Response({
                'success': True,
                'project_id': proyek.id,
                'project_name': proyek.nama,
                'status': proyek.status,
                'timeline': timeline_data
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal mengambil timeline proyek',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _calculate_work_progress(self, pekerjaan):
        """Calculate progress percentage for a work item"""
        activities = pekerjaan.aktivitas.all()
        total = activities.count()
        if total == 0:
            return 0
        done = activities.filter(selesai=True).count()
        return round((done / total) * 100, 2)



class PekerjaanViewSet(viewsets.ModelViewSet):
    """Pekerjaan CRUD endpoints - Global Access with Optimizations"""
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nama', 'deskripsi', 'lokasi', 'pelaksana', 'pengawas']
    ordering_fields = ['created_at', 'tanggal_mulai', 'tanggal_selesai', 'nama']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'create':
            return PekerjaanCreateSerializer
        return PekerjaanSerializer

    def get_queryset(self):
        """
        Optimized queryset with prefetch_related for nested data.
        Using global access pattern - all users can see all works.
        """
        try:
            queryset = Pekerjaan.objects.prefetch_related(
                'aktivitas__bukti'
            ).select_related('proyek').all()
            return queryset
        except Exception as e:
            # Fallback to basic query if optimization fails
            return Pekerjaan.objects.all()

    def list(self, request, *args, **kwargs):
        """Override list to add proper error handling"""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal mengambil data pekerjaan',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to add proper error handling"""
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Pekerjaan tidak ditemukan',
                'detail': str(e)
            }, status=status.HTTP_404_NOT_FOUND)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                pekerjaan = serializer.save()
                pekerjaan = Pekerjaan.objects.prefetch_related('aktivitas__bukti').select_related('proyek').get(id=pekerjaan.id)
                return Response(
                    PekerjaanSerializer(pekerjaan, context={'request': request}).data,
                    status=status.HTTP_201_CREATED
                )
            return Response({
                'success': False,
                'error': 'Validasi gagal',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal membuat pekerjaan',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'])
    def ubah_nama(self, request, pk=None):
        """Rename a work"""
        try:
            pekerjaan = self.get_object()
            nama = request.data.get('nama', '').strip()
            if not nama:
                return Response({
                    'success': False,
                    'error': 'Nama diperlukan'
                }, status=status.HTTP_400_BAD_REQUEST)
            pekerjaan.nama = nama
            pekerjaan.save()
            pekerjaan = Pekerjaan.objects.prefetch_related('aktivitas__bukti').select_related('proyek').get(id=pekerjaan.id)
            return Response(PekerjaanSerializer(pekerjaan, context={'request': request}).data)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal mengubah nama pekerjaan',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def berdasarkan_proyek(self, request):
        """Get works by project ID with full nested data"""
        try:
            id_proyek = request.query_params.get('id_proyek')
            if not id_proyek:
                return Response({
                    'success': False,
                    'error': 'id_proyek diperlukan'
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                proyek = Proyek.objects.get(id=id_proyek)
            except Proyek.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f'Proyek dengan ID {id_proyek} tidak ditemukan'
                }, status=status.HTTP_404_NOT_FOUND)

            daftar_pekerjaan = self.get_queryset().filter(proyek_id=id_proyek)
            serializer = self.get_serializer(daftar_pekerjaan, many=True, context={'request': request})
            return Response({
                'success': True,
                'project_id': id_proyek,
                'project_name': proyek.nama,
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal mengambil pekerjaan berdasarkan proyek',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AktivitasViewSet(viewsets.ModelViewSet):
    """Aktivitas CRUD endpoints - Global Access with Optimizations"""
    serializer_class = AktivitasSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nama', 'pelaksana']
    ordering_fields = ['created_at', 'nama']
    ordering = ['-created_at']

    def get_queryset(self):
        """
        Optimized queryset with prefetch_related for nested data.
        Using global access pattern - all users can see all activities.
        """
        try:
            queryset = Aktivitas.objects.prefetch_related(
                'bukti'
            ).select_related('pekerjaan__proyek').all()
            return queryset
        except Exception as e:
            # Fallback to basic query if optimization fails
            return Aktivitas.objects.all()

    def list(self, request, *args, **kwargs):
        """Override list to add proper error handling"""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal mengambil data aktivitas',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to add proper error handling"""
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Aktivitas tidak ditemukan',
                'detail': str(e)
            }, status=status.HTTP_404_NOT_FOUND)

    def update(self, request, *args, **kwargs):
        """Override update with optimized query"""
        try:
            partial = kwargs.pop('partial', True)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial, context={'request': request})
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            if getattr(instance, '_prefetched_objects_cache', None):
                instance._prefetched_objects_cache = {}

            instance = Aktivitas.objects.prefetch_related('bukti').select_related('pekerjaan__proyek').get(id=instance.id)
            return Response(self.get_serializer(instance, context={'request': request}).data)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal memperbarui aktivitas',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def create(self, request, *args, **kwargs):
        """Create aktivitas with proper validation and optimized response"""
        try:
            id_pekerjaan = request.data.get('id_pekerjaan')
            if not id_pekerjaan:
                return Response({
                    'success': False,
                    'error': 'id_pekerjaan diperlukan'
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                pekerjaan = Pekerjaan.objects.get(id=id_pekerjaan)
            except Pekerjaan.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f'Pekerjaan dengan ID {id_pekerjaan} tidak ditemukan'
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = self.get_serializer(data=request.data, context={'request': request})
            if serializer.is_valid():
                aktivitas = serializer.save(pekerjaan=pekerjaan)
                aktivitas = Aktivitas.objects.prefetch_related('bukti').select_related('pekerjaan__proyek').get(id=aktivitas.id)
                return Response(
                    AktivitasSerializer(aktivitas, context={'request': request}).data,
                    status=status.HTTP_201_CREATED
                )
            return Response({
                'success': False,
                'error': 'Validasi gagal',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal membuat aktivitas',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['patch'])
    def toggle_selesai(self, request, pk=None):
        """Set or toggle activity done status"""
        try:
            aktivitas = self.get_object()
            selesai_value = request.data.get('selesai')
            if selesai_value is not None:
                if isinstance(selesai_value, str):
                    aktivitas.selesai = selesai_value.strip().lower() in ('1', 'true', 'yes', 'ya', 'selesai')
                else:
                    aktivitas.selesai = bool(selesai_value)
            else:
                aktivitas.selesai = not aktivitas.selesai
            aktivitas.save()
            aktivitas = Aktivitas.objects.prefetch_related('bukti').select_related('pekerjaan__proyek').get(id=aktivitas.id)
            return Response({
                'success': True,
                'data': AktivitasSerializer(aktivitas, context={'request': request}).data
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal memperbarui status aktivitas',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def berdasarkan_pekerjaan(self, request):
        """Get activities by work ID with full nested data"""
        try:
            id_pekerjaan = request.query_params.get('id_pekerjaan')
            if not id_pekerjaan:
                return Response({
                    'success': False,
                    'error': 'id_pekerjaan diperlukan'
                }, status=status.HTTP_400_BAD_REQUEST)

            try:
                pekerjaan = Pekerjaan.objects.get(id=id_pekerjaan)
            except Pekerjaan.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f'Pekerjaan dengan ID {id_pekerjaan} tidak ditemukan'
                }, status=status.HTTP_404_NOT_FOUND)

            daftar_aktivitas = self.get_queryset().filter(pekerjaan_id=id_pekerjaan)
            serializer = self.get_serializer(daftar_aktivitas, many=True, context={'request': request})
            
            total = daftar_aktivitas.count()
            selesai = daftar_aktivitas.filter(selesai=True).count()
            progres = round((selesai / total * 100) if total > 0 else 0, 2)
            
            return Response({
                'success': True,
                'work_id': id_pekerjaan,
                'work_name': pekerjaan.nama,
                'statistics': {
                    'total': total,
                    'done': selesai,
                    'progress': progres
                },
                'data': serializer.data
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal mengambil aktivitas berdasarkan pekerjaan',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['delete'])
    def hapus_bukti(self, request, pk=None):
        """Delete a file from an activity with proper error handling"""
        try:
            id_bukti = request.query_params.get('id_bukti')
            if not id_bukti:
                return Response({
                    'success': False,
                    'error': 'id_bukti diperlukan'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                aktivitas = self.get_object()
                bukti = BuktiAktivitas.objects.get(id=id_bukti, aktivitas=aktivitas)
                bukti.delete()
                
                aktivitas = Aktivitas.objects.prefetch_related('bukti').select_related('pekerjaan__proyek').get(id=aktivitas.id)
                return Response({
                    'success': True,
                    'message': 'Bukti berhasil dihapus',
                    'data': AktivitasSerializer(aktivitas, context={'request': request}).data
                })
            except BuktiAktivitas.DoesNotExist:
                return Response({
                    'success': False,
                    'error': f'Bukti dengan ID {id_bukti} tidak ditemukan'
                }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal menghapus bukti',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TaskSubmissionViewSet(viewsets.ModelViewSet):
    """TaskSubmission CRUD endpoints"""
    permission_classes = [IsAuthenticated]
    serializer_class = TaskSubmissionSerializer

    def get_queryset(self):
        from django.db.models import Q
        queryset = TaskSubmission.objects.all().order_by('-created_at')
        category = self.request.query_params.get('category')
        status_filter = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        if category:
            queryset = queryset.filter(category=category)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(project_name__icontains=search)
                | Q(submitted_by__icontains=search)
                | Q(description__icontains=search)
            )
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        extra = {}
        if not serializer.validated_data.get('submitted_by'):
            extra['submitted_by'] = user.nama
        project_id = self.request.data.get('project_id')
        if project_id and not serializer.validated_data.get('project_id'):
            try:
                proyek = Proyek.objects.get(id=project_id)
                extra['project_id'] = proyek.id
                if not serializer.validated_data.get('project_name'):
                    extra['project_name'] = proyek.nama
            except Proyek.DoesNotExist:
                pass
        serializer.save(**extra)

    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update submission status"""
        submission = self.get_object()
        new_status = request.data.get('status')
        if new_status not in ['draft', 'submitted', 'reviewed', 'approved', 'rejected']:
            return Response({'error': 'Status tidak valid'}, status=status.HTTP_400_BAD_REQUEST)
        submission.status = new_status
        submission.save()
        return Response(TaskSubmissionSerializer(submission, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get submission statistics per category"""
        categories = ['engineering', 'creation', 'implementation']
        result = {}
        for cat in categories:
            qs = TaskSubmission.objects.filter(category=cat)
            result[cat] = {
                'total': qs.count(),
                'submitted': qs.filter(status='submitted').count(),
                'approved': qs.filter(status='approved').count(),
                'rejected': qs.filter(status='rejected').count(),
                'reviewed': qs.filter(status='reviewed').count(),
                'draft': qs.filter(status='draft').count(),
            }
        return Response(result)


def submissions_page(request):
    """Render submissions page"""
    return render(request, 'submissions.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def health_check(request):
    """Health check endpoint"""
    return Response({
        'status': 'OK',
        'user': str(request.user),
        'message': 'API sedang berjalan'
    })


class BuktiAktivitasViewSet(viewsets.ModelViewSet):
    """BuktiAktivitas CRUD endpoints - Global Access with Optimizations"""
    serializer_class = BuktiAktivitasSerializer
    permission_classes = [IsAuthenticated]
    ordering_fields = ['diunggah_pada']
    ordering = ['-diunggah_pada']

    def get_queryset(self):
        """
        Optimized queryset with proper filtering.
        """
        try:
            queryset = BuktiAktivitas.objects.select_related('aktivitas__pekerjaan').all()
            aktivitas_id = self.request.query_params.get('aktivitas')
            if aktivitas_id:
                queryset = queryset.filter(aktivitas_id=aktivitas_id)
            return queryset
        except Exception as e:
            # Fallback to basic query if optimization fails
            return BuktiAktivitas.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def list(self, request, *args, **kwargs):
        """Override list to add proper error handling"""
        try:
            return super().list(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Gagal mengambil data bukti aktivitas',
                'detail': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve to add proper error handling"""
        try:
            return super().retrieve(request, *args, **kwargs)
        except Exception as e:
            return Response({
                'success': False,
                'error': 'Bukti aktivitas tidak ditemukan',
                'detail': str(e)
            }, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def sync_integration_status(request):
    """Endpoint to receive activity logs from IE, IC, and Implementation.
    
    Expected payload:
    {
        "project_name": "...",
        "project_id": "...",           # optional PM project UUID
        "category": "engineering|creation|implementation",
        "activity_name": "...",        # nama aktivitas
        "activity_detail": "...",      # detail (optional)
        "status_text": "...",          # legacy compat
        "links": [{"title": "...", "url": "..."}]
    }
    """
    try:
        data = request.data
        project_id = data.get('project_id')
        category = data.get('category')
        project_name = data.get('project_name')

        activity_name = data.get('activity_name') or data.get('status_text', '')
        activity_detail = data.get('activity_detail', '')
        links = data.get('links', [])

        if not category:
            return Response({'error': 'category is required'}, status=400)
            
        if not project_id and not project_name:
            return Response({'error': 'Either project_id or project_name is required'}, status=400)

        proyek = None
        try:
            if project_id:
                proyek = Proyek.objects.get(id=project_id)
        except Proyek.DoesNotExist:
            pass
            
        if not proyek and project_name:
            proyek = Proyek.objects.filter(nama=project_name).first()
            
        if not proyek:
            return Response({'error': 'Project not found'}, status=404)

        # Map category to display names
        category_labels = {
            'engineering': 'Sinkronisasi Engineering',
            'creation': 'Sinkronisasi Creation',
            'implementation': 'Sinkronisasi Implementation',
        }
        work_name = category_labels.get(category, f'Sinkronisasi {category.capitalize()}')

        # UPSERT Pekerjaan for this category
        pekerjaan, created = Pekerjaan.objects.get_or_create(
            proyek=proyek,
            kategori=category,
            defaults={
                'nama': work_name,
                'deskripsi': f'Log aktivitas dari {work_name}',
                'lokasi': proyek.lokasi or '-',
                'tanggal_mulai': proyek.tanggal_mulai or timezone.now().date(),
                'tanggal_selesai': proyek.tanggal_selesai or timezone.now().date(),
                'pelaksana': data.get('source_label', category.capitalize()),
                'pengawas': proyek.pengawas or '-',
            }
        )

        # Update end date to today
        pekerjaan.tanggal_selesai = timezone.now().date()
        pekerjaan.save()

        # Create/update Aktivitas with dedup by (pekerjaan, nama)
        import json as json_lib
        evaluasi_data = json_lib.dumps({'links': links}) if links else ''
        final_name = activity_name or f'Update dari {category}'

        aktivitas, act_created = Aktivitas.objects.update_or_create(
            pekerjaan=pekerjaan,
            nama=final_name,
            defaults={
                'pelaksana': data.get('source_label', category.capitalize()),
                'waktu_pelaksanaan': timezone.now().strftime('%Y-%m-%dT%H:%M:%S'),
                'rencana_tambahan': activity_detail,
                'evaluasi': evaluasi_data,
                'selesai': True,
            }
        )

        # Auto-create/update TaskSubmission for Laporan Tugas page
        if links:
            submission_title = final_name
            submission_desc = activity_detail
            file_url = links[0].get('url', '') if links else ''
            
            import json as json_mod
            TaskSubmission.objects.update_or_create(
                category=category,
                project_id=str(proyek.id),
                title=submission_title,
                defaults={
                    'description': submission_desc,
                    'submitted_by': data.get('source_label', category.capitalize()),
                    'project_name': proyek.nama,
                    'status': 'submitted',
                }
            )

        return Response({
            'success': True,
            'message': 'Activity log upserted' if not act_created else 'Activity log created',
            'activity_id': aktivitas.id,
            'work_id': pekerjaan.id,
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)
