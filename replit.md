# Invoice Generator Application

## Overview

This is a Flask-based invoice generation system that allows users to create, manage, and download professional invoices. The application supports bilingual (English/Arabic) invoice generation with PDF export capabilities. It uses SQLite for data persistence and provides a Bootstrap-based user interface for invoice management.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Web Framework
- **Technology**: Flask
- **Rationale**: Lightweight Python web framework suitable for small to medium applications
- **Structure**: Single-file application (app.py) with template-based rendering
- **Routing**: Simple route-based navigation between invoice creation and listing views

### Frontend Architecture
- **UI Framework**: Bootstrap 5.3.0 (CDN-based)
- **Styling Approach**: Custom CSS with gradient backgrounds and card-based layouts
- **Templates**: Jinja2 templating engine (Flask default)
  - `index.html` - Invoice creation form
  - `list.html` - Invoice listing and management
- **Design Pattern**: Traditional server-side rendering (no JavaScript framework)

### Backend Architecture
- **Application Pattern**: Monolithic Flask application
- **Entry Point**: `app.py` - Main application with full functionality
- **Data Flow**: Form submission → Database storage → PDF generation
- **Routes**:
  - `/` - Home page with invoice creation form
  - `/create` - Process form submission and create invoice
  - `/invoices` - List all invoices
  - `/download/<id>` - Download PDF for specific invoice

### Data Storage
- **Database**: SQLite
- **ORM**: Flask-SQLAlchemy
- **Schema**: Single `Invoice` model with fields:
  - Client information (name, address)
  - Item details (name, quantity, price, total)
  - Invoice metadata (type, creation date)
- **Database File**: `invoices.db` (local file-based storage)
- **Rationale**: SQLite chosen for simplicity and zero-configuration deployment

### PDF Generation
- **Library**: ReportLab
- **Features**: 
  - Custom page layouts using canvas-based drawing
  - Support for Arabic text via `arabic-reshaper` and `python-bidi`
  - Font management using DejaVu Sans fonts
- **Text Processing**: 
  - Arabic text reshaping for proper right-to-left display
  - BiDi algorithm implementation for mixed-direction text
- **Output**: In-memory PDF generation using BytesIO buffers

### Internationalization
- **Arabic Support**: Full Arabic text rendering in PDFs
- **Font Strategy**: System fonts from `/usr/share/fonts/truetype/dejavu/`
- **Text Processing Pipeline**: Raw text → Arabic reshaper → BiDi algorithm → PDF rendering

### Authentication & Authorization
- **Current State**: No authentication implemented
- **Access Control**: Open access to all features
- **Consideration**: Single-user application design

## External Dependencies

### Python Packages
- **Flask** - Web framework
- **Flask-SQLAlchemy** - Database ORM integration
- **ReportLab** - PDF generation library
- **arabic-reshaper** - Arabic text processing
- **python-bidi** - Bidirectional text algorithm implementation

### Frontend Dependencies
- **Bootstrap 5.3.0** - CSS framework (CDN)
- Served via CDN (https://cdn.jsdelivr.net)

### System Dependencies
- **DejaVu Sans Fonts** - Required for Arabic text support in PDFs
- Expected location: `/usr/share/fonts/truetype/dejavu/`

### Database
- **SQLite** - Embedded database (no external server required)
- Database file stored locally in application directory

### Third-Party Services
- **None currently integrated**
- Application runs entirely self-contained with no external API calls or cloud services