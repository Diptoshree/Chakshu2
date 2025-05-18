# import streamlit as st
# import google.generativeai as genai
# from PIL import Image, UnidentifiedImageError
# import logging
# import io
# import matplotlib.pyplot as plt
# from docx import Document
# from docx.shared import Inches
# #from dotenv import load_dotenv
# import os
# import zipfile
# import json

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# api_key = st.secrets["secret_section"]["api_key"]
# # Configure the client using the API key
# genai.configure(api_key=api_key)
# #Retrieve API keys from Streamlit secrets
# # api_keys = st.secrets["secret_section"]["api_keys"]  # Ensure this is a list of 5 keys
# # api_index = 0  # Initialize index for key rotation

# # def get_next_api_key():
# #     """Rotates API keys in a round-robin fashion."""
# #     global api_index
# #     key = api_keys[api_index]
# #     api_index = (api_index + 1) % len(api_keys)  # Move to the next key
# #     return key

# def extract_text_from_image(image):
#     logging.info("Processing uploaded image")
    
#     model = genai.GenerativeModel("gemini-2.0-flash")
#     prompt = """
#     You are extracting text from a scanned newspaper cutting. Your task is to separate the text into three categories: Headline Body Text and other text.

#     - **Headline**: The main news headline, usually in the largest bold font, spanning between one to three lines with a uniform font size. Ignore subheaders, captions, dates, and newspaper organization names.
#                     This instruction needs to be followed strictly.

#     - **Body Text**: All other content, including subheaders, captions, and article text.
#     - **Other** Text**:Any other text which is placed in the top 5 lines apart from head line should come under other text.
# 					Example:
# 					Newspaper Brand name: 'दैनिक भास्कर'
# 					News provider/ news Bureau or place :'भास्कर संवाददाता | डभियाखेड़ा' or 'स्टार समाचार | सीधी'
# 					text which has smaller font size compared to headline such as subheading, location or brand, photo caption  must come under other text.
                  

#     **Output format (strictly follow this structure without any labels, explanations, or additional formatting):**

#     First, print the extracted headline (Between 1 to 3 lines).
#     Then, print a blank line.
#     Finally, print the extracted body text.

#     Ensure there are no extra words, labels, or formatting—just the extracted text in two sections.
#     """
    
#     response = model.generate_content([image, prompt])
#     extracted_text = response.text.strip()
    
#     # Process response to extract headline and body text
#     lines = extracted_text.split("\n")
#     headline = " ".join(lines[:3]).strip() if lines else "No headline detected"
#     body_text = "\n".join(lines[1:]).strip() if len(lines) > 3 else "No additional text found"

#     logging.info(f"Extracted Headline: {headline}")

#     return headline, body_text




# def generate_summary(article_text):
#     logging.info("Generating summary...")
#     summarization_prompt = f"""
#      You are an intelligent AI News Editor who summarizes news articles. Process the following article:
#     {article_text}
    
#     The summary should have less than {min(len(article_text.split()) // 2, 100)} words.
#     The language of the summary must be exactly same as the language of extracted text.
#     The summary should cover at least 3 key takeaways from the news in meaningful sentences.
#     It must answer fundamental questions like What, Where, When, Who, Why, and How.
#     Do not include a separate headline.
#     The summary should be in two paragraphs.
#         """
#     model = genai.GenerativeModel("gemini-2.0-flash")
#     response = model.generate_content(summarization_prompt)
#     summary = response.text.strip()
#     logging.info("Summary generated successfully.")
#     return summary

# def analyze_sentiment(article_text):
#     logging.info("Performing sentiment analysis...")
#     sentiment_prompt = f"""
#     Analyze the sentiment of the following news article and return only one word: Positive or Negative.
#     {article_text}
#     """
#     model = genai.GenerativeModel("gemini-2.0-flash")
#     response = model.generate_content(sentiment_prompt)
#     sentiment = response.text.strip()
#     logging.info(f"Sentiment detected: {sentiment}")
#     return sentiment

# def save_to_word(image, headline, sentiment, summary, body_text, doc):
#     logging.info("Saving data to Word document...")
#     img_buffer = io.BytesIO()
#     image.save(img_buffer, format='PNG')
#     img_buffer.seek(0)
#     doc.add_picture(img_buffer, width=Inches(4.5))
#     doc.add_heading("Headline:", level=1)
#     doc.add_paragraph(headline)
#     doc.add_heading("Sentiment:", level=1)
#     doc.add_paragraph(sentiment)
#     doc.add_heading("Summary:", level=1)
#     doc.add_paragraph(summary)
#     doc.add_heading("Extracted Text:", level=1)
#     doc.add_paragraph(body_text)

# def process_zip_file(zip_file):
#     logging.info("Processing ZIP file...")
#     doc = Document()
#     with zipfile.ZipFile(zip_file, 'r') as archive:
#         for file_name in archive.namelist():
#             if file_name.lower().endswith((".png", ".jpg", ".jpeg")):
#                 with archive.open(file_name) as file:
#                     try:
#                         image = Image.open(file).convert("RGB")
#                         headline, body_text = extract_text_from_image(image)
#                         summary = generate_summary(body_text)
#                         sentiment = analyze_sentiment(body_text)
#                         save_to_word(image, headline, sentiment, summary, body_text, doc)
#                     except UnidentifiedImageError:
#                         logging.error(f"Skipping non-image file: {file_name}")
#     output_filename = "Extracted_Text.docx"
#     doc.save(output_filename)
#     logging.info(f"Word document saved as: {output_filename}")
#     return output_filename

# st.title("Chakshu News Summarizer")
# st.write("Upload an image or a ZIP file containing images to extract information.")
# option = st.radio("Choose an upload option:", ["Single Image", "ZIP File"])

# if option == "Single Image":
#     uploaded_file = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"])
#     if uploaded_file is not None:
#         image = Image.open(uploaded_file).convert("RGB")
#         st.image(image, caption="Uploaded Image", use_container_width=True)
#         if st.button("Process Image"):
#             headline, body_text = extract_text_from_image(image)
#             summary = generate_summary(body_text)
#             sentiment = analyze_sentiment(body_text)
#             st.subheader("Extracted Headline")
#             st.write(headline)
#             st.subheader("Sentiment Analysis")
#             st.write(sentiment)
#             st.subheader("Summary")
#             st.write(summary)
#             doc = Document()
#             save_to_word(image, headline, sentiment, summary, body_text, doc)
#             doc.save("Extracted_Text.docx")
#             with open("Extracted_Text.docx", "rb") as f:
#                 st.download_button("Download Word Document", f, file_name="Extracted_Text.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")

# elif option == "ZIP File":
#     uploaded_zip = st.file_uploader("Choose a ZIP file", type=["zip"])
#     if uploaded_zip is not None:
#         if st.button("Process ZIP File"):
#             word_file = process_zip_file(uploaded_zip)
#             with open(word_file, "rb") as f:
#                 st.download_button("Download Word Document", f, file_name=word_file, mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
######################################zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz

import os
import zipfile
import streamlit as st
from PIL import Image
from io import BytesIO
import google.generativeai as genai
from docx import Document
from docx.shared import Inches
import json
import re

# ✅ Set your Gemini API key
genai.configure(api_key="AIzaSyAymA7P4sRcrb0S9IAsC2cgkfxc0a6Fzj8")  # Replace with your key

# 🔵 Original function for analyzing a newspaper image
def analyze_newspaper_image(image):
    prompt = """
You are an expert in analyzing newspaper clippings. From the newspaper image, extract the following structured information:
1. News Brand Name (e.g., 'Dainik Bhaskar', 'The Times of India')
2. Heading
3. Subheading (if any)
4. Callout Boxes (if any)(visually distinct boxed or highlighted texts. avoid adding any other words or explanation. Please keep the text as it is in original news.)
5. Date (if mentioned)
6. Location (usually before the main news)
7. News Bureau (e.g., 'New Delhi Bureau')
8. Body Text (remaining text that forms the main article body. Please avoid photo captions)
9. A concise summary of the article (within 120 words). Start the summary by repeating the original headline exactly, from next paragraph a brief summary in your own words. The language of summary should be same as the language of the original text.
10. Sentiment (The sentiment of the news in one word 'Positive' or 'Negative')
Return the result in this JSON format:
{
  "news_brand": "",
  "heading": "",
  "subheading": "",
  "callout_boxes": [],
  "date": "",
  "location": "",
  "news_bureau": "",
  "body_text": "",
  "summary": "",
  "sentiment": ""
}
"""
    model = genai.GenerativeModel("gemini-2.5-pro-exp-03-25")
    response = model.generate_content([prompt, image])
    return response.text

# 🔵 Format the extracted JSON into Word Document
def format_json_to_doc(doc, extracted_json_text):
    try:
        json_text_match = re.search(r"\{[\s\S]*\}", extracted_json_text)
        structured_data = json.loads(json_text_match.group())
    except:
        doc.add_paragraph("❌ Failed to parse structured JSON from Gemini response.")
        return

    doc.add_heading("📰 Extracted Newspaper Article", level=1)

    def add_section(label, content, style="Normal"):
        if content:
            doc.add_heading(label, level=2)
            if isinstance(content, list):
                for item in content:
                    doc.add_paragraph(f"• {item}", style=style)
            else:
                doc.add_paragraph(content.strip(), style=style)

    add_section("Heading", structured_data.get("heading"))
    add_section("Sentiment", structured_data.get("sentiment"))
    add_section("Summary", structured_data.get("summary"))

    heading = structured_data.get("heading")
    subheading = structured_data.get("subheading")
    body_text = structured_data.get("body_text")
    if any([heading, subheading, body_text]):
        doc.add_heading("Body Text", level=2)
        if heading:
            doc.add_paragraph(heading.strip())
        if subheading:
            doc.add_paragraph(subheading.strip())
        if body_text:
            doc.add_paragraph(body_text.strip())

    add_section("Callout Boxes", structured_data.get("callout_boxes", []))
    add_section("News Brand", structured_data.get("news_brand"))

# 🔵 Save single image and extracted text into Word
def save_to_word_with_image(image_file, extracted_text, doc=None):
    if doc is None:
        doc = Document()
    try:
        img = Image.open(image_file)
        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        buffer.seek(0)
        doc.add_picture(buffer, width=Inches(5.5))
        doc.add_paragraph("⬆️ Original Newspaper Image", style="Caption")
    except Exception as e:
        doc.add_paragraph(f"❌ Failed to insert image: {e}")

    format_json_to_doc(doc, extracted_text)
    return doc

# 🔵 Streamlit UI
st.set_page_config(page_title="Newspaper Analyzer", layout="centered")
st.title("📰 Newspaper Image Analyzer")

# 👉 Mode Selection
mode = st.radio("Choose Mode", ("Single Image Search", "Bulk Image Search"))

if mode == "Single Image Search":
    uploaded_file = st.file_uploader("Upload Newspaper Image", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption="🖼️ Uploaded Newspaper", use_container_width=True)

        if st.button("🔍 Analyze Image"):
            with st.spinner("Analyzing..."):
                extracted_text = analyze_newspaper_image(image)
                try:
                    json_text_match = re.search(r"\{[\s\S]*\}", extracted_text)
                    structured = json.loads(json_text_match.group())
                except:
                    structured = None

            if structured:
                st.success("✅ Extraction complete")
                st.subheader("📌 Extracted Details")
                st.markdown(f"**Headline:** {structured.get('heading', 'N/A')}")
                st.markdown(f"**Sentiment:** {structured.get('sentiment', 'N/A')}")
                st.markdown(f"**Summary:** {structured.get('summary', 'N/A')}")
                
                st.subheader("Body Text")
                if structured.get("heading"):
                    st.markdown(f"Headline: {structured['heading']}")
                if structured.get("subheading"):
                    st.markdown(f"Subheading: {structured['subheading']}")
                if structured.get("body_text"):
                    st.markdown(structured["body_text"])
                st.markdown(f"News Brand: {structured.get('news_brand', 'N/A')}")
                st.markdown(f"Callout Boxes: {structured.get('callout_boxes', '[]')}")

                word_file = BytesIO()
                save_to_word_with_image(uploaded_file, extracted_text).save(word_file)
                word_file.seek(0)
                st.download_button("📥 Download Word File", word_file, file_name="Extracted_News.docx")
            else:
                st.error("❌ Could not parse structured response.")

elif mode == "Bulk Image Search":
    uploaded_zip = st.file_uploader("Upload ZIP of Newspaper Images", type=["zip"])

    if uploaded_zip:
        if st.button("🔍 Analyze Bulk Images"):
            with st.spinner("Analyzing images..."):
                temp_folder = "temp_images"
                os.makedirs(temp_folder, exist_ok=True)

                # Extract ZIP
                with zipfile.ZipFile(uploaded_zip, "r") as zip_ref:
                    zip_ref.extractall(temp_folder)

                image_files = [os.path.join(temp_folder, f) for f in os.listdir(temp_folder)
                               if f.lower().endswith((".jpg", ".jpeg", ".png"))]

                if not image_files:
                    st.error("❌ No valid image files found in ZIP.")
                else:
                    doc = Document()
                    for img_path in image_files:
                        try:
                            img = Image.open(img_path)
                            extracted_text = analyze_newspaper_image(img)
                            save_to_word_with_image(img_path, extracted_text, doc)
                        except Exception as e:
                            doc.add_paragraph(f"⚠️ Failed to process {img_path}: {e}")

                    # Finalize Word file
                    output = BytesIO()
                    doc.save(output)
                    output.seek(0)

                    st.success(f"✅ Processed {len(image_files)} images.")
                    st.download_button("📥 Download Combined Word File", output, file_name="Bulk_Extracted_News.docx")

                # Cleanup temp folder
                try:
                    for f in os.listdir(temp_folder):
                        os.remove(os.path.join(temp_folder, f))
                    os.rmdir(temp_folder)
                except Exception as cleanup_error:
                    print(f"Cleanup error: {cleanup_error}")

