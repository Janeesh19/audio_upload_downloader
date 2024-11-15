import streamlit as st
import os

# Define the main folder where audio files are stored
AUDIO_FOLDER = "audio_files"
os.makedirs(AUDIO_FOLDER, exist_ok=True)  # Ensure the folder exists

# Initialize session state for uploaded files
if 'uploaded_files' not in st.session_state:
    st.session_state['uploaded_files'] = []

# Function to get list of categories (subfolders in AUDIO_FOLDER)
def get_categories():
    return [f.name for f in os.scandir(AUDIO_FOLDER) if f.is_dir()]

# Function to save uploaded file and get its path
def save_uploaded_file(uploaded_file, category):
    category_folder = os.path.join(AUDIO_FOLDER, category)
    os.makedirs(category_folder, exist_ok=True)
    file_path = os.path.join(category_folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    # Track the uploaded file in session state
    st.session_state['uploaded_files'].append(file_path)
    return file_path

# Function to get files in a specific category
def get_files_by_category(category):
    category_folder = os.path.join(AUDIO_FOLDER, category)
    if os.path.exists(category_folder):
        files = [(file_name, os.path.join(category_folder, file_name)) for file_name in os.listdir(category_folder)]
        return files
    return []

# Function to delete a file and remove the category if empty
def delete_file(file_path, category):
    if os.path.exists(file_path):
        os.remove(file_path)
        st.session_state['uploaded_files'].remove(file_path)  # Remove from session state
        st.success(f"File '{os.path.basename(file_path)}' has been deleted.")
        
        # Check if the category folder is empty, and delete it if so
        category_folder = os.path.join(AUDIO_FOLDER, category)
        if not os.listdir(category_folder):  # Folder is empty
            os.rmdir(category_folder)
            st.success(f"Category '{category}' has been deleted as it had no more files.")

# Page title
st.title("Audio File Downloader, Uploader, and Deleter")

# Upload Section
st.header("Upload an Audio File")
uploaded_file = st.file_uploader("Choose an audio file", type=["mp3"])

# Dropdown for category selection with an option to add a new category
existing_categories = get_categories()
category_option = st.selectbox("Select a category or type a new one", ["Create New Category"] + existing_categories)

if category_option == "Create New Category":
    # If 'Create New Category' is selected, show a text input for the new category
    category = st.text_input("Enter new category name")
else:
    # If an existing category is selected, use that category
    category = category_option

if st.button("Upload File"):
    if uploaded_file and category:
        file_path = save_uploaded_file(uploaded_file, category)
        st.success(f"File '{uploaded_file.name}' uploaded successfully to category '{category}'.")
    else:
        st.error("Please select a file and enter a category.")

# Dropdown to select category for managing files
st.header("Select Category to Manage Files")
categories = ["Choose a category"] + get_categories()  # Add placeholder as the first option

selected_category = st.selectbox("Choose a category", categories)

if selected_category == "Choose a category":
    st.write("Please select a category to view files available for download or deletion.")
else:
    # Display files in the selected category with download and delete options
    files = get_files_by_category(selected_category)
    
    if files:
        st.subheader(f"Files in '{selected_category}' category:")
        
        # Provide download links and delete buttons for each file in the category
        for file_name, file_path in files:
            # Display file name and size in MB
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB
            st.write(f"**{file_name}** - Size: {file_size_mb:.2f} MB")
            
            # Columns for download and delete buttons
            col1, col2 = st.columns(2)
            with col1:
                # Download button
                with open(file_path, "rb") as f:
                    audio_bytes = f.read()
                    st.download_button(
                        label=f"Download {file_name}",
                        data=audio_bytes,
                        file_name=file_name,
                        mime="audio/mpeg"
                    )
            with col2:
                # Show the delete button only if the file was uploaded in this session
                if file_path in st.session_state['uploaded_files']:
                    if st.button("Delete", key=file_path):
                        delete_file(file_path, selected_category)
    else:
        st.write("No files in this category.")
