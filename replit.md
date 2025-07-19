# CRM Lead Extractor

## Overview

This is a Flask-based web application that extracts lead data from CRM systems using a simple HTML paste interface. The application allows users to paste HTML content, configure field mappings, extract lead data, and export to CSV format. It now includes an optional lead scrubbing feature to filter out landlines, toll-free numbers, VOIP numbers, and litigation-related leads for higher quality mobile leads.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Framework**: Vanilla JavaScript with Bootstrap 5 for UI components
- **Structure**: Single-page application (SPA) with event-driven interactions
- **Styling**: Custom CSS with Bootstrap framework and Font Awesome icons
- **Communication**: RESTful API calls to Flask backend

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Structure**: Modular design with separate classes for different responsibilities
- **API**: RESTful endpoints for Chrome connection and data extraction
- **Logging**: Python logging module for debugging and monitoring

## Key Components

### Core Classes

1. **DataExtractor** (`data_extractor.py`)
   - Extracts lead data from HTML using BeautifulSoup
   - Configurable field mappings with CSS selectors
   - Data validation using regex patterns
   - Supports multiple extraction strategies
   - Handles up to 500,000 leads efficiently

2. **CSVExporter** (`csv_exporter.py`)
   - Exports extracted data to CSV format using pandas
   - Handles data formatting and validation
   - Creates exports directory and manages file naming

3. **BatchProcessor** (`batch_processor.py`)
   - Memory-efficient processing for large datasets (>10,000 leads)
   - Processes data in configurable batch sizes (default 5,000)
   - Direct CSV writing to avoid memory accumulation
   - Automatic garbage collection for performance

4. **LeadScrubber** (`lead_scrubber.py`)
   - Filters out landlines, toll-free, and VOIP numbers
   - Detects litigation-related keywords in lead data
   - Provides scrubbing statistics and summaries
   - Improves lead quality for mobile-focused campaigns

### Configuration System

- **Field Mappings** (`config/field_mappings.json`)
  - Pre-configured mappings for popular CRM systems (Salesforce, HubSpot, Pipedrive)
  - Generic fallback mappings for unknown systems
  - CSS selector-based field identification

### Frontend Components

- **Main Interface** (`templates/index.html`)
  - Step-by-step wizard interface
  - Real-time connection status
  - Dynamic field mapping configuration

- **JavaScript Controller** (`static/script.js`)
  - Manages Chrome connection workflow
  - Handles field mapping configuration
  - Coordinates data extraction and export

## Data Flow

1. **HTML Input Phase**
   - User pastes HTML content from CRM system
   - Application analyzes HTML structure for container suggestions
   - Field mappings are configured (manual or preset)

2. **Configuration Phase**
   - Container selectors are defined for data extraction
   - Maximum lead count is set (up to 500,000)
   - Optional lead scrubbing settings are configured

3. **Extraction Phase**
   - BeautifulSoup parses HTML structure
   - CSS selectors extract data based on field mappings
   - Data is validated and formatted
   - Large datasets use batch processing for memory efficiency

4. **Scrubbing Phase (Optional)**
   - Phone numbers are analyzed for landline/VOIP patterns
   - Lead data is checked for litigation-related keywords
   - Unwanted leads are filtered out based on user settings

5. **Export Phase**
   - Extracted data is formatted for CSV export
   - File is generated and served to user
   - Data is immediately cleared from memory after download

## External Dependencies

### Python Packages
- **Flask**: Web framework for backend API
- **BeautifulSoup4**: HTML parsing and data extraction
- **pandas**: Data manipulation and CSV export
- **requests**: HTTP client for Chrome debugging API
- **websocket-client**: WebSocket communication with Chrome

### Frontend Libraries
- **Bootstrap 5**: UI framework and responsive design
- **Font Awesome**: Icon library for visual elements

### Browser Integration
- **Chrome DevTools Protocol**: Remote debugging interface
- **WebSocket**: Real-time communication with browser tabs

## Deployment Strategy

### Development Setup
- Flask development server for local testing
- Static file serving through Flask
- Chrome browser with remote debugging enabled

### Production Considerations
- WSGI server (e.g., Gunicorn) for production deployment
- Reverse proxy (e.g., Nginx) for static file serving
- Environment-based configuration for different deployments
- Secure Chrome connection handling

### File Structure
- Static assets served from `/static/` directory
- Templates rendered from `/templates/` directory
- Exports generated in `/exports/` directory
- Configuration files in `/config/` directory

### Security Notes
- Chrome remote debugging should be restricted to localhost
- Input validation for all user-provided selectors
- File path validation for export functionality
- CORS considerations for cross-origin requests