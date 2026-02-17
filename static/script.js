// Port information database
const PORT_INFO = {
    21: 'FTP - File Transfer Protocol',
    22: 'SSH - Secure Shell',
    23: 'Telnet',
    25: 'SMTP - Simple Mail Transfer Protocol',
    53: 'DNS - Domain Name System',
    80: 'HTTP - Hypertext Transfer Protocol',
    110: 'POP3 - Post Office Protocol',
    143: 'IMAP - Internet Message Access Protocol',
    443: 'HTTPS - HTTP Secure',
    465: 'SMTPS - SMTP Secure',
    587: 'SMTP - Message Submission',
    993: 'IMAPS - IMAP Secure',
    995: 'POP3S - POP3 Secure',
    3306: 'MySQL Database',
    3389: 'RDP - Remote Desktop Protocol',
    5432: 'PostgreSQL Database',
    8080: 'HTTP Alternate',
    8443: 'HTTPS Alternate'
};

// Handle scan type selection
document.querySelectorAll('input[name="scanType"]').forEach(radio => {
    radio.addEventListener('change', function() {
        const customPortsDiv = document.getElementById('customPortsDiv');
        if (this.value === 'custom') {
            customPortsDiv.style.display = 'block';
        } else {
            customPortsDiv.style.display = 'none';
        }
    });
});

// Handle form submission
document.getElementById('scanForm').addEventListener('submit', async function(e) {
    e.preventDefault();
    
    const url = document.getElementById('url').value.trim();
    const scanType = document.querySelector('input[name="scanType"]:checked').value;
    const customPortsInput = document.getElementById('customPorts').value;
    
    // Validate URL
    if (!url) {
        showError('Please enter a URL or domain name');
        return;
    }
    
    // Validate custom ports if custom scan
    let customPorts = [];
    if (scanType === 'custom') {
        if (!customPortsInput.trim()) {
            showError('Please enter custom ports for custom scan');
            return;
        }
        customPorts = customPortsInput.split(',').map(p => parseInt(p.trim())).filter(p => !isNaN(p));
        if (customPorts.length === 0) {
            showError('Please enter valid port numbers (1-65535)');
            return;
        }
        
        // Check for invalid ports
        const invalidPorts = customPorts.filter(p => p < 1 || p > 65535);
        if (invalidPorts.length > 0) {
            showError(`Invalid port numbers: ${invalidPorts.join(', ')}. Ports must be between 1 and 65535.`);
            return;
        }
    }
    
    // Show loading state
    document.getElementById('scanForm').style.display = 'none';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('loadingState').style.display = 'block';
    
    try {
        const response = await fetch('/scan', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                url: url,
                scan_type: scanType,
                custom_ports: customPorts
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            displayResults(data);
        } else {
            // Show error message
            showError(data.message || data.error || 'An error occurred during scanning');
            document.getElementById('scanForm').style.display = 'block';
        }
    } catch (error) {
        showError('Network error: Unable to connect to the server. Please check your connection.');
        document.getElementById('scanForm').style.display = 'block';
    } finally {
        document.getElementById('loadingState').style.display = 'none';
    }
});

// Function to show error messages
function showError(message) {
    // Create error element if it doesn't exist
    let errorDiv = document.getElementById('errorMessage');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.id = 'errorMessage';
        errorDiv.className = 'error-message';
        document.querySelector('.scan-card').insertBefore(errorDiv, document.getElementById('scanForm'));
    }
    
    errorDiv.innerHTML = `
        <div class="error-content">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
            <div class="error-text">
                <strong>Error</strong>
                <p>${message}</p>
            </div>
            <button class="error-close" onclick="closeError()">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
            </button>
        </div>
    `;
    
    errorDiv.style.display = 'block';
    
    // Auto-hide after 8 seconds
    setTimeout(() => {
        closeError();
    }, 8000);
}

// Function to close error message
function closeError() {
    const errorDiv = document.getElementById('errorMessage');
    if (errorDiv) {
        errorDiv.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 300);
    }
}
// Display scan results
function displayResults(data) {
    document.getElementById('targetUrl').textContent = data.url;
    document.getElementById('ipAddress').textContent = data.ip_address;
    document.getElementById('hostingProvider').textContent = `${data.hosting_provider.org} (${data.hosting_provider.isp})`;
    document.getElementById('location').textContent = `${data.hosting_provider.city}, ${data.hosting_provider.country}`;
    document.getElementById('scanTimestamp').textContent = data.timestamp;
    
    // Display open ports
    const openPortsList = document.getElementById('openPortsList');
    const openPortCount = document.getElementById('openPortCount');
    openPortsList.innerHTML = '';
    openPortCount.textContent = data.open_ports.length;
    
    if (data.open_ports.length === 0) {
        openPortsList.innerHTML = '<div class="port-item">No open ports found</div>';
    } else {
        data.open_ports.forEach((port, index) => {
            const portItem = document.createElement('div');
            portItem.className = 'port-item open';
            portItem.style.animationDelay = `${index * 0.05}s`;
            portItem.innerHTML = `
                <span><strong>Port ${port}</strong></span>
                <span>${PORT_INFO[port] || 'Unknown Service'}</span>
            `;
            openPortsList.appendChild(portItem);
        });
    }
    
    // Display closed ports
    const closedPortsList = document.getElementById('closedPortsList');
    const closedPortCount = document.getElementById('closedPortCount');
    closedPortsList.innerHTML = '';
    closedPortCount.textContent = data.closed_ports.length;
    
    if (data.closed_ports.length === 0) {
        closedPortsList.innerHTML = '<div class="port-item">All scanned ports are open</div>';
    } else {
        data.closed_ports.forEach((port, index) => {
            const portItem = document.createElement('div');
            portItem.className = 'port-item closed';
            portItem.style.animationDelay = `${index * 0.05}s`;
            portItem.innerHTML = `
                <span><strong>Port ${port}</strong></span>
                <span>${PORT_INFO[port] || 'Unknown Service'}</span>
            `;
            closedPortsList.appendChild(portItem);
        });
    }
    
    document.getElementById('resultsSection').style.display = 'block';
}

// Toggle between scanner and history
function toggleHistory() {
    const scannerSection = document.getElementById('scannerSection');
    const historySection = document.getElementById('historySection');
    
    if (historySection.style.display === 'none') {
        scannerSection.style.display = 'none';
        historySection.style.display = 'block';
        loadHistory();
    } else {
        historySection.style.display = 'none';
        scannerSection.style.display = 'block';
        // Reset form
        document.getElementById('scanForm').style.display = 'block';
        document.getElementById('resultsSection').style.display = 'none';
    }
}

// Load scan history
async function loadHistory() {
    try {
        const response = await fetch('/history');
        const history = await response.json();
        
        const historyList = document.getElementById('historyList');
        historyList.innerHTML = '';
        
        if (history.length === 0) {
            historyList.innerHTML = '<div style="text-align: center; padding: 3rem; color: var(--text-muted);">No scan history yet. Start scanning to see results here!</div>';
            return;
        }
        
        history.forEach((scan, index) => {
            const historyItem = document.createElement('div');
            historyItem.className = 'history-item';
            historyItem.style.animationDelay = `${index * 0.05}s`;
            historyItem.innerHTML = `
                <div class="history-item-header">
                    <div class="history-item-info">
                        <h3>${scan.url}</h3>
                        <p>${scan.ip_address} • ${scan.timestamp}</p>
                    </div>
                    <div class="history-item-actions">
                        <button class="delete-button" onclick="deleteScan(${scan.id}, event)">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                            </svg>
                        </button>
                    </div>
                </div>
                <div class="history-item-stats">
                    <div class="stat">
                        <div class="stat-value success">${scan.open_ports.length}</div>
                        <div class="stat-label">Open Ports</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value danger">${scan.closed_ports.length}</div>
                        <div class="stat-label">Closed Ports</div>
                    </div>
                    <div class="stat">
                        <div class="stat-value">${scan.scan_type}</div>
                        <div class="stat-label">Scan Type</div>
                    </div>
                </div>
            `;
            
            // Add click handler to view details (except for delete button)
            historyItem.addEventListener('click', function(e) {
                if (!e.target.closest('.delete-button')) {
                    viewScanDetails(scan.id);
                }
            });
            
            historyList.appendChild(historyItem);
        });
    } catch (error) {
        console.error('Error loading history:', error);
        alert('Failed to load scan history');
    }
}

// View scan details
async function viewScanDetails(scanId) {
    try {
        const response = await fetch(`/history/${scanId}`);
        const scan = await response.json();
        
        // Switch to scanner view and display results
        document.getElementById('historySection').style.display = 'none';
        document.getElementById('scannerSection').style.display = 'block';
        document.getElementById('scanForm').style.display = 'none';
        
        displayResults(scan);
    } catch (error) {
        console.error('Error loading scan details:', error);
        alert('Failed to load scan details');
    }
}

// Delete a scan
async function deleteScan(scanId, event) {
    event.stopPropagation();
    
    if (!confirm('Are you sure you want to delete this scan?')) {
        return;
    }
    
    try {
        const response = await fetch(`/history/${scanId}`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            loadHistory();
        } else {
            alert('Failed to delete scan');
        }
    } catch (error) {
        console.error('Error deleting scan:', error);
        alert('Failed to delete scan');
    }
}

// Add animation styles
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .port-item {
        animation: fadeInUp 0.3s ease forwards;
        opacity: 0;
    }
    
    .history-item {
        animation: fadeInUp 0.3s ease forwards;
        opacity: 0;
    }
`;
document.head.appendChild(style);
// Make logo clickable to return home
document.querySelector('.logo').addEventListener('click', function() {
    // Hide history section
    document.getElementById('historySection').style.display = 'none';
    
    // Show scanner section
    document.getElementById('scannerSection').style.display = 'block';
    
    // Reset the form
    document.getElementById('scanForm').style.display = 'block';
    document.getElementById('resultsSection').style.display = 'none';
    document.getElementById('loadingState').style.display = 'none';
    
    // Clear form inputs
    document.getElementById('url').value = '';
    document.getElementById('customPorts').value = '';
    
    // Reset to default scan type
    document.querySelector('input[name="scanType"][value="default"]').checked = true;
    document.getElementById('customPortsDiv').style.display = 'none';
});