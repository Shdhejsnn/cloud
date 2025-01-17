import re

def extract_questions(transcript):
    questions = []
    # Split the transcript into sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', transcript)
    for sentence in sentences:
        # Check if the sentence ends with a question mark or starts with common question words
        if sentence.strip().endswith('?') or any(sentence.strip().lower().startswith(q) for q in ['what', 'why', 'how', 'when', 'where', 'who', 'which']):
            questions.append(sentence.strip())
    return questions
