from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import logging
from chrome_connector import ChromeConnector
from data_extractor import DataExtractor
from csv_exporter import CSVExporter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global instances
chrome_connector = ChromeConnector()
data_extractor = DataExtractor()
csv_exporter = CSVExporter()

@app.route('/')
def index():
    """Main application page"""
    return render_template('index.html')

@app.route('/api/connect', methods=['POST'])
def connect_to_chrome():
    """Connect to Chrome browser with remote debugging"""
    try:
        data = request.json
        port = data.get('port', 9222)
        
        success = chrome_connector.connect(port)
        if success:
            tabs = chrome_connector.get_tabs()
            return jsonify({
                'success': True,
                'message': f'Connected to Chrome on port {port}',
                'tabs': tabs
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to connect to Chrome. Make sure Chrome is running with --remote-debugging-port=9222'
            })
    except Exception as e:
        logger.error(f"Error connecting to Chrome: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Connection error: {str(e)}'
        })

@app.route('/api/select_tab', methods=['POST'])
def select_tab():
    """Select a specific Chrome tab for data extraction"""
    try:
        data = request.json
        tab_id = data.get('tab_id')
        
        if not tab_id:
            return jsonify({
                'success': False,
                'message': 'Tab ID is required'
            })
        
        success = chrome_connector.select_tab(tab_id)
        if success:
            # Get page content preview
            page_info = chrome_connector.get_page_info()
            return jsonify({
                'success': True,
                'message': 'Tab selected successfully',
                'page_info': page_info
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Failed to select tab'
            })
    except Exception as e:
        logger.error(f"Error selecting tab: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Tab selection error: {str(e)}'
        })

@app.route('/api/extract_data', methods=['POST'])
def extract_data():
    """Extract lead data from the selected CRM tab"""
    try:
        data = request.json
        field_mappings = data.get('field_mappings', {})
        extraction_config = data.get('extraction_config', {})
        
        if not chrome_connector.is_connected():
            return jsonify({
                'success': False,
                'message': 'Not connected to Chrome. Please connect first.'
            })
        
        # Get page HTML content
        html_content = chrome_connector.get_page_html()
        if not html_content:
            return jsonify({
                'success': False,
                'message': 'Failed to retrieve page content'
            })
        
        # Extract data using configured mappings
        extracted_data = data_extractor.extract_leads(
            html_content, 
            field_mappings, 
            extraction_config
        )
        
        return jsonify({
            'success': True,
            'message': f'Extracted {len(extracted_data)} leads',
            'data': extracted_data[:10],  # Return first 10 for preview
            'total_count': len(extracted_data)
        })
        
    except Exception as e:
        logger.error(f"Error extracting data: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Data extraction error: {str(e)}'
        })

@app.route('/api/export_csv', methods=['POST'])
def export_csv():
    """Export extracted data to CSV file"""
    try:
        data = request.json
        field_mappings = data.get('field_mappings', {})
        extraction_config = data.get('extraction_config', {})
        export_config = data.get('export_config', {})
        
        if not chrome_connector.is_connected():
            return jsonify({
                'success': False,
                'message': 'Not connected to Chrome. Please connect first.'
            })
        
        # Get page HTML content
        html_content = chrome_connector.get_page_html()
        if not html_content:
            return jsonify({
                'success': False,
                'message': 'Failed to retrieve page content'
            })
        
        # Extract data
        extracted_data = data_extractor.extract_leads(
            html_content, 
            field_mappings, 
            extraction_config
        )
        
        if not extracted_data:
            return jsonify({
                'success': False,
                'message': 'No data extracted from the page'
            })
        
        # Export to CSV
        csv_file_path = csv_exporter.export_to_csv(extracted_data, export_config)
        
        return send_file(
            csv_file_path,
            as_attachment=True,
            download_name=f"crm_leads_{len(extracted_data)}_records.csv",
            mimetype='text/csv'
        )
        
    except Exception as e:
        logger.error(f"Error exporting CSV: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'CSV export error: {str(e)}'
        })

@app.route('/api/field_mappings', methods=['GET'])
def get_field_mappings():
    """Get available field mapping configurations"""
    try:
        with open('config/field_mappings.json', 'r') as f:
            mappings = json.load(f)
        return jsonify({
            'success': True,
            'mappings': mappings
        })
    except Exception as e:
        logger.error(f"Error loading field mappings: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Failed to load field mappings: {str(e)}'
        })

@app.route('/api/analyze_page', methods=['POST'])
def analyze_page():
    """Analyze the current page to suggest field mappings"""
    try:
        if not chrome_connector.is_connected():
            return jsonify({
                'success': False,
                'message': 'Not connected to Chrome. Please connect first.'
            })
        
        html_content = chrome_connector.get_page_html()
        if not html_content:
            return jsonify({
                'success': False,
                'message': 'Failed to retrieve page content'
            })
        
        suggestions = data_extractor.analyze_page_structure(html_content)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f"Error analyzing page: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Page analysis error: {str(e)}'
        })

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('config', exist_ok=True)
    os.makedirs('exports', exist_ok=True)
    
    # Start the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)
