from model_training import SpamDetector
from email_handler import EmailHandler
import time
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def main():
    # Initialize the spam detector and email handler
    detector = SpamDetector()
    email_handler = EmailHandler()
    
    # Load the trained model if it exists
    if os.path.exists('spam_model.pkl'):
        detector.load_model()
    else:
        logger.error("No trained model found. Training new model...")
        # Train model with provided dataset
        detector.train("processed_spam_dataset.csv")
        detector.save_model()
    
    logger.info("Starting spam detection service...")
    
    try:
        # First, process all existing spam/advertising emails
        logger.info("\nProcessing existing emails...")
        email_handler.process_bulk_emails()
        
        logger.info("\nStarting continuous monitoring...")
        while True:
            # Connect to email
            if not email_handler.connect():
                logger.error("Failed to connect to email. Retrying in 60 seconds...")
                time.sleep(60)
                continue
            
            # Get recent emails
            emails = email_handler.get_all_emails()
            
            # Process each email
            for email_id, email_message in emails:
                content = extract_email_content(email_message)
                # Predict spam probability
                spam_prob = detector.predict(content)
                
                # Handle spam emails
                email_handler.handle_spam(email_id, spam_prob)
                
            # Close connection
            email_handler.close()
            
            # Wait before next check
            logger.info("Waiting 5 minutes before next check...")
            time.sleep(300)
            
    except KeyboardInterrupt:
        logger.info("\nStopping spam detection service...")
        email_handler.close()
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        email_handler.close()
        # On Heroku, exit on error to trigger restart
        sys.exit(1)

if __name__ == "__main__":
    main()
