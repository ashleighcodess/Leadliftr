import re
import logging
from typing import List, Dict, Tuple, Optional

logger = logging.getLogger(__name__)

class LeadScrubber:
    """Lead scrubbing service to filter out landlines, toll-free, and VOIP numbers"""
    
    def __init__(self):
        # Known landline prefixes (NPA-NXX format)
        self.LANDLINE_PREFIXES = {
            "205-222", "205-333", "212-222", "305-222", "407-222", "415-222", "713-222", 
            "312-222", "404-222", "503-222", "602-222", "702-222", "818-222", "919-222",
            "646-346", "718-455", "718-599", "914-220", "310-454", "212-555", "917-324", "516-466",
            "847-555", "630-620", "773-522", "312-698", "708-682", "815-759", "847-329",
            "203-234", "315-448", "518-474", "570-387", "631-444", "716-848", "718-422", "845-334",
            "860-486", "914-255", "978-658", "212-970", "214-220", "312-906", "512-465", "713-465",
            "972-465", "202-785", "305-810", "407-814", "504-861", "602-627", "702-486", "808-586"
        }
        
        # Toll-free prefixes
        self.TOLL_FREE_PREFIXES = {"800", "888", "877", "866", "855", "844", "833", "822"}
        
        # Common VOIP area codes
        self.VOIP_AREA_CODES = {"347", "646", "650", "678", "702", "704", "716", "818", "919"}
        
        # Litigation/spam patterns to filter out
        self.LITIGATION_PATTERNS = [
            r'legal',
            r'litigation',
            r'lawsuit',
            r'attorney',
            r'lawyer',
            r'court',
            r'settlement',
            r'claim',
            r'damages'
        ]
    
    def clean_phone_number(self, number: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Clean and standardize phone number format
        
        Returns:
            Tuple of (prefix in NPA-NXX format, area code)
        """
        if not number or not isinstance(number, str):
            return None, None
            
        # Check for extensions (usually landlines)
        if "x" in number.lower() or "ext" in number.lower():
            return None, None
        
        # Remove all non-numeric characters
        cleaned = re.sub(r"[^\d]", "", number)
        
        if len(cleaned) == 10:  # Standard US number
            return f"{cleaned[:3]}-{cleaned[3:6]}", cleaned[:3]
        elif len(cleaned) == 11 and cleaned.startswith("1"):  # US number with country code
            return f"{cleaned[1:4]}-{cleaned[4:7]}", cleaned[1:4]
        
        return None, None
    
    def is_landline_or_unwanted(self, phone_number: str) -> Tuple[bool, str]:
        """
        Check if phone number is landline, toll-free, or VOIP
        
        Returns:
            Tuple of (should_filter, reason)
        """
        if not phone_number:
            return True, "Empty number"
            
        prefix, area_code = self.clean_phone_number(phone_number)
        
        if not prefix or not area_code:
            return True, "Invalid format"
        
        # Check landline prefixes
        if prefix in self.LANDLINE_PREFIXES:
            return True, "Known landline prefix"
        
        # Check toll-free numbers
        if area_code in self.TOLL_FREE_PREFIXES:
            return True, "Toll-free number"
        
        # Check VOIP area codes
        if area_code in self.VOIP_AREA_CODES:
            return True, "VOIP area code"
        
        return False, "Valid mobile number"
    
    def check_litigation_risk(self, lead_data: Dict) -> Tuple[bool, str]:
        """
        Check if lead data contains litigation-related keywords
        
        Returns:
            Tuple of (is_risky, reason)
        """
        # Convert all values to lowercase string for checking
        text_content = ""
        for key, value in lead_data.items():
            if value and isinstance(value, str):
                text_content += f" {value.lower()}"
        
        # Check for litigation patterns
        for pattern in self.LITIGATION_PATTERNS:
            if re.search(pattern, text_content, re.IGNORECASE):
                return True, f"Contains litigation keyword: {pattern}"
        
        return False, "No litigation risk detected"
    
    def scrub_leads(self, leads: List[Dict], scrub_config: Dict = None) -> Dict:
        """
        Scrub leads based on phone number quality and litigation risk
        
        Args:
            leads: List of lead dictionaries
            scrub_config: Configuration for scrubbing options
        
        Returns:
            Dictionary with scrubbing results
        """
        scrub_config = scrub_config or {}
        
        filter_landlines = scrub_config.get('filter_landlines', True)
        filter_litigation = scrub_config.get('filter_litigation', False)
        phone_field = scrub_config.get('phone_field', 'number')
        
        clean_leads = []
        filtered_stats = {
            'original_count': len(leads),
            'filtered_landlines': 0,
            'filtered_litigation': 0,
            'clean_count': 0,
            'filter_reasons': {}
        }
        
        logger.info(f"Starting lead scrubbing for {len(leads)} leads")
        
        for lead in leads:
            should_filter = False
            filter_reason = None
            
            # Check phone number quality
            if filter_landlines and phone_field in lead:
                phone_number = lead[phone_field]
                is_unwanted, phone_reason = self.is_landline_or_unwanted(phone_number)
                
                if is_unwanted:
                    should_filter = True
                    filter_reason = f"Phone: {phone_reason}"
                    filtered_stats['filtered_landlines'] += 1
            
            # Check litigation risk
            if not should_filter and filter_litigation:
                is_risky, litigation_reason = self.check_litigation_risk(lead)
                
                if is_risky:
                    should_filter = True
                    filter_reason = f"Litigation: {litigation_reason}"
                    filtered_stats['filtered_litigation'] += 1
            
            # Add to results
            if not should_filter:
                clean_leads.append(lead)
                filtered_stats['clean_count'] += 1
            else:
                # Track filter reasons
                if filter_reason not in filtered_stats['filter_reasons']:
                    filtered_stats['filter_reasons'][filter_reason] = 0
                filtered_stats['filter_reasons'][filter_reason] += 1
        
        logger.info(f"Lead scrubbing complete: {len(clean_leads)} clean leads from {len(leads)} original")
        
        return {
            'clean_leads': clean_leads,
            'stats': filtered_stats
        }
    
    def get_scrubbing_summary(self, stats: Dict) -> str:
        """Generate human-readable summary of scrubbing results"""
        summary_parts = []
        
        original = stats['original_count']
        clean = stats['clean_count']
        filtered = original - clean
        
        summary_parts.append(f"Processed {original:,} leads")
        summary_parts.append(f"Kept {clean:,} clean leads ({clean/original*100:.1f}%)")
        
        if filtered > 0:
            summary_parts.append(f"Filtered out {filtered:,} leads ({filtered/original*100:.1f}%)")
            
            if stats['filtered_landlines'] > 0:
                summary_parts.append(f"  • {stats['filtered_landlines']:,} landlines/toll-free/VOIP")
            
            if stats['filtered_litigation'] > 0:
                summary_parts.append(f"  • {stats['filtered_litigation']:,} litigation risks")
        
        return "\n".join(summary_parts)