// CRM Lead Extractor - Frontend JavaScript

class CRMExtractor {
    constructor() {
        this.isConnected = false;
        this.selectedTab = null;
        this.currentPageInfo = null;
        this.extractedData = null;
        
        this.initializeEventListeners();
        this.initializeFieldMappings();
    }

    initializeEventListeners() {
        // Chrome connection
        document.getElementById('connectBtn').addEventListener('click', () => this.connectToChrome());
        
        // Tab selection
        document.getElementById('tabSelect').addEventListener('change', (e) => {
            document.getElementById('selectTabBtn').disabled = !e.target.value;
        });
        document.getElementById('selectTabBtn').addEventListener('click', () => this.selectTab());
        
        // Field mapping
        document.getElementById('addFieldBtn').addEventListener('click', () => this.addFieldMapping());
        document.getElementById('analyzePageBtn').addEventListener('click', () => this.analyzePage());
        
        // Data extraction
        document.getElementById('previewBtn').addEventListener('click', () => this.previewData());
        document.getElementById('exportBtn').addEventListener('click', () => this.exportToCSV());
    }

    initializeFieldMappings() {
        // Add default field mappings
        const defaultFields = [
            { name: 'name', label: 'Name', selector: '' },
            { name: 'email', label: 'Email', selector: '' },
            { name: 'phone', label: 'Phone', selector: '' },
            { name: 'company', label: 'Company', selector: '' }
        ];

        defaultFields.forEach(field => this.addFieldMapping(field.name, field.label, field.selector));
    }

    async connectToChrome() {
        const port = document.getElementById('chromePort').value;
        const connectBtn = document.getElementById('connectBtn');
        
        // Show loading state
        connectBtn.disabled = true;
        connectBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Connecting...';
        
        try {
            const response = await fetch('/api/connect', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ port: parseInt(port) })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.isConnected = true;
                this.updateConnectionStatus(true);
                this.populateTabs(result.tabs);
                this.showMessage('success', result.message);
                document.getElementById('tabSelectionCard').style.display = 'block';
            } else {
                this.showMessage('danger', result.message);
            }
            
        } catch (error) {
            this.showMessage('danger', `Connection failed: ${error.message}`);
        } finally {
            // Reset button state
            connectBtn.disabled = false;
            connectBtn.innerHTML = '<i class="fas fa-link me-2"></i>Connect to Chrome';
        }
    }

    populateTabs(tabs) {
        const tabSelect = document.getElementById('tabSelect');
        tabSelect.innerHTML = '<option value="">Select a tab...</option>';
        
        tabs.forEach(tab => {
            const option = document.createElement('option');
            option.value = tab.id;
            option.textContent = `${tab.title} - ${tab.url}`;
            tabSelect.appendChild(option);
        });
    }

    async selectTab() {
        const tabId = document.getElementById('tabSelect').value;
        const selectBtn = document.getElementById('selectTabBtn');
        
        if (!tabId) return;
        
        selectBtn.disabled = true;
        selectBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Selecting...';
        
        try {
            const response = await fetch('/api/select_tab', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ tab_id: tabId })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.selectedTab = tabId;
                this.currentPageInfo = result.page_info;
                this.updatePageInfo(result.page_info);
                this.showMessage('success', result.message);
                document.getElementById('fieldMappingCard').style.display = 'block';
                document.getElementById('extractCard').style.display = 'block';
            } else {
                this.showMessage('danger', result.message);
            }
            
        } catch (error) {
            this.showMessage('danger', `Tab selection failed: ${error.message}`);
        } finally {
            selectBtn.disabled = false;
            selectBtn.innerHTML = '<i class="fas fa-check me-2"></i>Select Tab';
        }
    }

    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (connected) {
            statusElement.innerHTML = '<i class="fas fa-circle text-success me-1"></i>Connected';
        } else {
            statusElement.innerHTML = '<i class="fas fa-circle text-danger me-1"></i>Not Connected';
        }
    }

    updatePageInfo(pageInfo) {
        document.getElementById('pageTitle').textContent = pageInfo.title || 'Unknown';
        document.getElementById('pageUrl').textContent = pageInfo.url || 'Unknown';
        document.getElementById('pageInfoCard').style.display = 'block';
    }

    addFieldMapping(fieldName = '', fieldLabel = '', selector = '') {
        const container = document.getElementById('fieldMappings');
        const mappingRow = document.createElement('div');
        mappingRow.className = 'field-mapping-row';
        
        const uniqueId = Date.now() + Math.random();
        
        mappingRow.innerHTML = `
            <div class="row align-items-center">
                <div class="col-3">
                    <input type="text" class="form-control form-control-sm field-name" 
                           placeholder="Field name" value="${fieldName}">
                </div>
                <div class="col-3">
                    <input type="text" class="form-control form-control-sm field-label" 
                           placeholder="Display label" value="${fieldLabel}">
                </div>
                <div class="col-5">
                    <input type="text" class="form-control form-control-sm field-selector" 
                           placeholder="CSS selector" value="${selector}">
                </div>
                <div class="col-1">
                    <button type="button" class="btn btn-outline-danger btn-sm remove-field">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            </div>
        `;
        
        // Add remove functionality
        mappingRow.querySelector('.remove-field').addEventListener('click', () => {
            mappingRow.remove();
        });
        
        container.appendChild(mappingRow);
    }

    async analyzePage() {
        const analyzeBtn = document.getElementById('analyzePageBtn');
        
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-1"></i>Analyzing...';
        
        try {
            const response = await fetch('/api/analyze_page', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayAnalysisResults(result.suggestions);
                this.showMessage('info', 'Page analysis completed. Check suggestions below.');
            } else {
                this.showMessage('danger', result.message);
            }
            
        } catch (error) {
            this.showMessage('danger', `Page analysis failed: ${error.message}`);
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<i class="fas fa-search me-1"></i>Analyze Page';
        }
    }

    displayAnalysisResults(suggestions) {
        const analysisCard = document.getElementById('analysisCard');
        const resultsContainer = document.getElementById('analysisResults');
        
        let html = '';
        
        // Container suggestions
        if (suggestions.potential_containers && suggestions.potential_containers.length > 0) {
            html += '<div class="analysis-section">';
            html += '<h6><i class="fas fa-layer-group me-2"></i>Suggested Container Selectors</h6>';
            suggestions.potential_containers.forEach(container => {
                html += `
                    <div class="suggestion-item" onclick="selectContainerSuggestion('${container.selector}')">
                        <div class="d-flex justify-content-between">
                            <code>${container.selector}</code>
                            <span class="suggestion-meta">${container.count} elements</span>
                        </div>
                        <small class="text-muted">${container.sample_text}</small>
                    </div>
                `;
            });
            html += '</div>';
        }
        
        // Field suggestions
        if (suggestions.field_suggestions) {
            html += '<div class="analysis-section">';
            html += '<h6><i class="fas fa-list me-2"></i>Field Mapping Suggestions</h6>';
            
            Object.entries(suggestions.field_suggestions).forEach(([fieldType, fieldSuggestions]) => {
                html += `<div class="mb-3">`;
                html += `<strong>${fieldType.charAt(0).toUpperCase() + fieldType.slice(1)}:</strong>`;
                fieldSuggestions.forEach(suggestion => {
                    html += `
                        <div class="suggestion-item mt-1" onclick="selectFieldSuggestion('${fieldType}', '${suggestion.selector}')">
                            <div class="d-flex justify-content-between">
                                <code>${suggestion.selector}</code>
                                <span class="suggestion-meta">${suggestion.count} elements</span>
                            </div>
                            <small class="text-muted">${suggestion.sample_value}</small>
                        </div>
                    `;
                });
                html += `</div>`;
            });
            html += '</div>';
        }
        
        // Page analysis
        if (suggestions.analysis) {
            html += '<div class="analysis-section">';
            html += '<h6><i class="fas fa-chart-pie me-2"></i>Page Structure</h6>';
            html += `
                <div class="row text-center">
                    <div class="col-3">
                        <div class="h5 text-primary">${suggestions.analysis.total_elements}</div>
                        <small>Elements</small>
                    </div>
                    <div class="col-3">
                        <div class="h5 text-success">${suggestions.analysis.forms}</div>
                        <small>Forms</small>
                    </div>
                    <div class="col-3">
                        <div class="h5 text-info">${suggestions.analysis.tables}</div>
                        <small>Tables</small>
                    </div>
                    <div class="col-3">
                        <div class="h5 text-warning">${suggestions.analysis.lists}</div>
                        <small>Lists</small>
                    </div>
                </div>
            `;
            html += '</div>';
        }
        
        resultsContainer.innerHTML = html;
        analysisCard.style.display = 'block';
        
        // Scroll to analysis results
        analysisCard.scrollIntoView({ behavior: 'smooth' });
    }

    async previewData() {
        const previewBtn = document.getElementById('previewBtn');
        
        previewBtn.disabled = true;
        previewBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Previewing...';
        
        try {
            const extractionConfig = this.getExtractionConfig();
            
            const response = await fetch('/api/extract_data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(extractionConfig)
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.extractedData = result.data;
                this.displayDataPreview(result.data, result.total_count);
                this.showMessage('success', result.message);
            } else {
                this.showMessage('danger', result.message);
            }
            
        } catch (error) {
            this.showMessage('danger', `Data preview failed: ${error.message}`);
        } finally {
            previewBtn.disabled = false;
            previewBtn.innerHTML = '<i class="fas fa-eye me-2"></i>Preview Data';
        }
    }

    async exportToCSV() {
        const exportBtn = document.getElementById('exportBtn');
        
        exportBtn.disabled = true;
        exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Exporting...';
        
        try {
            const extractionConfig = this.getExtractionConfig();
            
            const response = await fetch('/api/export_csv', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(extractionConfig)
            });
            
            if (response.ok) {
                // Create download link
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = 'crm_leads_export.csv';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                this.showMessage('success', 'CSV file exported successfully!');
            } else {
                const result = await response.json();
                this.showMessage('danger', result.message || 'Export failed');
            }
            
        } catch (error) {
            this.showMessage('danger', `Export failed: ${error.message}`);
        } finally {
            exportBtn.disabled = false;
            exportBtn.innerHTML = '<i class="fas fa-file-csv me-2"></i>Export to CSV';
        }
    }

    getExtractionConfig() {
        const fieldMappings = {};
        const containerSelector = document.getElementById('containerSelector').value;
        const maxLeads = parseInt(document.getElementById('maxLeads').value) || 100;
        
        // Collect field mappings
        document.querySelectorAll('.field-mapping-row').forEach(row => {
            const fieldName = row.querySelector('.field-name').value.trim();
            const selector = row.querySelector('.field-selector').value.trim();
            
            if (fieldName && selector) {
                fieldMappings[fieldName] = selector;
            }
        });
        
        return {
            field_mappings: fieldMappings,
            extraction_config: {
                container_selector: containerSelector,
                max_leads: maxLeads
            },
            export_config: {
                use_display_names: true,
                include_metadata: false
            }
        };
    }

    displayDataPreview(data, totalCount) {
        const previewCard = document.getElementById('previewCard');
        const previewContent = document.getElementById('previewContent');
        
        if (!data || data.length === 0) {
            previewContent.innerHTML = '<div class="alert alert-warning">No data extracted. Please check your field mappings.</div>';
        } else {
            let html = `<div class="mb-3">
                <div class="alert alert-info">
                    Showing ${data.length} of ${totalCount} extracted records
                </div>
            </div>`;
            
            // Create table
            html += '<div class="table-responsive"><table class="table table-striped table-hover">';
            
            // Headers
            const headers = Object.keys(data[0]).filter(key => !key.startsWith('_'));
            html += '<thead><tr>';
            headers.forEach(header => {
                html += `<th>${header.charAt(0).toUpperCase() + header.slice(1)}</th>`;
            });
            html += '</tr></thead>';
            
            // Rows
            html += '<tbody>';
            data.forEach(row => {
                html += '<tr>';
                headers.forEach(header => {
                    const value = row[header] || '';
                    html += `<td>${this.escapeHtml(value)}</td>`;
                });
                html += '</tr>';
            });
            html += '</tbody></table></div>';
            
            previewContent.innerHTML = html;
        }
        
        previewCard.style.display = 'block';
        previewCard.scrollIntoView({ behavior: 'smooth' });
    }

    showMessage(type, message) {
        const container = document.getElementById('statusMessages');
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        container.appendChild(alertDiv);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global functions for suggestion selection
function selectContainerSuggestion(selector) {
    document.getElementById('containerSelector').value = selector;
    
    // Highlight selected suggestion
    document.querySelectorAll('.suggestion-item').forEach(item => {
        item.classList.remove('selected');
    });
    event.target.closest('.suggestion-item').classList.add('selected');
}

function selectFieldSuggestion(fieldType, selector) {
    // Find or create field mapping for this type
    let found = false;
    document.querySelectorAll('.field-mapping-row').forEach(row => {
        const fieldName = row.querySelector('.field-name').value;
        if (fieldName === fieldType) {
            row.querySelector('.field-selector').value = selector;
            found = true;
        }
    });
    
    if (!found) {
        // Create new field mapping
        extractor.addFieldMapping(fieldType, fieldType.charAt(0).toUpperCase() + fieldType.slice(1), selector);
    }
    
    // Highlight selected suggestion
    event.target.closest('.suggestion-item').classList.add('selected');
}

// Initialize the application
const extractor = new CRMExtractor();
