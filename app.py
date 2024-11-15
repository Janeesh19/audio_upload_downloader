import streamlit as st
import os
from tinytag import TinyTag  # Lightweight library to get audio metadata

# Define the main folder where audio files are stored
AUDIO_FOLDER = "audio_files"
os.makedirs(AUDIO_FOLDER, exist_ok=True)  # Ensure the folder exists

# Define username and password 
USERNAME = "apprikart"
PASSWORD = "jfksonerk831" 

# Initialize session state for authentication and uploaded files
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False
if 'uploaded_files' not in st.session_state:
    st.session_state['uploaded_files'] = []

# Function to check authentication
def check_authentication(username, password):
    return username == USERNAME and password == PASSWORD

# Login function
def login():
    st.header("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_authentication(username, password):
            st.session_state['authenticated'] = True
            st.success("Login successful!please click on login button again")
        else:
            st.error("Invalid username or password")

# Logout function
def logout():
    st.session_state['authenticated'] = False
    st.success("You have been logged out! please click on logout button again.")

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
    st.session_state['uploaded_files'].append(file_path)
    return file_path

# Function to get audio metadata (duration in MM:SS and size in MB)
def get_audio_metadata(file_path):
    tag = TinyTag.get(file_path)
    duration_seconds = tag.duration  # Duration in seconds
    size_mb = os.path.getsize(file_path) / (1024 * 1024)  # Size in MB

    # Convert duration to minutes and seconds
    minutes = int(duration_seconds // 60)
    seconds = int(duration_seconds % 60)
    formatted_duration = f"{minutes}:{seconds:02d}"  # Format as MM:SS

    return formatted_duration, size_mb

# Function to get files in a specific category and their metadata
def get_files_by_category(category):
    category_folder = os.path.join(AUDIO_FOLDER, category)
    if os.path.exists(category_folder):
        files = []
        for file_name in os.listdir(category_folder):
            file_path = os.path.join(category_folder, file_name)
            duration, size_mb = get_audio_metadata(file_path)
            files.append((file_name, duration, size_mb, file_path))
        return files
    return []

# Function to delete a file and remove the category if empty
def delete_file(file_path, category):
    if os.path.exists(file_path):
        os.remove(file_path)
        if file_path in st.session_state['uploaded_files']:
            st.session_state['uploaded_files'].remove(file_path)
        st.success(f"File '{os.path.basename(file_path)}' has been deleted.")

        category_folder = os.path.join(AUDIO_FOLDER, category)
        if not os.listdir(category_folder):
            os.rmdir(category_folder)
            st.success(f"Category '{category}' has been deleted as it had no more files.")

# Main app
def main_app():
    st.title("Audio File Downloader, Uploader, Player, and Deleter")

    existing_categories = get_categories()
    category_option = st.selectbox("Select a category or type a new one for your file", ["Create New Category"] + existing_categories)

    if category_option == "Create New Category":
        category = st.text_input("Enter new category name")
    else:
        category = category_option

    st.header("Upload an Audio File")
    uploaded_file = st.file_uploader("Choose an audio file", type=["mp3"])

    if st.button("Upload File"):
        if uploaded_file and category:
            file_path = save_uploaded_file(uploaded_file, category)
            st.success(f"File '{uploaded_file.name}' uploaded successfully to category '{category}'.")
        else:
            st.error("Please select a file and enter a category.")

    st.header("Select Category to Manage Files")
    categories = ["Choose a category"] + get_categories()

    selected_category = st.selectbox("Choose a category", categories)

    if selected_category == "Choose a category":
        st.write("Please select a category to view files available for download, play, or deletion.")
    else:
        files = get_files_by_category(selected_category)
        
        if files:
            st.subheader(f"Files in '{selected_category}' category:")
            for file_name, duration, size_mb, file_path in files:
                st.write(f"**{file_name}** - Duration: {duration}, Size: {size_mb:.2f} MB")
                st.audio(file_path, format="audio/mp3")

                col1, col2 = st.columns(2)
                with col1:
                    with open(file_path, "rb") as f:
                        audio_bytes = f.read()
                        st.download_button(
                            label=f"Download {file_name}",
                            data=audio_bytes,
                            file_name=file_name,
                            mime="audio/mpeg"
                        )
                with col2:
                    if st.button("Delete", key=file_path):
                        delete_file(file_path, selected_category)
        else:
            st.write("No files in this category.")

    st.markdown("---")
    if st.button("Logout"):
        logout()

# Authentication flow
if not st.session_state['authenticated']:
    login()
else:
    main_app()
