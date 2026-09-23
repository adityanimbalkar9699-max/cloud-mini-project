# AWS S3 & CloudFront Production Deployment Guide

This guide provides step-by-step instructions to deploy both parts of your project to Amazon Web Services (AWS) or free cloud services so your family and evaluators can access it online over HTTPS.

---

## 1. Deploying the Documentation/Portfolio Website (`website/`) to AWS S3 & CloudFront CDN

### Step 1.1: Create Amazon S3 Bucket
1. Open the [AWS S3 Console](https://s3.console.aws.amazon.com/).
2. Click **Create Bucket**.
3. Set **Bucket Name**: `cryptex-vault-docs-unique-name` (Replace with your unique name).
4. Set **Region**: `us-east-1` (or your preferred region).
5. Uncheck **Block all public access** (for static hosting) or configure Origin Access Control (OAC).
6. Click **Create Bucket**.

### Step 1.2: Upload Website Assets
1. Open your new bucket in S3 Console.
2. Click **Upload** -> **Add Files** / **Add Folder**.
3. Select `index.html` and `style.css` from your `website/` folder.
4. Click **Upload**.

### Step 1.3: Enable S3 Static Website Hosting
1. Go to the bucket's **Properties** tab.
2. Scroll to the bottom to **Static website hosting** -> Click **Edit**.
3. Select **Enable**.
4. Set **Index document**: `index.html`.
5. Click **Save Changes**. Note down the S3 Website Endpoint URL (e.g. `http://cryptex-vault-docs.s3-website-us-east-1.amazonaws.com`).

### Step 1.4: Attach Amazon CloudFront CDN Distribution
1. Open the [AWS CloudFront Console](https://console.aws.amazon.com/cloudfront/).
2. Click **Create Distribution**.
3. Set **Origin Domain**: Select your S3 Website Endpoint.
4. Under **Viewer Protocol Policy**: Select **Redirect HTTP to HTTPS** (enforces secure HTTPS delivery).
5. Under **Cache Key and Origin Requests**: Choose **CachingOptimized**.
6. Click **Create Distribution**.
7. Once deployed, CloudFront provides a global domain (e.g. `https://d12345abcdef.cloudfront.net`) with SSL certificate enabled.

---

## 2. Deploying the Encrypted Vault Dashboard (`frontend/app.py`) to Streamlit Cloud (Free & Easy)

To host your personal cloud drive live so your family can access it from anywhere:

1. Push your project folder to a GitHub repository:
   ```bash
   git init
   git add .
   git commit -m "Deploying Cryptex Cloud Vault"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/cryptex-cloud-vault.git
   git push -u origin main
   ```
2. Go to [share.streamlit.io](https://share.streamlit.io/) (Streamlit Community Cloud).
3. Sign in with GitHub.
4. Click **New app**.
5. Select your repository, set **Main file path** to `frontend/app.py`.
6. Click **Deploy!**.
7. Your app will be live at `https://your-app-name.streamlit.app` with instant HTTPS security!

---

## 3. Architecture & Security Checklist

| Feature | Implementation | Security / Performance Standard |
| :--- | :--- | :--- |
| **Data at Rest Encryption** | AES-256-GCM | Authenticated cipher with 96-bit nonces |
| **Data in Transit** | HTTPS (TLS 1.3) | Enforced via CloudFront / Streamlit Cloud SSL |
| **Integrity Audit** | SHA-256 Checksums | 100% data parity verification on download |
| **Edge Distribution** | Amazon CloudFront | Sub-20ms edge latency via global PoPs |
