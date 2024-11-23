# Spam Mail Detection and Management

This project implements a machine learning-based spam email detection system with the ability to manage and unsubscribe from unwanted emails.

## Features
- Spam email detection using Machine Learning
- Email classification (Spam/Ham)
- Automated unsubscription handling
- Email management through IMAP

## Setup
1. Install the required packages:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your email credentials:
```
EMAIL=your_email@example.com
PASSWORD=your_email_password
IMAP_SERVER=imap.example.com
```

3. Run the main script:
```bash
python spam_detector.py
```

## Project Structure
- `spam_detector.py`: Main script for spam detection
- `model_training.py`: ML model training script
- `email_handler.py`: Email processing and unsubscription handling
- `utils.py`: Utility functions
