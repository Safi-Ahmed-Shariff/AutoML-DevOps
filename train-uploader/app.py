from flask import Flask, request, render_template, redirect, url_for, flash
import os
import subprocess
from dotenv import load_dotenv

load_dotenv()  # Load .env variables

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.secret_key = 'safi-super-secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('No file part in the request')
        return redirect(request.url)

    file = request.files['file']
    if file.filename == '':
        flash('No selected file')
        return redirect(request.url)

    if file and allowed_file(file.filename):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Commit and push
        try:
            # Configure git user (do this only once; harmless if repeated)
            subprocess.run(['git', 'config', '--global', 'user.email', 'uploader@local'], check=True)
            subprocess.run(['git', 'config', '--global', 'user.name', 'CSV Uploader'], check=True)

            # Stage changes
            subprocess.run(['git', 'add', 'train-uploader/uploads/'], check=True)

            # Commit
            subprocess.run(['git', 'commit', '-m', 'Auto-upload training CSV'], check=True)

            # Push using HTTPS with token
            github_token = os.environ['GITHUB_TOKEN']
            repo_url = f"https://{github_token}:x-oauth-basic@github.com/Safi-Ahmed-Shariff/AutoML-DevOps.git"
            subprocess.run(['git', 'push', repo_url, 'main'], check=True)

            flash("✅ File uploaded and pushed to GitHub!")
        except subprocess.CalledProcessError as e:
            flash(f"❌ Git operation failed: {e}")

        return redirect(url_for('home'))

    flash('Invalid file type. Please upload a .csv file.')
    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
