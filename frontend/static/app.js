let currentStep = 1;
let fileId = null;
let jobId = null;
const API = 'http://localhost:8001/api/v1';

// Init
document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    
    dropZone.onclick = () => fileInput.click();
    dropZone.ondragover = (e) => { e.preventDefault(); dropZone.classList.add('border-indigo-600'); };
    dropZone.ondragleave = () => dropZone.classList.remove('border-indigo-600');
    dropZone.ondrop = (e) => { e.preventDefault(); handleFile(e.dataTransfer.files[0]); };
    fileInput.onchange = (e) => handleFile(e.target.files[0]);
    
    document.getElementById('prevBtn').onclick = () => goToStep(currentStep - 1);
    document.getElementById('nextBtn').onclick = () => handleNext();
});

async function handleFile(file) {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const res = await fetch(`${API}/upload`, { method: 'POST', body: formData });
        const data = await res.json();
        fileId = data.file_id;
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileInfo').classList.remove('hidden');
    } catch (e) {
        alert('Upload failed: ' + e.message);
    }
}

async function handleNext() {
    if (currentStep < 5) {
        goToStep(currentStep + 1);
    } else {
        await startAnalysis();
    }
}

function goToStep(step) {
    document.getElementById(`step${currentStep}`).classList.add('hidden');
    document.getElementById(`step${currentStep}-ind`).classList.replace('step-active', 'step-completed');
    currentStep = step;
    document.getElementById(`step${step}`).classList.remove('hidden');
    document.getElementById(`step${step}-ind`).classList.replace('step-pending', 'step-active');
    document.getElementById('prevBtn').disabled = step === 1;
    document.getElementById('nextBtn').textContent = step === 5 ? 'Start Analysis' : 'Next →';
    
    if (step === 5) updateSummary();
}

function updateSummary() {
    document.getElementById('sumFile').textContent = document.getElementById('fileName').textContent;
    document.getElementById('sumLang').textContent = document.querySelector('input[name="language"]:checked').value;
    document.getElementById('sumModel').textContent = document.getElementById('modelSelect').value;
    document.getElementById('sumMode').textContent = document.querySelector('input[name="mode"]:checked').value;
}

async function startAnalysis() {
    const body = {
        file_id: fileId,
        output_language: document.querySelector('input[name="language"]:checked').value,
        model: document.getElementById('modelSelect').value,
        mode: document.querySelector('input[name="mode"]:checked').value
    };
    
    const res = await fetch(`${API}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    const data = await res.json();
    jobId = data.job_id;
    
    document.getElementById('progressModal').classList.remove('hidden');
    document.getElementById('progressModal').classList.add('flex');
    pollStatus();
}

async function pollStatus() {
    const interval = setInterval(async () => {
        const res = await fetch(`${API}/status/${jobId}`);
        const data = await res.json();
        
        document.getElementById('progressBar').style.width = `${data.progress}%`;
        document.getElementById('curScene').textContent = data.current_scene || 0;
        document.getElementById('totScenes').textContent = data.total_scenes || 0;
        
        if (data.status === 'completed') {
            clearInterval(interval);
            showSuccess();
        } else if (data.status === 'error') {
            clearInterval(interval);
            alert('Error: ' + data.error);
        }
    }, 2000);
}

function showSuccess() {
    document.getElementById('progressModal').classList.add('hidden');
    document.getElementById('successModal').classList.remove('hidden');
    document.getElementById('successModal').classList.add('flex');
    document.getElementById('downloadBtn').onclick = () => {
        window.location.href = `${API}/download/${jobId}`;
    };
}
