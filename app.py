from flask import Flask, request, render_template, send_file
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
DECRYPT_FOLDER = "decrypted"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DECRYPT_FOLDER, exist_ok=True)

KEY = get_random_bytes(16)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]
    data = file.read()
    iv = get_random_bytes(16)
    cipher = AES.new(KEY, AES.MODE_CBC, iv)
    encrypted = iv + cipher.encrypt(pad(data, AES.block_size))

    filename = file.filename + ".enc"
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "wb") as f:
        f.write(encrypted)

    return f"Encrypted and saved as {filename}"

@app.route("/download", methods=["POST"])
def download():
    filename = request.form["filename"]
    path = os.path.join(UPLOAD_FOLDER, filename)
    with open(path, "rb") as f:
        content = f.read()
        iv = content[:16]
        cipher = AES.new(KEY, AES.MODE_CBC, iv)
        decrypted = unpad(cipher.decrypt(content[16:]), AES.block_size)

    out_path = os.path.join(DECRYPT_FOLDER, filename.replace(".enc", ""))
    with open(out_path, "wb") as f:
        f.write(decrypted)

    return send_file(out_path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)
