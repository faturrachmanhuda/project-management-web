let currentProject = null;
let ganttChartInstance = null;
let uploadPreviewData = null;
let cameraStream = null;
let mediaRecorder = null;
let recordedChunks = [];



function getProjectId() {
  return window.PROJECT_ID || '';
}

function closeModal(id) {
  document.getElementById(id)?.classList.add('hidden');
  if (id === 'upload-file-modal') resetUploadModal();
}

function openModal(id) {
  document.getElementById(id)?.classList.remove('hidden');
  lucide.createIcons();
}

function switchWorkTab(workId, tabName) {
  // Hide all tabs for this work
  document.querySelectorAll(`[data-work-id="${workId}"][data-tab]`).forEach(el => {
    if (el.classList.contains('work-tab')) {
      el.classList.remove('border-b-red-800', 'text-red-800');
      el.classList.add('border-b-transparent', 'text-gray-600');
    } else if (el.classList.contains('work-tab-content')) {
      // Bug Fix #2: gunakan style display supaya override-safe
      el.style.display = 'none';
    }
  });

  // Show selected tab
  document.querySelectorAll(`[data-work-id="${workId}"][data-tab="${tabName}"]`).forEach(el => {
    if (el.classList.contains('work-tab')) {
      el.classList.add('border-b-red-800', 'text-red-800');
      el.classList.remove('border-b-transparent', 'text-gray-600');
    } else if (el.classList.contains('work-tab-content')) {
      // Bug Fix #2: gunakan style display supaya override-safe
      el.style.display = 'block';
    }
  });
}

document.addEventListener('DOMContentLoaded', async () => {
  if (!isAuthenticated()) {
    window.location.href = '/?login=1';
    return;
  }
  lucide.createIcons();
  await loadProjectData();
});

async function loadProjectData() {
  const projectId = getProjectId();
  if (!projectId) {
    showToast('ID proyek tidak valid', 'error');
    return;
  }
  try {
    console.log('[loadProjectData] Fetching project:', projectId);
    currentProject = await apiRequest(`/proyek/${projectId}/`);
    
    if (!currentProject) {
      console.error('[loadProjectData] API returned null or undefined');
      showToast('Data proyek tidak ditemukan', 'error');
      return;
    }
    
    console.log('[loadProjectData] Project loaded:', currentProject.nama, 'with', currentProject.pekerjaan?.length || 0, 'works');
    
    renderProjectHeader(currentProject);
    renderWorks(currentProject.pekerjaan || []);
    renderGanttChart(currentProject.pekerjaan || []);
    
    console.log('[loadProjectData] ✅ Project rendered successfully');
  } catch (e) {
    console.error('[loadProjectData] Error:', e);
    showToast('Gagal memuat proyek: ' + (e?.message || 'Kesalahan tidak diketahui'), 'error');
  }
}

function renderProjectHeader(p) {
  document.getElementById('header-project-name').textContent = p.nama || 'Proyek';
  const statusEl = document.getElementById('header-project-status');
  const status = p.sudah_selesai ? 'SELESAI' : (p.status || 'AKTIF').toUpperCase();
  statusEl.textContent = status;
  statusEl.className = `status-badge px-2 py-0.5 rounded ${p.sudah_selesai ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'}`;
  document.getElementById('val-location').textContent = p.lokasi || '-';
  document.getElementById('side-description').textContent = p.deskripsi || '-';
  document.getElementById('side-start').textContent = p.tanggal_mulai || '-';
  document.getElementById('side-end').textContent = p.tanggal_selesai || '-';
  document.getElementById('side-executor').textContent = p.pelaksana || '-';
  document.getElementById('side-supervisor').textContent = p.pengawas || '-';

  // Update tombol Tutup Proyek sesuai status
  const btnTutup = document.getElementById('btn-tutup-proyek');
  if (btnTutup) {
    if (p.sudah_selesai) {
      btnTutup.innerHTML = '<i data-lucide="unlock" class="w-4 h-4 inline mr-1"></i>Buka Kembali';
      btnTutup.title = 'Buka Kembali Proyek';
      btnTutup.className = 'px-4 py-2 text-sm font-bold text-green-700 hover:bg-green-50 rounded-lg transition-all border border-green-200';
    } else {
      btnTutup.innerHTML = '<i data-lucide="lock" class="w-4 h-4 inline mr-1"></i>Tutup Proyek';
      btnTutup.title = 'Tutup Proyek';
      btnTutup.className = 'px-4 py-2 text-sm font-bold text-gray-700 hover:bg-gray-100 rounded-lg transition-all border border-gray-200';
    }
    lucide.createIcons();
  }

  const works = p.pekerjaan || [];
  let totalActs = 0;
  let doneActs = 0;
  works.forEach((w) => {
    (w.aktivitas || []).forEach((a) => {
      totalActs++;
      if (a.selesai) doneActs++;
    });
  });
  const pct = totalActs ? Math.round((doneActs / totalActs) * 100) : p.progres || 0;
  document.getElementById('overall-progress').textContent = `${pct}%`;
  document.getElementById('completed-count').textContent = `${doneActs}/${totalActs} Selesai`;
  document.getElementById('progress-bar').style.width = `${pct}%`;
  document.getElementById('work-count').textContent = `${works.length} Pekerjaan`;
}

function renderWorks(works) {
  const container = document.getElementById('works-container');
  console.log('[renderWorks] Rendering', works?.length || 0, 'works');
  
  if (!works || !works.length) {
    console.log('[renderWorks] No works to render');
    container.innerHTML = `
      <div class="bg-white rounded-2xl p-10 text-center border border-gray-100">
        <i data-lucide="activity" class="w-14 h-14 text-gray-300 mx-auto mb-4"></i>
        <p class="text-gray-600 font-medium mb-2">Belum ada aktivitas dari modul eksternal</p>
        <p class="text-sm text-gray-400">Log akan otomatis muncul saat IE, IC, atau Implementation mengirim update.</p>
      </div>`;
    lucide.createIcons();
    return;
  }

  // Source config for styling
  const sourceConfig = {
    engineering: { icon: 'drafting-compass', color: 'text-indigo-600', bg: 'bg-indigo-50', border: 'border-indigo-200', label: 'IE', badgeColor: 'bg-indigo-100 text-indigo-700' },
    creation:    { icon: 'brain',            color: 'text-emerald-600', bg: 'bg-emerald-50', border: 'border-emerald-200', label: 'IC', badgeColor: 'bg-emerald-100 text-emerald-700' },
    implementation: { icon: 'rocket',        color: 'text-amber-600', bg: 'bg-amber-50', border: 'border-amber-200', label: 'IMPL', badgeColor: 'bg-amber-100 text-amber-700' },
  };

  container.innerHTML = works
    .map((work) => {
      const activities = work.aktivitas || [];
      console.log(`  [renderWorks] Work ${work.id}: ${activities.length} activities`);
      const totalActivities = activities.length;
      const completedActivities = activities.filter(a => a.selesai).length;
      
      // Determine source from kategori
      const src = sourceConfig[work.kategori] || sourceConfig.implementation;

      // Status badge
      let statusBadge = 'PROSES';
      let statusColor = 'bg-yellow-100 text-yellow-700';
      if (completedActivities === totalActivities && totalActivities > 0) {
        statusBadge = 'SELESAI';
        statusColor = 'bg-green-100 text-green-700';
      } else if (completedActivities === 0 && totalActivities > 0) {
        statusBadge = 'BELUM';
        statusColor = 'bg-red-100 text-red-700';
      }

      // Parse links from activity evaluasi field (JSON)
      function parseLinks(activity) {
        try {
          if (activity.evaluasi) {
            const data = JSON.parse(activity.evaluasi);
            return data.links || [];
          }
        } catch(e) {}
        return [];
      }

      const activitiesHtml = activities.length
        ? `<div class="space-y-1">
            ${activities
              .map((a) => {
                let displayTime = a.waktu_pelaksanaan || '';
                if (displayTime && displayTime.includes('T')) displayTime = displayTime.split('T')[1].slice(0,5);
                const links = parseLinks(a);
                const linksHtml = links.map(l => 
                  `<a href="${l.url}" target="_blank" rel="noopener" class="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-bold rounded-lg ${src.bg} ${src.color} border ${src.border} hover:shadow-sm transition-all">
                    <i data-lucide="external-link" class="w-3 h-3"></i>${l.title}
                  </a>`
                ).join('');
                
                return `
              <div class="flex items-start gap-3 p-3 rounded-lg hover:bg-gray-50/80 transition-colors">
                <div class="w-8 h-8 rounded-lg ${src.bg} flex items-center justify-center shrink-0 mt-0.5">
                  <i data-lucide="${src.icon}" class="w-4 h-4 ${src.color}"></i>
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-sm font-semibold text-gray-800">${a.nama}</p>
                  ${a.rencana_tambahan ? `<p class="text-xs text-gray-500 mt-0.5">${a.rencana_tambahan}</p>` : ''}
                  ${linksHtml ? `<div class="flex flex-wrap gap-2 mt-2">${linksHtml}</div>` : ''}
                </div>
                <div class="flex items-center gap-2 shrink-0">
                  <span class="text-xs text-gray-400 font-medium">${displayTime || ''}</span>
                  ${a.selesai ? '<span class="w-2 h-2 rounded-full bg-green-500 shrink-0" title="Selesai"></span>' : '<span class="w-2 h-2 rounded-full bg-yellow-400 shrink-0" title="Proses"></span>'}
                </div>
              </div>`;
              })
              .join('')}
          </div>`
        : '<p class="text-sm text-gray-400 px-3 py-6 italic text-center">Belum ada aktivitas dari modul ini</p>';

      return `
      <div class="work-card bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
        <!-- Header Pekerjaan -->
        <div class="p-4 border-b border-gray-100 bg-gradient-to-r from-gray-50 to-white">
          <div class="flex items-start justify-between gap-3 mb-3">
            <div class="flex-1 min-w-0 flex items-center gap-3">
              <div class="w-10 h-10 rounded-xl ${src.bg} flex items-center justify-center shrink-0">
                <i data-lucide="${src.icon}" class="w-5 h-5 ${src.color}"></i>
              </div>
              <div>
                <h3 class="text-lg font-black text-gray-900 leading-tight">${work.nama}</h3>
                <div class="flex items-center gap-2 mt-1">
                  <span class="inline-block px-2 py-0.5 rounded-full text-[10px] font-bold ${src.badgeColor}">${src.label}</span>
                  <span class="inline-block px-2 py-0.5 rounded-full text-[10px] font-bold ${statusColor}">${statusBadge}</span>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-1.5 shrink-0">
              <button type="button" onclick="openEditWorkModal('${work.id}')" class="p-2 text-gray-400 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors" title="Edit">
                <i data-lucide="edit-3" class="w-4 h-4"></i>
              </button>
              <button type="button" onclick="deleteWork('${work.id}')" class="p-2 text-gray-400 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors" title="Hapus">
                <i data-lucide="trash-2" class="w-4 h-4"></i>
              </button>
            </div>
          </div>
          <div class="flex flex-wrap gap-2 text-xs text-gray-500 ml-13">
            <span class="flex items-center gap-1"><i data-lucide="calendar" class="w-3 h-3"></i>${work.tanggal_mulai || '-'} – ${work.tanggal_selesai || '-'}</span>
            <span class="flex items-center gap-1"><i data-lucide="activity" class="w-3 h-3"></i>${totalActivities} log</span>
          </div>
        </div>

        <!-- Activities Feed (no tabs) -->
        <div class="p-5">
          ${activitiesHtml}
        </div>
      </div>`;
    })
    .join('');
  lucide.createIcons();
}


function renderGanttChart(works) {
  const card = document.getElementById('gantt-card');
  const canvas = document.getElementById('ganttChart');
  if (!works.length || typeof Chart === 'undefined') {
    card?.classList.add('hidden');
    return;
  }

  // Filter hanya pekerjaan yang punya tanggal
  const worksWithDates = works.filter(w => w.tanggal_mulai && w.tanggal_selesai);
  if (!worksWithDates.length) {
    card?.classList.add('hidden');
    return;
  }

  card.classList.remove('hidden');

  // Tinggi dinamis sesuai jumlah pekerjaan (min 300px)
  const rowHeight = 52;
  const chartHeight = Math.max(300, worksWithDates.length * rowHeight + 80);
  const wrapper = document.getElementById('gantt-chart-wrapper');
  if (wrapper) wrapper.style.height = chartHeight + 'px';

  // Konversi tanggal ke timestamp ms
  const toMs = (d) => new Date(d).getTime();

  // Rentang sumbu X: 3 hari sebelum mulai tercepat hingga 3 hari setelah selesai terlama
  const allStarts = worksWithDates.map(w => toMs(w.tanggal_mulai));
  const allEnds   = worksWithDates.map(w => toMs(w.tanggal_selesai));
  const xMin = Math.min(...allStarts) - 3 * 86400000;
  const xMax = Math.max(...allEnds)   + 3 * 86400000;

  // Warna berdasarkan progres
  const barColor = (progres) => {
    if (progres >= 100) return 'rgba(22, 163, 74, 0.85)';   // hijau
    if (progres >= 50)  return 'rgba(234, 179, 8, 0.85)';   // kuning
    return 'rgba(185, 28, 28, 0.85)';                        // merah
  };
  const borderColor = (progres) => {
    if (progres >= 100) return 'rgb(21, 128, 61)';
    if (progres >= 50)  return 'rgb(161, 98, 7)';
    return 'rgb(153, 27, 27)';
  };

  const labels   = worksWithDates.map(w => w.nama);
  const datasets = [
    // Bar latar belakang abu-abu (total durasi)
    {
      label: 'Durasi Pekerjaan',
      data: worksWithDates.map(w => [toMs(w.tanggal_mulai), toMs(w.tanggal_selesai)]),
      backgroundColor: 'rgba(229, 231, 235, 0.6)',
      borderColor: 'rgba(209, 213, 219, 0.8)',
      borderWidth: 1,
      borderRadius: 6,
      borderSkipped: false,
    },
    // Bar progres (overlay)
    {
      label: 'Progres',
      data: worksWithDates.map(w => {
        const start = toMs(w.tanggal_mulai);
        const end   = toMs(w.tanggal_selesai);
        const pct   = (w.progres ?? 0) / 100;
        return [start, start + (end - start) * pct];
      }),
      backgroundColor: worksWithDates.map(w => barColor(w.progres ?? 0)),
      borderColor: worksWithDates.map(w => borderColor(w.progres ?? 0)),
      borderWidth: 1,
      borderRadius: 6,
      borderSkipped: false,
    },
  ];

  if (ganttChartInstance) ganttChartInstance.destroy();

  ganttChartInstance = new Chart(canvas, {
    type: 'bar',
    data: { labels, datasets },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 600 },
      layout: { padding: { right: 8 } },
      plugins: {
        legend: { display: false },
        tooltip: {
          callbacks: {
            title: (items) => items[0]?.label || '',
            label: (ctx) => {
              const w = worksWithDates[ctx.dataIndex];
              if (ctx.datasetIndex === 0) {
                return ` Durasi: ${w.tanggal_mulai} → ${w.tanggal_selesai}`;
              }
              return ` Progres: ${w.progres ?? 0}%`;
            },
          },
        },
        // Label progres % di ujung bar
        afterDatasetsDraw: undefined,
      },
      scales: {
        x: {
          type: 'time',
          time: {
            unit: 'week',
            tooltipFormat: 'dd MMM yyyy',
            displayFormats: { week: 'dd MMM', month: 'MMM yyyy' },
          },
          min: xMin,
          max: xMax,
          grid: { color: 'rgba(0,0,0,0.04)' },
          ticks: {
            font: { size: 10 },
            color: '#9ca3af',
            maxRotation: 0,
          },
        },
        y: {
          grid: { display: false },
          ticks: {
            font: { size: 11, weight: 'bold' },
            color: '#374151',
            // Potong label yang terlalu panjang
            callback: (val, idx) => {
              const name = labels[idx] || '';
              return name.length > 22 ? name.substring(0, 20) + '…' : name;
            },
          },
        },
      },
    },
    // Plugin custom untuk menggambar % di atas bar progres
    plugins: [{
      id: 'ganttLabels',
      afterDatasetsDraw(chart) {
        const { ctx } = chart;
        const meta = chart.getDatasetMeta(1); // dataset progres
        meta.data.forEach((bar, i) => {
          const w = worksWithDates[i];
          const pct = w.progres ?? 0;
          const label = `${pct}%`;
          ctx.save();
          ctx.font = 'bold 10px sans-serif';
          ctx.fillStyle = pct > 0 ? '#fff' : '#9ca3af';
          ctx.textBaseline = 'middle';
          ctx.textAlign = 'right';
          // Gambar di dalam bar jika cukup lebar, atau di luar kalau terlalu kecil
          const barWidth = bar.width ?? 0;
          if (barWidth > 30) {
            ctx.fillText(label, bar.x - 6, bar.y);
          } else if (pct === 0) {
            ctx.fillStyle = '#9ca3af';
            ctx.textAlign = 'left';
            // Ambil x dari bar durasi (dataset 0)
            const durationBar = chart.getDatasetMeta(0).data[i];
            ctx.fillText('0%', durationBar.base + 4, bar.y);
          }
          ctx.restore();
        });
      },
    }],
  });
}

async function toggleStatus(id) {
  try {
    await apiRequest(`/aktivitas/${id}/toggle_selesai/`, { method: 'PATCH' });
    await loadProjectData();
  } catch (e) {
    console.error(e);
    showToast('Gagal mengubah status', 'error');
  }
}

async function deleteWork(workId) {
  try {
    await apiRequest(`/pekerjaan/${workId}/`, { method: 'DELETE' });
    showToast('Pekerjaan dihapus', 'success');
    await loadProjectData();
  } catch (e) {
    console.error(e);
    showToast('Gagal menghapus pekerjaan', 'error');
  }
}

// Bug Fix #4: fungsi hapus aktivitas
async function deleteActivity(activityId) {
  if (!confirm('Hapus aktivitas ini?')) return;
  try {
    await apiRequest(`/aktivitas/${activityId}/`, { method: 'DELETE' });
    showToast('Aktivitas dihapus', 'success');
    await loadProjectData();
  } catch (e) {
    console.error(e);
    showToast('Gagal menghapus aktivitas', 'error');
  }
}

function openAddWorkModal() {
  openModal('add-work-modal');
}

async function handleWorkSubmit(e) {
  e.preventDefault();
  let projectId = getProjectId();
  try {
    await apiRequest('/pekerjaan/', {
      method: 'POST',
      body: JSON.stringify({
        id_proyek: projectId,
        nama: document.getElementById('new-work-name').value,
        deskripsi: document.getElementById('new-work-description').value,
        lokasi: document.getElementById('new-work-location').value,
        tanggal_mulai: document.getElementById('new-work-start').value,
        tanggal_selesai: document.getElementById('new-work-end').value,
        pelaksana: document.getElementById('new-work-executor').value,
        pengawas: document.getElementById('new-work-supervisor').value,
      }),
    });
    closeModal('add-work-modal');
    e.target.reset();
    showToast('Pekerjaan ditambahkan', 'success');
    await loadProjectData();
  } catch (err) {
    console.error(err);
  }
}

function openEditWorkModal(workId) {
  const work = (currentProject?.pekerjaan || []).find((w) => w.id === workId);
  if (!work) return;
  document.getElementById('edit-work-id').value = work.id;
  document.getElementById('edit-work-name').value = work.nama || '';
  document.getElementById('edit-work-description').value = work.deskripsi || '';
  document.getElementById('edit-work-location').value = work.lokasi || '';
  document.getElementById('edit-work-start').value = work.tanggal_mulai || '';
  document.getElementById('edit-work-end').value = work.tanggal_selesai || '';
  document.getElementById('edit-work-executor').value = work.pelaksana || '';
  document.getElementById('edit-work-supervisor').value = work.pengawas || '';
  openModal('edit-work-modal');
}

async function submitEditWork(e) {
  e.preventDefault();
  const id = document.getElementById('edit-work-id').value;
  try {
    await apiRequest(`/pekerjaan/${id}/`, {
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
    await loadProjectData();
  } catch (err) {
    console.error(err);
  }
}

function openAddActivityModal(workId) {
  document.getElementById('target-work-id').value = workId;
  openModal('add-activity-modal');
}

async function handleActivitySubmit(e) {
  e.preventDefault();
  try {
    // Validate required fields
    const workId = document.getElementById('target-work-id').value;
    const activityName = document.getElementById('new-activity-name').value?.trim();
    const activityTime = document.getElementById('new-activity-time').value;
    const activityExecutor = document.getElementById('new-activity-executor').value?.trim();

    if (!workId) {
      showToast('Pilih pekerjaan terlebih dahulu', 'error');
      return;
    }
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

    // Log: Starting activity creation
    console.log('[handleActivitySubmit] Creating activity:', { workId, activityName, activityTime, activityExecutor });

    // Combine selected time with work start date to produce full datetime
    const work = (currentProject?.pekerjaan || []).find(w => String(w.id) === String(workId));
    let timeVal = activityTime; // HH:MM
    if (work && work.tanggal_mulai) {
      const datePart = String(work.tanggal_mulai).split('T')[0];
      timeVal = `${datePart}T${timeVal}:00`;
    }

    // Create activity via API
    const activityResponse = await apiRequest('/aktivitas/', {
      method: 'POST',
      body: JSON.stringify({
        id_pekerjaan: workId,
        nama: activityName,
        waktu_pelaksanaan: timeVal,
        pelaksana: activityExecutor,
      }),
    });

    // Log: Activity creation successful
    console.log('[handleActivitySubmit] Activity created:', activityResponse);

    closeModal('add-activity-modal');
    e.target.reset();
    showToast('Aktivitas ditambahkan. Memperbarui data...', 'success');

    // Log: Reloading project data
    console.log('[handleActivitySubmit] Reloading project data...');
    await loadProjectData();

    // Log: Project data reloaded
    console.log('[handleActivitySubmit] Project data reloaded. Activities in work:', 
      (currentProject?.pekerjaan?.find(w => String(w.id) === String(workId))?.aktivitas || []).length);

    // Verify activity appears in the list
    const updatedWork = currentProject?.pekerjaan?.find(w => String(w.id) === String(workId));
    const activityInList = updatedWork?.aktivitas?.find(a => a.id === activityResponse.id);
    if (activityInList) {
      console.log('[handleActivitySubmit] ✅ Activity successfully found in list');
    } else {
      console.warn('[handleActivitySubmit] ⚠️ Activity NOT found in list after reload!');
      console.warn('[handleActivitySubmit] Work has', updatedWork?.aktivitas?.length || 0, 'activities');
      showToast('⚠️ Aktivitas dibuat tapi tidak terlihat di list. Silakan refresh halaman jika tetap tidak muncul.', 'warning');
    }
  } catch (err) {
    console.error('[handleActivitySubmit] Error:', err);
    showToast('Gagal membuat aktivitas: ' + (err?.message || 'Kesalahan tidak diketahui'), 'error');
  }
}

function findActivity(activityId) {
  for (const w of currentProject?.pekerjaan || []) {
    const a = (w.aktivitas || []).find((x) => x.id === activityId);
    if (a) return { activity: a, work: w };
  }
  return null;
}

function openEditActivity(activityId) {
  const found = findActivity(activityId);
  if (!found) return;
  const a = found.activity;
  const w = found.work;
  document.getElementById('edit-activity-id').value = a.id;
  document.getElementById('edit-activity-name').value = a.nama || '';
  // extract time portion if ISO datetime
  let timeVal = a.waktu_pelaksanaan || '';
  if (timeVal && timeVal.includes('T')) timeVal = timeVal.split('T')[1].slice(0,5);
  document.getElementById('edit-activity-time').value = timeVal;
  document.getElementById('edit-activity-executor').value = a.pelaksana || '';
  document.getElementById('edit-activity-evaluation').value = a.evaluasi || '';
  document.getElementById('edit-activity-plan').value = a.rencana_tambahan || '';
  document.getElementById('edit-activity-work-start').value = (w && w.tanggal_mulai) ? String(w.tanggal_mulai).split('T')[0] : '';
  openModal('edit-activity-modal');
}

async function submitEditActivity(e) {
  e.preventDefault();
  let id = document.getElementById('edit-activity-id').value;
  try {
    console.log('[submitEditActivity] Updating activity:', id);
    
    // combine edit time with work start if necessary
    let timeVal = document.getElementById('edit-activity-time').value;
    const workDate = document.getElementById('edit-activity-work-start').value; // YYYY-MM-DD
    if (timeVal && !timeVal.includes('T') && workDate) {
      timeVal = `${workDate}T${timeVal}:00`;
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
    await loadProjectData();
    
    console.log('[submitEditActivity] ✅ Project data reloaded');
  } catch (err) {
    console.error('[submitEditActivity] Error:', err);
    showToast('Gagal memperbarui aktivitas: ' + (err?.message || 'Kesalahan tidak diketahui'), 'error');
  }
}

function handleEditProject() {
  if (!currentProject) return;
  document.getElementById('edit-project-name').value = currentProject.nama || '';
  document.getElementById('edit-project-description').value = currentProject.deskripsi || '';
  document.getElementById('edit-project-location').value = currentProject.lokasi || '';
  document.getElementById('edit-project-status').value = currentProject.status || 'Aktif';
  document.getElementById('edit-project-closed').checked = !!currentProject.sudah_selesai;
  document.getElementById('edit-project-start').value = currentProject.tanggal_mulai || '';
  document.getElementById('edit-project-end').value = currentProject.tanggal_selesai || '';
  document.getElementById('edit-project-executor').value = currentProject.pelaksana || '';
  document.getElementById('edit-project-supervisor').value = currentProject.pengawas || '';
  openModal('edit-project-modal');
}

async function submitEditProject(e) {
  e.preventDefault();
  let projectId = getProjectId();
  const closed = document.getElementById('edit-project-closed').checked;
  try {
    await apiRequest(`/proyek/${projectId}/`, {
      method: 'PATCH',
      body: JSON.stringify({
        nama: document.getElementById('edit-project-name').value,
        deskripsi: document.getElementById('edit-project-description').value,
        lokasi: document.getElementById('edit-project-location').value,
        status: document.getElementById('edit-project-status').value,
        sudah_selesai: closed,
        tanggal_mulai: document.getElementById('edit-project-start').value,
        tanggal_selesai: document.getElementById('edit-project-end').value,
        pelaksana: document.getElementById('edit-project-executor').value,
        pengawas: document.getElementById('edit-project-supervisor').value,
      }),
    });
    closeModal('edit-project-modal');
    showToast('Proyek diperbarui', 'success');
    await loadProjectData();
  } catch (err) {
    console.error(err);
  }
}

async function handleDeleteProject() {
  if (!confirm('Hapus proyek ini? Tindakan tidak dapat dibatalkan.')) return;
  try {
    await apiRequest(`/proyek/${getProjectId()}/`, { method: 'DELETE' });
    showToast('Proyek dihapus', 'success');
    window.location.href = '/proyek/';
  } catch (e) {
    console.error(e);
  }
}

async function handleTutupProyek() {
  const isClosed = currentProject?.sudah_selesai;
  const msg = isClosed
    ? 'Buka kembali proyek ini? Status akan kembali menjadi Aktif.'
    : 'Tutup proyek ini? Proyek akan ditandai sebagai Selesai Sepenuhnya.';
  if (!confirm(msg)) return;
  try {
    await apiRequest(`/proyek/${getProjectId()}/`, {
      method: 'PATCH',
      body: JSON.stringify({
        sudah_selesai: !isClosed,
        status: isClosed ? 'Aktif' : 'Selesai',
      }),
    });
    showToast(isClosed ? 'Proyek dibuka kembali' : 'Proyek berhasil ditutup', 'success');
    await loadProjectData();
  } catch (e) {
    console.error(e);
    showToast('Gagal mengubah status proyek', 'error');
  }
}

async function downloadPdf() {
  try {
    showToast('Mengunduh PDF...', 'info');
    const res = await fetch(`/api/reports/project/${getProjectId()}/pdf/`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Gagal');
    const blob = await res.blob();
    let a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `proyek-${getProjectId()}.pdf`;
    a.click();
    showToast('PDF berhasil diunduh', 'success');
  } catch (e) {
    showToast('Gagal mengunduh PDF', 'error');
  }
}

async function downloadExcel() {
  try {
    showToast('Mengunduh Excel...', 'info');
    let res = await fetch(`/api/reports/project/${getProjectId()}/excel/`, {
      headers: { Authorization: `Bearer ${getToken()}` },
    });
    if (!res.ok) throw new Error('Gagal');
    let blob = await res.blob();
    let a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `proyek-${getProjectId()}.xlsx`;
    a.click();
    showToast('Excel berhasil diunduh', 'success');
  } catch (e) {
    showToast('Gagal mengunduh Excel', 'error');
  }
}

function openUploadModal(activityId) {
  // Bug Fix #3: findActivity mengembalikan {activity, work}, bukan langsung aktivitas
  const found = findActivity(activityId);
  if (found?.activity?.bukti_urls?.length) {
    showToast('BUKTI SUDAH ADA. Hapus bukti lama untuk mengganti.', 'error');
    return;
  }
  document.getElementById('upload-activity-id').value = activityId;
  resetUploadModal();
  openModal('upload-file-modal');
}

function resetUploadModal() {
  uploadPreviewData = null;
  ['upload-selection', 'method-file', 'method-camera', 'method-voice', 'method-preview', 'uploading-state'].forEach((id) => {
    const el = document.getElementById(id);
    if (el) el.classList.add('hidden');
  });
  document.getElementById('upload-selection')?.classList.remove('hidden');
  stopCamera();
}

function showUploadMethod(method) {
  ['upload-selection', 'method-file', 'method-camera', 'method-voice', 'method-preview', 'uploading-state'].forEach((id) => {
    document.getElementById(id)?.classList.add('hidden');
  });
  if (method === 'selection') {
    document.getElementById('upload-selection')?.classList.remove('hidden');
    stopCamera();
    return;
  }
  if (method === 'file') document.getElementById('method-file')?.classList.remove('hidden');
  if (method === 'camera') {
    document.getElementById('method-camera')?.classList.remove('hidden');
    startCamera();
  }
  if (method === 'voice') document.getElementById('method-voice')?.classList.remove('hidden');
  if (method === 'preview') document.getElementById('method-preview')?.classList.remove('hidden');
  lucide.createIcons();
}

async function startCamera() {
  try {
    cameraStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
    const video = document.getElementById('camera-preview');
    if (video) {
      video.srcObject = cameraStream;
      document.getElementById('camera-loading')?.classList.add('hidden');
    }
  } catch (e) {
    showToast('Kamera tidak tersedia', 'error');
  }
}

function stopCamera() {
  if (cameraStream) {
    cameraStream.getTracks().forEach((t) => t.stop());
    cameraStream = null;
  }
}

function capturePhoto() {
  let video = document.getElementById('camera-preview');
  let canvas = document.getElementById('camera-canvas');
  if (!video?.videoWidth) return;
  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  canvas.getContext('2d').drawImage(video, 0, 0);
  showPreview(canvas.toDataURL('image/jpeg', 0.85), 'image', 'foto.jpg');
}

function handleFileSelect(input) {
  const file = input.files?.[0];
  if (file) processFile(file);
}

function handleFileUpload(input) {
  handleFileSelect(input);
}

function processFile(file) {
  if (file.size > 5 * 1024 * 1024) {
    showToast('Maksimal 5MB', 'error');
    return;
  }
  const reader = new FileReader();
  reader.onload = () => showPreview(reader.result, file.type.startsWith('image/') ? 'image' : 'file', file.name);
  reader.readAsDataURL(file);
}

function showPreview(dataUrl, type, name) {
  uploadPreviewData = { dataUrl, type, name };
  ['preview-img', 'preview-video', 'preview-audio-container', 'preview-file-info'].forEach((id) => {
    document.getElementById(id)?.classList.add('hidden');
  });
  if (type === 'image') {
    const img = document.getElementById('preview-img');
    img.src = dataUrl;
    img.classList.remove('hidden');
  } else {
    const info = document.getElementById('preview-file-info');
    info.classList.remove('hidden');
    document.getElementById('preview-filename').textContent = name;
  }
  showUploadMethod('preview');
}

function cancelPreview() {
  uploadPreviewData = null;
  showUploadMethod('selection');
}

async function confirmUpload() {
  if (!uploadPreviewData) return;
  const activityId = document.getElementById('upload-activity-id').value;
  document.getElementById('uploading-state')?.classList.remove('hidden');
  document.getElementById('method-preview')?.classList.add('hidden');
  try {
    await apiRequest(`/aktivitas/${activityId}/`, {
      method: 'PATCH',
      body: JSON.stringify({
        bukti: [{ name: uploadPreviewData.name, data: uploadPreviewData.dataUrl }],
      }),
    });
    closeModal('upload-file-modal');
    showToast('Bukti berhasil diunggah', 'success');
    await loadProjectData();
  } catch (e) {
    console.error(e);
    showToast('Gagal mengunggah bukti', 'error');
  } finally {
    document.getElementById('uploading-state')?.classList.add('hidden');
  }
}

function toggleVideoRecording() {
  showToast('Rekam video: gunakan upload file untuk saat ini', 'info');
}

function toggleVoiceRecording() {
  showToast('Rekam suara: gunakan upload file untuk saat ini', 'info');
}
