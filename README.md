# SEU Question Bank 📚

A comprehensive, centralized repository for academic question papers, built with **Streamlit**. This platform allows students and faculty to easily upload, browse, search, and manage past question papers across various departments and courses.

## Features ✨

- **Browse & Search:** Effortlessly search for question papers by Department, Course, Semester, and Question Type (CT, Mid, Final, Others).
- **Upload Papers:** Contribute to the community by uploading new question papers (supports image uploads via Cloudinary).
- **Admin Dashboard:** Built-in admin panel to review, approve, or reject uploaded question papers to ensure quality.
- **Database Support:** Seamlessly handles data storage using either **SQLite** (for local development) or **PostgreSQL** (for production environments).
- **Interactive UI:** A clean, responsive interface powered by Streamlit.

## Tech Stack 🛠️

- **Frontend:** Streamlit
- **Backend/Database:** Python, SQLite, PostgreSQL (`psycopg2`)
- **Image Hosting:** Cloudinary
- **Environment Management:** `python-dotenv`

## Project Structure 📂

- `app.py`: Main entry point for the Streamlit application and navigation configuration.
- `db_manager.py`: Handles all database connections and CRUD operations (SQLite/PostgreSQL).
- `pages/`: Contains the individual pages of the app.
  - `home.py`: Landing page.
  - `1_Question_Bank.py`: Browse and search existing question papers.
  - `2_Upload.py`: Interface for users to upload new question papers.
  - `3_Admin.py`: Admin dashboard for managing uploads.
- `requirements.txt`: Python dependencies required to run the project.

## Installation & Setup 🚀

1. **Clone the repository:**
   ```bash
   git clone https://github.com/arrahmanriju/SEU_Question_Bank.git
   cd QuestionBank
   ```

2. **Create a virtual environment (Recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Create a `.env` file in the root directory (you can use `.env.example` as a template) and add your necessary keys:
   ```env
   # Database (Optional, uses SQLite by default if not provided)
   DATABASE_URL=your_postgresql_database_url
   
   # Admin Secrets
   ADMIN_PASSWORD=your_admin_password
   
   # Cloudinary (For image uploads)
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

5. **Run the Application:**
   ```bash
   streamlit run app.py
   ```
   The app should now be running locally at `http://localhost:8501`.

## Contributing 🤝

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.

## License 📝

[MIT License](LICENSE)
