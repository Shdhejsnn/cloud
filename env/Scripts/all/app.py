import os
from flask import Flask, request, jsonify, render_template, session, send_file
from preprocessing import preprocess_text
from summarization import generate_summary
from topic_modeling import extract_topics
from action_items import extract_action_items
from questions import extract_questions
from textblob import TextBlob
from io import BytesIO
from fpdf import FPDF
import boto3
from botocore.exceptions import NoCredentialsError
from google.cloud import storage  # Import Google Cloud Storage client

# Set the Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "C:\\Users\\LENOVO\\Desktop\\Swift GC\\env\\keys\\keyfile.json"

app = Flask(__name__)
app.secret_key = 'teamflexbox'

# Google Cloud Storage Bucket Configuration
GCS_BUCKET_NAME = "meeting-minutes-storage"  # Your GCS bucket name

def upload_to_gcs(file_content, bucket_name, object_name):
    """Uploads a file to Google Cloud Storage."""
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.bucket(bucket_name)

    # Create a new blob (object) in the bucket
    blob = bucket.blob(object_name)

    # Upload the file content
    blob.upload_from_string(file_content, content_type='application/pdf')

    # Generate the public URL for the uploaded file
    file_url = f"https://storage.googleapis.com/{bucket_name}/{object_name}"

    return file_url

events = []

class MyPDF(FPDF):
    def header(self):
        self.set_font("Arial", 'B', 12)
        self.cell(0, 10, "Meeting Summary", 0, 1, 'C')

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_body(self, body_text):
        self.set_font("Arial", size=12)
        self.multi_cell(0, 10, txt=body_text)

@app.route('/')
def index():
    results = {
        'tokens': session.get('tokens', []),
        'summary': session.get('summary', 'No summary available.'),
        'topics': session.get('topics', []),
        'keywords': session.get('keywords', []),
        'sentiment': session.get('sentiment', 'No sentiment available.'),
        'action_items': session.get('action_items', {'tasks': [], 'decisions': [], 'follow_ups': []}),
        'questions': session.get('questions', []),
        'department': session.get('department', 'No department selected.')
    }
    return render_template('index.html', results=results)

@app.route('/generate_minutes', methods=['POST'])
def generate_minutes():
    transcript = request.form['transcript']
    event_date = request.form['eventDate']
    department = request.form['department']  

    blob = TextBlob(transcript)
    sentiment_polarity = blob.sentiment.polarity
    sentiment_label = 'Positive' if sentiment_polarity > 0 else 'Negative' if sentiment_polarity < 0 else 'Neutral'
    color = 'green' if sentiment_label == 'Positive' else 'red' if sentiment_label == 'Negative' else 'gray'

    tokens = preprocess_text(transcript)
    action_items = extract_action_items(transcript)
    questions = extract_questions(transcript)
    topics = extract_topics([transcript])
    formatted_topics = [{'topic_id': topic['topic_id'],
                         'words': ', '.join([f"{word['word']} ({word['weight']:.2f})" for word in sorted(topic['top_words'], key=lambda x: x['weight'], reverse=True)])} for topic in topics]

    keywords = action_items['all_keywords']
    summary = generate_summary(transcript, keywords)

    session.update({
        'tokens': tokens,
        'summary': summary,
        'topics': formatted_topics,
        'keywords': keywords,
        'sentiment': sentiment_label,
        'action_items': action_items,
        'questions': questions,
        'department': department
    })

    events.append({
        'title': f'{department} Meeting Summary',
        'start': event_date,
        'summary': summary,
        'color': color
    })

    return jsonify({
        'tokens': tokens,
        'summary': summary,
        'topics': formatted_topics,
        'keywords': keywords,
        'sentiment': sentiment_label,
        'action_items': action_items,
        'questions': questions,
        'department': department
    })

@app.route('/download_pdf')
def download_pdf():
    summary_text = session.get('summary', 'No summary available.')
    department = session.get('department', 'General')

    # Replace problematic characters with simpler ones
    summary_text = summary_text.replace(u'\u2019', "'")  # Replace right single quotation mark
    summary_text = summary_text.replace(u'\u2018', "'")  # Replace left single quotation mark
    summary_text = summary_text.replace(u'\u201C', '"')  # Replace left double quotation mark
    summary_text = summary_text.replace(u'\u201D', '"')  # Replace right double quotation mark

    pdf = MyPDF()
    pdf.add_page()

    # Set font to Arial (with Latin-1 support for basic characters)
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, txt=f"{department} - Detailed Summary", ln=True, align='C')
    pdf.ln(10)
    pdf.multi_cell(0, 10, txt=f"Department: {department}\n\n")
    pdf.multi_cell(0, 10, txt=f"Summary:\n{summary_text}")

    # Generate PDF in memory
    pdf_output = BytesIO()
    pdf_output.write(pdf.output(dest='S').encode('latin1'))  # Ensure Latin-1 encoding
    pdf_output.seek(0)

    # Upload PDF to GCS
    file_name = f"detailed_summary_{department}.pdf"
    gcs_url = upload_to_gcs(pdf_output.getvalue(), GCS_BUCKET_NAME, file_name)

    if gcs_url:
        return jsonify({"message": "PDF uploaded successfully", "url": gcs_url})
    else:
        return jsonify({"message": "PDF upload failed"}), 500

@app.route('/tokenized')
def tokenized():
    tokens = session.get('tokens', [])
    return render_template('tokenized.html', tokens=tokens)

@app.route('/summary')
def summary():
    summary_text = session.get('summary', 'No summary available.')
    return render_template('summary.html', summary=summary_text)

@app.route('/topics')
def topics():
    topics = session.get('topics', [])
    return render_template('topics.html', topics=topics)

@app.route('/keywords')
def keywords():
    keywords = session.get('keywords', [])
    return render_template('keywords.html', keywords=keywords)

@app.route('/action_items')
def action_items():
    action_items = session.get('action_items', {'tasks': [], 'decisions': [], 'follow_ups': []})
    return render_template('action_items.html', action_items=action_items)

@app.route('/questions')
def questions():
    questions = session.get('questions', [])
    return render_template('questions.html', questions=questions)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
