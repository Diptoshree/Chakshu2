import streamlit as st
import google.generativeai as genai
from PIL import Image, UnidentifiedImageError
import logging
import io
import matplotlib.pyplot as plt
from docx import Document
from docx.shared import Inches
#from dotenv import load_dotenv
import os
import zipfile
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

api_key = st.secrets["secret_section"]["api_key"]
# Configure the client using the API key
genai.configure(api_key=api_key)
#Retrieve API keys from Streamlit secrets
# api_keys = st.secrets["secret_section"]["api_keys"]  # Ensure this is a list of 5 keys
# api_index = 0  # Initialize index for key rotation

# def get_next_api_key():
#     """Rotates API keys in a round-robin fashion."""
#     global api_index
#     key = api_keys[api_index]
#     api_index = (api_index + 1) % len(api_keys)  # Move to the next key
#     return key

def extract_text_from_image(image):
    logging.info("Processing uploaded image")
    
    model = genai.GenerativeModel("gemini-2.5-pro-exp-03-25")
    prompt = """
    You are extracting text from a scanned newspaper cutting. Your task is to separate the text into three categories: Headline Body Text and other text.

    - **Headline**: The main news headline, usually in the largest bold font, spanning between one to three lines with a uniform font size. Ignore subheaders, captions, dates, and newspaper organization names.
                    This instruction needs to be followed strictly.

    - **Body Text**: All other content, including subheaders, captions, and article text.
    - **Other** Text**:Any other text which is placed in the top 5 lines apart from head line should come under other text.
					Example:
					Newspaper Brand name: 'दैनिक भास्कर'
					News provider/ news Bureau or place :'भास्कर संवाददाता | डभियाखेड़ा' or 'स्टार समाचार | सीधी'
					text which has smaller font size compared to headline such as subheading, location or brand, photo caption  must come under other text.
                  

    **Output format (strictly follow this structure without any labels, explanations, or additional formatting):**

    First, print the extracted headline (Between 1 to 3 lines).
    Then, print a blank line.
    Finally, print the extracted body text.

    Ensure there are no extra words, labels, or formatting—just the extracted text in two sections.
    """
    
    response = model.generate_content([image, prompt])
    extracted_text = response.text.strip()
    
    # Process response to extract headline and body text
    lines = extracted_text.split("\n")
    headline = " ".join(lines[:3]).strip() if lines else "No headline detected"
    body_text = "\n".join(lines[1:]).strip() if len(lines) > 3 else "No additional text found"

    logging.info(f"Extracted Headline: {headline}")

    return headline, body_text




def generate_summary(article_text):
    logging.info("Generating summary...")
    summarization_prompt = f"""
     You are an intelligent AI News Editor who summarizes news articles. Process the following article:
    {article_text}
    
    The summary should have less than {min(len(article_text.split()) // 2, 100)} words.
    The language of the summary must be exactly same as the language of extracted text.
    The summary should cover at least 3 key takeaways from the news in meaningful sentences.
    It must answer fundamental questions like What, Where, When, Who, Why, and How.
    Do not include a separate headline.
    The summary should be in two paragraphs.
        """
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(summarization_prompt)
    summary = response.text.strip()
    logging.info("Summary generated successfully.")
    return summary

def analyze_sentiment(article_text):
    logging.info("Performing sentiment analysis...")
    sentiment_prompt = f"""
    Analyze the sentiment of the following news article and return only one word: Positive or Negative.
    {article_text}
    """
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(sentiment_prompt)
    sentiment = response.text.strip()
    logging.info(f"Sentiment detected: {sentiment}")
    return sentiment

def save_to_word(image, headline, sentiment, summary, body_text, doc):
    logging.info("Saving data to Word document...")
    img_buffer = io.BytesIO()
    image.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    doc.add_picture(img_buffer, width=Inches(4.5))
    doc.add_heading("Headline:", level=1)
    doc.add_paragraph(headline)
    doc.add_heading("Sentiment:", level=1)
    doc.add_paragraph(sentiment)
    doc.add_heading("Summary:", level=1)
    doc.add_paragraph(summary)
    doc.add_heading("Extracted Text:", level=1)
    doc.add_paragraph(body_text)

def process_zip_file(zip_file):
    logging.info("Processing ZIP file...")
    doc = Document()
    with zipfile.ZipFile(zip_file, 'r') as archive:
        for file_name in archive.namelist():
            if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
                with archive.open(file_name) as file:
                    try:
                        image = Image.open(file).convert("RGB")
                        headline, body_text = extract_text_from_image(image)
                        summary = generate_summary(body_text)
                        sentiment = analyze_sentiment(body_text)
                        save_to_word(image, headline, sentiment, summary, body_text, doc)
                    except UnidentifiedImageError:
                        logging.error(f"Skipping non-image file: {file_name}")
    output_filename = "Extracted_Text.docx"
    doc.save(output_filename)
    logging.info(f"Word document saved as: {output_filename}")
    return output_filename

st.title("Chakshu News Summarizer")
st.write("Upload an image or a ZIP file containing images to extract information.")
option = st.radio("Choose an upload option:", ["Single Image", "ZIP File"])

if option == "Single Image":
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file).convert("RGB")
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
            doc = Document()
            save_to_word(image, headline, sentiment, summary, body_text, doc)
            doc.save("Extracted_Text.docx")
            with open("Extracted_Text.docx", "rb") as f:
                st.download_button("Download Word Document", f, file_name="Extracted_Text.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

elif option == "ZIP File":
    uploaded_zip = st.file_uploader("Choose a ZIP file", type=["zip"])
    if uploaded_zip is not None:
        if st.button("Process ZIP File"):
            word_file = process_zip_file(uploaded_zip)
            with open(word_file, "rb") as f:
                st.download_button("Download Word Document", f, file_name=word_file, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
