# Personal Info Detector

A Flask-based educational project that demonstrates how browser-provided client information can be collected and displayed for learning purposes.

> **Disclaimer:** This project is intended for educational use and authorized testing environments only.

---

## Features

- Browser detection
- Operating system detection
- Device information
- Screen resolution
- Battery status
- Network information
- Timezone
- Language detection

---

## Requirements

- Python 3.x
- Flask
- Requests
- Cloudflared (optional, for public access)

---

## Installation

### 1. Update your system

```bash
sudo apt update
sudo apt install python3-venv -y
```

### 2. Create a virtual environment

```bash
python3 -m venv flasklab
```

### 3. Activate the virtual environment

```bash
source flasklab/bin/activate
```

### 4. Install dependencies

```bash
pip install flask requests
```

---

## Running the Application

Start the Flask server:

```bash
python app.py
```

The application will be available at:

```
http://127.0.0.1:8080
```

---

## Public Access (Cloudflare Tunnel)

Install Cloudflared:

```bash
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb

sudo dpkg -i cloudflared-linux-amd64.deb
```

Start a tunnel:

```bash
cloudflared tunnel --url http://localhost:8080
```

Cloudflare will generate a temporary public URL similar to:

```
https://xxxxxxxx.trycloudflare.com
```

---

## Running Both Services

Open two terminal windows.

### Terminal 1

```bash
source flasklab/bin/activate
python main_config.py
```

### Terminal 2

```bash
cloudflared tunnel --url http://localhost:8080
```

---

## Project Structure

```
Personal_Info/
├── main_config.py
├── requirements.txt
├── README.md
├── .gitignore
├── static/
└── templates/
```

---

## Technologies Used

- Python
- Flask
- HTML
- CSS
- JavaScript
- Cloudflare Tunnel

---

## License

This project is provided for educational purposes only.
```
