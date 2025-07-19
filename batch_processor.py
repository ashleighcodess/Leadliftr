import pandas as pd
import logging
from typing import Dict, List, Generator
from bs4 import BeautifulSoup
import gc

logger = logging.getLogger(__name__)

class BatchProcessor:
    """Handles large-scale data extraction with memory optimization"""
    
    def __init__(self, batch_size: int = 5000):
        self.batch_size = batch_size
    
    def process_large_dataset(self, html_content: str, field_mappings: Dict, 
                            extraction_config: Dict = None) -> Generator[List[Dict], None, None]:
        """
        Process large datasets in batches to manage memory efficiently
        
        Args:
            html_content: HTML content of the CRM page
            field_mappings: Dictionary mapping field names to CSS selectors
            extraction_config: Additional configuration for extraction
            
        Yields:
            Batches of extracted lead data
        """
        try:
            if not html_content or not field_mappings:
                logger.warning("Missing HTML content or field mappings")
                return
            
            soup = BeautifulSoup(html_content, 'html.parser')
            extraction_config = extraction_config or {}
            container_selector = extraction_config.get('container_selector')
            max_leads = extraction_config.get('max_leads', 500000)
            
            if not container_selector:
                logger.warning("Container selector required for large dataset processing")
                return
            
            # Find all lead containers
            lead_containers = soup.select(container_selector)
            total_containers = min(len(lead_containers), max_leads)
            
            logger.info(f"Processing {total_containers} lead containers in batches of {self.batch_size}")
            
            # Process in batches
            for batch_start in range(0, total_containers, self.batch_size):
                batch_end = min(batch_start + self.batch_size, total_containers)
                batch_containers = lead_containers[batch_start:batch_end]
                
                batch_leads = []
                for i, container in enumerate(batch_containers):
                    lead_data = self._extract_single_lead(container, field_mappings)
                    if lead_data and self._is_valid_lead(lead_data):
                        lead_data['_extraction_index'] = batch_start + i + 1
                        batch_leads.append(lead_data)
                
                logger.info(f"Processed batch {batch_start//self.batch_size + 1}: {len(batch_leads)} valid leads")
                
                # Yield the batch and clean up memory
                yield batch_leads
                
                # Force garbage collection for large datasets
                if batch_start > 0 and batch_start % (self.batch_size * 10) == 0:
                    gc.collect()
                    
        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
            return
    
    def _extract_single_lead(self, container: BeautifulSoup, field_mappings: Dict) -> Dict:
        """Extract data for a single lead from a container element"""
        lead_data = {}
        
        try:
            for field_name, selector_config in field_mappings.items():
                if isinstance(selector_config, str):
                    selector = selector_config
                    attribute = 'text'
                elif isinstance(selector_config, dict):
                    selector = selector_config.get('selector', '')
                    attribute = selector_config.get('attribute', 'text')
                else:
                    continue
                
                if not selector:
                    continue
                
                try:
                    elements = container.select(selector)
                    if elements:
                        element = elements[0]
                        
                        if attribute == 'text':
                            value = element.get_text(strip=True)
                        elif attribute == 'html':
                            value = str(element)
                        else:
                            value = element.get(attribute, '')
                        
                        cleaned_value = self._clean_field_value(value, field_name)
                        if cleaned_value:
                            lead_data[field_name] = cleaned_value
                            
                except Exception as e:
                    logger.debug(f"Error extracting field {field_name}: {str(e)}")
                    continue
            
            return lead_data
            
        except Exception as e:
            logger.error(f"Error extracting single lead: {str(e)}")
            return {}
    
    def _clean_field_value(self, value: str, field_type: str) -> str:
        """Basic field value cleaning"""
        if not value or not isinstance(value, str):
            return None
        
        value = value.strip()
        if not value:
            return None
        
        # Basic cleaning for common field types
        if field_type in ['first_name', 'last_name']:
            return value.title()
        elif field_type == 'number':
            # Keep phone numbers as-is but clean whitespace
            return ' '.join(value.split())
        elif field_type in ['city', 'state']:
            return value.title()
        elif field_type == 'zip_code':
            return value.upper()
        else:
            return value
    
    def _is_valid_lead(self, lead_data: Dict) -> bool:
        """Check if extracted lead data meets minimum requirements"""
        if not lead_data:
            return False
        
        # For large datasets, be more permissive - require at least one field
        return len(lead_data) > 0
    
    def export_large_csv(self, html_content: str, field_mappings: Dict, 
                        extraction_config: Dict, export_config: Dict, 
                        output_path: str) -> int:
        """
        Export large datasets directly to CSV without loading everything into memory
        
        Returns:
            Number of records exported
        """
        try:
            total_records = 0
            first_batch = True
            
            for batch_data in self.process_large_dataset(html_content, field_mappings, extraction_config):
                if not batch_data:
                    continue
                
                # Convert batch to DataFrame
                df = pd.DataFrame(batch_data)
                
                # Apply column ordering and display names
                df = self._format_dataframe(df, export_config)
                
                # Write to CSV (header only on first batch)
                mode = 'w' if first_batch else 'a'
                header = first_batch
                
                df.to_csv(
                    output_path,
                    mode=mode,
                    header=header,
                    index=False,
                    encoding='utf-8-sig'
                )
                
                total_records += len(batch_data)
                first_batch = False
                
                logger.info(f"Exported batch: {len(batch_data)} records (Total: {total_records})")
            
            logger.info(f"Successfully exported {total_records} records to {output_path}")
            return total_records
            
        except Exception as e:
            logger.error(f"Error exporting large CSV: {str(e)}")
            raise
    
    def _format_dataframe(self, df: pd.DataFrame, export_config: Dict) -> pd.DataFrame:
        """Format DataFrame with proper column order and names"""
        try:
            # Define preferred column order
            preferred_order = ['first_name', 'last_name', 'number', 'city', 'state', 'zip_code']
            
            # Reorder columns
            available_columns = []
            for col in preferred_order:
                if col in df.columns:
                    available_columns.append(col)
            
            # Add any remaining columns
            for col in df.columns:
                if col not in available_columns and not col.startswith('_'):
                    available_columns.append(col)
            
            df = df[available_columns]
            
            # Apply display names
            if export_config.get('use_display_names', True):
                display_names = {
                    'first_name': 'First Name',
                    'last_name': 'Last Name',
                    'number': 'Number',
                    'city': 'City',
                    'state': 'State',
                    'zip_code': 'Zip Code'
                }
                
                rename_map = {}
                for col in df.columns:
                    if col in display_names:
                        rename_map[col] = display_names[col]
                    else:
                        rename_map[col] = col.replace('_', ' ').title()
                
                df = df.rename(columns=rename_map)
            
            # Clean data
            df = df.fillna('')
            
            return df
            
        except Exception as e:
            logger.error(f"Error formatting DataFrame: {str(e)}")
            return df