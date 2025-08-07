/**
 * AFROTC 695 Analytics Configuration
 * Custom analytics tracking for Vercel Analytics
 */

// Check if Vercel Analytics is available
function isVercelAnalyticsAvailable() {
    return typeof window !== 'undefined' && window.va;
}

// Track custom events
function trackEvent(eventName, properties = {}) {
    if (isVercelAnalyticsAvailable()) {
        window.va.track(eventName, properties);
    } else {
        // Fallback logging for development
        console.log('Analytics Event:', eventName, properties);
    }
}

// Track page views (already handled by Vercel Analytics automatically)
function trackPageView(pageName, properties = {}) {
    trackEvent('page_view', {
        page_name: pageName,
        ...properties
    });
}

// Track user interactions
function trackUserInteraction(action, target, properties = {}) {
    trackEvent('user_interaction', {
        action: action,
        target: target,
        ...properties
    });
}

// Track form submissions
function trackFormSubmission(formName, success = true, properties = {}) {
    trackEvent('form_submission', {
        form_name: formName,
        success: success,
        ...properties
    });
}

// Track file operations
function trackFileOperation(operation, fileType, fileSize = null, properties = {}) {
    trackEvent('file_operation', {
        operation: operation,
        file_type: fileType,
        file_size: fileSize,
        ...properties
    });
}

// Track search queries
function trackSearch(query, resultsCount = null, properties = {}) {
    trackEvent('search', {
        query: query,
        results_count: resultsCount,
        ...properties
    });
}

// Track authentication events
function trackAuthEvent(event, success = true, properties = {}) {
    trackEvent('authentication', {
        event: event,
        success: success,
        ...properties
    });
}

// Track data export events
function trackDataExport(format, recordCount = null, properties = {}) {
    trackEvent('data_export', {
        format: format,
        record_count: recordCount,
        ...properties
    });
}

// Track admin actions
function trackAdminAction(action, target, properties = {}) {
    trackEvent('admin_action', {
        action: action,
        target: target,
        ...properties
    });
}

// Initialize analytics when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Track initial page load
    const currentPage = window.location.pathname;
    const pageName = currentPage === '/' ? 'dashboard' : currentPage.substring(1).replace(/\//g, '_');
    trackPageView(pageName, {
        url: window.location.href,
        referrer: document.referrer
    });

    // Track form submissions
    document.addEventListener('submit', function(e) {
        const form = e.target;
        const formName = form.getAttribute('id') || form.getAttribute('name') || 'unknown_form';
        
        // Track form submission
        trackFormSubmission(formName, true, {
            form_action: form.getAttribute('action'),
            form_method: form.getAttribute('method')
        });
    });

    // Track button clicks for important actions
    document.addEventListener('click', function(e) {
        const target = e.target;
        
        // Track specific button clicks
        if (target.tagName === 'BUTTON' || target.tagName === 'A') {
            const action = target.getAttribute('data-analytics-action') || 
                          target.getAttribute('aria-label') || 
                          target.textContent.trim();
            
            if (action) {
                trackUserInteraction('click', action, {
                    element_type: target.tagName.toLowerCase(),
                    element_id: target.getAttribute('id'),
                    element_class: target.getAttribute('class')
                });
            }
        }
    });

    // Track file uploads
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const files = e.target.files;
            if (files.length > 0) {
                const file = files[0];
                trackFileOperation('upload', file.type, file.size, {
                    file_name: file.name,
                    input_id: input.getAttribute('id')
                });
            }
        });
    });

    // Track search functionality
    const searchInputs = document.querySelectorAll('input[type="search"], input[placeholder*="search"], input[placeholder*="Search"]');
    searchInputs.forEach(input => {
        let searchTimeout;
        input.addEventListener('input', function(e) {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                const query = e.target.value.trim();
                if (query.length > 2) {
                    trackSearch(query, null, {
                        input_id: input.getAttribute('id'),
                        search_type: 'live_search'
                    });
                }
            }, 500);
        });
    });
});

// Export functions for use in other scripts
window.AFROTCAnalytics = {
    trackEvent,
    trackPageView,
    trackUserInteraction,
    trackFormSubmission,
    trackFileOperation,
    trackSearch,
    trackAuthEvent,
    trackDataExport,
    trackAdminAction
};
