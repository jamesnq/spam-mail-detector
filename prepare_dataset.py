import pandas as pd
import requests
import os

def download_dataset():
    """Download the Spam SMS Collection dataset"""
    # URL for the dataset
    url = "https://raw.githubusercontent.com/mohitgupta-omg/Kaggle-SMS-Spam-Collection-Dataset-/master/spam.csv"
    
    print("Downloading dataset...")
    response = requests.get(url)
    
    if response.status_code == 200:
        # Save the dataset
        with open("spam_dataset.csv", "wb") as f:
            f.write(response.content)
        print("Dataset downloaded successfully!")
        return True
    else:
        print("Failed to download dataset")
        return False

def prepare_dataset():
    """Prepare the dataset for training"""
    # Read the dataset
    df = pd.read_csv("spam_dataset.csv", encoding='latin-1')
    
    # Rename columns
    df = df[['v1', 'v2']]
    df.columns = ['label', 'text']
    
    # Convert spam/ham to binary labels
    df['label'] = df['label'].map({'ham': 0, 'spam': 1})
    
    # Save the processed dataset
    df.to_csv("processed_spam_dataset.csv", index=False)
    print("Dataset prepared and saved as 'processed_spam_dataset.csv'")

def main():
    if not os.path.exists("spam_dataset.csv"):
        if not download_dataset():
            return
    
    prepare_dataset()
    print("\nDataset is ready for training!")
    print("You can now run 'python model_training.py' to train the spam detection model.")

if __name__ == "__main__":
    main()
