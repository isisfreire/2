# 🐔 Broiler Farm Manager - Standalone Application

## Quick Start

### Linux/Mac
```bash
./start_broiler_manager.sh
```

### Manual Start
```bash
python3 BroilerFarmManager.py
```

## What This Is
A completely standalone, offline broiler chicken farm management application that includes:

✅ **Entry & Exit Date Tracking** - Track when chicks arrive and when batches are closed
✅ **Viability Calculations** - Monitor how many chickens are successfully caught
✅ **Feed Conversion Analysis** - Calculate FCR and feed efficiency
✅ **Cost Management** - Track all costs including feed, medicine, bedding
✅ **PDF Report Generation** - Professional reports with all batch data
✅ **Handler Performance** - Track and rank handler performance
✅ **Shed Management** - Organize by shed numbers and locations
✅ **Flexible Age Input** - No restrictions on chicken removal ages

## Features Added
- **Date Management**: Entry date, exit date, and batch duration calculation
- **Viability Tracking**: Total chickens caught and viability rate percentage  
- **Age Flexibility**: Removed 35-60 day restrictions for chicken removal
- **Enhanced Reports**: All new data included in PDF reports

## Technical Details
- **Backend**: FastAPI server with SQLite database (completely offline)
- **Frontend**: React web application (runs in your browser)
- **Database**: Local SQLite file - all data stays on your computer
- **Reports**: Generated locally in `exports/` folder
- **Size**: ~40MB executable + ~100MB frontend build

## Data Storage
- **Database File**: `broiler_data.db` (created automatically)
- **Reports**: `exports/` folder (created automatically)
- **Configuration**: No external configuration needed

## System Requirements
- Python 3.7+ (for frontend server)
- Modern web browser (Chrome, Firefox, Safari, Edge)
- 200MB free disk space
- No internet connection required

## How It Works
1. The application starts a local backend server (port 8001)
2. A local web server serves the frontend (port 3000)  
3. Your browser opens automatically to the application
4. All data is stored locally in SQLite database
5. Reports are generated as PDF files in the exports folder

## Troubleshooting
- **Port conflicts**: If ports 3000 or 8001 are in use, close other applications
- **Python not found**: Install Python 3.7+ from python.org
- **Permission denied**: Run `chmod +x BroilerBackend` to make executable
- **Browser doesn't open**: Manually navigate to http://127.0.0.1:3000

## Support
This is a completely self-contained application. All features from the web version are included:
- Batch calculations with enhanced date tracking
- Handler and shed management
- Performance analytics and rankings
- Professional PDF report generation
- Cost breakdown analysis
- Feed conversion calculations
- Mortality tracking
- Viability calculations

No internet connection or external services required!
