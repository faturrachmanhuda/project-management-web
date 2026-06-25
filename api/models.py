from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid


class UserManager(BaseUserManager):
    def create_user(self, email, nim, nama, password=None):
        if not email:
            raise ValueError('User harus memiliki email')
        if not nim:
            raise ValueError('User harus memiliki NIM')

        email = self.normalize_email(email)
        user = self.model(email=email, nim=nim, nama=nama)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nim, nama, password=None):
        user = self.create_user(email, nim, nama, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=255)
    nim = models.CharField(max_length=20, unique=True, verbose_name='NIM')
    nama = models.CharField(max_length=255)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nim', 'nama']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email


class Proyek(models.Model):
    STATUS_PILIHAN = [
        ('Aktif', 'Aktif'),
        ('Selesai', 'Selesai'),
        ('Tertunda', 'Tertunda'),
    ]

    id = models.CharField(primary_key=True, max_length=50, editable=False)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='proyek', null=True, blank=True)
    nama = models.CharField(max_length=255)
    deskripsi = models.TextField()
    lokasi = models.CharField(max_length=255)
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField()
    pelaksana = models.CharField(max_length=255)
    pengawas = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_PILIHAN, default='Aktif')
    sudah_selesai = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'proyek'
        ordering = ['-created_at']
        verbose_name = 'Proyek'
        verbose_name_plural = 'Proyek'

    def save(self, *args, **kwargs):
        if not self.id:
            import uuid
            self.id = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama


class Pekerjaan(models.Model):
    id = models.CharField(primary_key=True, max_length=50, editable=False)
    proyek = models.ForeignKey(Proyek, on_delete=models.CASCADE, related_name='pekerjaan')
    nama = models.CharField(max_length=255)
    KATEGORI_PILIHAN = [
        ('engineering', 'Engineering'),
        ('creation', 'Creation'),
        ('implementation', 'Implementation'),
    ]
    kategori = models.CharField(max_length=20, choices=KATEGORI_PILIHAN, default='engineering')
    deskripsi = models.TextField()
    lokasi = models.CharField(max_length=255)
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField()
    pelaksana = models.CharField(max_length=255)
    pengawas = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'pekerjaan'
        ordering = ['-created_at']
        verbose_name = 'Pekerjaan'
        verbose_name_plural = 'Pekerjaan'

    def save(self, *args, **kwargs):
        if not self.id:
            import uuid
            self.id = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama


class Aktivitas(models.Model):
    id = models.CharField(primary_key=True, max_length=50, editable=False)
    pekerjaan = models.ForeignKey(Pekerjaan, on_delete=models.CASCADE, related_name='aktivitas')
    nama = models.CharField(max_length=255)
    waktu_pelaksanaan = models.CharField(max_length=255)
    pelaksana = models.CharField(max_length=255)
    selesai = models.BooleanField(default=False)
    evaluasi = models.TextField(blank=True, null=True)
    rencana_tambahan = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'aktivitas'
        ordering = ['-created_at']
        verbose_name = 'Aktivitas'
        verbose_name_plural = 'Aktivitas'

    def save(self, *args, **kwargs):
        if not self.id:
            import uuid
            self.id = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nama


class BuktiAktivitas(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    aktivitas = models.ForeignKey(Aktivitas, on_delete=models.CASCADE, related_name='bukti')
    file = models.FileField(upload_to='bukti_aktivitas/%Y/%m/%d/')
    ukuran_file = models.IntegerField(null=True, blank=True)
    diunggah_pada = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'bukti_aktivitas'
        ordering = ['-diunggah_pada']
        verbose_name = 'Bukti Aktivitas'
        verbose_name_plural = 'Bukti Aktivitas'

    def __str__(self):
        return f"Bukti untuk {self.aktivitas.nama}"


class TaskSubmission(models.Model):
    KATEGORI_PILIHAN = [
        ('engineering', 'Engineering'),
        ('creation', 'Creation'),
        ('implementation', 'Implementation'),
    ]

    STATUS_PILIHAN = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.CharField(max_length=50, choices=KATEGORI_PILIHAN, default='engineering')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to='submissions/%Y/%m/%d/', blank=True, null=True)
    submitted_by = models.CharField(max_length=255)
    project_name = models.CharField(max_length=255, blank=True, null=True)
    project_id = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_PILIHAN, default='submitted')
    deadline_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task_submissions'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.get_category_display()}] {self.title}"

    @property
    def is_late(self):
        from django.utils import timezone
        if self.deadline_date and self.status == 'submitted':
            return timezone.now().date() > self.deadline_date
        return False
