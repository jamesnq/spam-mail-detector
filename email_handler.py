import imaplib
import email
import os
from dotenv import load_dotenv
import requests
from utils import extract_email_content, extract_unsubscribe_link
import re
import time
from datetime import datetime

class EmailHandler:
    def __init__(self):
        load_dotenv()
        self.email = os.getenv('EMAIL')
        self.password = os.getenv('PASSWORD')
        self.imap_server = os.getenv('IMAP_SERVER')
        self.mail = None
        self.processed_emails = []  # Store information about processed emails
        
    def connect(self):
        """Connect to the email server"""
        try:
            self.mail = imaplib.IMAP4_SSL(self.imap_server)
            self.mail.login(self.email, self.password)
            return True
        except Exception as e:
            print(f"Failed to connect to email server: {str(e)}")
            return False
    
    def is_advertising_or_spam(self, email_message):
        """Check if email is likely advertising or spam"""
        # Common advertising keywords
        ad_keywords = [
            'unsubscribe', 'sale', 'discount', 'offer', 'limited time',
            'promotion', 'deal', 'subscription', 'marketing', 'newsletter',
            'advertisement', 'promotional', 'coupon', 'off selected', 'clearance',
            'special offer', 'exclusive offer', 'best deal', 'free shipping'
        ]
        
        subject = str(email_message.get('subject', '')).lower()
        content = extract_email_content(email_message).lower()
        
        # Check for advertising keywords in subject or content
        for keyword in ad_keywords:
            if keyword in subject or keyword in content:
                return True
        
        # Check for typical marketing email patterns
        marketing_patterns = [
            r'\b\d+%\s+off\b',
            r'\bsave\s+\d+%?\b',
            r'\bfree\s+shipping\b',
            r'\blimited\s+time\b',
            r'\bspecial\s+offer\b',
            r'\bsubscribe\b',
            r'\bnewsletter\b'
        ]
        
        for pattern in marketing_patterns:
            if re.search(pattern, subject) or re.search(pattern, content):
                return True
        
        return False
            
    def get_all_emails(self, folder="INBOX"):
        """
        Retrieve all emails from specified folder
        Returns: List of (email_id, email_message) tuples
        """
        if not self.mail:
            if not self.connect():
                return []
                
        try:
            self.mail.select(folder)
            _, message_numbers = self.mail.search(None, "ALL")
            email_list = []
            
            for num in message_numbers[0].split():
                try:
                    _, msg = self.mail.fetch(num, '(RFC822)')
                    email_message = email.message_from_bytes(msg[0][1])
                    email_list.append((num, email_message))
                except Exception as e:
                    print(f"Error fetching email {num}: {str(e)}")
                    continue
                
            return email_list
            
        except Exception as e:
            print(f"Error retrieving emails: {str(e)}")
            return []
    
    def process_bulk_emails(self, spam_threshold=0.8):
        """Process all emails, unsubscribe from spam/advertising and delete them"""
        start_time = time.time()
        print(f"\nStarting bulk email processing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
        
        # Get all emails
        emails = self.get_all_emails()
        print(f"Found {len(emails)} emails to process")
        
        processed_count = 0
        spam_count = 0
        unsubscribe_count = 0
        delete_count = 0
        
        for email_id, email_message in emails:
            processed_count += 1
            if processed_count % 10 == 0:
                elapsed = time.time() - start_time
                print(f"Processed {processed_count}/{len(emails)} emails... (Time elapsed: {elapsed:.2f}s)")
            
            try:
                # Check if it's spam or advertising
                if self.is_advertising_or_spam(email_message):
                    spam_count += 1
                    subject = email_message['subject']
                    sender = email_message['from']
                    date = email_message['date']
                    
                    print(f"\nFound spam/advertising email:")
                    print(f"Subject: {subject}")
                    print(f"From: {sender}")
                    print(f"Date: {date}")
                    
                    # Store email info
                    email_info = {
                        'subject': subject,
                        'sender': sender,
                        'date': date,
                        'type': 'spam/advertising'
                    }
                    
                    # Try to unsubscribe
                    content = extract_email_content(email_message)
                    unsubscribe_link = extract_unsubscribe_link(content)
                    
                    if unsubscribe_link:
                        try:
                            response = requests.get(unsubscribe_link)
                            if response.status_code == 200:
                                print(f"Successfully unsubscribed using link: {unsubscribe_link}")
                                unsubscribe_count += 1
                                email_info['unsubscribed'] = True
                            else:
                                print(f"Failed to unsubscribe: Status code {response.status_code}")
                                email_info['unsubscribed'] = False
                        except Exception as e:
                            print(f"Error during unsubscription: {str(e)}")
                            email_info['unsubscribed'] = False
                    
                    # Delete the email
                    try:
                        self.mail.store(email_id, '+FLAGS', '\\Deleted')
                        delete_count += 1
                        print(f"Deleted email: {subject}")
                        email_info['deleted'] = True
                    except Exception as e:
                        print(f"Error deleting email: {str(e)}")
                        email_info['deleted'] = False
                    
                    self.processed_emails.append(email_info)
                
            except Exception as e:
                print(f"Error processing email: {str(e)}")
                continue
        
        # Permanently remove deleted messages
        try:
            self.mail.expunge()
        except Exception as e:
            print(f"Error expunging deleted messages: {str(e)}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        print("\n" + "="*50)
        print("BULK PROCESSING SUMMARY")
        print("="*50)
        print(f"Start time: {datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End time: {datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total processing time: {total_time:.2f} seconds")
        print(f"\nTotal emails processed: {processed_count}")
        print(f"Spam/Advertising emails found: {spam_count}")
        print(f"Successful unsubscriptions: {unsubscribe_count}")
        print(f"Emails deleted: {delete_count}")
        
        if spam_count > 0:
            print("\nDetailed Spam/Advertising Email List:")
            print("-"*50)
            for idx, email_info in enumerate(self.processed_emails, 1):
                print(f"\n{idx}. Subject: {email_info['subject']}")
                print(f"   From: {email_info['sender']}")
                print(f"   Date: {email_info['date']}")
                print(f"   Unsubscribed: {'Yes' if email_info.get('unsubscribed', False) else 'No'}")
                print(f"   Deleted: {'Yes' if email_info.get('deleted', False) else 'No'}")
        
        print("\n" + "="*50)
    
    def handle_spam(self, email_id, is_spam, threshold=0.8):
        """Handle individual spam email"""
        if not is_spam or is_spam < threshold:
            return
            
        try:
            # Move to spam folder
            self.mail.store(email_id, '+X-GM-LABELS', '\\Spam')
            
            # Get email content for unsubscription
            _, msg = self.mail.fetch(email_id, '(RFC822)')
            email_message = email.message_from_bytes(msg[0][1])
            content = extract_email_content(email_message)
            
            # Try to unsubscribe
            unsubscribe_link = extract_unsubscribe_link(content)
            if unsubscribe_link:
                try:
                    response = requests.get(unsubscribe_link)
                    if response.status_code == 200:
                        print(f"Successfully unsubscribed using link: {unsubscribe_link}")
                        # Delete the email after unsubscribing
                        self.mail.store(email_id, '+FLAGS', '\\Deleted')
                        self.mail.expunge()
                    else:
                        print(f"Failed to unsubscribe: Status code {response.status_code}")
                except Exception as e:
                    print(f"Error during unsubscription: {str(e)}")
                    
        except Exception as e:
            print(f"Error handling spam email: {str(e)}")
            
    def close(self):
        """Close the email connection"""
        if self.mail:
            self.mail.close()
            self.mail.logout()
