from flask import Flask, request, render_template, redirect, url_for, flash
import os
import subprocess

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # Use absolute path for Docker bind
ALLOWED_EXTENSIONS = {'csv'}

app = Flask(__name__)
app.secret_key = 'safi-super-secret'  # For production, read from env variables
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the uploads/ folder exists
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

        # Call the Docker container
        try:
            subprocess.run([
                "docker", "run",
                "--rm",  # Auto-remove the container after running
                "-v", f"{UPLOAD_FOLDER}:/app/uploads",  # Bind mount
                "model-trainer",  # Make sure this image is built and available
                "python", "train.py", f"/app/uploads/{file.filename}"
            ], check=True)
            flash("File uploaded and training completed!")
        except subprocess.CalledProcessError:
            flash("Training failed. Check container logs.")
        return redirect(url_for('home'))

    flash('Invalid file type. Please upload a .csv file')
    return redirect(request.url)

if __name__ == '__main__':
    app.run(debug=True)
