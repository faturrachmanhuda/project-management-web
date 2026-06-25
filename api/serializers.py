from rest_framework import serializers
# pyrefly: ignore [missing-import]
from .models import User, Proyek, Pekerjaan, Aktivitas, BuktiAktivitas, TaskSubmission
import binascii
import base64
import uuid
from django.core.files.base import ContentFile


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and ';base64,' in data:
            try:
                format, imgstr = data.split(';base64,')
                ext = format.split('/')[-1]
                if ext == 'jpeg':
                    ext = 'jpg'
                id_str = str(uuid.uuid4())
                data = ContentFile(base64.b64decode(imgstr), name=f"{id_str}.{ext}")
            except Exception:
                raise serializers.ValidationError("Base64 string tidak valid.")
        elif isinstance(data, str):
            raise serializers.ValidationError("Harap unggah file atau string base64 yang valid.")
        return super().to_internal_value(data)


class UserSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField(read_only=True)
    profile_picture = Base64ImageField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ['id', 'nama', 'email', 'nim', 'profile_picture', 'profile_picture_url']
        read_only_fields = ['id']

    def get_profile_picture_url(self, obj):
        if obj.profile_picture:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_picture.url)
            return obj.profile_picture.url
        return None


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ['nama', 'nim', 'email', 'password']

    def validate_nama(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError('Nama wajib diisi.')
        return cleaned

    def validate_nim(self, value):
        cleaned = value.strip()
        if not cleaned:
            raise serializers.ValidationError('NIM wajib diisi.')
        return cleaned

    def validate_email(self, value):
        return value.strip().lower()

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            nim=validated_data['nim'],
            nama=validated_data['nama'],
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=1)

    def validate_email(self, value):
        return value.strip().lower()


class BuktiAktivitasSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = BuktiAktivitas
        fields = ['id', 'aktivitas', 'file', 'file_url', 'ukuran_file', 'diunggah_pada']
        read_only_fields = ['id', 'diunggah_pada']

    def create(self, validated_data):
        file = validated_data.get('file')
        if file and not validated_data.get('ukuran_file'):
            validated_data['ukuran_file'] = file.size
        return super().create(validated_data)

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class AktivitasSerializer(serializers.ModelSerializer):
    id_pekerjaan = serializers.ReadOnlyField(source='pekerjaan.id')
    bukti = serializers.ListField(
        child=serializers.JSONField(),
        write_only=True,
        required=False,
        allow_empty=True
    )
    bukti_urls = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Aktivitas
        fields = [
            'id', 'id_pekerjaan', 'nama', 'waktu_pelaksanaan', 'pelaksana',
            'selesai', 'evaluasi', 'rencana_tambahan',
            'bukti', 'bukti_urls', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'nama': {'required': False, 'allow_blank': True},
            'waktu_pelaksanaan': {'required': False, 'allow_blank': True},
            'pelaksana': {'required': False, 'allow_blank': True},
            'evaluasi': {'required': False, 'allow_blank': True},
            'rencana_tambahan': {'required': False, 'allow_blank': True},
        }

    def get_bukti_urls(self, obj):
        request = self.context.get('request')
        bukti_list = obj.bukti.all()
        return [{
            'id': b.id,
            'url': request.build_absolute_uri(b.file.url) if b.file else None,
            'name': (b.file.name.split('/')[-1].split('_', 1)[-1] if '_' in b.file.name else b.file.name.split('/')[-1]) if b.file else "File tidak ditemukan",
            'size': b.ukuran_file
        } for b in bukti_list] if request else []

    def _proses_bukti(self, aktivitas, bukti_data):
        if not bukti_data:
            return

        if aktivitas.bukti.exists():
            raise serializers.ValidationError({'bukti': 'BUKTI SUDAH ADA. Silakan hapus bukti lama terlebih dahulu.'})

        for bukti_item in bukti_data:
            nama_file = None
            file_base64 = None

            if isinstance(bukti_item, dict):
                nama_file = bukti_item.get('name')
                file_base64 = bukti_item.get('data')
            else:
                file_base64 = bukti_item

            if not file_base64 or ';base64,' not in file_base64:
                raise serializers.ValidationError({'bukti': 'Format file bukti tidak valid.'})

            try:
                format, filestr = file_base64.split(';base64,')
                ext = format.split('/')[-1]
                if 'jpeg' in ext:
                    ext = 'jpg'
                elif 'mpeg' in ext:
                    ext = 'mp3'
                elif 'webm' in ext:
                    if nama_file and nama_file.endswith('.mp4'):
                        ext = 'mp4'
                    elif nama_file and nama_file.endswith('.mp3'):
                        ext = 'mp3'
                    else:
                        ext = 'webm'
                elif 'octet-stream' in ext and nama_file and '.' in nama_file:
                    ext = nama_file.split('.')[-1]

                decoded_file = base64.b64decode(filestr)
            except (ValueError, TypeError, binascii.Error):
                raise serializers.ValidationError({'bukti': 'Data file bukti tidak valid.'})

            ukuran_file = len(decoded_file)
            if ukuran_file > 5 * 1024 * 1024:
                raise serializers.ValidationError({'bukti': 'Ukuran file maksimal 5MB.'})

            if not nama_file:
                nama_file = f"bukti.{ext}"

            nama_unik = f"{uuid.uuid4().hex[:8]}_{nama_file}"
            data = ContentFile(decoded_file, name=nama_unik)
            BuktiAktivitas.objects.create(aktivitas=aktivitas, file=data, ukuran_file=ukuran_file)

    def create(self, validated_data):
        bukti_data = validated_data.pop('bukti', [])

        # Normalize waktu_pelaksanaan if provided (accepts ISO datetime or YYYY-MM-DDTHH:MM[:SS])
        wp = validated_data.get('waktu_pelaksanaan')
        if wp:
            try:
                import datetime
                # If contains 'T' assume ISO
                if 'T' in wp:
                    dt = datetime.datetime.fromisoformat(wp)
                else:
                    # try parse date and time separated by space
                    dt = datetime.datetime.fromisoformat(wp)
                # store as ISO string without microseconds
                validated_data['waktu_pelaksanaan'] = dt.replace(microsecond=0).isoformat()
            except Exception:
                # leave as-is if parsing fails
                pass

        aktivitas = Aktivitas.objects.create(**validated_data)
        self._proses_bukti(aktivitas, bukti_data)
        return aktivitas

    def update(self, instance, validated_data):
        bukti_data = validated_data.pop('bukti', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if bukti_data is not None:
            self._proses_bukti(instance, bukti_data)

        return instance


class PekerjaanSerializer(serializers.ModelSerializer):
    id_proyek = serializers.ReadOnlyField(source='proyek.id')
    aktivitas = AktivitasSerializer(many=True, read_only=True)
    progres = serializers.SerializerMethodField()

    class Meta:
        model = Pekerjaan
        fields = [
            'id', 'id_proyek', 'nama', 'kategori', 'deskripsi', 'lokasi',
            'tanggal_mulai', 'tanggal_selesai', 'pelaksana', 'pengawas',
            'aktivitas', 'progres', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_progres(self, obj):
        daftar_aktivitas = obj.aktivitas.all()
        total = daftar_aktivitas.count()
        if total == 0:
            return 0
        selesai = daftar_aktivitas.filter(selesai=True).count()
        return round((selesai / total) * 100, 2)


class PekerjaanCreateSerializer(serializers.ModelSerializer):
    id_proyek = serializers.CharField(write_only=True)
    description = serializers.CharField(write_only=True, required=False, allow_blank=True)
    start_date = serializers.CharField(write_only=True, required=False, allow_blank=True)
    end_date = serializers.CharField(write_only=True, required=False, allow_blank=True)
    # Override DateField sebagai CharField
    tanggal_mulai = serializers.CharField(required=False, allow_blank=True)
    tanggal_selesai = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Pekerjaan
        fields = [
            'id_proyek', 'nama', 'kategori', 'deskripsi', 'description', 'lokasi',
            'tanggal_mulai', 'start_date', 'tanggal_selesai', 'end_date',
            'pelaksana', 'pengawas'
        ]
        extra_kwargs = {
            'nama': {'required': False, 'allow_blank': True},
            'kategori': {'required': False},
            'deskripsi': {'required': False, 'allow_blank': True},
            'lokasi': {'required': False, 'allow_blank': True},
            'pelaksana': {'required': False, 'allow_blank': True},
            'pengawas': {'required': False, 'allow_blank': True},
        }

    def _parse_date(self, value):
        """Parse string tanggal ke format YYYY-MM-DD."""
        import datetime
        if not value or not isinstance(value, str):
            return datetime.date.today().isoformat()
        value = value.strip()
        if ' - ' in value:
            value = value.split(' - ')[0].strip()
        try:
            datetime.date.fromisoformat(value)
            return value
        except (ValueError, TypeError):
            pass
        try:
            dt = datetime.datetime.strptime(value, '%d/%m/%Y')
            return dt.date().isoformat()
        except (ValueError, TypeError):
            pass
        return datetime.date.today().isoformat()

    def validate(self, data):
        # Alias handling
        if 'description' in data and not data.get('deskripsi'):
            data['deskripsi'] = data.pop('description')
        else:
            data.pop('description', None)
        if 'start_date' in data and not data.get('tanggal_mulai'):
            data['tanggal_mulai'] = data.pop('start_date')
        else:
            data.pop('start_date', None)
        if 'end_date' in data and not data.get('tanggal_selesai'):
            data['tanggal_selesai'] = data.pop('end_date')
        else:
            data.pop('end_date', None)

        # Defaults
        if not data.get('nama'): data['nama'] = "Pekerjaan Baru"
        if not data.get('deskripsi'): data['deskripsi'] = "-"
        if not data.get('lokasi'): data['lokasi'] = "-"
        if not data.get('pelaksana'): data['pelaksana'] = "-"
        if not data.get('pengawas'): data['pengawas'] = "-"

        # Parse tanggal
        data['tanggal_mulai'] = self._parse_date(data.get('tanggal_mulai'))
        data['tanggal_selesai'] = self._parse_date(data.get('tanggal_selesai'))
            
        return data

    def create(self, validated_data):
        id_proyek = validated_data.pop('id_proyek')
        try:
            proyek = Proyek.objects.get(id=id_proyek)
        except Proyek.DoesNotExist:
            raise serializers.ValidationError({'id_proyek': 'Proyek tidak ditemukan.'})
            
        pekerjaan = Pekerjaan.objects.create(proyek=proyek, **validated_data)
        return pekerjaan


class ProyekSerializer(serializers.ModelSerializer):
    pekerjaan = PekerjaanSerializer(many=True, read_only=True)
    progres = serializers.SerializerMethodField()
    is_closed = serializers.BooleanField(source='sudah_selesai', required=False)

    class Meta:
        model = Proyek
        fields = [
            'id', 'nama', 'deskripsi', 'lokasi',
            'tanggal_mulai', 'tanggal_selesai', 'pelaksana', 'pengawas',
            'status', 'sudah_selesai', 'is_closed', 'pekerjaan', 'progres', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_progres(self, obj):
        daftar_aktivitas = Aktivitas.objects.filter(pekerjaan__proyek=obj)
        total = daftar_aktivitas.count()
        if total == 0:
            return 0
        selesai = daftar_aktivitas.filter(selesai=True).count()
        return round((selesai / total) * 100, 2)

    def validate(self, data):
        if data.get('sudah_selesai') is True:
            data['status'] = 'Selesai'
        elif data.get('status') == 'Selesai':
            data['sudah_selesai'] = True
        elif data.get('status') in ('Aktif', 'Tertunda'):
            data['sudah_selesai'] = False
        return data


class ProyekCreateSerializer(serializers.ModelSerializer):
    description = serializers.CharField(write_only=True, required=False, allow_blank=True)
    start_date = serializers.CharField(write_only=True, required=False, allow_blank=True)
    end_date = serializers.CharField(write_only=True, required=False, allow_blank=True)
    is_closed = serializers.BooleanField(write_only=True, required=False)
    # Override DateField sebagai CharField agar DRF tidak memvalidasi format sebelum validate()
    tanggal_mulai = serializers.CharField(required=False, allow_blank=True)
    tanggal_selesai = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Proyek
        fields = [
            'nama', 'deskripsi', 'description', 'lokasi',
            'tanggal_mulai', 'start_date', 'tanggal_selesai', 'end_date',
            'pelaksana', 'pengawas', 'status', 'sudah_selesai', 'is_closed'
        ]
        extra_kwargs = {
            'nama': {'required': False, 'allow_blank': True},
            'deskripsi': {'required': False, 'allow_blank': True},
            'lokasi': {'required': False, 'allow_blank': True},
            'pelaksana': {'required': False, 'allow_blank': True},
            'pengawas': {'required': False, 'allow_blank': True},
            'status': {'required': False},
            'sudah_selesai': {'required': False},
        }

    def _parse_date(self, value):
        """Parse string tanggal ke format YYYY-MM-DD. Mendukung berbagai format."""
        import datetime
        if not value or not isinstance(value, str):
            return datetime.date.today().isoformat()
        value = value.strip()
        # Jika mengandung ' - ', ambil bagian pertama saja
        if ' - ' in value:
            value = value.split(' - ')[0].strip()
        # Coba parse YYYY-MM-DD
        try:
            datetime.date.fromisoformat(value)
            return value
        except (ValueError, TypeError):
            pass
        # Coba parse DD/MM/YYYY
        try:
            dt = datetime.datetime.strptime(value, '%d/%m/%Y')
            return dt.date().isoformat()
        except (ValueError, TypeError):
            pass
        # Default: hari ini
        return datetime.date.today().isoformat()

    def validate(self, data):
        # Alias handling
        if 'description' in data and not data.get('deskripsi'):
            data['deskripsi'] = data.pop('description')
        else:
            data.pop('description', None)
        if 'start_date' in data and not data.get('tanggal_mulai'):
            data['tanggal_mulai'] = data.pop('start_date')
        else:
            data.pop('start_date', None)
        if 'end_date' in data and not data.get('tanggal_selesai'):
            data['tanggal_selesai'] = data.pop('end_date')
        else:
            data.pop('end_date', None)
        if 'is_closed' in data and 'sudah_selesai' not in data:
            data['sudah_selesai'] = data.pop('is_closed')
        else:
            data.pop('is_closed', None)

        # Defaults
        if not data.get('nama'): data['nama'] = "Proyek Tanpa Nama"
        if not data.get('deskripsi'): data['deskripsi'] = "-"
        if not data.get('lokasi'): data['lokasi'] = "-"
        if not data.get('pelaksana'): data['pelaksana'] = "-"
        if not data.get('pengawas'): data['pengawas'] = "-"

        # Parse tanggal ke format yang benar
        data['tanggal_mulai'] = self._parse_date(data.get('tanggal_mulai'))
        data['tanggal_selesai'] = self._parse_date(data.get('tanggal_selesai'))
        if data.get('sudah_selesai'):
            data['status'] = 'Selesai'

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        proyek = Proyek.objects.create(user=user, **validated_data)
        return proyek


class TaskSubmissionSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField(read_only=True)
    is_late = serializers.ReadOnlyField()
    file = serializers.FileField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = TaskSubmission
        fields = [
            'id', 'category', 'title', 'description',
            'file', 'file_url', 'submitted_by',
            'project_name', 'project_id',
            'status', 'deadline_date', 'is_late',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None

    def to_internal_value(self, data):
        # Handle base64 file upload if provided as base64 string
        if 'file' in data and isinstance(data['file'], str) and ';base64,' in data['file']:
            try:
                format, filestr = data['file'].split(';base64,')
                ext = format.split('/')[-1]
                if 'jpeg' in ext: ext = 'jpg'
                elif 'mpeg' in ext: ext = 'mp3'
                elif 'octet-stream' in ext: ext = 'bin'

                decoded_file = base64.b64decode(filestr)
                file_name = f"{uuid.uuid4().hex[:8]}.{ext}"
                data['file'] = ContentFile(decoded_file, name=file_name)
            except Exception:
                raise serializers.ValidationError({"file": "Invalid file data"})

        return super().to_internal_value(data)
