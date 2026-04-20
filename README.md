# 🛡️ AI-Gen Image Detector

A professional-grade **AI Image Verification Ecosystem**. This project combines classical digital forensics with a modern mobile experience to identify and explain the hidden signatures of synthetic content.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-green.svg)
![React Native](https://img.shields.io/badge/react--native-latest-blue.svg)

## 🎯 The Core Objective
In an era of deepfakes and AI-generated misinformation, this tool bridges the gap between "eye-balling" an image and having mathematical proof. It detects synthetic fingerprints left behind by AI generators like **Stable Diffusion, DALL-E 3, and Midjourney**.

---

## 🚀 Key Features

### **Forensic Engine (Backend)**
*   **Error Level Analysis (ELA)**: Detects inconsistencies in JPEG compression.
*   **LBP (Local Binary Patterns)**: Analyzes textures (skin, hair, fabric) for synthetic mathematically-perfect patterns.
*   **Frequency Harmonic Mapping**: Identifies the "checkerboard" residue left by AI upscalers.
*   **Metadata Audit**: Deep-scans EXIF/XMP data for camera and software markers.

### **Mobile Experience (Frontend)**
*   **Live Analysis**: Take or upload photos for instant forensic scanning.
*   **Interactive Anomalies**: Visual bounding boxes highlight "suspicious" regions on the image.
*   **AI Forensic Chat**: An integrated assistant to discuss forensic findings in plain language.
*   **Scan History**: A persistent local archive of all past detections with risk-level badges.

---

## 🛠️ Tech Stack

### **Backend**
- **Python / FastAPI**: High-performance async API.
- **OpenCV & NumPy**: Pixel-level forensic math.
- **SQLite / SQLAlchemy**: Secure result and user persistence.

### **Mobile**
- **React Native / Expo**: Cross-platform mobile architecture.
- **Axios**: Real-time communication with the forensic engine.
- **BlurView & Material Icons**: For a premium, dark-mode professional aesthetic.

---

## 📦 Installation & Setup

### **1. Backend Setup**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### **2. Mobile Setup**
1.  Update the `BASE_URL` in `src/services/api.js` with your local IP.
2.  Install dependencies:
    ```bash
    cd mobile
    npm install
    npx expo start
    ```

---

## ⚖️ License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/Herve-ndzye/AI-Gen-Images-Detector/issues).

---
*Created with ❤️ for Digital Forensics.*
