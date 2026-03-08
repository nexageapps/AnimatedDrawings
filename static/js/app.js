// App state
let currentMode = 'testing';
let selectedImage = null;

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadMode();
    loadTestImages();
    setupEventListeners();
});

// Load current mode
async function loadMode() {
    try {
        const response = await fetch('/api/mode');
        const data = await response.json();
        currentMode = data.mode;
        updateModeIndicator();
    } catch (error) {
        console.error('Error loading mode:', error);
    }
}

// Update mode indicator
function updateModeIndicator() {
    const indicator = document.getElementById('mode-indicator');
    indicator.textContent = `${currentMode.toUpperCase()} MODE`;
    indicator.style.background = currentMode === 'testing' 
        ? 'rgba(255, 193, 7, 0.9)' 
        : 'rgba(76, 175, 80, 0.9)';
}

// Load test images
async function loadTestImages() {
    try {
        const response = await fetch('/api/test-images');
        const data = await response.json();
        displayTestImages(data.images);
    } catch (error) {
        console.error('Error loading test images:', error);
        document.getElementById('test-images-grid').innerHTML = 
            '<p class="loading">Error loading test images</p>';
    }
}

// Display test images
function displayTestImages(images) {
    const grid = document.getElementById('test-images-grid');
    
    if (images.length === 0) {
        grid.innerHTML = '<p class="loading">No test images available</p>';
        return;
    }
    
    grid.innerHTML = images.map(img => `
        <div class="test-image-card" data-path="${img.path}">
            <img src="/${img.path}" alt="${img.name}">
            <p>${img.name}</p>
        </div>
    `).join('');
    
    // Add click handlers
    document.querySelectorAll('.test-image-card').forEach(card => {
        card.addEventListener('click', () => selectTestImage(card));
    });
}

// Select test image
function selectTestImage(card) {
    document.querySelectorAll('.test-image-card').forEach(c => 
        c.classList.remove('selected')
    );
    card.classList.add('selected');
    selectedImage = card.dataset.path;
    showAnimationControls();
}

// Setup event listeners
function setupEventListeners() {
    // Mode toggle buttons
    document.getElementById('testing-mode-btn').addEventListener('click', () => {
        switchMode('testing');
    });
    
    document.getElementById('production-mode-btn').addEventListener('click', () => {
        switchMode('production');
    });
    
    // File upload
    document.getElementById('upload-btn').addEventListener('click', () => {
        document.getElementById('file-input').click();
    });
    
    document.getElementById('file-input').addEventListener('change', handleFileUpload);
    
    // Animate button
    document.getElementById('animate-btn').addEventListener('click', startAnimation);
}

// Switch mode
function switchMode(mode) {
    const testingBtn = document.getElementById('testing-mode-btn');
    const productionBtn = document.getElementById('production-mode-btn');
    const testingSection = document.getElementById('testing-section');
    const productionSection = document.getElementById('production-section');
    
    if (mode === 'testing') {
        testingBtn.classList.add('active');
        productionBtn.classList.remove('active');
        testingSection.classList.remove('hidden');
        testingSection.classList.add('active');
        productionSection.classList.add('hidden');
        productionSection.classList.remove('active');
    } else {
        productionBtn.classList.add('active');
        testingBtn.classList.remove('active');
        productionSection.classList.remove('hidden');
        productionSection.classList.add('active');
        testingSection.classList.add('hidden');
        testingSection.classList.remove('active');
    }
    
    hideAnimationControls();
}

// Handle file upload
async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        const previewArea = document.getElementById('preview-area');
        const previewImage = document.getElementById('preview-image');
        previewImage.src = e.target.result;
        previewArea.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
    
    // Upload file
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        if (data.success) {
            selectedImage = `uploads/${data.filename}`;
            showAnimationControls();
        } else {
            alert('Upload failed: ' + data.error);
        }
    } catch (error) {
        console.error('Upload error:', error);
        alert('Upload failed. Please try again.');
    }
}

// Show animation controls
function showAnimationControls() {
    document.getElementById('animation-controls').classList.remove('hidden');
}

// Hide animation controls
function hideAnimationControls() {
    document.getElementById('animation-controls').classList.add('hidden');
    document.getElementById('result-area').classList.add('hidden');
}

// Start animation
async function startAnimation() {
    if (!selectedImage) {
        alert('Please select or upload an image first');
        return;
    }
    
    const motion = document.getElementById('motion-select').value;
    const animateBtn = document.getElementById('animate-btn');
    
    animateBtn.disabled = true;
    animateBtn.textContent = 'Animating...';
    
    try {
        const response = await fetch('/api/animate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                image_path: selectedImage,
                motion: motion
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showResult(data);
        } else {
            alert('Animation failed: ' + data.error);
        }
    } catch (error) {
        console.error('Animation error:', error);
        alert('Animation failed. Please try again.');
    } finally {
        animateBtn.disabled = false;
        animateBtn.textContent = 'Animate!';
    }
}

// Show result
function showResult(data) {
    const resultArea = document.getElementById('result-area');
    const resultContent = document.getElementById('result-content');
    
    resultContent.innerHTML = `
        <p style="color: green; font-weight: bold;">${data.message}</p>
        <p>Output: ${data.output}</p>
        <p style="margin-top: 20px; color: #666;">
            Note: Full animation integration coming soon!
        </p>
    `;
    
    resultArea.classList.remove('hidden');
}
