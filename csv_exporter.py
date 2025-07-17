import pandas as pd
import os
import logging
from typing import Dict, List, Optional
from datetime import datetime
import re

logger = logging.getLogger(__name__)

class CSVExporter:
    """Handles exporting lead data to CSV files with proper formatting and validation"""
    
    def __init__(self):
        self.export_dir = 'exports'
        self.ensure_export_dir()
        
        # Default column mapping and order
        self.default_columns = [
            'name', 'email', 'phone', 'company', 'title', 'status', 
            'lead_source', 'notes', 'created_date', 'last_contact'
        ]
        
        # Column display names
        self.column_display_names = {
            'name': 'Full Name',
            'email': 'Email Address',
            'phone': 'Phone Number',
            'company': 'Company Name',
            'title': 'Job Title',
            'status': 'Lead Status',
            'lead_source': 'Lead Source',
            'notes': 'Notes',
            'created_date': 'Created Date',
            'last_contact': 'Last Contact Date',
            '_extraction_index': 'Extraction Index'
        }
    
    def ensure_export_dir(self):
        """Ensure the exports directory exists"""
        try:
            os.makedirs(self.export_dir, exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating export directory: {str(e)}")
    
    def export_to_csv(self, leads_data: List[Dict], export_config: Dict = None) -> str:
        """
        Export lead data to CSV file
        
        Args:
            leads_data: List of lead dictionaries
            export_config: Configuration for export (columns, filename, etc.)
        
        Returns:
            Path to the exported CSV file
        """
        try:
            if not leads_data:
                raise ValueError("No lead data provided for export")
            
            export_config = export_config or {}
            
            # Create DataFrame
            df = pd.DataFrame(leads_data)
            
            # Configure columns
            columns_config = export_config.get('columns', {})
            
            # Determine which columns to include
            if 'include_columns' in columns_config:
                # Use specified columns
                include_columns = columns_config['include_columns']
                available_columns = [col for col in include_columns if col in df.columns]
            else:
                # Use all available columns, ordered by default preference
                available_columns = []
                for col in self.default_columns:
                    if col in df.columns:
                        available_columns.append(col)
                # Add any additional columns not in default list
                for col in df.columns:
                    if col not in available_columns and not col.startswith('_'):
                        available_columns.append(col)
            
            # Select and reorder columns
            if available_columns:
                df = df[available_columns]
            
            # Apply column display names if requested
            if export_config.get('use_display_names', True):
                column_rename_map = {}
                for col in df.columns:
                    if col in self.column_display_names:
                        column_rename_map[col] = self.column_display_names[col]
                    else:
                        # Convert snake_case to Title Case
                        display_name = col.replace('_', ' ').title()
                        column_rename_map[col] = display_name
                
                df = df.rename(columns=column_rename_map)
            
            # Clean and format data
            df = self._clean_dataframe(df, export_config)
            
            # Generate filename
            filename = self._generate_filename(export_config, len(leads_data))
            file_path = os.path.join(self.export_dir, filename)
            
            # Export to CSV
            df.to_csv(
                file_path,
                index=False,
                encoding='utf-8-sig',  # Ensures proper UTF-8 encoding with BOM for Excel
                quoting=1  # Quote all fields to handle commas in data
            )
            
            logger.info(f"Successfully exported {len(leads_data)} leads to {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {str(e)}")
            raise
    
    def _clean_dataframe(self, df: pd.DataFrame, export_config: Dict) -> pd.DataFrame:
        """Clean and format the DataFrame before export"""
        try:
            # Fill NaN values with empty strings
            df = df.fillna('')
            
            # Clean text fields
            for column in df.columns:
                if df[column].dtype == 'object':  # String columns
                    # Remove extra whitespace and normalize
                    df[column] = df[column].astype(str).str.strip()
                    df[column] = df[column].str.replace(r'\s+', ' ', regex=True)
                    
                    # Handle specific field types
                    column_lower = column.lower()
                    if 'email' in column_lower:
                        df[column] = df[column].str.lower()
                    elif 'phone' in column_lower:
                        df[column] = df[column].apply(self._format_phone)
                    elif 'name' in column_lower or 'company' in column_lower:
                        df[column] = df[column].apply(self._format_name)
            
            # Add export metadata if requested
            if export_config.get('include_metadata', False):
                df['Export Date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                df['Total Records'] = len(df)
            
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning DataFrame: {str(e)}")
            return df
    
    def _format_phone(self, phone: str) -> str:
        """Format phone number consistently"""
        if not phone or phone == '':
            return ''
        
        try:
            # Remove all non-digit characters except + for international
            digits_only = re.sub(r'[^\d\+]', '', str(phone))
            
            # Basic formatting for US numbers
            if len(digits_only) == 10 and digits_only.isdigit():
                return f"({digits_only[:3]}) {digits_only[3:6]}-{digits_only[6:]}"
            elif len(digits_only) == 11 and digits_only.startswith('1'):
                return f"+1 ({digits_only[1:4]}) {digits_only[4:7]}-{digits_only[7:]}"
            else:
                return phone  # Return original if can't format
                
        except Exception:
            return phone
    
    def _format_name(self, name: str) -> str:
        """Format name with proper capitalization"""
        if not name or name == '':
            return ''
        
        try:
            # Split on spaces and capitalize each word
            words = str(name).split()
            formatted_words = []
            
            for word in words:
                if len(word) > 0:
                    # Handle special cases like McDonald, O'Connor, etc.
                    if "'" in word:
                        parts = word.split("'")
                        formatted_word = "'".join([part.capitalize() for part in parts])
                    else:
                        formatted_word = word.capitalize()
                    formatted_words.append(formatted_word)
            
            return ' '.join(formatted_words)
            
        except Exception:
            return name
    
    def _generate_filename(self, export_config: Dict, record_count: int) -> str:
        """Generate filename for the CSV export"""
        try:
            # Use custom filename if provided
            if 'filename' in export_config:
                filename = export_config['filename']
                if not filename.endswith('.csv'):
                    filename += '.csv'
                return filename
            
            # Generate default filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"crm_leads_{record_count}_records_{timestamp}.csv"
            
            # Sanitize filename
            filename = re.sub(r'[^\w\-_\.]', '_', filename)
            
            return filename
            
        except Exception as e:
            logger.error(f"Error generating filename: {str(e)}")
            return f"crm_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    def get_export_history(self) -> List[Dict]:
        """Get list of previously exported files"""
        try:
            files = []
            if os.path.exists(self.export_dir):
                for filename in os.listdir(self.export_dir):
                    if filename.endswith('.csv'):
                        file_path = os.path.join(self.export_dir, filename)
                        stat = os.stat(file_path)
                        files.append({
                            'filename': filename,
                            'size': stat.st_size,
                            'created': datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S'),
                            'path': file_path
                        })
            
            # Sort by creation time, newest first
            files.sort(key=lambda x: x['created'], reverse=True)
            return files
            
        except Exception as e:
            logger.error(f"Error getting export history: {str(e)}")
            return []
