import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Download required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

def preprocess_text(text):
    """
    Preprocess the email text by removing special characters, converting to lowercase,
    removing stopwords, and lemmatizing words.
    """
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [token for token in tokens if token not in stop_words]
    
    # Lemmatization
    lemmatizer = WordNetLemmatizer()
    tokens = [lemmatizer.lemmatize(token) for token in tokens]
    
    return ' '.join(tokens)

def extract_unsubscribe_link(email_body):
    """
    Extract unsubscribe link from email body using regular expressions.
    """
    # Common patterns for unsubscribe links
    patterns = [
        r'https?://[^\s<>"]+?/unsubscribe[^\s<>"]*',
        r'https?://[^\s<>"]+?/opt-out[^\s<>"]*',
        r'https?://[^\s<>"]+?/remove[^\s<>"]*'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, email_body, re.IGNORECASE)
        if match:
            return match.group(0)
    
    return None

def extract_email_content(email_message):
    """
    Extract the content from email message object.
    """
    content = ""
    if email_message.is_multipart():
        for part in email_message.walk():
            if part.get_content_type() == "text/plain":
                content += part.get_payload(decode=True).decode()
    else:
        content = email_message.get_payload(decode=True).decode()
    
    return content
