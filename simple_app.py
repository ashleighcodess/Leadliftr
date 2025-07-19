from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import logging
from data_extractor import DataExtractor
from csv_exporter import CSVExporter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global instances
data_extractor = DataExtractor()
csv_exporter = CSVExporter()

@app.route('/')
def index():
    """Main application page"""
    return render_template('simple_index.html')

@app.route('/api/extract_from_html', methods=['POST'])
def extract_from_html():
    """Extract lead data from provided HTML content"""
    try:
        data = request.json
        html_content = data.get('html_content', '')
        field_mappings = data.get('field_mappings', {})
        extraction_config = data.get('extraction_config', {})
        
        if not html_content:
            return jsonify({
                'success': False,
                'message': 'Please provide HTML content to extract from'
            })
        
        if not field_mappings:
            return jsonify({
                'success': False,
                'message': 'Please configure at least one field mapping'
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

@app.route('/api/export_from_html', methods=['POST'])
def export_from_html():
    """Extract and export data to CSV from provided HTML content"""
    try:
        data = request.json
        html_content = data.get('html_content', '')
        field_mappings = data.get('field_mappings', {})
        extraction_config = data.get('extraction_config', {})
        export_config = data.get('export_config', {})
        
        if not html_content:
            return jsonify({
                'success': False,
                'message': 'Please provide HTML content to extract from'
            })
        
        if not field_mappings:
            return jsonify({
                'success': False,
                'message': 'Please configure at least one field mapping'
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
                'message': 'No data extracted from the provided HTML'
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

@app.route('/api/analyze_html', methods=['POST'])
def analyze_html():
    """Analyze provided HTML to suggest field mappings"""
    try:
        data = request.json
        html_content = data.get('html_content', '')
        
        if not html_content:
            return jsonify({
                'success': False,
                'message': 'Please provide HTML content to analyze'
            })
        
        suggestions = data_extractor.analyze_page_structure(html_content)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        logger.error(f"Error analyzing HTML: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'HTML analysis error: {str(e)}'
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

if __name__ == '__main__':
    # Ensure required directories exist
    os.makedirs('config', exist_ok=True)
    os.makedirs('exports', exist_ok=True)
    
    # Start the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)