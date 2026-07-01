let profileUser = null;
let cameraStream = null;
let pendingProfileImage = null;

document.addEventListener('DOMContentLoaded', async () => {
  if (!isAuthenticated()) {
    window.location.href = (typeof SCRIPT_PREFIX !== 'undefined' ? SCRIPT_PREFIX : '') + '/';
    return;
  }
  lucide.createIcons();
  await loadProfile();
});

async function loadProfile() {
  try {
    const user = await apiRequest('/users/me/');
    if (!user) return;
    profileUser = user;
    localStorage.setItem('user', JSON.stringify(user));

    document.getElementById('profile-name').textContent = user.nama || '-';
    document.getElementById('profile-nim').textContent = user.nim || '-';
    document.getElementById('profile-email').textContent = user.email || '-';

    const img = document.getElementById('profile-image');
    const icon = document.getElementById('default-avatar-icon');
    const url = user.profile_picture_url;
    if (url) {
      img.src = url;
      img.classList.remove('hidden');
      icon.classList.add('hidden');
    } else {
      img.classList.add('hidden');
      icon.classList.remove('hidden');
    }
    if (typeof updateHeaderUI === 'function') updateHeaderUI();
  } catch (e) {
    console.error(e);
    showToast('Gagal memuat profil', 'error');
  }
}

function toggleEditProfile() {
  const editing = !document.getElementById('input-name').classList.contains('hidden');
  if (editing) {
    cancelEditProfile();
    return;
  }
  document.getElementById('profile-name').classList.add('hidden');
  document.getElementById('profile-nim').classList.add('hidden');
  document.getElementById('input-name').classList.remove('hidden');
  document.getElementById('input-nim').classList.remove('hidden');
  document.getElementById('edit-actions').classList.remove('hidden');
  document.getElementById('email-help').classList.remove('hidden');
  document.getElementById('input-name').value = profileUser?.nama || '';
  document.getElementById('input-nim').value = profileUser?.nim || '';
}

function cancelEditProfile() {
  document.getElementById('profile-name').classList.remove('hidden');
  document.getElementById('profile-nim').classList.remove('hidden');
  document.getElementById('input-name').classList.add('hidden');
  document.getElementById('input-nim').classList.add('hidden');
  document.getElementById('edit-actions').classList.add('hidden');
  document.getElementById('email-help').classList.add('hidden');
}

async function saveProfile(e) {
  e.preventDefault();
  try {
    const updated = await apiRequest('/users/update_profile/', {
      method: 'PATCH',
      body: JSON.stringify({
        nama: document.getElementById('input-name').value,
        nim: document.getElementById('input-nim').value,
      }),
    });
    if (updated) {
      profileUser = updated;
      localStorage.setItem('user', JSON.stringify(updated));
      await loadProfile();
      cancelEditProfile();
      showToast('Profil berhasil disimpan', 'success');
      if (typeof updateHeaderUI === 'function') updateHeaderUI();
    }
  } catch (err) {
    console.error(err);
  }
}

document.getElementById('file-upload')?.addEventListener('change', async (e) => {
  const file = e.target.files?.[0];
  if (!file) return;
  if (file.size > 5 * 1024 * 1024) {
    showToast('Ukuran file maksimal 5MB', 'error');
    return;
  }
  const reader = new FileReader();
  reader.onload = () => {
    pendingProfileImage = reader.result;
    document.getElementById('preview-img').src = pendingProfileImage;
    document.getElementById('preview-modal').classList.remove('hidden');
    lucide.createIcons();
  };
  reader.readAsDataURL(file);
  e.target.value = '';
});

async function openCameraModal() {
  document.getElementById('camera-modal').classList.remove('hidden');
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'user' } });
    document.getElementById('camera-stream').srcObject = cameraStream;
  } catch (err) {
    showToast('Tidak dapat mengakses kamera', 'error');
    closeCameraModal();
  }
}

function closeCameraModal() {
  document.getElementById('camera-modal').classList.add('hidden');
  if (cameraStream) {
    cameraStream.getTracks().forEach((t) => t.stop());
    cameraStream = null;
  }
}

function takeSnapshot() {
  const video = document.getElementById('camera-stream');
  const canvas = document.getElementById('camera-canvas');
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  pendingProfileImage = canvas.toDataURL('image/jpeg', 0.85);
  closeCameraModal();
  document.getElementById('preview-img').src = pendingProfileImage;
  document.getElementById('preview-modal').classList.remove('hidden');
  lucide.createIcons();
}

function closePreviewModal() {
  document.getElementById('preview-modal').classList.add('hidden');
  pendingProfileImage = null;
}

async function confirmProfilePictureUpload() {
  if (!pendingProfileImage) return;
  try {
    let updated = await apiRequest('/users/update_profile/', {
      method: 'PATCH',
      body: JSON.stringify({ profile_picture: pendingProfileImage }),
    });
    if (updated) {
      profileUser = updated;
      localStorage.setItem('user', JSON.stringify(updated));
      closePreviewModal();
      await loadProfile();
      showToast('Foto profil berhasil diunggah', 'success');
      if (typeof updateHeaderUI === 'function') updateHeaderUI();
    }
  } catch (err) {
    console.error(err);
    showToast('Gagal mengunggah foto', 'error');
  }
}
