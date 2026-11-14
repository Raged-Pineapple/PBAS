/**
 * RNSIT PBAS Digital Portal - Complete Frontend Logic for All Sections
 * Seamless multi-section navigation, asynchronous uploads & live backend calculation
 */

let activeUploadTarget = null;
let currentSubmissionId = null;
let uploadedFileIds = [];

// ==========================================
// SECTION & TAB NAVIGATION
// ==========================================
function switchSection(secId) {
    document.querySelectorAll('.section-container').forEach(el => el.classList.add('hidden'));
    document.querySelectorAll('.sec-nav-btn').forEach(btn => {
        btn.classList.remove('bg-blue-600', 'text-white', 'shadow-sm');
        btn.classList.add('text-slate-600');
    });

    const targetSec = document.getElementById(secId);
    if (targetSec) targetSec.classList.remove('hidden');

    const activeBtn = document.getElementById('nav-btn-' + secId);
    if (activeBtn) {
        activeBtn.classList.remove('text-slate-600');
        activeBtn.classList.add('bg-blue-600', 'text-white', 'shadow-sm');
    }
    window.scrollTo({ top: 120, behavior: 'smooth' });
}

function switchSec1Tab(tabId) {
    document.querySelectorAll('.sec1-tab-content').forEach(el => el.classList.add('hidden'));
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

// ==========================================
// SECTION I DYNAMIC ROWS
// ==========================================
function addFeedbackRow(sem, courseName = '', r1 = '', r2 = '', evidence = '') {
    const tbody = document.getElementById(`${sem}-feedback-tbody`);
    const rowId = `fb-${sem}-${Date.now()}-${Math.floor(Math.random()*1000)}`;
    const tr = document.createElement('tr');
    tr.id = rowId;
    tr.className = 'hover:bg-slate-50 transition border-b border-slate-100';
    tr.innerHTML = `
        <td class="px-3 py-2">
            <input type="text" value="${courseName}" placeholder="Course Name & Code" class="fb-course-name w-full px-2 py-1 border border-slate-300 rounded text-xs focus:ring-1 focus:ring-blue-500">
        </td>
        <td class="px-3 py-2 text-center">
            <input type="number" step="0.01" min="0" max="100" value="${r1}" placeholder="0-100" oninput="recalcRowFeedback('${rowId}'); recalcLocal();" class="fb-r1 w-16 px-1.5 py-1 border border-slate-300 rounded text-xs text-center font-mono">
        </td>
        <td class="px-3 py-2 text-center">
            <input type="number" step="0.01" min="0" max="100" value="${r2}" placeholder="0-100" oninput="recalcRowFeedback('${rowId}'); recalcLocal();" class="fb-r2 w-16 px-1.5 py-1 border border-slate-300 rounded text-xs text-center font-mono">
        </td>
        <td class="px-3 py-2 text-center font-mono font-bold text-xs text-slate-700">
            <span class="fb-row-avg">0.00</span>%
        </td>
        <td class="px-3 py-2 text-center">
            <div class="flex items-center justify-center space-x-1">
                <button type="button" onclick="openUploadModal('${rowId}', '${sem.toUpperCase()}-Feedback')" class="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[11px] border border-slate-300 transition">
                    <span class="upload-btn-label">${evidence ? 'Attached' : 'Proof'}</span>
                </button>
                <input type="hidden" class="fb-evidence-url" value="${evidence}">
                <span class="file-indicator text-emerald-600 text-xs ${evidence ? '' : 'hidden'}"><i class="fa-solid fa-circle-check"></i></span>
            </div>
        </td>
        <td class="px-3 py-2 text-center">
            <button type="button" onclick="removeRow('${rowId}'); recalcLocal();" class="text-rose-500 hover:text-rose-700 text-xs"><i class="fa-solid fa-trash-can"></i></button>
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

function addResultsRow(sem, courseName = '', appeared = '', passed = '', evidence = '') {
    const tbody = document.getElementById(`${sem}-results-tbody`);
    const rowId = `res-${sem}-${Date.now()}-${Math.floor(Math.random()*1000)}`;
    const tr = document.createElement('tr');
    tr.id = rowId;
    tr.className = 'hover:bg-slate-50 transition border-b border-slate-100';
    tr.innerHTML = `
        <td class="px-3 py-2">
            <input type="text" value="${courseName}" placeholder="Course Name & Code" class="res-course-name w-full px-2 py-1 border border-slate-300 rounded text-xs focus:ring-1 focus:ring-blue-500">
        </td>
        <td class="px-3 py-2 text-center">
            <input type="number" min="0" value="${appeared}" placeholder="Total" oninput="recalcRowResult('${rowId}'); recalcLocal();" class="res-appeared w-16 px-1.5 py-1 border border-slate-300 rounded text-xs text-center font-mono">
        </td>
        <td class="px-3 py-2 text-center">
            <input type="number" min="0" value="${passed}" placeholder="Passed" oninput="recalcRowResult('${rowId}'); recalcLocal();" class="res-passed w-16 px-1.5 py-1 border border-slate-300 rounded text-xs text-center font-mono">
        </td>
        <td class="px-3 py-2 text-center font-mono font-bold text-xs text-slate-700">
            <span class="res-row-pct">0.00</span>%
        </td>
        <td class="px-3 py-2 text-center">
            <div class="flex items-center justify-center space-x-1">
                <button type="button" onclick="openUploadModal('${rowId}', '${sem.toUpperCase()}-Results')" class="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded text-[11px] border border-slate-300 transition">
                    <span class="upload-btn-label">${evidence ? 'Attached' : 'Proof'}</span>
                </button>
                <input type="hidden" class="res-evidence-url" value="${evidence}">
                <span class="file-indicator text-emerald-600 text-xs ${evidence ? '' : 'hidden'}"><i class="fa-solid fa-circle-check"></i></span>
            </div>
        </td>
        <td class="px-3 py-2 text-center">
            <button type="button" onclick="removeRow('${rowId}'); recalcLocal();" class="text-rose-500 hover:text-rose-700 text-xs"><i class="fa-solid fa-trash-can"></i></button>
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

// Section I Components C
function addOwnSyllabusRow(title = '') {
    createSimpleRow('container-c-ii', title, 'Course developed', 'C_II_Syllabus');
}
function addFundedActivityRow(title = '', role = 'PI', amt = '100000') {
    const container = document.getElementById('container-c-iii');
    const id = `c-iii-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 text-xs p-1.5 bg-slate-50 border rounded';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="Activity Title" class="c-iii-title flex-1 px-2 py-1 border rounded">
        <select class="c-iii-role px-1.5 py-1 border rounded bg-white" onchange="recalcLocal()">
            <option value="PI" ${role === 'PI' ? 'selected' : ''}>PI</option>
            <option value="Co-PI" ${role === 'Co-PI' ? 'selected' : ''}>Co-PI</option>
        </select>
        <input type="number" step="10000" min="100000" value="${amt}" placeholder="₹" oninput="recalcLocal()" class="c-iii-amt w-20 px-1 py-1 border rounded font-mono">
        <button type="button" onclick="openUploadModal('${id}', 'C_III_Sanction')" class="px-2 py-1 bg-white border rounded text-[11px]">Proof</button>
        <input type="hidden" class="c-iii-evidence">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500 text-xs"><i class="fa-solid fa-times"></i></button>
    `;
    container.appendChild(div);
    recalcLocal();
}
function addOrgFdpRow(title = '', inst = '') {
    createSimpleRow('container-c-iv', title, 'FDP Title & NIRF Partner', 'C_IV_FDP');
}
function addOnlineCompletedRow(title = '', hrs = '35') {
    createTwoInputRow('container-c-v', title, hrs, 'Course Title', 'Hours (≥30)', 'C_V_Cert');
}
function addNptelRow(title = '', grade = 'elite', weeks = '8') {
    const container = document.getElementById('container-c-vi');
    const id = `c-vi-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 text-xs p-1.5 bg-slate-50 border rounded';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="NPTEL Course" class="c-vi-title flex-1 px-2 py-1 border rounded">
        <select class="c-vi-grade px-1.5 py-1 border rounded bg-white" onchange="recalcLocal()">
            <option value="completed" ${grade === 'completed' ? 'selected' : ''}>Completed (5)</option>
            <option value="elite" ${grade === 'elite' ? 'selected' : ''}>Elite (6)</option>
            <option value="elite_silver" ${grade === 'elite_silver' ? 'selected' : ''}>Elite+Silver (8)</option>
            <option value="elite_gold" ${grade === 'elite_gold' ? 'selected' : ''}>Elite+Gold (10)</option>
        </select>
        <button type="button" onclick="openUploadModal('${id}', 'C_VI_Cert')" class="px-2 py-1 bg-white border rounded text-[11px]">Cert</button>
        <input type="hidden" class="c-vi-evidence">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500 text-xs"><i class="fa-solid fa-times"></i></button>
    `;
    container.appendChild(div);
    recalcLocal();
}
function addCourseDevRow(title = '', ptype = 'external') {
    const container = document.getElementById('container-c-vii');
    const id = `c-vii-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 text-xs p-1.5 bg-slate-50 border rounded';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="Course Title" class="c-vii-title flex-1 px-2 py-1 border rounded">
        <select class="c-vii-ptype px-1.5 py-1 border rounded bg-white" onchange="recalcLocal()">
            <option value="external" ${ptype === 'external' ? 'selected' : ''}>External (10)</option>
            <option value="rnsit_youtube" ${ptype === 'rnsit_youtube' ? 'selected' : ''}>RNSIT YouTube (5)</option>
        </select>
        <button type="button" onclick="openUploadModal('${id}', 'C_VII_Proof')" class="px-2 py-1 bg-white border rounded text-[11px]">Proof</button>
        <input type="hidden" class="c-vii-evidence">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500 text-xs"><i class="fa-solid fa-times"></i></button>
    `;
    container.appendChild(div);
    recalcLocal();
}
function addResourcePersonRow(title = '', type = 'internship') {
    const container = document.getElementById('container-c-viii');
    const id = `c-viii-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 text-xs p-1.5 bg-slate-50 border rounded';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="Internship / Course" class="c-viii-title flex-1 px-2 py-1 border rounded">
        <select class="c-viii-type px-1.5 py-1 border rounded bg-white" onchange="recalcLocal()">
            <option value="internship" ${type === 'internship' ? 'selected' : ''}>Summer Intern (5)</option>
            <option value="professional" ${type === 'professional' ? 'selected' : ''}>Prof. Course (10)</option>
        </select>
        <button type="button" onclick="openUploadModal('${id}', 'C_VIII_Cert')" class="px-2 py-1 bg-white border rounded text-[11px]">Cert</button>
        <input type="hidden" class="c-viii-evidence">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500 text-xs"><i class="fa-solid fa-times"></i></button>
    `;
    container.appendChild(div);
    recalcLocal();
}
function addAiToolRow(name = '') {
    createSimpleRow('container-c-ix', name, 'e.g. ChatGPT, GitHub Copilot', 'C_IX_AI');
}

// ==========================================
// SECTION II DYNAMIC ROWS (PUBLICATIONS & R&D)
// ==========================================
function addPubRow(title = '', category = 'q1', order = 1, doi = '') {
    const container = document.getElementById('container-sec2-pub');
    const id = `sec2-pub-${Date.now()}-${Math.floor(Math.random()*1000)}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'p-2 bg-slate-50 rounded-lg border border-slate-200 text-xs space-y-1.5';
    div.innerHTML = `
        <div class="flex items-center space-x-2">
            <input type="text" value="${title}" placeholder="Paper Title with RNSIT Affiliation" class="sec2-pub-title flex-1 px-2 py-1 border rounded font-medium">
            <select class="sec2-pub-cat px-2 py-1 border rounded bg-white font-semibold text-blue-700" onchange="recalcLocal()">
                <option value="q1" ${category === 'q1' ? 'selected' : ''}>Q1 Journal (20 / 10)</option>
                <option value="q2" ${category === 'q2' ? 'selected' : ''}>Q2 Journal (15 / 7.5)</option>
                <option value="q3" ${category === 'q3' ? 'selected' : ''}>Q3 Journal (12.5 / 6.25)</option>
                <option value="q4" ${category === 'q4' ? 'selected' : ''}>Q4 / Scopus / WoS (10 / 5)</option>
                <option value="conf" ${category === 'conf' ? 'selected' : ''}>Indexed Conf (5 / 2.5)</option>
            </select>
        </div>
        <div class="flex items-center space-x-2">
            <select class="sec2-pub-order px-2 py-1 border rounded bg-white w-40" onchange="recalcLocal()">
                <option value="1" ${order == 1 ? 'selected' : ''}>1st or 2nd Author (100%)</option>
                <option value="3" ${order == 3 ? 'selected' : ''}>3rd Author (50%)</option>
            </select>
            <input type="text" value="${doi}" placeholder="DOI / Journal Link" class="sec2-pub-doi flex-1 px-2 py-1 border rounded text-[11px] font-mono">
            <button type="button" onclick="openUploadModal('${id}', 'SEC2_Pub')" class="px-2.5 py-1 bg-white border border-slate-300 rounded text-slate-700 flex items-center space-x-1">
                <i class="fa-solid fa-paperclip text-slate-400"></i>
                <span class="upload-btn-label">Paper PDF</span>
            </button>
            <input type="hidden" class="sec2-pub-evidence">
            <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500 hover:text-rose-700"><i class="fa-solid fa-trash-can"></i></button>
        </div>
    `;
    container.appendChild(div);
    recalcLocal();
}

function addTalkRow(title = '') { createSimpleRow('container-sec2-talk', title, 'Topic / Host Institution', 'SEC2_Talk'); }
function addBookRow(title = '') { createSimpleRow('container-sec2-book', title, 'Book / Chapter Title & ISBN', 'SEC2_Book'); }
function addProposalRow(title = '') { createSimpleRow('container-sec2-proposal', title, 'Proposal Title & Agency', 'SEC2_Proposal'); }
function addResearchProjectRow(title = '', amt = '600000', role = 'PI') {
    const container = document.getElementById('container-sec2-project');
    const id = `sec2-pr-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 p-1.5 bg-slate-50 border rounded text-xs';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="Project Title" class="sec2-pr-title flex-1 px-2 py-1 border rounded">
        <input type="number" step="50000" min="100000" value="${amt}" placeholder="₹" oninput="recalcLocal()" class="sec2-pr-amt w-24 px-1 py-1 border rounded font-mono">
        <select class="sec2-pr-role px-1 py-1 border rounded bg-white" onchange="recalcLocal()">
            <option value="PI" ${role === 'PI' ? 'selected' : ''}>PI (100%)</option>
            <option value="Co-PI" ${role === 'Co-PI' ? 'selected' : ''}>Co-PI (60%)</option>
        </select>
        <button type="button" onclick="openUploadModal('${id}', 'SEC2_Proj')" class="px-2 py-1 bg-white border rounded text-[11px]">Sanction</button>
        <input type="hidden" class="sec2-pr-evidence">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500"><i class="fa-solid fa-times"></i></button>
    `;
    container.appendChild(div);
    recalcLocal();
}
function addConsultancyRow(title = '', amt = '550000') {
    const container = document.getElementById('container-sec2-consult');
    const id = `sec2-con-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 p-1.5 bg-slate-50 border rounded text-xs';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="Consultancy Client/Title" class="sec2-con-title flex-1 px-2 py-1 border rounded">
        <input type="number" step="50000" value="${amt}" placeholder="₹" oninput="recalcLocal()" class="sec2-con-amt w-24 px-1 py-1 border rounded font-mono">
        <button type="button" onclick="openUploadModal('${id}', 'SEC2_Consult')" class="px-2 py-1 bg-white border rounded text-[11px]">Proof</button>
        <input type="hidden" class="sec2-con-evidence">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500"><i class="fa-solid fa-times"></i></button>
    `;
    container.appendChild(div);
    recalcLocal();
}
function addPatentRow(title = '', status = 'granted') {
    const container = document.getElementById('container-sec2-patent');
    const id = `sec2-pat-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 p-1.5 bg-slate-50 border rounded text-xs';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="Patent Application / Title" class="sec2-pat-title flex-1 px-2 py-1 border rounded">
        <select class="sec2-pat-status px-2 py-1 border rounded bg-white font-semibold" onchange="recalcLocal()">
            <option value="granted" ${status === 'granted' ? 'selected' : ''}>Granted (10)</option>
            <option value="published" ${status === 'published' ? 'selected' : ''}>Published (5)</option>
        </select>
        <button type="button" onclick="openUploadModal('${id}', 'SEC2_Patent')" class="px-2 py-1 bg-white border rounded text-[11px]">Cert</button>
        <input type="hidden" class="sec2-pat-evidence">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500"><i class="fa-solid fa-times"></i></button>
    `;
    container.appendChild(div);
    recalcLocal();
}
function addPhdRow(name = '', role = 'guide', status = 'awarded') {
    const container = document.getElementById('container-sec2-phd');
    const id = `sec2-phd-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 p-1.5 bg-slate-50 border rounded text-xs';
    div.innerHTML = `
        <input type="text" value="${name}" placeholder="Scholar Name / VTU No." class="sec2-phd-name flex-1 px-2 py-1 border rounded">
        <select class="sec2-phd-role px-1.5 py-1 border rounded bg-white" onchange="recalcLocal()">
            <option value="guide" ${role === 'guide' ? 'selected' : ''}>Guide</option>
            <option value="co-guide" ${role === 'co-guide' ? 'selected' : ''}>Co-Guide</option>
        </select>
        <select class="sec2-phd-status px-1.5 py-1 border rounded bg-white" onchange="recalcLocal()">
            <option value="awarded" ${status === 'awarded' ? 'selected' : ''}>Awarded</option>
            <option value="full_time" ${status === 'full_time' ? 'selected' : ''}>Full-Time</option>
            <option value="part_time" ${status === 'part_time' ? 'selected' : ''}>Part-Time</option>
        </select>
        <button type="button" onclick="openUploadModal('${id}', 'SEC2_PhD')" class="px-2 py-1 bg-white border rounded text-[11px]">Proof</button>
        <input type="hidden" class="sec2-phd-evidence">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500"><i class="fa-solid fa-times"></i></button>
    `;
    container.appendChild(div);
    recalcLocal();
}
function addImmersionRow(company = '', weeks = 4) {
    createTwoInputRow('container-sec2-immersion', company, weeks, 'Company Name', 'Weeks (≥4)', 'SEC2_Immersion');
}
function addStartupRow(title = '') { createSimpleRow('container-sec2-startup', title, 'Startup Name & Incubation Proof', 'SEC2_Startup'); }
function addSigRow(title = '') { createSimpleRow('container-sec2-sig', title, 'SIG Group Name & Research Output', 'SEC2_SIG'); }

// ==========================================
// SECTION III DYNAMIC ROWS (TECHNICAL & PROFESSIONAL)
// ==========================================
function addFdpAttRow(title = '', days = 5, level = 'national') {
    const container = document.getElementById('container-sec3-fdp');
    const id = `sec3-fdp-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 p-1.5 bg-slate-50 border rounded text-xs';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="FDP Attended" class="sec3-fdp-title flex-1 px-2 py-1 border rounded">
        <input type="number" min="1" value="${days}" placeholder="Days" oninput="recalcLocal()" class="sec3-fdp-days w-16 px-1 py-1 border rounded text-center font-mono">
        <select class="sec3-fdp-level px-1.5 py-1 border rounded bg-white" onchange="recalcLocal()">
            <option value="national" ${level === 'national' ? 'selected' : ''}>Nat/Int (1/day)</option>
            <option value="state" ${level === 'state' ? 'selected' : ''}>State (0.5/day)</option>
        </select>
        <button type="button" onclick="openUploadModal('${id}', 'SEC3_FDP')" class="px-2 py-1 bg-white border rounded text-[11px]">Cert</button>
        <input type="hidden" class="sec3-fdp-evidence">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500"><i class="fa-solid fa-times"></i></button>
    `;
    container.appendChild(div);
    recalcLocal();
}
function addMembershipRow(society = 'IEEE') {
    const container = document.getElementById('container-sec3-mem');
    const id = `sec3-mem-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 p-1.5 bg-slate-50 border rounded text-xs';
    div.innerHTML = `
        <select class="sec3-mem-soc flex-1 px-2 py-1 border rounded bg-white font-semibold" onchange="recalcLocal()">
            <option value="IEEE">IEEE Member</option>
            <option value="ACM">ACM Member</option>
            <option value="ISTE">ISTE Member</option>
            <option value="IEI">IEI Member</option>
            <option value="IETE">IETE Member</option>
            <option value="CSI">Other Approved Society</option>
        </select>
        <button type="button" onclick="openUploadModal('${id}', 'SEC3_Mem')" class="px-2 py-1 bg-white border rounded text-[11px]">Card/Receipt</button>
        <input type="hidden" class="sec3-mem-evidence">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500"><i class="fa-solid fa-times"></i></button>
    `;
    container.appendChild(div);
    recalcLocal();
}
function addCoeRow(title = '') { createSimpleRow('container-sec3-coe', title, 'COE / Lab / Collab Title', 'SEC3_COE'); }
function addCertRow(title = '') { createSimpleRow('container-sec3-cert', title, 'Global Certification (AWS/Cisco/Microsoft/etc)', 'SEC3_Cert'); }
function addOrgEventRow(title = '', type = 'conference') {
    const container = document.getElementById('container-sec3-org');
    const id = `sec3-org-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 p-1.5 bg-slate-50 border rounded text-xs';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="Event Title" class="sec3-org-title flex-1 px-2 py-1 border rounded">
        <select class="sec3-org-type px-1.5 py-1 border rounded bg-white" onchange="recalcLocal()">
            <option value="conference" ${type === 'conference' ? 'selected' : ''}>Int. Conference (5)</option>
            <option value="fdp" ${type === 'fdp' ? 'selected' : ''}>FDP (1/day)</option>
        </select>
        <button type="button" onclick="openUploadModal('${id}', 'SEC3_OrgEvent')" class="px-2 py-1 bg-white border rounded text-[11px]">Brochure</button>
        <input type="hidden" class="sec3-org-evidence">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500"><i class="fa-solid fa-times"></i></button>
    `;
    container.appendChild(div);
    recalcLocal();
}
function addKscstRow(title = '') { createSimpleRow('container-sec3-kscst', title, 'Project Title & KSCST Sanction', 'SEC3_KSCST'); }
function addSeedGrantRow(title = '') { createSimpleRow('container-sec3-seed', title, 'Seed Grant Title & RNSIT Sanction', 'SEC3_Seed'); }
function addUrfRow(title = '') { createSimpleRow('container-sec3-urf', title, 'URF / PRF Title', 'SEC3_URF'); }
function addStudentPubRow(title = '') { createSimpleRow('container-sec3-studpub', title, 'Student Paper Title & Conference Details', 'SEC3_StudPub'); }
function addHackathonRow(title = '', level = 'national') {
    const container = document.getElementById('container-sec3-hackathon');
    const id = `sec3-hack-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 p-1.5 bg-slate-50 border rounded text-xs';
    div.innerHTML = `
        <input type="text" value="${title}" placeholder="Hackathon Name & Team" class="sec3-hack-title flex-1 px-2 py-1 border rounded">
        <select class="sec3-hack-level px-1.5 py-1 border rounded bg-white" onchange="recalcLocal()">
            <option value="national" ${level === 'national' ? 'selected' : ''}>Nat/Int (3)</option>
            <option value="state" ${level === 'state' ? 'selected' : ''}>State (2)</option>
        </select>
        <button type="button" onclick="openUploadModal('${id}', 'SEC3_Hack')" class="px-2 py-1 bg-white border rounded text-[11px]">Cert</button>
        <input type="hidden" class="sec3-hack-evidence">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500"><i class="fa-solid fa-times"></i></button>
    `;
    container.appendChild(div);
    recalcLocal();
}
function addAutomationRow(title = '') { createSimpleRow('container-sec3-auto', title, 'Software System Name, Intern Batch & Live Deployment URL', 'SEC3_Auto'); }

// ==========================================
// SECTION IV: DEPARTMENTAL RESPONSIBILITIES
// ==========================================
let sec4Index = 0;
function addResponsibilityRow(role = '', contribution = '') {
    sec4Index++;
    if (sec4Index > 10) { alert('Maximum 10 departmental responsibilities can be listed in Section IV.'); return; }
    const tbody = document.getElementById('sec4-tbody');
    const rowId = `sec4-row-${Date.now()}`;
    const tr = document.createElement('tr');
    tr.id = rowId;
    tr.className = 'hover:bg-slate-50 transition border-b border-slate-100';
    tr.innerHTML = `
        <td class="px-3 py-2 font-mono text-slate-400 font-bold">${sec4Index}</td>
        <td class="px-3 py-2">
            <input type="text" value="${role}" placeholder="e.g. NAAC Criterion 3 In-Charge / Exam Coordinator" class="sec4-role w-full px-2 py-1 border rounded text-xs">
        </td>
        <td class="px-3 py-2">
            <input type="text" value="${contribution}" placeholder="Measurable outcome & contribution" class="sec4-contrib w-full px-2 py-1 border rounded text-xs">
        </td>
        <td class="px-3 py-2 text-center">
            <button type="button" onclick="openUploadModal('${rowId}', 'SEC4_Resp_${sec4Index}')" class="px-2 py-0.5 bg-slate-100 hover:bg-slate-200 border rounded text-[11px]">Proof</button>
            <input type="hidden" class="sec4-evidence">
        </td>
        <td class="px-3 py-2 text-center">
            <button type="button" onclick="removeRow('${rowId}');" class="text-rose-500 text-xs"><i class="fa-solid fa-trash-can"></i></button>
        </td>
    `;
    tbody.appendChild(tr);
}

// Helpers
function createSimpleRow(containerId, value, placeholder, compCode) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const id = `${compCode}-${Date.now()}-${Math.floor(Math.random()*1000)}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 text-xs';
    div.innerHTML = `
        <input type="text" value="${value}" placeholder="${placeholder}" class="row-text flex-1 px-2.5 py-1.5 border border-slate-300 rounded focus:ring-1 focus:ring-blue-500">
        <button type="button" onclick="openUploadModal('${id}', '${compCode}')" class="px-2 py-1.5 bg-slate-100 hover:bg-slate-200 border border-slate-300 rounded text-slate-700 flex items-center space-x-1">
            <i class="fa-solid fa-paperclip text-slate-400"></i>
            <span class="upload-btn-label">Proof</span>
        </button>
        <input type="hidden" class="row-evidence">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500 hover:text-rose-700 p-1"><i class="fa-solid fa-times"></i></button>
    `;
    container.appendChild(div);
    recalcLocal();
}

function createTwoInputRow(containerId, val1, val2, p1, p2, compCode) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const id = `${compCode}-${Date.now()}`;
    const div = document.createElement('div');
    div.id = id;
    div.className = 'flex items-center space-x-2 text-xs';
    div.innerHTML = `
        <input type="text" value="${val1}" placeholder="${p1}" class="row-text flex-1 px-2 py-1 border rounded">
        <input type="number" value="${val2}" placeholder="${p2}" oninput="recalcLocal()" class="row-num w-24 px-1 py-1 border rounded font-mono text-center">
        <button type="button" onclick="openUploadModal('${id}', '${compCode}')" class="px-2 py-1 bg-slate-100 border rounded text-[11px]">Cert</button>
        <input type="hidden" class="row-evidence">
        <button type="button" onclick="removeRow('${id}'); recalcLocal();" class="text-rose-500 text-xs"><i class="fa-solid fa-times"></i></button>
    `;
    container.appendChild(div);
    recalcLocal();
}

function removeRow(rowId) {
    const el = document.getElementById(rowId);
    if (el) el.remove();
}

// ==========================================
// UPLOAD MODAL LOGIC
// ==========================================
function openUploadModal(targetRowId, componentCode) {
    activeUploadTarget = { rowId: targetRowId, component: componentCode };
    document.getElementById('modal-component-desc').innerText = `Evidence Document for: ${componentCode}`;
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
        alert('Please select a file to upload.');
        return;
    }

    const file = fileInput.files[0];
    const formData = new FormData();
    formData.append('file', file);
    formData.append('component_code', activeUploadTarget ? activeUploadTarget.component : 'GEN');
    if (currentSubmissionId) {
        formData.append('submission_id', currentSubmissionId);
    }

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
            showToast('Document uploaded: ' + data.file_name);
            closeUploadModal();
        } else {
            alert('Upload failed: ' + (data.error || 'Server error'));
        }
    })
    .catch(err => {
        uploadBtn.innerHTML = '<i class="fa-solid fa-upload"></i> <span>Confirm Upload</span>';
        uploadBtn.disabled = false;
        alert('Upload network error: ' + err);
    });
}

// ==========================================
// GATHER COMPLETE PAYLOAD
// ==========================================
function gatherCompletePayload() {
    // Section 1
    const sec1 = {
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
    document.querySelectorAll('#odd-feedback-tbody tr').forEach(tr => {
        sec1.odd_feedback_courses.push({
            course_name: tr.querySelector('.fb-course-name')?.value || '',
            round_1: tr.querySelector('.fb-r1')?.value || null,
            round_2: tr.querySelector('.fb-r2')?.value || null,
            evidence_file: tr.querySelector('.fb-evidence-url')?.value || ''
        });
    });
    document.querySelectorAll('#even-feedback-tbody tr').forEach(tr => {
        sec1.even_feedback_courses.push({
            course_name: tr.querySelector('.fb-course-name')?.value || '',
            round_1: tr.querySelector('.fb-r1')?.value || null,
            round_2: tr.querySelector('.fb-r2')?.value || null,
            evidence_file: tr.querySelector('.fb-evidence-url')?.value || ''
        });
    });
    document.querySelectorAll('#odd-results-tbody tr').forEach(tr => {
        sec1.odd_results_courses.push({
            course_name: tr.querySelector('.res-course-name')?.value || '',
            appeared: tr.querySelector('.res-appeared')?.value || 0,
            passed: tr.querySelector('.res-passed')?.value || 0,
            evidence_file: tr.querySelector('.res-evidence-url')?.value || ''
        });
    });
    document.querySelectorAll('#even-results-tbody tr').forEach(tr => {
        sec1.even_results_courses.push({
            course_name: tr.querySelector('.res-course-name')?.value || '',
            appeared: tr.querySelector('.res-appeared')?.value || 0,
            passed: tr.querySelector('.res-passed')?.value || 0,
            evidence_file: tr.querySelector('.res-evidence-url')?.value || ''
        });
    });
    document.querySelectorAll('#container-c-ii > div').forEach(div => {
        sec1.other_tlp_c.c_ii_own_syllabus.push({ title: div.querySelector('.row-text')?.value || '' });
    });
    document.querySelectorAll('#container-c-iii > div').forEach(div => {
        sec1.other_tlp_c.c_iii_funded_activities.push({
            title: div.querySelector('.c-iii-title')?.value || '',
            role: div.querySelector('.c-iii-role')?.value || 'PI',
            funding_amount: div.querySelector('.c-iii-amt')?.value || 0
        });
    });
    document.querySelectorAll('#container-c-iv > div').forEach(div => {
        sec1.other_tlp_c.c_iv_org_fdp.push({ title: div.querySelector('.row-text')?.value || '' });
    });
    document.querySelectorAll('#container-c-v > div').forEach(div => {
        sec1.other_tlp_c.c_v_online_completed.push({
            title: div.querySelector('.row-text')?.value || '',
            duration_hours: div.querySelector('.row-num')?.value || 0
        });
    });
    document.querySelectorAll('#container-c-vi > div').forEach(div => {
        sec1.other_tlp_c.c_vi_nptel.push({
            title: div.querySelector('.c-vi-title')?.value || '',
            grade_type: div.querySelector('.c-vi-grade')?.value || 'completed'
        });
    });
    document.querySelectorAll('#container-c-vii > div').forEach(div => {
        sec1.other_tlp_c.c_vii_courses_developed.push({
            title: div.querySelector('.c-vii-title')?.value || '',
            platform_type: div.querySelector('.c-vii-ptype')?.value || 'external'
        });
    });
    document.querySelectorAll('#container-c-viii > div').forEach(div => {
        sec1.other_tlp_c.c_viii_resource_person.push({
            title: div.querySelector('.c-viii-title')?.value || '',
            type: div.querySelector('.c-viii-type')?.value || 'internship'
        });
    });
    document.querySelectorAll('#container-c-ix > div').forEach(div => {
        sec1.other_tlp_c.c_ix_ai_tools.push({ tool_name: div.querySelector('.row-text')?.value || '' });
    });
    document.querySelectorAll('input[name="innovative_method"]:checked').forEach(cb => {
        sec1.other_tlp_c.c_x_tlp_methods.push(cb.value);
    });

    // Section 2
    const sec2 = {
        sec2_ii_publications: [],
        sec2_i_talks: [],
        sec2_iii_books: [],
        sec2_iv_proposals: [],
        sec2_v_projects: [],
        sec2_vi_consultancy: [],
        sec2_vii_patents: [],
        sec2_viii_phd: [],
        sec2_ix_immersion: [],
        sec2_x_startups: [],
        sec2_xi_sig: []
    };
    document.querySelectorAll('#container-sec2-pub > div').forEach(div => {
        sec2.sec2_ii_publications.push({
            title: div.querySelector('.sec2-pub-title')?.value || '',
            category: div.querySelector('.sec2-pub-cat')?.value || 'q4',
            author_order: div.querySelector('.sec2-pub-order')?.value || 1
        });
    });
    document.querySelectorAll('#container-sec2-talk > div').forEach(div => { sec2.sec2_i_talks.push({ title: div.querySelector('.row-text')?.value || '' }); });
    document.querySelectorAll('#container-sec2-book > div').forEach(div => { sec2.sec2_iii_books.push({ title: div.querySelector('.row-text')?.value || '' }); });
    document.querySelectorAll('#container-sec2-proposal > div').forEach(div => { sec2.sec2_iv_proposals.push({ title: div.querySelector('.row-text')?.value || '' }); });
    document.querySelectorAll('#container-sec2-project > div').forEach(div => {
        sec2.sec2_v_projects.push({
            title: div.querySelector('.sec2-pr-title')?.value || '',
            funding_amount: div.querySelector('.sec2-pr-amt')?.value || 0,
            role: div.querySelector('.sec2-pr-role')?.value || 'PI'
        });
    });
    document.querySelectorAll('#container-sec2-consult > div').forEach(div => {
        sec2.sec2_vi_consultancy.push({
            title: div.querySelector('.sec2-con-title')?.value || '',
            consultancy_amount: div.querySelector('.sec2-con-amt')?.value || 0
        });
    });
    document.querySelectorAll('#container-sec2-patent > div').forEach(div => {
        sec2.sec2_vii_patents.push({
            title: div.querySelector('.sec2-pat-title')?.value || '',
            status: div.querySelector('.sec2-pat-status')?.value || 'granted'
        });
    });
    document.querySelectorAll('#container-sec2-phd > div').forEach(div => {
        sec2.sec2_viii_phd.push({
            scholar: div.querySelector('.sec2-phd-name')?.value || '',
            role: div.querySelector('.sec2-phd-role')?.value || 'guide',
            status: div.querySelector('.sec2-phd-status')?.value || 'awarded'
        });
    });
    document.querySelectorAll('#container-sec2-immersion > div').forEach(div => {
        sec2.sec2_ix_immersion.push({
            company: div.querySelector('.row-text')?.value || '',
            weeks: div.querySelector('.row-num')?.value || 4
        });
    });
    document.querySelectorAll('#container-sec2-startup > div').forEach(div => { sec2.sec2_x_startups.push({ name: div.querySelector('.row-text')?.value || '' }); });
    document.querySelectorAll('#container-sec2-sig > div').forEach(div => { sec2.sec2_xi_sig.push({ name: div.querySelector('.row-text')?.value || '' }); });

    // Section 3
    const sec3 = {
        sec3_i_fdp_attended: [],
        sec3_ii_memberships: [],
        sec3_iii_coe: [],
        sec3_iv_certifications: [],
        sec3_v_organized: [],
        sec3_vi_kscst: [],
        sec3_vii_seed_grant: [],
        sec3_viii_urf: [],
        sec3_ix_student_pub: [],
        sec3_x_hackathons: [],
        sec3_xi_automation: []
    };
    document.querySelectorAll('#container-sec3-fdp > div').forEach(div => {
        sec3.sec3_i_fdp_attended.push({
            title: div.querySelector('.sec3-fdp-title')?.value || '',
            days: div.querySelector('.sec3-fdp-days')?.value || 5,
            level: div.querySelector('.sec3-fdp-level')?.value || 'national'
        });
    });
    document.querySelectorAll('#container-sec3-mem > div').forEach(div => {
        sec3.sec3_ii_memberships.push({ society: div.querySelector('.sec3-mem-soc')?.value || 'IEEE' });
    });
    document.querySelectorAll('#container-sec3-coe > div').forEach(div => { sec3.sec3_iii_coe.push({ title: div.querySelector('.row-text')?.value || '' }); });
    document.querySelectorAll('#container-sec3-cert > div').forEach(div => { sec3.sec3_iv_certifications.push({ title: div.querySelector('.row-text')?.value || '' }); });
    document.querySelectorAll('#container-sec3-org > div').forEach(div => {
        sec3.sec3_v_organized.push({
            title: div.querySelector('.sec3-org-title')?.value || '',
            type: div.querySelector('.sec3-org-type')?.value || 'conference'
        });
    });
    document.querySelectorAll('#container-sec3-kscst > div').forEach(div => { sec3.sec3_vi_kscst.push({ title: div.querySelector('.row-text')?.value || '' }); });
    document.querySelectorAll('#container-sec3-seed > div').forEach(div => { sec3.sec3_vii_seed_grant.push({ title: div.querySelector('.row-text')?.value || '' }); });
    document.querySelectorAll('#container-sec3-urf > div').forEach(div => { sec3.sec3_viii_urf.push({ title: div.querySelector('.row-text')?.value || '' }); });
    document.querySelectorAll('#container-sec3-studpub > div').forEach(div => { sec3.sec3_ix_student_pub.push({ title: div.querySelector('.row-text')?.value || '' }); });
    document.querySelectorAll('#container-sec3-hackathon > div').forEach(div => {
        sec3.sec3_x_hackathons.push({
            title: div.querySelector('.sec3-hack-title')?.value || '',
            level: div.querySelector('.sec3-hack-level')?.value || 'national'
        });
    });
    document.querySelectorAll('#container-sec3-auto > div').forEach(div => { sec3.sec3_xi_automation.push({ title: div.querySelector('.row-text')?.value || '' }); });

    // Section 4
    const sec4 = {
        sec4_responsibilities: [],
        sec4_marks_awarded: document.getElementById('sec4-marks-input')?.value || 16
    };
    document.querySelectorAll('#sec4-tbody tr').forEach(tr => {
        sec4.sec4_responsibilities.push({
            role: tr.querySelector('.sec4-role')?.value || '',
            contribution: tr.querySelector('.sec4-contrib')?.value || ''
        });
    });

    // Reviews
    const hod = {
        discipline_attitude: document.getElementById('hod_c1')?.value || 3,
        academic_planning: document.getElementById('hod_c2')?.value || 3,
        dept_admin_support: document.getElementById('hod_c3')?.value || 3,
        accreditation_fdp: document.getElementById('hod_c4')?.value || 3,
        autonomous_support: document.getElementById('hod_c5')?.value || 3,
        remarks: document.getElementById('hod_remarks')?.value || '',
        increment_recommended: document.getElementById('hod_increment')?.checked || true
    };
    const principal = {
        vision_goal: document.getElementById('p_c1')?.value || 1,
        leadership_mgmt: document.getElementById('p_c2')?.value || 1,
        involvement_admin: document.getElementById('p_c3')?.value || 1,
        research_innovation: document.getElementById('p_c4')?.value || 1,
        overall_discipline: document.getElementById('p_c5')?.value || 1,
        remarks: document.getElementById('principal_remarks')?.value || '',
        increment_approved: document.getElementById('principal_increment')?.checked || true
    };

    return {
        section1: sec1,
        section2: sec2,
        section3: sec3,
        section4: sec4,
        hod_review: hod,
        principal_review: principal
    };
}

// Local live calculation
function recalcLocal() {
    const hodTotal = (parseFloat(document.getElementById('hod_c1')?.value) || 0) +
                     (parseFloat(document.getElementById('hod_c2')?.value) || 0) +
                     (parseFloat(document.getElementById('hod_c3')?.value) || 0) +
                     (parseFloat(document.getElementById('hod_c4')?.value) || 0) +
                     (parseFloat(document.getElementById('hod_c5')?.value) || 0);
    const pTotal = (parseFloat(document.getElementById('p_c1')?.value) || 0) +
                   (parseFloat(document.getElementById('p_c2')?.value) || 0) +
                   (parseFloat(document.getElementById('p_c3')?.value) || 0) +
                   (parseFloat(document.getElementById('p_c4')?.value) || 0) +
                   (parseFloat(document.getElementById('p_c5')?.value) || 0);
    const sec4Marks = parseFloat(document.getElementById('sec4-marks-input')?.value) || 0;

    const elHod = document.getElementById('score-hod-total');
    if (elHod) elHod.innerText = `${Math.min(hodTotal, 15)} / 15`;
    const elP = document.getElementById('score-principal-total');
    if (elP) elP.innerText = `${Math.min(pTotal, 5)} / 5`;
    const elRev = document.getElementById('reviews-total-badge');
    if (elRev) elRev.innerText = `${Math.min(hodTotal + pTotal, 20)}`;
    const elSec4 = document.getElementById('sec4-score-badge');
    if (elSec4) elSec4.innerText = `${Math.min(sec4Marks, 20)}`;
}

// ==========================================
// BACKEND API CALCULATION
// ==========================================
function calculateCompleteBackend() {
    const payload = gatherCompletePayload();
    payload.target_section = 'all';

    fetch('/api/section1/calculate/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    })
    .then(r => r.json())
    .then(res => {
        if (res.success) {
            updatePortalUI(res.data);
            showToast('Calculated entire PBAS via backend successfully!');
        } else {
            alert('Backend error: ' + res.error);
        }
    })
    .catch(err => alert('Network error during backend calculation: ' + err));
}

function updatePortalUI(data) {
    const s1 = data.section1;
    const s2 = data.section2;
    const s3 = data.section3;
    const s4 = data.section4;
    const sm = data.summary;

    // Header scores
    document.getElementById('top-sec1-score').innerText = s1.section_score;
    document.getElementById('top-sec2-score').innerText = s2.section_score;
    document.getElementById('top-sec3-score').innerText = s3.section_score;
    document.getElementById('top-grand-total').innerText = sm.grand_total_100;
    document.getElementById('top-grade-pill').innerText = sm.grade;

    // Section 1 badges
    document.getElementById('badge-marks-a').innerText = s1.feedback_a.marks_awarded;
    document.getElementById('badge-marks-b').innerText = s1.results_b.marks_awarded;
    document.getElementById('badge-total-ab').innerText = `${s1.total_ab.score_awarded} / 50`;
    document.getElementById('label-a1-avg').innerText = `${s1.feedback_a.a1_odd_sem_average}%`;
    document.getElementById('label-a2-avg').innerText = `${s1.feedback_a.a2_even_sem_average}%`;
    document.getElementById('label-b1-avg').innerText = `${s1.results_b.b1_odd_sem_average}%`;
    document.getElementById('label-b2-avg').innerText = `${s1.results_b.b2_even_sem_average}%`;
    document.getElementById('foot-sec1-score').innerText = s1.section_score;

    const cComp = s1.other_tlp_c.components;
    if (cComp.c_ii) document.getElementById('score-c-ii').innerText = `${cComp.c_ii.score} / 10`;
    if (cComp.c_iii) document.getElementById('score-c-iii').innerText = `${cComp.c_iii.score} / 10`;
    if (cComp.c_iv) document.getElementById('score-c-iv').innerText = `${cComp.c_iv.score} / 10`;
    if (cComp.c_v) document.getElementById('score-c-v').innerText = `${cComp.c_v.score} / 10`;
    if (cComp.c_vi) document.getElementById('score-c-vi').innerText = `${cComp.c_vi.score} / 10`;
    if (cComp.c_vii) document.getElementById('score-c-vii').innerText = `${cComp.c_vii.score} / 10`;
    if (cComp.c_viii) document.getElementById('score-c-viii').innerText = `${cComp.c_viii.score} / 10`;
    if (cComp.c_ix) document.getElementById('score-c-ix').innerText = `${cComp.c_ix.score} / 5`;
    if (cComp.c_x) document.getElementById('score-c-x').innerText = `${cComp.c_x.score} / 10`;

    // Section 2 badges
    document.getElementById('sec2-score-badge').innerText = s2.section_score;
    document.getElementById('foot-sec2-score').innerText = s2.section_score;
    const s2Comp = s2.components;
    if (s2Comp.sec2_ii) document.getElementById('score-sec2-pub').innerText = `${s2Comp.sec2_ii.score} / 30`;
    if (s2Comp.sec2_i) document.getElementById('score-sec2-talk').innerText = `${s2Comp.sec2_i.score} / 5`;
    if (s2Comp.sec2_iii) document.getElementById('score-sec2-book').innerText = `${s2Comp.sec2_iii.score} / 5`;
    if (s2Comp.sec2_iv) document.getElementById('score-sec2-proposal').innerText = `${s2Comp.sec2_iv.score} / 5`;
    if (s2Comp.sec2_v) document.getElementById('score-sec2-project').innerText = `${s2Comp.sec2_v.score} / 20`;
    if (s2Comp.sec2_vi) document.getElementById('score-sec2-consult').innerText = `${s2Comp.sec2_vi.score} / 10`;
    if (s2Comp.sec2_vii) document.getElementById('score-sec2-patent').innerText = `${s2Comp.sec2_vii.score} / 10`;
    if (s2Comp.sec2_viii) document.getElementById('score-sec2-phd').innerText = `${s2Comp.sec2_viii.score} / 10`;
    if (s2Comp.sec2_ix) document.getElementById('score-sec2-immersion').innerText = `${s2Comp.sec2_ix.score} / 10`;
    if (s2Comp.sec2_x) document.getElementById('score-sec2-startup').innerText = `${s2Comp.sec2_x.score} / 10`;
    if (s2Comp.sec2_xi) document.getElementById('score-sec2-sig').innerText = `${s2Comp.sec2_xi.score} / 5`;

    // Section 3 badges
    document.getElementById('sec3-score-badge').innerText = s3.section_score;
    document.getElementById('foot-sec3-score').innerText = s3.section_score;
    const s3Comp = s3.components;
    if (s3Comp.sec3_i) document.getElementById('score-sec3-fdp').innerText = `${s3Comp.sec3_i.score} / 5`;
    if (s3Comp.sec3_ii) document.getElementById('score-sec3-mem').innerText = `${s3Comp.sec3_ii.score} / 2.5`;
    if (s3Comp.sec3_iii) document.getElementById('score-sec3-coe').innerText = `${s3Comp.sec3_iii.score} / 5`;
    if (s3Comp.sec3_iv) document.getElementById('score-sec3-cert').innerText = `${s3Comp.sec3_iv.score} / 10`;
    if (s3Comp.sec3_v) document.getElementById('score-sec3-org').innerText = `${s3Comp.sec3_v.score} / 5`;
    if (s3Comp.sec3_vi) document.getElementById('score-sec3-kscst').innerText = `${s3Comp.sec3_vi.score} / 2.5`;
    if (s3Comp.sec3_vii) document.getElementById('score-sec3-seed').innerText = `${s3Comp.sec3_vii.score} / 7.5`;
    if (s3Comp.sec3_viii) document.getElementById('score-sec3-urf').innerText = `${s3Comp.sec3_viii.score} / 5`;
    if (s3Comp.sec3_ix) document.getElementById('score-sec3-studpub').innerText = `${s3Comp.sec3_ix.score} / 10`;
    if (s3Comp.sec3_x) document.getElementById('score-sec3-hackathon').innerText = `${s3Comp.sec3_x.score} / 5`;
    if (s3Comp.sec3_xi) document.getElementById('score-sec3-auto').innerText = `${s3Comp.sec3_xi.score} / 10`;

    // Section 4
    document.getElementById('sec4-score-badge').innerText = s4.marks_awarded;

    // Summary Scorecard
    document.getElementById('sum-sec1').innerText = s1.section_score;
    document.getElementById('sum-sec2').innerText = s2.section_score;
    document.getElementById('sum-sec3').innerText = s3.section_score;
    document.getElementById('sum-scaled80').innerText = sm.scaled_80;
    document.getElementById('sum-grand-total').innerText = sm.grand_total_100;
    document.getElementById('sum-grade-text').innerText = sm.grade;
}

// ==========================================
// SAVE ALL SUBMISSION TO DATABASE
// ==========================================
function saveAllSubmission() {
    const payload = gatherCompletePayload();
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
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    })
    .then(r => r.json())
    .then(res => {
        if (res.success) {
            currentSubmissionId = res.submission_id;
            updatePortalUI(res.result);
            document.getElementById('portal-status-badge').innerText = 'Saved & Finalized';
            document.getElementById('portal-status-badge').className = 'font-bold text-emerald-600';
            showToast(`PBAS Saved! Score: ${res.grand_total_100}/100 [${res.grade}]`);
        } else {
            alert('Save failed: ' + res.error);
        }
    })
    .catch(err => alert('Network error saving PBAS: ' + err));
}

function showToast(msg) {
    const toast = document.getElementById('toast');
    document.getElementById('toast-msg').innerText = msg;
    toast.classList.remove('hidden');
    setTimeout(() => { toast.classList.add('hidden'); }, 3500);
}

// ==========================================
// RESTORE SAVED SUBMISSION OR SEED SAMPLE DATA
// ==========================================
function restorePayload(payload) {
    if (!payload) return false;
    const s1 = payload.section1 || payload;
    const s2 = payload.section2 || {};
    const s3 = payload.section3 || {};
    const s4 = payload.section4 || {};

    let hasData = false;

    // Sec 1 Feedback
    if (s1.odd_feedback_courses && s1.odd_feedback_courses.length > 0) {
        s1.odd_feedback_courses.forEach(c => addFeedbackRow('odd', c.course_name, c.round_1, c.round_2, c.evidence_file));
        hasData = true;
    }
    if (s1.even_feedback_courses && s1.even_feedback_courses.length > 0) {
        s1.even_feedback_courses.forEach(c => addFeedbackRow('even', c.course_name, c.round_1, c.round_2, c.evidence_file));
        hasData = true;
    }

    // Sec 1 Results
    if (s1.odd_results_courses && s1.odd_results_courses.length > 0) {
        s1.odd_results_courses.forEach(c => addResultsRow('odd', c.course_name, c.appeared, c.passed, c.evidence_file));
        hasData = true;
    }
    if (s1.even_results_courses && s1.even_results_courses.length > 0) {
        s1.even_results_courses.forEach(c => addResultsRow('even', c.course_name, c.appeared, c.passed, c.evidence_file));
        hasData = true;
    }

    // Sec 1 Other C
    const c = s1.other_tlp_c || {};
    if (c.c_ii_own_syllabus) c.c_ii_own_syllabus.forEach(x => addOwnSyllabusRow(x.title));
    if (c.c_iii_funded_activities) c.c_iii_funded_activities.forEach(x => addFundedActivityRow(x.title, x.role, x.funding_amount));
    if (c.c_iv_org_fdp) c.c_iv_org_fdp.forEach(x => addOrgFdpRow(x.title));
    if (c.c_v_online_completed) c.c_v_online_completed.forEach(x => addOnlineCompletedRow(x.title, x.duration_hours));
    if (c.c_vi_nptel) c.c_vi_nptel.forEach(x => addNptelRow(x.title, x.grade_type));
    if (c.c_vii_courses_developed) c.c_vii_courses_developed.forEach(x => addCourseDevRow(x.title, x.platform_type));
    if (c.c_viii_resource_person) c.c_viii_resource_person.forEach(x => addResourcePersonRow(x.title, x.type));
    if (c.c_ix_ai_tools) c.c_ix_ai_tools.forEach(x => addAiToolRow(x.tool_name));
    if (c.c_x_tlp_methods && c.c_x_tlp_methods.length > 0) {
        c.c_x_tlp_methods.forEach(m => {
            const cb = document.querySelector(`input[name="innovative_method"][value="${m}"]`);
            if (cb) cb.checked = true;
        });
    }

    // Sec 2 Publications & R&D
    if (s2.sec2_ii_publications && s2.sec2_ii_publications.length > 0) {
        s2.sec2_ii_publications.forEach(p => addPubRow(p.title, p.category, p.author_order, p.doi));
        hasData = true;
    }
    if (s2.sec2_i_talks) s2.sec2_i_talks.forEach(x => addTalkRow(x.title));
    if (s2.sec2_iii_books) s2.sec2_iii_books.forEach(x => addBookRow(x.title));
    if (s2.sec2_iv_proposals) s2.sec2_iv_proposals.forEach(x => addProposalRow(x.title));
    if (s2.sec2_v_projects) s2.sec2_v_projects.forEach(x => addResearchProjectRow(x.title, x.funding_amount, x.role));
    if (s2.sec2_vi_consultancy) s2.sec2_vi_consultancy.forEach(x => addConsultancyRow(x.title, x.consultancy_amount));
    if (s2.sec2_vii_patents) s2.sec2_vii_patents.forEach(x => addPatentRow(x.title, x.status));
    if (s2.sec2_viii_phd) s2.sec2_viii_phd.forEach(x => addPhdRow(x.scholar, x.role, x.status));
    if (s2.sec2_ix_immersion) s2.sec2_ix_immersion.forEach(x => addImmersionRow(x.company, x.weeks));
    if (s2.sec2_x_startups) s2.sec2_x_startups.forEach(x => addStartupRow(x.name));
    if (s2.sec2_xi_sig) s2.sec2_xi_sig.forEach(x => addSigRow(x.name));

    // Sec 3 Tech & Prof
    if (s3.sec3_i_fdp_attended) s3.sec3_i_fdp_attended.forEach(x => addFdpAttRow(x.title, x.days, x.level));
    if (s3.sec3_ii_memberships && s3.sec3_ii_memberships.length > 0) addMembershipRow(s3.sec3_ii_memberships[0].society);
    if (s3.sec3_iii_coe) s3.sec3_iii_coe.forEach(x => addCoeRow(x.title));
    if (s3.sec3_iv_certifications) s3.sec3_iv_certifications.forEach(x => addCertRow(x.title));
    if (s3.sec3_v_organized) s3.sec3_v_organized.forEach(x => addOrgEventRow(x.title, x.type));
    if (s3.sec3_vi_kscst) s3.sec3_vi_kscst.forEach(x => addKscstRow(x.title));
    if (s3.sec3_vii_seed_grant) s3.sec3_vii_seed_grant.forEach(x => addSeedGrantRow(x.title));
    if (s3.sec3_viii_urf) s3.sec3_viii_urf.forEach(x => addUrfRow(x.title));
    if (s3.sec3_ix_student_pub) s3.sec3_ix_student_pub.forEach(x => addStudentPubRow(x.title));
    if (s3.sec3_x_hackathons) s3.sec3_x_hackathons.forEach(x => addHackathonRow(x.title, x.level));
    if (s3.sec3_xi_automation) s3.sec3_xi_automation.forEach(x => addAutomationRow(x.title));

    // Sec 4 Administration
    if (s4.sec4_responsibilities && s4.sec4_responsibilities.length > 0) {
        s4.sec4_responsibilities.forEach(r => addResponsibilityRow(r.role, r.contribution));
    }

    return hasData;
}

// Initial Sample Seeding if fresh
function seedInitialSampleData() {
    addFeedbackRow('odd', '21CS51 - Management & Entrepreneurship', 88.5, 91.0);
    addFeedbackRow('odd', '21CS52 - Computer Networks', 82.0, 86.5);
    addFeedbackRow('even', '21CS61 - Software Engineering', 90.0, 93.0);
    addResultsRow('odd', '21CS51 - Management & Entrepreneurship', 62, 59);
    addResultsRow('even', '21CS61 - Software Engineering', 60, 57);
    addOwnSyllabusRow('Cloud Computing & DevOps (Core Syllabus)');
    addOnlineCompletedRow('Coursera - Machine Learning with Python', 36);
    addNptelRow('Cloud Computing by IIT Kharagpur', 'elite_silver', 8);
    addAiToolRow('GitHub Copilot (Assisted Code Reviews)');

    addPubRow('Deep Learning Based Medical Image Classification', 'q1', 1, '10.1016/j.jbi.2026.1042');
    addPubRow('Blockchain Architecture for Autonomous Supply Chains', 'q2', 1, '10.1109/TSC.2026.312');
    addTalkRow('Keynote Speaker on Generative AI at BMSIT National FDP');
    addResearchProjectRow('AI-Driven Smart Irrigation Sensor Network (DST-SERB)', 800000, 'PI');
    addPatentRow('System and Method for Secure Edge Computing (Granted)', 'granted');

    addFdpAttRow('ATAL 5-Day Online FDP on Cyber Security', 5, 'national');
    addMembershipRow('IEEE');
    addCertRow('AWS Certified Solutions Architect – Associate');
    addAutomationRow('PBAS Automated Faculty Appraisal Portal (Deployed internally)');

    addResponsibilityRow('NAAC Criterion 3 Department Coordinator', 'Prepared research compilation, verified publications & MOUs');
    addResponsibilityRow('Department Time-Table & IA Test Committee In-Charge', 'Seamless conduction of internal assessments and autonomous schedules');
}

document.addEventListener('DOMContentLoaded', () => {
    let restored = false;
    if (window.SERVER_SUBMISSION) {
        currentSubmissionId = window.SERVER_SUBMISSION.id;
        if (window.SERVER_SUBMISSION.status && window.SERVER_SUBMISSION.status !== 'DRAFT') {
            const badge = document.getElementById('portal-status-badge');
            if (badge) {
                badge.innerText = window.SERVER_SUBMISSION.status;
                badge.className = 'font-bold text-emerald-600';
            }
        }
        if (window.SERVER_SUBMISSION.raw_payload && Object.keys(window.SERVER_SUBMISSION.raw_payload).length > 0) {
            restored = restorePayload(window.SERVER_SUBMISSION.raw_payload);
        }
    }

    if (!restored) {
        seedInitialSampleData();
    }

    setTimeout(() => {
        calculateCompleteBackend();
    }, 400);
});
