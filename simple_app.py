from flask import Flask, render_template, request, jsonify, send_file
import json
import os
import logging
import gc
import tempfile
import time
from data_extractor import DataExtractor
from csv_exporter import CSVExporter
from batch_processor import BatchProcessor
from lead_scrubber import LeadScrubber

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global instances
data_extractor = DataExtractor()
csv_exporter = CSVExporter()
batch_processor = BatchProcessor()
lead_scrubber = LeadScrubber()

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
        
        preview_data = extracted_data[:10]  # Get preview before clearing
        total_count = len(extracted_data)
        
        # Clear the full dataset from memory after getting preview
        extracted_data = None
        gc.collect()
        
        return jsonify({
            'success': True,
            'message': f'Extracted {total_count} leads',
            'data': preview_data,  # Return first 10 for preview
            'total_count': total_count
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
        
        max_leads = extraction_config.get('max_leads', 1000)
        
        # For large datasets, use batch processing to avoid memory issues
        if max_leads > 10000:
            logger.info(f"Processing large dataset with {max_leads} max leads using batch processor")
            
            # Create temporary file for large dataset processing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as temp_file:
                temp_path = temp_file.name
            
            try:
                # Use batch processor for large datasets
                total_records = batch_processor.export_large_csv(
                    html_content, field_mappings, extraction_config, export_config, temp_path
                )
                
                if total_records == 0:
                    os.unlink(temp_path)  # Clean up temp file
                    return jsonify({
                        'success': False,
                        'message': 'No data extracted from the provided HTML'
                    })
                
                # Send file and clean up immediately after
                def remove_file(response):
                    try:
                        os.unlink(temp_path)
                        gc.collect()  # Force garbage collection
                    except Exception:
                        pass
                    return response
                
                response = send_file(
                    temp_path,
                    as_attachment=True,
                    download_name=f"crm_leads_{total_records}_records.csv",
                    mimetype='text/csv'
                )
                
                # Schedule file cleanup after response
                response.call_on_close(lambda: os.unlink(temp_path) if os.path.exists(temp_path) else None)
                
                return response
                
            except Exception as e:
                # Clean up temp file on error
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                raise e
        
        else:
            # For smaller datasets, use normal processing
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
            
            # Apply lead scrubbing if enabled
            scrub_config = export_config.get('scrub_config', {})
            if scrub_config.get('enable_scrubbing', False):
                scrub_results = lead_scrubber.scrub_leads(extracted_data, scrub_config)
                final_data = scrub_results['clean_leads']
                scrub_summary = lead_scrubber.get_scrubbing_summary(scrub_results['stats'])
                logger.info(f"Lead scrubbing results:\n{scrub_summary}")
                filename_suffix = f"_scrubbed_{len(final_data)}_clean"
            else:
                final_data = extracted_data
                filename_suffix = f"_{len(final_data)}_records"
            
            # Export to CSV
            csv_file_path = csv_exporter.export_to_csv(final_data, export_config)
            
            # Clear extracted data from memory immediately
            extracted_data = None
            final_data = None
            gc.collect()
            
            return send_file(
                csv_file_path,
                as_attachment=True,
                download_name=f"crm_leads{filename_suffix}.csv",
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
    
    # Clean up old export files on startup
    try:
        export_files = [f for f in os.listdir('exports') if f.endswith('.csv')]
        for file in export_files:
            file_path = os.path.join('exports', file)
            # Remove files older than 1 hour
            if os.path.getmtime(file_path) < (time.time() - 3600):
                os.unlink(file_path)
                logger.info(f"Cleaned up old export file: {file}")
    except Exception as e:
        logger.warning(f"Error cleaning up old files: {str(e)}")
    
    # Start the Flask application
    app.run(host='0.0.0.0', port=5000, debug=True)