import re
import PyPDF2
import pandas as pd
import streamlit as st
from io import BytesIO


# Function to extract text from a PDF file
def extract_text_from_pdf(file):
    text = ""
    try:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    except Exception as e:
        st.error(f"Error reading file: {e}")
    return text


# Function to extract name, phone, and email from text
def extract_name_and_phone(text):
    phone_pattern = r'(\+?\d{1,2}\s?\(?\d{2,3}\)?\s?\d{3,4}[\s.-]?\d{4})'
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    name_pattern = r'^([A-Z]+(?:\s+[A-Z]+\.)?\s+[A-Z]+(?:\s+[A-Z][a-zA-Z]*)*)|([A-Z][a-zA-Z]*\s(?:[A-Z]\.\s)?(?:[A-Z][a-zA-Z]*\s?)*)'

    phone_match = re.findall(phone_pattern, text)
    phone = phone_match[0] if phone_match else "Not Found"

    email_match = re.findall(email_pattern, text)
    email = email_match[0] if email_match else "Not Found"

    name_match = re.search(name_pattern, text, re.IGNORECASE)
    if name_match:
        full_name = name_match.group(0).strip()
        limited_name = ' '.join(full_name.split()[:3])
    else:
        limited_name = "Not Found"
    name = limited_name

    return name, phone, email


# Streamlit app setup
st.title("Resume Processing App")
st.write("Upload PDF resumes to extract Name, Phone, and Email.")

# File uploader to allow multiple files
uploaded_files = st.file_uploader("Upload PDF files", type="pdf", accept_multiple_files=True)

if uploaded_files:
    # Process uploaded files
    data = []
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        text = extract_text_from_pdf(uploaded_file)
        name, phone, email = extract_name_and_phone(text)
        data.append({"File Name": file_name, "Name": name, "Phone": phone, "Email": email})

    # Convert data to DataFrame
    df = pd.DataFrame(data)

    # Save results to Excel
    output_excel = "extracted_data.xlsx"
    df.to_excel(output_excel, index=False)

    # Display results and provide download link
    st.write("Processing complete! Below is the extracted details:")
    st.dataframe(df)
    st.download_button(
        label="Download Results as Excel",
        data=open(output_excel, "rb").read(),
        file_name="Resume_extracted_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
