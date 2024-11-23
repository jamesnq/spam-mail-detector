import nltk

def download_nltk_data():
    """Download required NLTK data"""
    required_packages = [
        'punkt',
        'stopwords',
        'wordnet',
        'punkt_tab',
        'averaged_perceptron_tagger'
    ]
    
    for package in required_packages:
        print(f"Downloading {package}...")
        nltk.download(package)
        
if __name__ == "__main__":
    download_nltk_data()
    print("NLTK setup complete!")
