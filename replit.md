# CRM Lead Extractor

## Overview

This is a Flask-based web application that extracts lead data from CRM systems by connecting to Chrome's remote debugging interface. The application allows users to connect to Chrome, select tabs, configure field mappings, and extract lead data to CSV format.

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

1. **ChromeConnector** (`chrome_connector.py`)
   - Handles connection to Chrome via DevTools Protocol
   - Manages WebSocket connections and tab interactions
   - Uses Chrome's remote debugging port (default 9222)

2. **DataExtractor** (`data_extractor.py`)
   - Extracts lead data from HTML using BeautifulSoup
   - Configurable field mappings with CSS selectors
   - Data validation using regex patterns
   - Supports multiple extraction strategies

3. **CSVExporter** (`csv_exporter.py`)
   - Exports extracted data to CSV format using pandas
   - Handles data formatting and validation
   - Creates exports directory and manages file naming

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

1. **Connection Phase**
   - User starts Chrome with remote debugging enabled
   - Application connects to Chrome on specified port
   - Available tabs are retrieved and displayed

2. **Configuration Phase**
   - User selects target CRM tab
   - Field mappings are configured (manual or preset)
   - Container selectors are defined for data extraction

3. **Extraction Phase**
   - HTML content is retrieved from selected tab
   - BeautifulSoup parses HTML structure
   - CSS selectors extract data based on field mappings
   - Data is validated and formatted

4. **Export Phase**
   - Extracted data is formatted for CSV export
   - File is generated in exports directory
   - User can download the CSV file

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