# topic_modeling.py

from gensim import corpora, models
from preprocessing import preprocess_text
import re  # Import the re module

def extract_topics(texts, num_topics=5, passes=15):
    """
    Extract topics from a list of texts using LDA (Latent Dirichlet Allocation).

    Parameters:
    - texts: List of strings, each representing a document or text to analyze.
    - num_topics: Number of topics to extract.
    - passes: Number of passes over the corpus during training.

    Returns:
    - List of dictionaries where each dictionary represents a topic with its ID, top words, and description.
    """
    # Preprocess and tokenize texts
    tokenized_texts = [preprocess_text(text) for text in texts]

    # Create a dictionary and corpus needed for LDA
    dictionary = corpora.Dictionary(tokenized_texts)
    corpus = [dictionary.doc2bow(text) for text in tokenized_texts]

    # Train LDA model
    lda_model = models.LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=passes)

    # Extract topics
    topics = lda_model.print_topics()
    
    # Format topics for return
    formatted_topics = []
    for i, topic in enumerate(topics):
        # Parse the topic string
        topic_string = topic[1]
        top_words = []
        for item in topic_string.split(' + '):
            weight_word = re.match(r"(\d*\.\d+|\d+)\*\"(.+)\"", item)
            if weight_word:
                weight = float(weight_word.group(1))
                word = weight_word.group(2)
                top_words.append({'word': word, 'weight': weight})
        
        description = "Description not provided"  # You can add logic to generate descriptions
        formatted_topics.append({
            'topic_id': i,
            'top_words': top_words,
            'description': description
        })
    
    return formatted_topics
