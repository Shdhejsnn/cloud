import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import string

nltk.download('punkt')
nltk.download('stopwords')

def preprocess_text(text):
    # Tokenize the text
    tokens = word_tokenize(text)
    
    # Load stop words
    stop_words = set(stopwords.words('english'))
    
    # Remove stop words and punctuation from tokens
    filtered_tokens = [
        word for word in tokens 
        if word.lower() not in stop_words and word not in string.punctuation
    ]
    
    return filtered_tokens
