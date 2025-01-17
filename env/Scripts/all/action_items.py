import spacy

# Load spaCy's English model
nlp = spacy.load('en_core_web_sm')

def extract_action_items(text):
    # Preprocess text with spaCy
    doc = nlp(text)

    # Initialize categories
    action_items = {
        'tasks': set(),
        'decisions': set(),
        'follow_ups': set()
    }

    # Define common words/phrases to filter out
    common_words = {'the', 'on', 'a', 'an', 'and', 'of', 'in', 'to', 'for', 'with','thank','welcome','let'}
    stop_words = set(nlp.Defaults.stop_words)

    # Extract action items based on patterns and entities
    for sent in doc.sents:
        action = None
        for token in sent:
            if token.pos_ == 'VERB' and token.dep_ in ['ROOT', 'dobj']:
                action = f"{token.lemma_} {token.head.lemma_}".strip()
                if 'review' in token.lemma_ or 'discuss' in token.lemma_:
                    action_items['decisions'].add(action)
                elif 'prepare' in token.lemma_ or 'finalize' in token.lemma_:
                    action_items['tasks'].add(action)
                else:
                    action_items['follow_ups'].add(action)
                
        # Extract named entities for potential action items
        for ent in sent.ents:
            if ent.label_ in ['PERSON', 'DATE', 'TIME', 'ORG']:
                action_items['follow_ups'].add(f"Follow up on {ent.text}")

    # Remove common words from follow-ups
    filtered_follow_ups = {
        phrase for phrase in action_items['follow_ups']
        if not any(word in common_words or word.lower() in stop_words for word in phrase.lower().split())
    }

    # Convert sets to lists and remove duplicates
    all_keywords = sorted(set(
        action_items['tasks'] |
        action_items['decisions'] |
        filtered_follow_ups
    ))

    # Ensure each keyword only appears once and sort them
    unique_keywords = set()
    for keyword in all_keywords:
        # Add only the first word of each keyword to ensure uniqueness
        unique_keywords.add(keyword.split()[0])

    return {
        'tasks': list(sorted(action_items['tasks'])),
        'decisions': list(sorted(action_items['decisions'])),
        'follow_ups': list(sorted(filtered_follow_ups)),
        'all_keywords': sorted(unique_keywords)
    }
