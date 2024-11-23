import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report
import pickle
from utils import preprocess_text

class SpamDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.classifier = MultinomialNB()
        
    def train(self, data_path):
        """
        Train the spam detection model using the provided dataset.
        Expected CSV format: 'text' and 'label' columns
        """
        # Load and preprocess the data
        df = pd.read_csv(data_path)
        
        # Preprocess the text
        df['processed_text'] = df['text'].apply(preprocess_text)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            df['processed_text'],
            df['label'],
            test_size=0.2,
            random_state=42
        )
        
        # Vectorize the text
        X_train_vectorized = self.vectorizer.fit_transform(X_train)
        X_test_vectorized = self.vectorizer.transform(X_test)
        
        # Train the classifier
        self.classifier.fit(X_train_vectorized, y_train)
        
        # Evaluate the model
        y_pred = self.classifier.predict(X_test_vectorized)
        print("\nModel Performance:")
        print(classification_report(y_test, y_pred))
        
    def predict(self, text):
        """
        Predict if a given text is spam or not.
        Returns: probability of being spam
        """
        processed_text = preprocess_text(text)
        text_vectorized = self.vectorizer.transform([processed_text])
        return self.classifier.predict_proba(text_vectorized)[0][1]
    
    def save_model(self, model_path='spam_model.pkl', vectorizer_path='vectorizer.pkl'):
        """Save the trained model and vectorizer"""
        with open(model_path, 'wb') as f:
            pickle.dump(self.classifier, f)
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(self.vectorizer, f)
    
    def load_model(self, model_path='spam_model.pkl', vectorizer_path='vectorizer.pkl'):
        """Load the trained model and vectorizer"""
        with open(model_path, 'rb') as f:
            self.classifier = pickle.load(f)
        with open(vectorizer_path, 'rb') as f:
            self.vectorizer = pickle.load(f)

if __name__ == "__main__":
    # Example usage
    detector = SpamDetector()
    
    # Train the model with the prepared dataset
    print("Training spam detection model...")
    detector.train("processed_spam_dataset.csv")
    
    # Save the trained model
    print("\nSaving trained model...")
    detector.save_model()
    print("Model saved successfully! You can now run spam_detector.py")
