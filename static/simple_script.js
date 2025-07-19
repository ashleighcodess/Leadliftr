// Simple CRM Lead Extractor - Frontend JavaScript

class SimpleCRMExtractor {
    constructor() {
        this.extractedData = null;
        this.availablePresets = {};
        
        this.initializeEventListeners();
        this.initializeFieldMappings();
        this.loadPresets();
    }

    initializeEventListeners() {
        // HTML analysis
        document.getElementById('analyzeBtn').addEventListener('click', () => this.analyzeHTML());
        
        // CRM presets
        document.getElementById('crmPreset').addEventListener('change', (e) => {
            document.getElementById('loadPresetBtn').disabled = !e.target.value;
        });
        document.getElementById('loadPresetBtn').addEventListener('click', () => this.loadPreset());
        
        // Field mapping
        document.getElementById('addFieldBtn').addEventListener('click', () => this.addFieldMapping());
        
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

    async loadPresets() {
        try {
            const response = await fetch('/api/field_mappings');
            const result = await response.json();
            
            if (result.success) {
                this.availablePresets = result.mappings;
            }
        } catch (error) {
            console.error('Failed to load presets:', error);
        }
    }

    async analyzeHTML() {
        const htmlContent = document.getElementById('htmlContent').value.trim();
        const analyzeBtn = document.getElementById('analyzeBtn');
        
        if (!htmlContent) {
            this.showMessage('warning', 'Please paste HTML content first');
            return;
        }
        
        analyzeBtn.disabled = true;
        analyzeBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Analyzing...';
        
        try {
            const response = await fetch('/api/analyze_html', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ html_content: htmlContent })
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.displayAnalysisResults(result.suggestions);
                this.showMessage('success', 'HTML analysis completed. Check suggestions below.');
            } else {
                this.showMessage('danger', result.message);
            }
            
        } catch (error) {
            this.showMessage('danger', `Analysis failed: ${error.message}`);
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.innerHTML = '<i class="fas fa-search me-2"></i>Analyze HTML Structure';
        }
    }

    loadPreset() {
        const presetName = document.getElementById('crmPreset').value;
        
        if (!presetName || !this.availablePresets[presetName]) {
            this.showMessage('warning', 'Please select a valid preset');
            return;
        }
        
        const preset = this.availablePresets[presetName];
        
        // Clear existing field mappings
        document.getElementById('fieldMappings').innerHTML = '';
        
        // Set container selector
        if (preset.container_selector) {
            document.getElementById('containerSelector').value = preset.container_selector;
        }
        
        // Add field mappings from preset in specific order
        const fieldOrder = presetName === 'ringy' ? 
            ['first_name', 'last_name', 'number', 'city', 'state', 'zip_code'] :
            Object.keys(preset.mappings);
            
        fieldOrder.forEach(fieldName => {
            if (preset.mappings[fieldName]) {
                const displayName = fieldName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                this.addFieldMapping(fieldName, displayName, preset.mappings[fieldName]);
            }
        });
        
        this.showMessage('success', `Loaded ${preset.name} configuration`);
    }

    addFieldMapping(fieldName = '', fieldLabel = '', selector = '') {
        const container = document.getElementById('fieldMappings');
        const mappingRow = document.createElement('div');
        mappingRow.className = 'field-mapping-row';
        
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
                    <div class="suggestion-item cursor-pointer" onclick="selectContainerSuggestion('${container.selector}')">
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
                        <div class="suggestion-item cursor-pointer mt-1" onclick="selectFieldSuggestion('${fieldType}', '${suggestion.selector}')">
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
            html += '<h6><i class="fas fa-chart-pie me-2"></i>HTML Structure Overview</h6>';
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
        const htmlContent = document.getElementById('htmlContent').value.trim();
        const previewBtn = document.getElementById('previewBtn');
        
        if (!htmlContent) {
            this.showMessage('warning', 'Please paste HTML content first');
            return;
        }
        
        previewBtn.disabled = true;
        previewBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Previewing...';
        
        try {
            const extractionConfig = this.getExtractionConfig();
            extractionConfig.html_content = htmlContent;
            
            const response = await fetch('/api/extract_from_html', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(extractionConfig)
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Don't store extracted data - just use for preview
                this.displayDataPreview(result.data, result.total_count);
                this.showMessage('success', result.message);
            } else {
                this.showMessage('danger', result.message);
            }
            
        } catch (error) {
            this.showMessage('danger', `Preview failed: ${error.message}`);
        } finally {
            previewBtn.disabled = false;
            previewBtn.innerHTML = '<i class="fas fa-eye me-2"></i>Preview Data';
        }
    }

    async exportToCSV() {
        const htmlContent = document.getElementById('htmlContent').value.trim();
        const exportBtn = document.getElementById('exportBtn');
        
        if (!htmlContent) {
            this.showMessage('warning', 'Please paste HTML content first');
            return;
        }
        
        exportBtn.disabled = true;
        exportBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Exporting...';
        
        try {
            const extractionConfig = this.getExtractionConfig();
            extractionConfig.html_content = htmlContent;
            
            const response = await fetch('/api/export_from_html', {
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
                
                this.showMessage('success', 'CSV file downloaded successfully!');
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
        const containerSelector = document.getElementById('containerSelector').value.trim();
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
                include_metadata: true
            }
        };
    }

    displayDataPreview(data, totalCount) {
        const previewCard = document.getElementById('previewCard');
        const previewContent = document.getElementById('previewContent');
        
        if (!data || data.length === 0) {
            previewContent.innerHTML = '<p class="text-muted">No data extracted. Please check your field mappings.</p>';
            previewCard.style.display = 'block';
            return;
        }
        
        // Create table
        let html = `<div class="mb-3">
            <strong>Showing ${data.length} of ${totalCount} extracted leads</strong>
        </div>`;
        
        html += '<div class="table-responsive">';
        html += '<table class="table table-striped table-hover">';
        html += '<thead><tr>';
        
        // Table headers
        const headers = Object.keys(data[0]);
        headers.forEach(header => {
            if (!header.startsWith('_')) {
                html += `<th>${header.charAt(0).toUpperCase() + header.slice(1)}</th>`;
            }
        });
        html += '</tr></thead><tbody>';
        
        // Table rows
        data.forEach(row => {
            html += '<tr>';
            headers.forEach(header => {
                if (!header.startsWith('_')) {
                    const value = row[header] || '';
                    html += `<td>${this.escapeHtml(value)}</td>`;
                }
            });
            html += '</tr>';
        });
        
        html += '</tbody></table></div>';
        
        previewContent.innerHTML = html;
        previewCard.style.display = 'block';
        
        // Scroll to preview
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
        
        // Auto-remove success messages after 5 seconds
        if (type === 'success') {
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }
        
        // Scroll to message
        alertDiv.scrollIntoView({ behavior: 'smooth' });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Global functions for suggestion clicks
function selectContainerSuggestion(selector) {
    document.getElementById('containerSelector').value = selector;
    document.querySelector(`[onclick="selectContainerSuggestion('${selector}')"]`).classList.add('selected');
}

function selectFieldSuggestion(fieldType, selector) {
    // Find the field mapping row for this field type
    const fieldRows = document.querySelectorAll('.field-mapping-row');
    let targetRow = null;
    
    fieldRows.forEach(row => {
        const fieldName = row.querySelector('.field-name').value.toLowerCase();
        if (fieldName === fieldType.toLowerCase()) {
            targetRow = row;
        }
    });
    
    // If no existing row found, create a new one
    if (!targetRow) {
        app.addFieldMapping(fieldType, fieldType.charAt(0).toUpperCase() + fieldType.slice(1), selector);
    } else {
        targetRow.querySelector('.field-selector').value = selector;
    }
    
    document.querySelector(`[onclick="selectFieldSuggestion('${fieldType}', '${selector}')"]`).classList.add('selected');
}

// Initialize the application
const app = new SimpleCRMExtractor();