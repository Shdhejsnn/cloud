from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
import re

def generate_summary(text, keywords):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    
    # Increase the number of sentences in the summary
    num_sentences = 7
    summary = summarizer(parser.document, num_sentences)
    
    summary_text = ' '.join([str(sentence) for sentence in summary])
    
    # Highlight keywords
    for keyword in keywords:
        summary_text = re.sub(rf'\b{re.escape(keyword)}\b', f'<strong>{keyword}</strong>', summary_text, flags=re.IGNORECASE)
    
    return summary_text