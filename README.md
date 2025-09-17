# Freepik Image Downloader

A modern, responsive web application for downloading premium images from Freepik with an improved backend system.

## Features

### Frontend
- **Modern Bootstrap 5 UI** with gradient design and animations
- **Responsive design** that works on all devices
- **Real-time status updates** with progress tracking
- **Download history** with statistics
- **AJAX-powered** for smooth user experience
- **Professional styling** with hover effects and micro-interactions

### Backend
- **Improved PHP API** with proper error handling
- **Enhanced Python downloader** with retry logic and logging
- **Database management** with proper indexing and relationships
- **File management** with size validation and MIME type detection
- **Security features** including input validation and sanitization
- **Comprehensive logging** for debugging and monitoring

## Installation

### Prerequisites
- PHP 7.4 or higher
- MySQL 5.7 or higher
- Python 3.8 or higher
- Chrome browser
- ChromeDriver

### Database Setup
1. Import the database schema:
```sql
mysql -u root -p < database.sql
```

### Backend Setup
1. Install Python dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Configure the settings in `backend/improved_downloader.py`:
   - Update database credentials
   - Set your Freepik login credentials
   - Configure ChromeDriver path
   - Set download directory

### Web Server Setup
1. Place files in your web server directory
2. Ensure the `downloads/` directory is writable
3. Configure your web server to serve the `index.html` file

## Usage

### Web Interface
1. Open `index.html` in your browser
2. Paste a Freepik image URL
3. Click "Add to Queue"
4. Monitor the download progress
5. Download the file when ready

### Backend Service
1. Start the Python downloader service:
```bash
cd backend
python improved_downloader.py
```

The service will:
- Automatically login to Freepik
- Monitor the database for new download requests
- Process downloads in the background
- Update status in real-time

## API Endpoints

### POST /api/submit.php
Submit a new download request
- **Parameters**: `url` (Freepik image URL)
- **Response**: JSON with success status and URL code

### GET /api/status.php
Check download status
- **Parameters**: `url_code`
- **Response**: JSON with current status and progress

### GET /api/download.php
Download the processed file
- **Parameters**: `url_code`
- **Response**: File download

### GET /api/stats.php
Get download statistics
- **Response**: JSON with total, completed, and pending counts

## Configuration

### Database Configuration
Edit `api/config.php` to update database settings:
```php
define('DB_HOST', 'localhost');
define('DB_USER', 'root');
define('DB_PASS', '');
define('DB_NAME', 'freepik');
```

### Python Configuration
Edit `backend/improved_downloader.py` CONFIG section:
```python
CONFIG = {
    'db': {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'freepik'
    },
    'freepik': {
        'email': 'your_email@example.com',
        'password': 'your_password'
    }
}
```

## Security Features

- **Input validation** and sanitization
- **SQL injection protection** with prepared statements
- **File type validation** and size limits
- **Domain whitelist** for allowed URLs
- **Error logging** without exposing sensitive information
- **CORS headers** for API security

## File Structure

```
├── index.html              # Main web interface
├── api/
│   ├── config.php         # Configuration and database class
│   ├── submit.php         # Submit download request
│   ├── status.php         # Check download status
│   ├── download.php       # Download file
│   └── stats.php          # Get statistics
├── backend/
│   ├── improved_downloader.py  # Enhanced Python downloader
│   └── requirements.txt        # Python dependencies
├── downloads/             # Downloaded files directory
├── database.sql          # Database schema
└── README.md            # This file
```

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   - Download ChromeDriver from https://chromedriver.chromium.org/
   - Update the path in the configuration

2. **Database connection failed**
   - Verify MySQL is running
   - Check database credentials
   - Ensure database exists

3. **Downloads not working**
   - Check Freepik login credentials
   - Verify download directory permissions
   - Check Chrome browser compatibility

4. **CAPTCHA issues**
   - The system will pause for manual CAPTCHA solving
   - Keep the browser window visible during operation

### Logs
- Python logs: `backend/downloader.log`
- PHP errors: Check your web server error logs
- Database queries: Enable MySQL query logging if needed

## License

This project is for educational purposes only. Please respect Freepik's terms of service and only download content you have the right to use.

## Support

For issues and questions:
1. Check the logs for error messages
2. Verify all configuration settings
3. Ensure all dependencies are installed
4. Test with a simple Freepik URL first