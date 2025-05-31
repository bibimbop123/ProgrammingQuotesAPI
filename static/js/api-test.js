// API Testing functionality

let currentResponse = null;

/**
 * Test a specific API endpoint
 * @param {string} endpoint - The API endpoint to test
 */
function testEndpoint(endpoint) {
    const fullUrl = window.location.origin + endpoint;
    makeApiRequest(fullUrl);
}

/**
 * Test a custom endpoint from the input field
 */
function testCustomEndpoint() {
    const apiUrl = document.getElementById('apiUrl');
    const endpoint = apiUrl.value.trim();
    
    if (!endpoint) {
        showError('Please enter an API endpoint');
        return;
    }
    
    // Ensure endpoint starts with /
    const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : '/' + endpoint;
    const fullUrl = window.location.origin + normalizedEndpoint;
    
    makeApiRequest(fullUrl);
}

/**
 * Make an API request and display the response
 * @param {string} url - The full URL to request
 */
async function makeApiRequest(url) {
    const responseContainer = document.getElementById('responseContainer');
    const responseOutput = document.getElementById('responseOutput');
    
    // Show loading state
    responseContainer.style.display = 'block';
    responseOutput.textContent = 'Loading...';
    responseOutput.className = 'bg-dark p-3 rounded text-light loading';
    
    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        });
        
        const data = await response.json();
        currentResponse = {
            status: response.status,
            statusText: response.statusText,
            data: data
        };
        
        // Format and display response
        const formattedResponse = {
            status: response.status,
            statusText: response.statusText,
            url: url,
            response: data
        };
        
        responseOutput.textContent = JSON.stringify(formattedResponse, null, 2);
        
        // Color code based on status
        if (response.ok) {
            responseOutput.className = 'bg-dark p-3 rounded text-success';
        } else {
            responseOutput.className = 'bg-dark p-3 rounded text-warning';
        }
        
    } catch (error) {
        currentResponse = {
            error: error.message
        };
        
        responseOutput.textContent = JSON.stringify({
            error: 'Network Error',
            message: error.message,
            url: url
        }, null, 2);
        
        responseOutput.className = 'bg-dark p-3 rounded text-danger';
    }
}

/**
 * Copy the API response to clipboard
 */
function copyResponse() {
    const responseOutput = document.getElementById('responseOutput');
    const text = responseOutput.textContent;
    
    if (!text || text === 'Loading...') {
        showToast('No response to copy', 'warning');
        return;
    }
    
    navigator.clipboard.writeText(text).then(() => {
        showToast('Response copied to clipboard!', 'success');
    }).catch(() => {
        // Fallback for older browsers
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showToast('Response copied to clipboard!', 'success');
    });
}

/**
 * Show a toast notification
 * @param {string} message - The message to show
 * @param {string} type - The type of toast (success, warning, error)
 */
function showToast(message, type = 'info') {
    // Create toast element
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 3000);
}

/**
 * Show error message
 * @param {string} message - The error message
 */
function showError(message) {
    showToast(message, 'danger');
}

// Initialize API tester on page load
document.addEventListener('DOMContentLoaded', function() {
    // Add enter key support for the API URL input
    const apiUrlInput = document.getElementById('apiUrl');
    apiUrlInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            testCustomEndpoint();
        }
    });
    
    // Load and display available categories
    loadCategories();
});

/**
 * Load and display available categories from the API
 */
async function loadCategories() {
    try {
        const response = await fetch('/api/quotes/categories');
        if (response.ok) {
            const data = await response.json();
            console.log('Available categories:', data.categories);
        }
    } catch (error) {
        console.log('Could not load categories:', error.message);
    }
}
