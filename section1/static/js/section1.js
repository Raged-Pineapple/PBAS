/**
 * RNSIT PBAS Section 1 Frontend Logic
 * Supports dynamic rows, asynchronous file upload, backend calculation, and draft saving.
 */

let activeUploadTarget = null;
let currentSubmissionId = null;
let uploadedFileIds = [];

// Tab Navigation
function switchTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('border-blue-600', 'text-blue-700', 'bg-white', 'shadow-sm');
        btn.classList.add('border-transparent', 'text-slate-500');
    });

    const activeContent = document.getElementById(tabId);
    if (activeContent) activeContent.classList.remove('hidden');

    const activeBtn = document.getElementById('tab-btn-' + tabId.replace('tab-', ''));
    if (activeBtn) {
        activeBtn.classList.remove('border-transparent', 'text-slate-500');
        activeBtn.classList.add('border-blue-600', 'text-blue-700', 'bg-white', 'shadow-sm');
    }
}

// Add Feedback Row
function addFeedbackRow(sem, courseName = '', r1 = '', r2 = '', evidence = '') {
    const tbody = document.getElementById(`${sem}-feedback-tbody`);
    const rowId = `fb-${sem}-${Date.now()}-${Math.floor(Math.random()*1000)}`;
    
    const tr = document.createElement('tr');
    tr.id = rowId;
    tr.className = 'hover:bg-slate-50 transition border-b border-slate-100';
    tr.innerHTML = `
        <td class="px-4 py-2.5">
            <input type="text" value="${courseName}" placeholder="e.g. 21CS31 - Data Structures" class="fb-course-name w-full px-2.5 py-1.5 border border-slate-300 rounded text-xs focus:ring-1 focus:ring-blue-500 focus:outline-none">
        </td>
        <td class="px-4 py-2.5 text-center">
            <input type="number" step="0.01" min="0" max="100" value="${r1}" placeholder="0-100" oninput="recalcRowFeedback('${rowId}'); recalcLocal();" class="fb-r1 w-20 px-2 py-1.5 border border-slate-300 rounded text-xs text-center font-mono focus:ring-1 focus:ring-blue-500 focus:outline-none">
        </td>
        <td class="px-4 py-2.5 text-center">
            <input type="number" step="0.01" min="0" max="100" value="${r2}" placeholder="0-100" oninput="recalcRowFeedback('${rowId}'); recalcLocal();" class="fb-r2 w-20 px-2 py-1.5 border border-slate-300 rounded text-xs text-center font-mono focus:ring-1 focus:ring-blue-500 focus:outline-none">
        </td>
        <td class="px-4 py-2.5 text-center font-mono font-bold text-xs text-slate-700">
            <span class="fb-row-avg">0.00</span>%
        </td>
        <td class="px-4 py-2.5 text-center">
            <div class="flex items-center justify-center space-x-1.5">
                <button type="button" onclick="openUploadModal('${rowId}', '${sem.toUpperCase()}-Feedback')" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-xs border border-slate-300 transition flex items-center space-x-1">
                    <i class="fa-solid fa-paperclip text-slate-500"></i>
                    <span class="upload-btn-label">${evidence ? 'Attached' : 'Upload'}</span>
                </button>
                <input type="hidden" class="fb-evidence-url" value="${evidence}">
                <span class="file-indicator text-[11px] text-emerald-600 ${evidence ? '' : 'hidden'}"><i class="fa-solid fa-circle-check"></i></span>
            </div>
        </td>
        <td class="px-4 py-2.5 text-center">
            <button type="button" onclick="removeRow('${rowId}'); recalcLocal();" class="text-rose-500 hover:text-rose-700 text-sm">
                <i class="fa-solid fa-trash-can"></i>
            </button>
        </td>
    `;
    tbody.appendChild(tr);
    recalcRowFeedback(rowId);
}

function recalcRowFeedback(rowId) {
    const row = document.getElementById(rowId);
    if (!row) return;
    const r1 = parseFloat(row.querySelector('.fb-r1').value);
    const r2 = parseFloat(row.querySelector('.fb-r2').value);
    const rounds = [];
    if (!isNaN(r1)) rounds.push(r1);
    if (!isNaN(r2)) rounds.push(r2);
    const avg = rounds.length > 0 ? (rounds.reduce((a, b) => a + b, 0) / rounds.length) : 0;
    row.querySelector('.fb-row-avg').innerText = avg.toFixed(2);
}

// Add Results Row
function addResultsRow(sem, courseName = '', appeared = '', passed = '', evidence = '') {
    const tbody = document.getElementById(`${sem}-results-tbody`);
    const rowId = `res-${sem}-${Date.now()}-${Math.floor(Math.random()*1000)}`;
    
    const tr = document.createElement('tr');
    tr.id = rowId;
    tr.className = 'hover:bg-slate-50 transition border-b border-slate-100';
    tr.innerHTML = `
        <td class="px-4 py-2.5">
            <input type="text" value="${courseName}" placeholder="e.g. 21CS32 - Computer Organization" class="res-course-name w-full px-2.5 py-1.5 border border-slate-300 rounded text-xs focus:ring-1 focus:ring-blue-500 focus:outline-none">
        </td>
        <td class="px-4 py-2.5 text-center">
            <input type="number" min="0" value="${appeared}" placeholder="Total" oninput="recalcRowResult('${rowId}'); recalcLocal();" class="res-appeared w-20 px-2 py-1.5 border border-slate-300 rounded text-xs text-center font-mono focus:ring-1 focus:ring-blue-500 focus:outline-none">
        </td>
        <td class="px-4 py-2.5 text-center">
            <input type="number" min="0" value="${passed}" placeholder="Passed" oninput="recalcRowResult('${rowId}'); recalcLocal();" class="res-passed w-20 px-2 py-1.5 border border-slate-300 rounded text-xs text-center font-mono focus:ring-1 focus:ring-blue-500 focus:outline-none">
        </td>
        <td class="px-4 py-2.5 text-center font-mono font-bold text-xs text-slate-700">
            <span class="res-row-pct">0.00</span>%
        </td>
        <td class="px-4 py-2.5 text-center">
            <div class="flex items-center justify-center space-x-1.5">
                <button type="button" onclick="openUploadModal('${rowId}', '${sem.toUpperCase()}-Results')" class="px-2.5 py-1 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-xs border border-slate-300 transition flex items-center space-x-1">
                    <i class="fa-solid fa-paperclip text-slate-500"></i>
                    <span class="upload-btn-label">${evidence ? 'Attached' : 'Upload'}</span>
                </button>
                <input type="hidden" class="res-evidence-url" value="${evidence}">
                <span class="file-indicator text-[11px] text-emerald-600 ${evidence ? '' : 'hidden'}"><i class="fa-solid fa-circle-check"></i></span>
            </div>
        </td>
        <td class="px-4 py-2.5 text-center">
            <button type="button" onclick="removeRow('${rowId}'); recalcLocal();" class="text-rose-500 hover:text-rose-700 text-sm">
                <i class="fa-solid fa-trash-can"></i>
            </button>
        </td>
    `;
    tbody.appendChild(tr);
    recalcRowResult(rowId);
}

function recalcRowResult(rowId) {
    const row = document.getElementById(rowId);
    if (!row) return;
    const appeared = parseFloat(row.querySelector('.res-appeared').value) || 0;
    const passed = parseFloat(row.querySelector('.res-passed').value) || 0;
    const pct = appeared > 0 ? ((passed / appeared) * 100) : 0;
    row.querySelector('.res-row-pct').innerText = pct.toFixed(2);
}

function removeRow(rowId) {
    const el = document.getElementById(rowId);
    if (el) el.remove();
}

// Add Rows for Sub-Components C (ii to ix)
function addOwnSyllabusRow(title = '', evidence = '') {
    const container = document.getElementById('container-c-ii');
    const id = `c-ii-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 text-xs';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="Course Title & Code" class="c-ii-title flex-1 px-2.5 py-1.5 border border-slate-300 rounded focus:ring-1 focus:ring-blue-500 focus:outline-none">
        <button type="button" onclick="openUploadModal('${id}', 'C_II_Syllabus')" class="px-2 py-1.5 bg-slate-100 hover:bg-slate-200 border border-slate-300 rounded text-slate-700 flex items-center space-x-1">
            <i class="fa-solid fa-paperclip text-slate-500"></i>
            <span class="upload-btn-label">Proof</span>
        </button>
        <input type="hidden" class="c-ii-evidence" value="${evidence}">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500 hover:text-rose-700 p-1">
            <i class="fa-solid fa-times"></i>
        </button>
    `;
    container.appendChild(div);
    recalcLocal();
}

function addFundedActivityRow(title = '', role = 'PI', amount = '100000', evidence = '') {
    const container = document.getElementById('container-c-iii');
    const id = `c-iii-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'space-y-1.5 p-2 bg-slate-50 rounded-lg border border-slate-200 text-xs';
    div.innerHTML = `
        <div class="flex items-center space-x-2">
            <input type="text" value="${title}" placeholder="Event Title (FDP/SDP/Conf)" class="c-iii-title flex-1 px-2 py-1 border border-slate-300 rounded">
            <select class="c-iii-role px-2 py-1 border border-slate-300 rounded bg-white" onchange="recalcLocal()">
                <option value="PI" ${role === 'PI' ? 'selected' : ''}>PI (2/₹1L)</option>
                <option value="Co-PI" ${role === 'Co-PI' ? 'selected' : ''}>Co-PI (1/₹1L)</option>
            </select>
        </div>
        <div class="flex items-center space-x-2">
            <input type="number" step="10000" min="100000" value="${amount}" placeholder="Funding in ₹" oninput="recalcLocal()" class="c-iii-amount w-32 px-2 py-1 border border-slate-300 rounded font-mono">
            <button type="button" onclick="openUploadModal('${id}', 'C_III_Funding')" class="px-2 py-1 bg-white border border-slate-300 rounded text-slate-700 flex items-center space-x-1">
                <i class="fa-solid fa-paperclip text-slate-500"></i>
                <span class="upload-btn-label">Sanction Order</span>
            </button>
            <input type="hidden" class="c-iii-evidence" value="${evidence}">
            <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500 hover:text-rose-700 ml-auto">
                <i class="fa-solid fa-trash-can"></i>
            </button>
        </div>
    `;
    container.appendChild(div);
    recalcLocal();
}

function addOrgFdpRow(title = '', nirfInst = '', amount = '100000', evidence = '') {
    const container = document.getElementById('container-c-iv');
    const id = `c-iv-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'p-2 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1.5';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="FDP Title" class="c-iv-title w-full px-2 py-1 border border-slate-300 rounded">
        <div class="flex items-center space-x-2">
            <input type="text" value="${nirfInst}" placeholder="NIRF / National Host Inst." class="c-iv-inst flex-1 px-2 py-1 border border-slate-300 rounded">
            <button type="button" onclick="openUploadModal('${id}', 'C_IV_FDP')" class="px-2 py-1 bg-white border border-slate-300 rounded text-slate-700 flex items-center space-x-1">
                <i class="fa-solid fa-paperclip text-slate-500"></i>
                <span class="upload-btn-label">Brochure/Proof</span>
            </button>
            <input type="hidden" class="c-iv-evidence" value="${evidence}">
            <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500 hover:text-rose-700">
                <i class="fa-solid fa-trash-can"></i>
            </button>
        </div>
    `;
    container.appendChild(div);
    recalcLocal();
}

function addOnlineCompletedRow(title = '', hours = '30', evidence = '') {
    const container = document.getElementById('container-c-v');
    const id = `c-v-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 text-xs';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="Course Title (Coursera/Udemy/etc)" class="c-v-title flex-1 px-2.5 py-1.5 border border-slate-300 rounded">
        <input type="number" min="30" value="${hours}" placeholder="Hours" oninput="recalcLocal()" class="c-v-hours w-20 px-2 py-1.5 border border-slate-300 rounded text-center font-mono">
        <button type="button" onclick="openUploadModal('${id}', 'C_V_Certificate')" class="px-2 py-1.5 bg-slate-100 hover:bg-slate-200 border border-slate-300 rounded text-slate-700 flex items-center space-x-1">
            <i class="fa-solid fa-paperclip text-slate-500"></i>
            <span class="upload-btn-label">Cert</span>
        </button>
        <input type="hidden" class="c-v-evidence" value="${evidence}">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500 hover:text-rose-700 p-1">
            <i class="fa-solid fa-times"></i>
        </button>
    `;
    container.appendChild(div);
    recalcLocal();
}

function addNptelRow(title = '', weeks = '8', grade = 'elite', evidence = '') {
    const container = document.getElementById('container-c-vi');
    const id = `c-vi-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'p-2 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1.5';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="NPTEL Course Title" class="c-vi-title w-full px-2 py-1 border border-slate-300 rounded">
        <div class="flex items-center space-x-2">
            <select class="c-vi-grade px-2 py-1 border border-slate-300 rounded bg-white flex-1" onchange="recalcLocal()">
                <option value="completed" ${grade === 'completed' ? 'selected' : ''}>Completed (5 marks)</option>
                <option value="elite" ${grade === 'elite' ? 'selected' : ''}>Elite (6 marks)</option>
                <option value="elite_silver" ${grade === 'elite_silver' ? 'selected' : ''}>Elite + Silver (8 marks)</option>
                <option value="elite_gold" ${grade === 'elite_gold' ? 'selected' : ''}>Elite + Gold (10 marks)</option>
            </select>
            <input type="number" min="4" value="${weeks}" placeholder="Wks" oninput="recalcLocal()" class="c-vi-weeks w-16 px-2 py-1 border border-slate-300 rounded text-center font-mono">
            <button type="button" onclick="openUploadModal('${id}', 'C_VI_NPTEL')" class="px-2 py-1 bg-white border border-slate-300 rounded text-slate-700 flex items-center space-x-1">
                <i class="fa-solid fa-paperclip text-slate-500"></i>
                <span class="upload-btn-label">Cert</span>
            </button>
            <input type="hidden" class="c-vi-evidence" value="${evidence}">
            <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500 hover:text-rose-700">
                <i class="fa-solid fa-trash-can"></i>
            </button>
        </div>
    `;
    container.appendChild(div);
    recalcLocal();
}

function addCourseDevRow(title = '', ptype = 'external', evidence = '') {
    const container = document.getElementById('container-c-vii');
    const id = `c-vii-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 text-xs';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="Developed Course Title" class="c-vii-title flex-1 px-2.5 py-1.5 border border-slate-300 rounded">
        <select class="c-vii-ptype px-2 py-1.5 border border-slate-300 rounded bg-white" onchange="recalcLocal()">
            <option value="external" ${ptype === 'external' ? 'selected' : ''}>External (10)</option>
            <option value="rnsit_youtube" ${ptype === 'rnsit_youtube' ? 'selected' : ''}>RNSIT YouTube (5)</option>
        </select>
        <button type="button" onclick="openUploadModal('${id}', 'C_VII_CourseDev')" class="px-2 py-1.5 bg-slate-100 hover:bg-slate-200 border border-slate-300 rounded text-slate-700 flex items-center space-x-1">
            <i class="fa-solid fa-paperclip text-slate-500"></i>
            <span class="upload-btn-label">Proof</span>
        </button>
        <input type="hidden" class="c-vii-evidence" value="${evidence}">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500 hover:text-rose-700 p-1">
            <i class="fa-solid fa-times"></i>
        </button>
    `;
    container.appendChild(div);
    recalcLocal();
}

function addResourcePersonRow(title = '', rtype = 'internship', hours = '18', evidence = '') {
    const container = document.getElementById('container-c-viii');
    const id = `c-viii-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'p-2 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1.5';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="Internship / Course Title" class="c-viii-title w-full px-2 py-1 border border-slate-300 rounded">
        <div class="flex items-center space-x-2">
            <select class="c-viii-type px-2 py-1 border border-slate-300 rounded bg-white flex-1" onchange="recalcLocal()">
                <option value="internship" ${rtype === 'internship' ? 'selected' : ''}>Summer Internship (5)</option>
                <option value="professional" ${rtype === 'professional' ? 'selected' : ''}>Prof. Course (10)</option>
            </select>
            <input type="number" min="18" value="${hours}" placeholder="Hrs" oninput="recalcLocal()" class="c-viii-hours w-16 px-2 py-1 border border-slate-300 rounded text-center font-mono">
            <button type="button" onclick="openUploadModal('${id}', 'C_VIII_Resource')" class="px-2 py-1 bg-white border border-slate-300 rounded text-slate-700 flex items-center space-x-1">
                <i class="fa-solid fa-paperclip text-slate-500"></i>
                <span class="upload-btn-label">Cert</span>
            </button>
            <input type="hidden" class="c-viii-evidence" value="${evidence}">
            <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500 hover:text-rose-700">
                <i class="fa-solid fa-trash-can"></i>
            </button>
        </div>
    `;
    container.appendChild(div);
    recalcLocal();
}

function addAiToolRow(toolName = '', evidence = '') {
    const container = document.getElementById('container-c-ix');
    const id = `c-ix-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 text-xs';
    div.innerHTML = `
        <input type="text" value="${toolName}" placeholder="e.g. ChatGPT, GitHub Copilot" class="c-ix-title flex-1 px-2.5 py-1.5 border border-slate-300 rounded">
        <button type="button" onclick="openUploadModal('${id}', 'C_IX_AI')" class="px-2 py-1.5 bg-slate-100 hover:bg-slate-200 border border-slate-300 rounded text-slate-700 flex items-center space-x-1">
            <i class="fa-solid fa-paperclip text-slate-500"></i>
            <span class="upload-btn-label">Evidence</span>
        </button>
        <input type="hidden" class="c-ix-evidence" value="${evidence}">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500 hover:text-rose-700 p-1">
            <i class="fa-solid fa-times"></i>
        </button>
    `;
    container.appendChild(div);
    recalcLocal();
}

// Upload Modal Logic
function openUploadModal(targetRowId, componentCode) {
    activeUploadTarget = { rowId: targetRowId, component: componentCode };
    document.getElementById('modal-component-desc').innerText = `Uploading evidence document for: ${componentCode}`;
    document.getElementById('modal-selected-filename').innerText = '';
    document.getElementById('modal-file-input').value = '';
    document.getElementById('upload-modal').classList.remove('hidden');
}

function closeUploadModal() {
    document.getElementById('upload-modal').classList.add('hidden');
    activeUploadTarget = null;
}

function handleModalFileSelected(input) {
    if (input.files && input.files[0]) {
        document.getElementById('modal-selected-filename').innerText = input.files[0].name;
    }
}

function executeUpload() {
    const fileInput = document.getElementById('modal-file-input');
    if (!fileInput.files || !fileInput.files[0]) {
        alert('Please select a file first.');
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('component_code', activeUploadTarget.component);

    const uploadBtn = document.getElementById('modal-upload-btn');
    uploadBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Uploading...';
    uploadBtn.disabled = true;

    fetch('/api/upload/', {
        method: 'POST',
        body: formData
    })
    .then(r => r.json())
    .then(data => {
        uploadBtn.innerHTML = '<i class="fa-solid fa-upload"></i> <span>Confirm Upload</span>';
        uploadBtn.disabled = false;

        if (data.success) {
            uploadedFileIds.push(data.file_id);
            // Update row indicator
            if (activeUploadTarget && activeUploadTarget.rowId) {
                const row = document.getElementById(activeUploadTarget.rowId);
                if (row) {
                    const hiddenInput = row.querySelector('input[type="hidden"]');
                    if (hiddenInput) hiddenInput.value = data.file_url;
                    const label = row.querySelector('.upload-btn-label');
                    if (label) label.innerText = 'Attached';
                    const indicator = row.querySelector('.file-indicator');
                    if (indicator) indicator.classList.remove('hidden');
                }
            }
            showToast('Document uploaded successfully: ' + data.file_name);
            closeUploadModal();
        } else {
            alert('Upload failed: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(err => {
        uploadBtn.innerHTML = '<i class="fa-solid fa-upload"></i> <span>Confirm Upload</span>';
        uploadBtn.disabled = false;
        alert('Upload network error: ' + err);
    });
}

// Gather Full Form Payload
function gatherPayload() {
    const payload = {
        odd_feedback_courses: [],
        even_feedback_courses: [],
        odd_results_courses: [],
        even_results_courses: [],
        other_tlp_c: {
            c_ii_own_syllabus: [],
            c_iii_funded_activities: [],
            c_iv_org_fdp: [],
            c_v_online_completed: [],
            c_vi_nptel: [],
            c_vii_courses_developed: [],
            c_viii_resource_person: [],
            c_ix_ai_tools: [],
            c_x_tlp_methods: []
        }
    };

    // Odd Feedback
    document.querySelectorAll('#odd-feedback-tbody tr').forEach(tr => {
        payload.odd_feedback_courses.push({
            course_name: tr.querySelector('.fb-course-name')?.value || '',
            round_1: tr.querySelector('.fb-r1')?.value || null,
            round_2: tr.querySelector('.fb-r2')?.value || null,
            evidence_file: tr.querySelector('.fb-evidence-url')?.value || ''
        });
    });

    // Even Feedback
    document.querySelectorAll('#even-feedback-tbody tr').forEach(tr => {
        payload.even_feedback_courses.push({
            course_name: tr.querySelector('.fb-course-name')?.value || '',
            round_1: tr.querySelector('.fb-r1')?.value || null,
            round_2: tr.querySelector('.fb-r2')?.value || null,
            evidence_file: tr.querySelector('.fb-evidence-url')?.value || ''
        });
    });

    // Odd Results
    document.querySelectorAll('#odd-results-tbody tr').forEach(tr => {
        payload.odd_results_courses.push({
            course_name: tr.querySelector('.res-course-name')?.value || '',
            appeared: tr.querySelector('.res-appeared')?.value || 0,
            passed: tr.querySelector('.res-passed')?.value || 0,
            evidence_file: tr.querySelector('.res-evidence-url')?.value || ''
        });
    });

    // Even Results
    document.querySelectorAll('#even-results-tbody tr').forEach(tr => {
        payload.even_results_courses.push({
            course_name: tr.querySelector('.res-course-name')?.value || '',
            appeared: tr.querySelector('.res-appeared')?.value || 0,
            passed: tr.querySelector('.res-passed')?.value || 0,
            evidence_file: tr.querySelector('.res-evidence-url')?.value || ''
        });
    });

    // C(ii) Own Syllabus
    document.querySelectorAll('#container-c-ii > div').forEach(div => {
        payload.other_tlp_c.c_ii_own_syllabus.push({
            title: div.querySelector('.c-ii-title')?.value || '',
            evidence: div.querySelector('.c-ii-evidence')?.value || ''
        });
    });

    // C(iii) Funded Activities
    document.querySelectorAll('#container-c-iii > div').forEach(div => {
        payload.other_tlp_c.c_iii_funded_activities.push({
            title: div.querySelector('.c-iii-title')?.value || '',
            role: div.querySelector('.c-iii-role')?.value || 'PI',
            funding_amount: div.querySelector('.c-iii-amount')?.value || 0,
            evidence: div.querySelector('.c-iii-evidence')?.value || ''
        });
    });

    // C(iv) Org FDP
    document.querySelectorAll('#container-c-iv > div').forEach(div => {
        payload.other_tlp_c.c_iv_org_fdp.push({
            title: div.querySelector('.c-iv-title')?.value || '',
            institution: div.querySelector('.c-iv-inst')?.value || '',
            evidence: div.querySelector('.c-iv-evidence')?.value || '',
            is_eligible: true
        });
    });

    // C(v) Online Completed
    document.querySelectorAll('#container-c-v > div').forEach(div => {
        payload.other_tlp_c.c_v_online_completed.push({
            title: div.querySelector('.c-v-title')?.value || '',
            duration_hours: div.querySelector('.c-v-hours')?.value || 0,
            evidence: div.querySelector('.c-v-evidence')?.value || ''
        });
    });

    // C(vi) NPTEL
    document.querySelectorAll('#container-c-vi > div').forEach(div => {
        payload.other_tlp_c.c_vi_nptel.push({
            title: div.querySelector('.c-vi-title')?.value || '',
            grade_type: div.querySelector('.c-vi-grade')?.value || 'completed',
            duration_weeks: div.querySelector('.c-vi-weeks')?.value || 8,
            evidence: div.querySelector('.c-vi-evidence')?.value || ''
        });
    });

    // C(vii) Courses Developed
    document.querySelectorAll('#container-c-vii > div').forEach(div => {
        payload.other_tlp_c.c_vii_courses_developed.push({
            title: div.querySelector('.c-vii-title')?.value || '',
            platform_type: div.querySelector('.c-vii-ptype')?.value || 'external',
            evidence: div.querySelector('.c-vii-evidence')?.value || ''
        });
    });

    // C(viii) Resource Person
    document.querySelectorAll('#container-c-viii > div').forEach(div => {
        payload.other_tlp_c.c_viii_resource_person.push({
            title: div.querySelector('.c-viii-title')?.value || '',
            type: div.querySelector('.c-viii-type')?.value || 'internship',
            hours: div.querySelector('.c-viii-hours')?.value || 18,
            evidence: div.querySelector('.c-viii-evidence')?.value || ''
        });
    });

    // C(ix) AI Tools
    document.querySelectorAll('#container-c-ix > div').forEach(div => {
        payload.other_tlp_c.c_ix_ai_tools.push({
            tool_name: div.querySelector('.c-ix-title')?.value || '',
            evidence: div.querySelector('.c-ix-evidence')?.value || ''
        });
    });

    // C(x) Innovative Methods
    document.querySelectorAll('input[name="innovative_method"]:checked').forEach(cb => {
        payload.other_tlp_c.c_x_tlp_methods.push(cb.value);
    });

    return payload;
}

// Local live calculation for instant feedback
function recalcLocal() {
    // Quick preview calculations before backend confirmation
    const payload = gatherPayload();
    // Count methods
    const methodCount = payload.other_tlp_c.c_x_tlp_methods.length;
    const methodScore = Math.min(methodCount * 2.5, 10);
    document.getElementById('score-c-x').innerText = `${methodScore} / 10`;
}

// Backend API Calculation
function calculateBackend() {
    const payload = gatherPayload();

    fetch('/api/section1/calculate/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(res => {
        if (res.success) {
            updateUIWithCalculation(res.data);
            showToast('Calculated in backend successfully!');
        } else {
            alert('Calculation error: ' + res.error);
        }
    })
    .catch(err => {
        console.error(err);
        alert('Network error during backend calculation.');
    });
}

function updateUIWithCalculation(data) {
    const fa = data.feedback_a;
    const rb = data.results_b;
    const ab = data.total_ab;
    const tc = data.other_tlp_c;
    const total = data.section1_total;

    // Header & Badges
    document.getElementById('header-score').innerText = total.final_score;
    document.getElementById('badge-marks-a').innerText = fa.marks_awarded;
    document.getElementById('badge-marks-b').innerText = rb.marks_awarded;
    document.getElementById('foot-a').innerText = fa.marks_awarded;
    document.getElementById('foot-b').innerText = rb.marks_awarded;
    document.getElementById('badge-total-ab').innerText = `${ab.score_awarded} / 50`;
    document.getElementById('badge-total-c').innerText = `${tc.total_c_score} marks`;

    // A1 / A2 labels
    document.getElementById('label-a1-avg').innerText = `${fa.a1_odd_sem_average}%`;
    document.getElementById('label-a2-avg').innerText = `${fa.a2_even_sem_average}%`;

    // B1 / B2 labels
    document.getElementById('label-b1-avg').innerText = `${rb.b1_odd_sem_average}%`;
    document.getElementById('label-b2-avg').innerText = `${rb.b2_even_sem_average}%`;

    // C Subcomponents Scores
    const comp = tc.components;
    if (comp.c_ii) document.getElementById('score-c-ii').innerText = `${comp.c_ii.score} / 10`;
    if (comp.c_iii) document.getElementById('score-c-iii').innerText = `${comp.c_iii.score} / 10`;
    if (comp.c_iv) document.getElementById('score-c-iv').innerText = `${comp.c_iv.score} / 10`;
    if (comp.c_v) document.getElementById('score-c-v').innerText = `${comp.c_v.score} / 10`;
    if (comp.c_vi) document.getElementById('score-c-vi').innerText = `${comp.c_vi.score} / 10`;
    if (comp.c_vii) document.getElementById('score-c-vii').innerText = `${comp.c_vii.score} / 10`;
    if (comp.c_viii) document.getElementById('score-c-viii').innerText = `${comp.c_viii.score} / 10`;
    if (comp.c_ix) document.getElementById('score-c-ix').innerText = `${comp.c_ix.score} / 5`;
    if (comp.c_x) document.getElementById('score-c-x').innerText = `${comp.c_x.score} / 10`;

    // Summary Tab
    document.getElementById('sum-marks-a').innerText = fa.marks_awarded;
    document.getElementById('sum-a1-avg').innerText = fa.a1_odd_sem_average;
    document.getElementById('sum-a2-avg').innerText = fa.a2_even_sem_average;
    document.getElementById('sum-a-comb').innerText = fa.combined_feedback_average;

    document.getElementById('sum-marks-b').innerText = rb.marks_awarded;
    document.getElementById('sum-b1-avg').innerText = rb.b1_odd_sem_average;
    document.getElementById('sum-b2-avg').innerText = rb.b2_even_sem_average;
    document.getElementById('sum-b-comb').innerText = rb.combined_results_average;

    document.getElementById('sum-marks-c').innerText = tc.total_c_score;
    document.getElementById('sum-final-score').innerText = total.final_score;
}

// Save Submission to Database
function saveSubmission() {
    const payload = gatherPayload();
    const data = {
        submission_id: currentSubmissionId,
        faculty_name: document.getElementById('faculty_name').value,
        employee_id: document.getElementById('employee_id').value,
        department: document.getElementById('department').value,
        academic_year: document.getElementById('academic_year').value,
        payload: payload,
        file_ids: uploadedFileIds,
        status: 'SUBMITTED'
    };

    fetch('/api/section1/save/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(r => r.json())
    .then(res => {
        if (res.success) {
            currentSubmissionId = res.submission_id;
            updateUIWithCalculation(res.result);
            showToast(`Saved draft successfully! Final Score: ${res.final_score}/70`);
        } else {
            alert('Save failed: ' + res.error);
        }
    })
    .catch(err => {
        alert('Network error saving submission: ' + err);
    });
}

// Toast notification helper
function showToast(msg) {
    const toast = document.getElementById('toast');
    document.getElementById('toast-msg').innerText = msg;
    toast.classList.remove('hidden');
    setTimeout(() => {
        toast.classList.add('hidden');
    }, 3500);
}

// Initial seed sample data
document.addEventListener('DOMContentLoaded', () => {
    // Add default initial sample courses matching the PBAS document
    addFeedbackRow('odd', '21CS51 - Management & Entrepreneurship', 88.5, 91.0);
    addFeedbackRow('odd', '21CS52 - Computer Networks', 82.0, 86.5);
    addFeedbackRow('even', '21CS61 - Software Engineering', 90.0, 93.0);

    addResultsRow('odd', '21CS51 - Management & Entrepreneurship', 62, 59);
    addResultsRow('even', '21CS61 - Software Engineering', 60, 57);

    addOwnSyllabusRow('Cloud Computing & DevOps (Core Syllabus)');
    addOnlineCompletedRow('Coursera - Machine Learning with Python', 36);
    addNptelRow('Cloud Computing by IIT Kharagpur', 8, 'elite_silver');
    addAiToolRow('GitHub Copilot (Assisted Code Reviews)');

    // Trigger initial calculation
    setTimeout(() => {
        calculateBackend();
    }, 300);
});
