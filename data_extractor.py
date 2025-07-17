from bs4 import BeautifulSoup
import re
import logging
from typing import Dict, List, Optional, Any
import json

logger = logging.getLogger(__name__)

class DataExtractor:
    """Extracts lead data from CRM pages using configurable field mappings"""
    
    def __init__(self):
        self.validation_patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^[\+]?[1-9][\d\s\-\(\)]{7,15}$',
            'name': r'^[a-zA-Z\s\-\'\.]{2,50}$',
            'company': r'^[a-zA-Z0-9\s\-\&\.\,\(\)]{1,100}$'
        }
    
    def extract_leads(self, html_content: str, field_mappings: Dict, extraction_config: Dict = None) -> List[Dict]:
        """
        Extract lead data from HTML content using provided field mappings
        
        Args:
            html_content: HTML content of the CRM page
            field_mappings: Dictionary mapping field names to CSS selectors
            extraction_config: Additional configuration for extraction
        
        Returns:
            List of dictionaries containing extracted lead data
        """
        try:
            if not html_content or not field_mappings:
                logger.warning("Missing HTML content or field mappings")
                return []
            
            soup = BeautifulSoup(html_content, 'html.parser')
            leads = []
            
            extraction_config = extraction_config or {}
            container_selector = extraction_config.get('container_selector')
            max_leads = extraction_config.get('max_leads', 100)
            
            # If container selector is provided, find all lead containers
            if container_selector:
                lead_containers = soup.select(container_selector)
                logger.info(f"Found {len(lead_containers)} lead containers using selector: {container_selector}")
                
                for i, container in enumerate(lead_containers[:max_leads]):
                    lead_data = self._extract_single_lead(container, field_mappings)
                    if lead_data and self._is_valid_lead(lead_data):
                        lead_data['_extraction_index'] = i + 1
                        leads.append(lead_data)
            else:
                # Extract single lead from entire page
                lead_data = self._extract_single_lead(soup, field_mappings)
                if lead_data and self._is_valid_lead(lead_data):
                    lead_data['_extraction_index'] = 1
                    leads.append(lead_data)
            
            logger.info(f"Successfully extracted {len(leads)} valid leads")
            return leads
            
        except Exception as e:
            logger.error(f"Error extracting leads: {str(e)}")
            return []
    
    def _extract_single_lead(self, container: BeautifulSoup, field_mappings: Dict) -> Dict:
        """Extract data for a single lead from a container element"""
        lead_data = {}
        
        try:
            for field_name, selector_config in field_mappings.items():
                if isinstance(selector_config, str):
                    # Simple CSS selector
                    selector = selector_config
                    attribute = 'text'
                elif isinstance(selector_config, dict):
                    # Advanced configuration
                    selector = selector_config.get('selector', '')
                    attribute = selector_config.get('attribute', 'text')
                else:
                    continue
                
                if not selector:
                    continue
                
                try:
                    elements = container.select(selector)
                    if elements:
                        element = elements[0]  # Take first match
                        
                        if attribute == 'text':
                            value = element.get_text(strip=True)
                        elif attribute == 'html':
                            value = str(element)
                        else:
                            value = element.get(attribute, '')
                        
                        # Clean and validate the extracted value
                        cleaned_value = self._clean_field_value(value, field_name)
                        if cleaned_value:
                            lead_data[field_name] = cleaned_value
                            
                except Exception as e:
                    logger.debug(f"Error extracting field {field_name} with selector {selector}: {str(e)}")
                    continue
            
            return lead_data
            
        except Exception as e:
            logger.error(f"Error extracting single lead: {str(e)}")
            return {}
    
    def _clean_field_value(self, value: str, field_type: str) -> Optional[str]:
        """Clean and validate a field value based on its type"""
        if not value or not isinstance(value, str):
            return None
        
        # Basic cleaning
        value = value.strip()
        value = re.sub(r'\s+', ' ', value)  # Replace multiple whitespace with single space
        
        if not value:
            return None
        
        # Type-specific cleaning and validation
        if field_type == 'email':
            # Extract email from text that might contain other content
            email_match = re.search(self.validation_patterns['email'], value)
            if email_match:
                return email_match.group().lower()
            return None
            
        elif field_type == 'phone':
            # Clean phone number
            phone = re.sub(r'[^\d\+\-\(\)\s]', '', value)
            phone = re.sub(r'\s+', ' ', phone).strip()
            if re.match(self.validation_patterns['phone'], phone):
                return phone
            return None
            
        elif field_type == 'name':
            # Clean name field
            name = re.sub(r'[^\w\s\-\'\.]', '', value)
            name = name.title().strip()
            if len(name) >= 2 and re.match(self.validation_patterns['name'], name):
                return name
            return None
            
        elif field_type == 'company':
            # Clean company name
            company = value.strip()
            if len(company) >= 1 and re.match(self.validation_patterns['company'], company):
                return company
            return None
            
        else:
            # Generic field - basic cleaning only
            return value if len(value.strip()) > 0 else None
    
    def _is_valid_lead(self, lead_data: Dict) -> bool:
        """Check if extracted lead data meets minimum requirements"""
        if not lead_data:
            return False
        
        # Require at least one of: name, email, or company
        required_fields = ['name', 'email', 'company']
        has_required_field = any(field in lead_data and lead_data[field] for field in required_fields)
        
        return has_required_field
    
    def analyze_page_structure(self, html_content: str) -> Dict:
        """
        Analyze page structure to suggest field mappings
        
        Returns suggestions for CSS selectors based on common patterns
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            suggestions = {
                'potential_containers': [],
                'field_suggestions': {},
                'analysis': {}
            }
            
            # Look for common container patterns
            container_patterns = [
                'tr',  # Table rows
                '.lead', '.contact', '.record',  # Common CSS classes
                '[data-lead]', '[data-contact]',  # Data attributes
                '.row', '.item', '.entry'  # Generic container classes
            ]
            
            for pattern in container_patterns:
                elements = soup.select(pattern)
                if len(elements) > 1:  # Multiple similar elements suggest containers
                    suggestions['potential_containers'].append({
                        'selector': pattern,
                        'count': len(elements),
                        'sample_text': elements[0].get_text(strip=True)[:100] if elements else ''
                    })
            
            # Look for common field patterns
            field_patterns = {
                'email': ['input[type="email"]', '[data-field="email"]', '.email', 'a[href^="mailto:"]'],
                'phone': ['input[type="tel"]', '[data-field="phone"]', '.phone', 'a[href^="tel:"]'],
                'name': ['[data-field="name"]', '.name', '.contact-name', 'h1, h2, h3'],
                'company': ['[data-field="company"]', '.company', '.organization', '.company-name']
            }
            
            for field_type, patterns in field_patterns.items():
                field_suggestions = []
                for pattern in patterns:
                    elements = soup.select(pattern)
                    if elements:
                        field_suggestions.append({
                            'selector': pattern,
                            'count': len(elements),
                            'sample_value': elements[0].get_text(strip=True)[:50] if elements else ''
                        })
                
                if field_suggestions:
                    suggestions['field_suggestions'][field_type] = field_suggestions
            
            # General analysis
            suggestions['analysis'] = {
                'total_elements': len(soup.find_all()),
                'forms': len(soup.find_all('form')),
                'tables': len(soup.find_all('table')),
                'lists': len(soup.find_all(['ul', 'ol'])),
                'has_data_attributes': len(soup.select('[data-*]')) > 0
            }
            
            return suggestions
            
        except Exception as e:
            logger.error(f"Error analyzing page structure: {str(e)}")
            return {
                'error': str(e),
                'potential_containers': [],
                'field_suggestions': {},
                'analysis': {}
            }
