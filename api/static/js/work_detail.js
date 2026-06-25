let currentWork = null;

function getWorkId() {
  return typeof WORK_ID !== 'undefined' ? WORK_ID : window.WORK_ID || '';
}

document.addEventListener('DOMContentLoaded', async () => {
  if (!isAuthenticated()) {
    window.location.href = '/?login=1';
    return;
  }
  lucide.createIcons();
  await loadWorkDetail();
});

function closeModal(id) {
  document.getElementById(id)?.classList.add('hidden');
}

function openModal(id) {
  document.getElementById(id)?.classList.remove('hidden');
  lucide.createIcons();
}

async function loadWorkDetail() {
  const workId = getWorkId();
  if (!workId) {
    showToast('ID pekerjaan tidak valid', 'error');
    return;
  }
  try {
    console.log('[loadWorkDetail] Fetching work:', workId);
    currentWork = await apiRequest(`/pekerjaan/${workId}/`);
    
    if (!currentWork) {
      console.error('[loadWorkDetail] API returned null or undefined');
      showToast('Data pekerjaan tidak ditemukan', 'error');
      return;
    }
    
    console.log('[loadWorkDetail] Work loaded:', currentWork.nama, 'with', currentWork.aktivitas?.length || 0, 'activities');
    
    document.getElementById('work-name').textContent = currentWork.nama || 'Pekerjaan';
    document.getElementById('work-location').textContent = currentWork.lokasi || '-';
    document.getElementById('work-start').textContent = currentWork.tanggal_mulai || '-';
    document.getElementById('work-end').textContent = currentWork.tanggal_selesai || '-';
    document.getElementById('work-executor').textContent = currentWork.pelaksana || '-';
    document.getElementById('work-supervisor').textContent = currentWork.pengawas || '-';
    renderActivities(currentWork.aktivitas || []);
    
    console.log('[loadWorkDetail] ✅ Work rendered successfully');
  } catch (e) {
    console.error('[loadWorkDetail] Error:', e);
    showToast('Gagal memuat pekerjaan: ' + (e?.message || 'Kesalahan tidak diketahui'), 'error');
  }
}

function renderActivities(activities) {
  const list = document.getElementById('activities-list');
  if (!activities || !activities.length) {
    list.innerHTML = `
      <div class="bg-white rounded-xl p-8 text-center border border-gray-100">
        <i data-lucide="clipboard-list" class="w-12 h-12 text-gray-300 mx-auto mb-3"></i>
        <p class="text-gray-600 font-medium">Belum ada aktivitas</p>
      </div>`;
    lucide.createIcons();
    return;
  }
  list.innerHTML = activities
    .map((a) => {
      let displayTime = a.waktu_pelaksanaan || '-';
      if (displayTime && displayTime.includes('T')) displayTime = displayTime.split('T')[1].slice(0,5);
      return `
    <div class="bg-white rounded-xl p-5 shadow-sm border border-gray-100 flex items-start gap-4 group">
      <button onclick="toggleActivityStatus('${a.id}')" class="mt-1 w-6 h-6 rounded border-2 flex items-center justify-center flex-shrink-0 transition-colors ${a.selesai ? 'bg-green-600 border-green-600' : 'border-gray-300 hover:border-red-800'}">
        ${a.selesai ? '<i data-lucide="check" class="w-4 h-4 text-white"></i>' : ''}
      </button>
      <div class="flex-1 min-w-0">
        <h3 class="font-bold text-gray-900 ${a.selesai ? 'line-through text-gray-500' : ''}">${a.nama}</h3>
        <p class="text-sm text-gray-500 mt-1">${displayTime} · ${a.pelaksana || '-'}</p>
        ${a.evaluasi ? `<p class="text-xs text-blue-500 mt-1 italic"><span class="font-semibold not-italic">Evaluasi:</span> ${a.evaluasi}</p>` : ''}
        ${a.rencana_tambahan ? `<p class="text-xs text-amber-600 mt-0.5 italic"><span class="font-semibold not-italic">Rencana:</span> ${a.rencana_tambahan}</p>` : ''}
        ${(a.bukti_urls && a.bukti_urls.length) ? `<div class="flex flex-wrap gap-1 mt-2">${a.bukti_urls.map(b => `<a href="${b.url}" target="_blank" class="block w-10 h-10 rounded-md overflow-hidden border border-gray-200 hover:border-red-800 transition-colors" title="Bukti"><img src="${b.url}" alt="" style="width:40px;height:40px;object-fit:cover;" onerror="this.parentElement.innerHTML='<div class=\'flex items-center justify-center w-full h-full bg-gray-50\'><i data-lucide=\'file\' class=\'w-4 h-4 text-gray-400\'></i></div>'"/></a>`).join('')}</div>` : ''}
      </div>
      <!-- Tombol aksi -->
      <div class="flex items-center gap-1 shrink-0">
        <button onclick="openUploadBukti('${a.id}')" class="p-1.5 ${(a.bukti_urls||[]).length ? 'text-green-600 bg-green-50' : 'text-gray-400 hover:text-green-600 hover:bg-green-50'} rounded-lg transition-colors" title="${(a.bukti_urls||[]).length ? 'Lihat/Ganti Bukti' : 'Upload Bukti'}">
          <i data-lucide="${(a.bukti_urls||[]).length ? 'image' : 'upload'}" class="w-4 h-4"></i>
        </button>
        <div class="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
          <button onclick="openEditActivityModal('${a.id}')" class="p-1.5 text-gray-400 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors" title="Edit Aktivitas">
            <i data-lucide="edit-3" class="w-4 h-4"></i>
          </button>
          <button onclick="deleteActivity('${a.id}')" class="p-1.5 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors" title="Hapus Aktivitas">
            <i data-lucide="trash-2" class="w-4 h-4"></i>
          </button>
        </div>
      </div>
    </div>`;
    })
    .join('');
  lucide.createIcons();
}

async function toggleActivityStatus(id) {
  try {
    await apiRequest(`/aktivitas/${id}/toggle_selesai/`, { method: 'PATCH' });
    await loadWorkDetail();
  } catch (e) {
    console.error(e);
  }
}

function openAddActivityModal() {
  openModal('add-activity-modal');
}

async function handleActivitySubmit(e) {
  e.preventDefault();
  try {
    let workId = getWorkId();
    
    // Validate required fields
    const activityName = document.getElementById('new-activity-name').value?.trim();
    const activityTime = document.getElementById('new-activity-time').value;
    const activityExecutor = document.getElementById('new-activity-executor').value?.trim();
    
    if (!activityName) {
      showToast('Nama aktivitas diperlukan', 'error');
      return;
    }
    if (!activityTime) {
      showToast('Waktu pelaksanaan diperlukan', 'error');
      return;
    }
    if (!activityExecutor) {
      showToast('Pelaksana diperlukan', 'error');
      return;
    }
    
    console.log('[handleActivitySubmit] Creating activity:', { workId, activityName, activityTime, activityExecutor });
    
    // Combine selected time with current work's start date to build ISO datetime
    let timeVal = activityTime; // HH:MM
    if (currentWork && currentWork.tanggal_mulai) {
      const datePart = String(currentWork.tanggal_mulai).split('T')[0];
      timeVal = `${datePart}T${timeVal}:00`;
    }

    const activityResponse = await apiRequest('/aktivitas/', {
      method: 'POST',
      body: JSON.stringify({
        id_pekerjaan: workId,
        nama: activityName,
        waktu_pelaksanaan: timeVal,
        pelaksana: activityExecutor,
      }),
    });
    
    console.log('[handleActivitySubmit] Activity created:', activityResponse);
    
    closeModal('add-activity-modal');
    e.target.reset();
    showToast('Aktivitas ditambahkan. Memperbarui data...', 'success');
    
    console.log('[handleActivitySubmit] Reloading work detail...');
    await loadWorkDetail();
    
    console.log('[handleActivitySubmit] ✅ Work detail reloaded');
  } catch (err) {
    console.error('[handleActivitySubmit] Error:', err);
    showToast('Gagal membuat aktivitas: ' + (err?.message || 'Kesalahan tidak diketahui'), 'error');
  }
}

function openEditWorkModal() {
  if (!currentWork) return;
  document.getElementById('edit-work-name').value = currentWork.nama || '';
  document.getElementById('edit-work-description').value = currentWork.deskripsi || '';
  document.getElementById('edit-work-location').value = currentWork.lokasi || '';
  document.getElementById('edit-work-start').value = currentWork.tanggal_mulai || '';
  document.getElementById('edit-work-end').value = currentWork.tanggal_selesai || '';
  document.getElementById('edit-work-executor').value = currentWork.pelaksana || '';
  document.getElementById('edit-work-supervisor').value = currentWork.pengawas || '';
  openModal('edit-work-modal');
}

async function submitEditWork(e) {
  e.preventDefault();
  let workId = getWorkId();
  try {
    await apiRequest(`/pekerjaan/${workId}/`, {
      method: 'PATCH',
      body: JSON.stringify({
        nama: document.getElementById('edit-work-name').value,
        deskripsi: document.getElementById('edit-work-description').value,
        lokasi: document.getElementById('edit-work-location').value,
        tanggal_mulai: document.getElementById('edit-work-start').value,
        tanggal_selesai: document.getElementById('edit-work-end').value,
        pelaksana: document.getElementById('edit-work-executor').value,
        pengawas: document.getElementById('edit-work-supervisor').value,
      }),
    });
    closeModal('edit-work-modal');
    showToast('Pekerjaan diperbarui', 'success');
    await loadWorkDetail();
  } catch (err) {
    console.error(err);
  }
}

// Fungsi edit aktivitas dari work_detail
function openEditActivityModal(activityId) {
  const a = (currentWork?.aktivitas || []).find(x => x.id === activityId);
  if (!a) return;

  document.getElementById('edit-activity-id').value = a.id;
  document.getElementById('edit-activity-name').value = a.nama || '';
  let timeVal = a.waktu_pelaksanaan || '';
  if (timeVal && timeVal.includes('T')) timeVal = timeVal.split('T')[1].slice(0, 5);
  document.getElementById('edit-activity-time').value = timeVal;
  document.getElementById('edit-activity-executor').value = a.pelaksana || '';
  document.getElementById('edit-activity-evaluation').value = a.evaluasi || '';
  document.getElementById('edit-activity-plan').value = a.rencana_tambahan || '';
  openModal('edit-activity-modal');
}

async function submitEditActivity(e) {
  e.preventDefault();
  const id = document.getElementById('edit-activity-id').value;
  try {
    console.log('[submitEditActivity] Updating activity:', id);
    
    let timeVal = document.getElementById('edit-activity-time').value;
    if (currentWork && currentWork.tanggal_mulai && timeVal && !timeVal.includes('T')) {
      const datePart = String(currentWork.tanggal_mulai).split('T')[0];
      timeVal = `${datePart}T${timeVal}:00`;
    }
    
    const updateResponse = await apiRequest(`/aktivitas/${id}/`, {
      method: 'PATCH',
      body: JSON.stringify({
        nama: document.getElementById('edit-activity-name').value,
        waktu_pelaksanaan: timeVal,
        pelaksana: document.getElementById('edit-activity-executor').value,
        evaluasi: document.getElementById('edit-activity-evaluation').value,
        rencana_tambahan: document.getElementById('edit-activity-plan').value,
      }),
    });
    
    console.log('[submitEditActivity] Activity updated:', updateResponse);
    
    closeModal('edit-activity-modal');
    showToast('Aktivitas diperbarui', 'success');
    await loadWorkDetail();
    
    console.log('[submitEditActivity] ✅ Work detail reloaded');
  } catch (err) {
    console.error('[submitEditActivity] Error:', err);
    showToast('Gagal memperbarui aktivitas: ' + (err?.message || 'Kesalahan tidak diketahui'), 'error');
  }
}

// ===== Upload Bukti untuk work_detail =====
let wdUploadData = null;
let wdCameraStream = null;

function openUploadBukti(activityId) {
  const a = (currentWork?.aktivitas || []).find(x => x.id === activityId);
  if (a?.bukti_urls?.length) {
    showToast('Bukti sudah ada. Hapus bukti lama untuk mengganti.', 'error');
    return;
  }
  document.getElementById('upload-activity-id').value = activityId;
  wdResetUpload();
  openModal('upload-file-modal');
}

function wdResetUpload() {
  wdUploadData = null;
  ['wd-upload-selection', 'wd-method-camera', 'wd-method-preview', 'wd-uploading-state'].forEach(id => {
    document.getElementById(id)?.classList.add('hidden');
  });
  document.getElementById('wd-upload-selection')?.classList.remove('hidden');
  wdStopCamera();
}

function wdHandleFileSelect(input) {
  const file = input.files?.[0];
  if (!file) return;
  if (file.size > 5 * 1024 * 1024) { showToast('Maksimal 5MB', 'error'); return; }
  const reader = new FileReader();
  reader.onload = () => wdShowPreview(reader.result, file.type.startsWith('image/') ? 'image' : 'file', file.name);
  reader.readAsDataURL(file);
}

async function wdShowCamera() {
  ['wd-upload-selection', 'wd-method-preview'].forEach(id => document.getElementById(id)?.classList.add('hidden'));
  document.getElementById('wd-method-camera')?.classList.remove('hidden');
  try {
    wdCameraStream = await navigator.mediaDevices.getUserMedia({ video: true });
    document.getElementById('wd-camera-preview').srcObject = wdCameraStream;
  } catch {
    showToast('Kamera tidak tersedia', 'error');
    wdResetUpload();
  }
}

function wdCapturePhoto() {
  const video = document.getElementById('wd-camera-preview');
  const canvas = document.getElementById('wd-camera-canvas');
  if (!video?.videoWidth) return;
  canvas.width = video.videoWidth; canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  wdShowPreview(canvas.toDataURL('image/jpeg', 0.85), 'image', 'foto.jpg');
}

function wdStopCamera() {
  if (wdCameraStream) { wdCameraStream.getTracks().forEach(t => t.stop()); wdCameraStream = null; }
}

function wdShowPreview(dataUrl, type, name) {
  wdUploadData = { dataUrl, type, name };
  ['wd-upload-selection', 'wd-method-camera'].forEach(id => document.getElementById(id)?.classList.add('hidden'));
  wdStopCamera();
  const imgEl = document.getElementById('wd-preview-img');
  const fileEl = document.getElementById('wd-preview-file-info');
  if (type === 'image') {
    imgEl.src = dataUrl; imgEl.classList.remove('hidden'); fileEl?.classList.add('hidden');
  } else {
    imgEl.classList.add('hidden');
    if (fileEl) { fileEl.classList.remove('hidden'); document.getElementById('wd-preview-filename').textContent = name; }
  }
  document.getElementById('wd-method-preview')?.classList.remove('hidden');
  lucide.createIcons();
}

async function wdConfirmUpload() {
  if (!wdUploadData) return;
  const activityId = document.getElementById('upload-activity-id').value;
  document.getElementById('wd-method-preview')?.classList.add('hidden');
  document.getElementById('wd-uploading-state')?.classList.remove('hidden');
  try {
    await apiRequest(`/aktivitas/${activityId}/`, {
      method: 'PATCH',
      body: JSON.stringify({ bukti: [{ name: wdUploadData.name, data: wdUploadData.dataUrl }] }),
    });
    closeModal('upload-file-modal');
    showToast('Bukti berhasil diunggah', 'success');
    await loadWorkDetail();
  } catch (e) {
    console.error(e);
    showToast('Gagal mengunggah bukti', 'error');
  } finally {
    document.getElementById('wd-uploading-state')?.classList.add('hidden');
  }
}

// Bug Fix #5: fungsi hapus aktivitas dari work_detail
async function deleteActivity(activityId) {
  if (!confirm('Hapus aktivitas ini?')) return;
  try {
    await apiRequest(`/aktivitas/${activityId}/`, { method: 'DELETE' });
    showToast('Aktivitas dihapus', 'success');
    await loadWorkDetail();
  } catch (e) {
    console.error(e);
    showToast('Gagal menghapus aktivitas', 'error');
  }
}
