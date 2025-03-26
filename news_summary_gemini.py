
import streamlit as st
import google.generativeai as genai
from PIL import Image
import logging
import io
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Set your Gemini API Key
genai.configure(api_key="AIzaSyB-rKNXSo5FF_Szk2kvSw5Ew_rcfG9jxzs")  # Replace with your actual API key

# Function to extract text from an image using Gemini Vision API
def extract_text_from_image(image):
    logging.info("Processing uploaded image")
    model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05")
    response = model.generate_content([image, """
    Extract only the news headline and body text from this image.
    The headline may be spread across multiple lines but must have the same font and size.
    Return only the extracted text without any extra labels or explanations.
    Do not include Subheadings in Headlins.All lines of headline must have same font and size. 
    Do not join the headline and body text together. Headline cannot be more than 3 lines.                                                                   
    """])
    
    extracted_text = response.text.strip()
    lines = extracted_text.split("\n")
    
    # Extract all continuous lines before the body text starts
    headline_lines = []
    body_start_index = None
    for i, line in enumerate(lines):
        if line.strip() == "":  # Assuming an empty line separates headline and body
            body_start_index = i + 1
            break
        headline_lines.append(line.strip())
    
    headline = " ".join(headline_lines) if headline_lines else "No headline detected"
    body_text = "\n".join(lines[body_start_index:]).strip() if body_start_index and body_start_index < len(lines) else "No additional text found"
    
    logging.info(f"Extracted Headline: {headline}")
    return headline, body_text

# Function to generate a summary using Gemini API
def generate_summary(article_text):
    logging.info("Generating summary...")
    summarization_prompt = f"""
    You are an intelligent AI News Editor who summarizes news articles. Process the following article:
    {article_text}
    
    The summary should have less than {min(len(article_text.split()) // 2, 150)} words.
    The language of the 
    The summary should cover at least 3 key takeaways from the news in meaningful sentences.
    It must answer fundamental questions like What, Where, When, Who, Why, and How.
    Do not include a separate headline.
    The summary should be in two paragraphs.
    """
    
    model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05")
    response = model.generate_content(summarization_prompt)
    summary = response.text.strip()
    logging.info("Summary generated successfully.")
    return summary

# Function to perform sentiment analysis
def analyze_sentiment(article_text):
    logging.info("Performing sentiment analysis...")
    sentiment_prompt = f"""
    Analyze the sentiment of the following news article and return only one word: Positive or Negative.
    {article_text}
    """
    
    model = genai.GenerativeModel("gemini-2.0-pro-exp-02-05")
    response = model.generate_content(sentiment_prompt)
    sentiment = response.text.strip()
    logging.info(f"Sentiment detected: {sentiment}")
    
    return sentiment

# Function to save extracted data to a Word document
def save_to_word(image, headline, sentiment, summary, body_text):
    logging.info("Saving data to Word document...")
    doc = Document()
    
    # Save image to a BytesIO buffer
    img_buffer = io.BytesIO()
    plt.figure(figsize=(5, 5))
    plt.imshow(image)
    plt.axis('off')
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    plt.close()
    img_buffer.seek(0)
    
    # Save image to Word document
    doc.add_heading("Image:", level=1)
    doc.add_picture(img_buffer, width=Inches(4.5))
    
    doc.add_heading("Headline:", level=1)
    doc.add_paragraph(headline)
    
    doc.add_heading("Sentiment:", level=1)
    doc.add_paragraph(sentiment)
    
    doc.add_heading("Summary:", level=1)
    doc.add_paragraph(summary)
    
    doc.add_heading("Extracted Text:", level=1)
    doc.add_paragraph(body_text)
    
    output_filename = "Extracted_Text.docx"
    doc.save(output_filename)
    logging.info(f"Word document saved as: {output_filename}")
    return output_filename

# Streamlit UI
st.title("News Image Analyzer")
st.write("Upload an image containing news text to extract information.")

uploaded_file = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_container_width=True)
    
    if st.button("Process Image"):
        headline, body_text = extract_text_from_image(image)
        summary = generate_summary(body_text)
        sentiment = analyze_sentiment(body_text)
        
        st.subheader("Extracted Headline")
        st.write(headline)
        
        st.subheader("Sentiment Analysis")
        st.write(sentiment)
        
        st.subheader("Summary")
        st.write(summary)
        
        word_file = save_to_word(image, headline, sentiment, summary, body_text)
        with open(word_file, "rb") as f:
            st.download_button("Download Word Document", f, file_name=word_file, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
