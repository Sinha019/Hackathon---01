from flask import Flask, render_template, request, jsonify
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd

app = Flask(__name__)

# Load spaCy's English language model (download it if not available)
try:
    nlp = spacy.load("en_core_web_sm")
except:
    # Install spaCy and download the model
    nlp = spacy.load("en_core_web_sm")

# Replace 'path_to_your_excel_file.xlsx' with the actual path to your Excel file
csv_file_path = r'C:\Users\Pyush\OneDrive\Desktop\tt\final\google_books_1299.csv'

# Read the Excel file into a DataFrame
df = pd.read_csv(csv_file_path)

# Assuming you have already loaded your data into 'df' DataFrame
df['description'] = df['description'].fillna('')

# Create and fit the TfidfVectorizer
vectorizer = TfidfVectorizer(stop_words='english')
abstract_vectors = vectorizer.fit_transform(df['description'].apply(str.lower))  # Convert to lowercase

# Your answer_question function
def answer_question(question):
    # Preprocess question
    question_vector = vectorizer.transform([question.lower()])  # Convert the question to lowercase

    # Calculate similarities
    similarities = cosine_similarity(question_vector, abstract_vectors)

    # Find the index of the most similar abstract
    most_similar_index = similarities.argmax()

    # Retrieve the complete abstract, title, and author
    complete_abstract = df.iloc[most_similar_index]['description']
    title = df.iloc[most_similar_index]['title']
    author = df.iloc[most_similar_index]['author']  # Replace 'author' with the actual column name

    # Initialize publication_date and rating variables
    publication_date = None
    rating = None

    # Check if 'publication_date' and 'rating' columns exist in the DataFrame
    if 'publication_date' in df.columns:
        publication_date = df.iloc[most_similar_index]['publication_date']  # Fix typo in column name
    if 'rating' in df.columns:
        rating = df.iloc[most_similar_index]['rating']

    # Use spaCy for named entity recognition and part-of-speech tagging
    doc = nlp(complete_abstract)

    # Extract relevant sentences for summary
    sentences = [sent.text for sent in doc.sents]

    # Combine sentences into a 2-3 lines summary
    summary = ' '.join(sentences[:3])  # Adjust the slice for desired length

    # Include publication year in the title if available
    if publication_date is not None:
        title_with_year = f"{title} ({publication_date})"
    else:
        title_with_year = title

    return {'Title': title_with_year, 'Summary': summary, 'Similarity': similarities[0, most_similar_index], 'Author': author}

# Suppress favicon.ico error
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# Define routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    if request.method == 'POST':
        user_question = request.form.get('question')
        if not user_question:
            return jsonify({'error': 'Please enter a question.'})

        result = answer_question(user_question)
        if 'Similarity' not in result or result['Similarity'] < 0.1:
            return jsonify({'error': 'Sorry, no matching results.'})
        else:
            return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True)
