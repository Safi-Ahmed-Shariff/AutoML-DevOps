from flask import Flask, request, render_template, redirect, url_for, flash
import os
import subprocess
import shutil

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.secret_key = 'safi-super-secret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


DATA_FOLDER = os.path.join(os.getcwd(), '..', 'data')  
os.makedirs(DATA_FOLDER, exist_ok=True)

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
        filename = file.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        try:
            subprocess.run([
                "docker", "run", "--rm",
                "-v", f"{UPLOAD_FOLDER}:/app/uploads",
                "model-trainer",
                "python", "train.py", f"/app/uploads/{filename}"
            ], check=True)
            flash("✅ Training completed inside Docker!")
        except subprocess.CalledProcessError:
            flash("❌ Docker training failed!")
            return redirect(request.url)

        tracked_file_path = os.path.join(DATA_FOLDER, filename)
        shutil.move(file_path, tracked_file_path)


        try:
            subprocess.run(["git", "add", tracked_file_path], check=True)
            subprocess.run(["git", "commit", "-m", f"🔼 Uploaded {filename} for training"], check=True)
            subprocess.run(["git", "push"], check=True)
            flash("✅ File pushed to GitHub successfully!")
        except subprocess.CalledProcessError:
            flash("❌ Git operation failed. Check access or Git status.")

        return redirect(url_for('home'))

    flash('❌ Invalid file type. Please upload a .csv file.')
    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)