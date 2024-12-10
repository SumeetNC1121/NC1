import os
import re
import PyPDF2
import pandas as pd
import streamlit as st

# Function to extract text from a PDF file
def extract_text_from_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as pdf_file:
            reader = PyPDF2.PdfReader(pdf_file)
            for page in reader.pages:
                text += page.extract_text()
    except Exception as e:
        st.error(f"Error reading {file_path}: {e}")
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

# Function to process resumes and save results to an Excel file
def process_resumes(folder_path, output_excel):
    data = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            file_path = os.path.join(folder_path, filename)
            text = extract_text_from_pdf(file_path)
            name, phone, email = extract_name_and_phone(text)
            data.append({"File Name": filename, "Name": name, "Phone": phone, "Email": email})

    # Save results to an Excel file
    df = pd.DataFrame(data)
    df.to_excel(output_excel, index=False)
    return output_excel

# Streamlit app setup
st.title("Resume Processing App")
st.write("Extract Name, Phone, and Email from PDF resumes.")

# User input for folder path
folder_path = st.text_input("Enter the folder path containing PDF resumes:")
excel_name = "extracted_data.xlsx"

if st.button("Process Resumes"):
    if os.path.isdir(folder_path):
        output_excel = os.path.join(folder_path, excel_name)
        try:
            process_resumes(folder_path, output_excel)
            st.success(f"All PDFs have been read. Results are stored in folder - {folder_path} . Excel file - `{excel_name}`.")
        except Exception as e:
            st.error(f"An error occurred: {e}")
    else:
        st.error("The entered folder path is invalid. Please enter a valid path.")
