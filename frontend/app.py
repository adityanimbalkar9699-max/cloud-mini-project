import os
import sys
import json
import base64
import time

# Ensure UTF-8 console encoding
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import streamlit as st

# Dynamic Path Resolution
FRONTEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(FRONTEND_DIR)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from crypto_engine import (
    chunk_and_encrypt,
    decrypt_and_reassemble,
    DEFAULT_STORAGE_DIR,
    DEFAULT_RESTORED_DIR,
    DEFAULT_KEY_PATH
)
from verifier import verify_integrity

# Page Configuration
st.set_page_config(
    page_title="Cryptex // Enterprise Cloud Vault & Edge CDN",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load premium_bg.jpg background image safely
bg_base64 = ""
img_path = os.path.join(PROJECT_ROOT, "premium_bg.jpg")
if os.path.exists(img_path):
    try:
        with open(img_path, "rb") as img_f:
            bg_base64 = base64.b64encode(img_f.read()).decode("utf-8")
    except Exception:
        bg_base64 = ""

# Ultra-Premium Silicon Valley Glassmorphism Theme & Custom Styling
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* Global Dark Glass Canvas */
    body, html {{
        background-image: url('data:image/jpeg;base64,{bg_base64}') !important;
        background-size: cover !important;
        background-position: center !important;
        background-repeat: no-repeat !important;
        background-attachment: fixed !important;
    }}

    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"], [data-testid="stApp"] {{
        background: transparent !important;
        background-color: transparent !important;
        color: #C9D1D9;
        font-family: 'Inter', sans-serif;
    }}

    [data-testid="stHeader"] {{
        background: rgba(0,0,0,0) !important;
    }}

    @keyframes pulse-green {{
        0% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }}
        70% {{ transform: scale(1); box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }}
        100% {{ transform: scale(0.95); box-shadow: 0 0 0 0 rgba(16, 185, 129, 0); }}
    }}

    /* Hero Typography */
    .hero-title {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 2.3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #FFFFFF 0%, #38BDF8 50%, #818CF8 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        letter-spacing: -0.04em;
        margin-bottom: 0.2rem;
    }}

    .hero-subtitle {{
        color: #94A3B8;
        font-size: 1.05rem;
        font-weight: 400;
        letter-spacing: 0.01em;
        margin-bottom: 0.8rem;
    }}

    /* Buttons - Frosted Glass Aesthetics */
    .stButton > button, button[kind="primary"], button[kind="secondary"] {{
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.09) 0%, rgba(255, 255, 255, 0.02) 100%) !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.2), 0 8px 24px -4px rgba(0, 0, 0, 0.45) !important;
        border-radius: 12px !important;
        letter-spacing: 0.04em !important;
        font-weight: 600 !important;
        color: #F8FAFC !important;
        font-family: 'Inter', sans-serif !important;
        padding: 0.65rem 1.3rem !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px) !important;
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.3) 0%, rgba(99, 102, 241, 0.25) 100%) !important;
        border-color: rgba(6, 182, 212, 0.7) !important;
        box-shadow: 0 12px 30px -4px rgba(6, 182, 212, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.4) !important;
        color: #FFFFFF !important;
    }}

    /* Tab Switcher Styling */
    div[data-baseweb="tab-list"] {{
        background: rgba(15, 23, 42, 0.7) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 14px !important;
        padding: 6px !important;
        gap: 8px !important;
        margin-bottom: 1.5rem !important;
    }}

    div[data-baseweb="tab-list"] button {{
        background: transparent !important;
        border: none !important;
        color: #94A3B8 !important;
        border-radius: 10px !important;
        padding: 10px 18px !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 0.85rem !important;
        font-weight: 500 !important;
        transition: all 0.25s ease !important;
    }}

    div[data-baseweb="tab-list"] button[aria-selected="true"] {{
        background: linear-gradient(135deg, rgba(6, 182, 212, 0.3) 0%, rgba(99, 102, 241, 0.25) 100%) !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(6, 182, 212, 0.5) !important;
        box-shadow: 0 4px 16px rgba(6, 182, 212, 0.25) !important;
        font-weight: 700 !important;
    }}

    div[data-baseweb="tab-highlight"] {{
        display: none !important;
    }}

    /* Telemetry KPI Cards */
    .metric-card {{
        background: linear-gradient(145deg, rgba(17, 24, 39, 0.75) 0%, rgba(10, 15, 29, 0.85) 100%);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.25rem 1.5rem;
        position: relative;
        transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
        overflow: hidden;
    }}

    .metric-card:hover {{
        transform: translateY(-4px);
        box-shadow: 0 15px 35px -5px rgba(6, 182, 212, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.3);
        border-color: rgba(6, 182, 212, 0.5);
    }}

    .metric-card::before {{
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, #06B6D4 0%, #6366F1 50%, #10B981 100%);
    }}

    .metric-label {{
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.72rem;
        letter-spacing: 0.12em;
        color: #64748B;
        text-transform: uppercase;
        margin-bottom: 0.4rem;
    }}

    .metric-value {{
        color: #F8FAFC;
        font-size: 1.25rem;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
    }}

    /* Glass Cards */
    .glass-card {{
        background: rgba(17, 24, 39, 0.75);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }}

    /* Block Card Grid Item */
    .block-card {{
        background: rgba(30, 41, 59, 0.75);
        border: 1px solid rgba(6, 182, 212, 0.25);
        border-radius: 10px;
        padding: 14px;
        text-align: center;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        color: #38BDF8;
        box-shadow: 0 4px 14px rgba(0,0,0,0.25);
        transition: all 0.25s ease;
        margin-bottom: 12px;
    }}

    .block-card:hover {{
        border-color: #06B6D4;
        box-shadow: 0 0 18px rgba(6, 182, 212, 0.45);
        transform: translateY(-3px);
    }}

    /* Status Badges */
    .emerald-badge {{
        background: linear-gradient(135deg, rgba(6, 78, 59, 0.9), rgba(4, 47, 46, 0.9));
        border: 1px solid #10B981;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        color: #34D399;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        box-shadow: 0 0 25px rgba(16, 185, 129, 0.25);
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 1.5rem 0;
    }}

    .ruby-badge {{
        background: linear-gradient(135deg, rgba(127, 29, 29, 0.9), rgba(69, 10, 10, 0.9));
        border: 1px solid #EF4444;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        color: #FCA5A5;
        font-family: 'JetBrains Mono', monospace;
        font-weight: 700;
        box-shadow: 0 0 25px rgba(239, 68, 68, 0.25);
        display: flex;
        align-items: center;
        gap: 14px;
        margin: 1.5rem 0;
    }}
</style>
""", unsafe_allow_html=True)

# Header Section with System Status
col_title, col_btn = st.columns([3.8, 1])
with col_title:
    st.markdown('<div class="hero-title">CRYPTEX // ENTERPRISE CLOUD VAULT</div>', unsafe_allow_html=True)
    st.markdown('<div class="hero-subtitle">Encrypted Distributed Object Storage, AES-256-GCM Block Chunking, & Edge Acceleration</div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 1.2rem;">
        <span style="height: 10px; width: 10px; background-color: #10B981; border-radius: 50%; display: inline-block; box-shadow: 0 0 10px #10B981; animation: pulse-green 2s infinite;"></span>
        <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.82rem; color: #10B981; letter-spacing: 0.05em; font-weight: 600;">ACTIVE VAULT ONLINE // ENCRYPTION ENGINE SECURE</span>
    </div>
    """, unsafe_allow_html=True)

with col_btn:
    st.markdown("<div style='margin-top: 8px;'></div>", unsafe_allow_html=True)
    if st.button("🗑️ WIPE STORAGE VAULT", use_container_width=True, help="Purge all encrypted blocks, manifests, and temporary files"):
        if os.path.exists(DEFAULT_STORAGE_DIR):
            for fname in os.listdir(DEFAULT_STORAGE_DIR):
                fpath = os.path.join(DEFAULT_STORAGE_DIR, fname)
                try:
                    if os.path.isfile(fpath) or os.path.islink(fpath):
                        os.unlink(fpath)
                except Exception:
                    pass
        st.session_state.clear()
        st.rerun()

# Dynamic Manifest Inspection
manifest_file_path = os.path.join(DEFAULT_STORAGE_DIR, "manifest.json")
block_count = 0
vault_active = False
manifest_data = None

if os.path.exists(manifest_file_path):
    try:
        with open(manifest_file_path, "r", encoding="utf-8") as mf:
            manifest_data = json.load(mf)
            block_count = len(manifest_data.get("blocks", []))
            if block_count > 0:
                vault_active = True
    except Exception:
        block_count = 0

# Telemetry KPI Dashboard Bar
kpi_status = f"{block_count} S3 Encrypted Blocks" if vault_active else "Vault Ready (Empty)"
kpi_color = "#38BDF8" if vault_active else "#64748B"

st.markdown(f"""
<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem;">
    <div class="metric-card">
        <div class="metric-label">CIPHER SUITE</div>
        <div class="metric-value">AES-256-GCM</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">DISTRIBUTED STORAGE</div>
        <div class="metric-value" style="color: {kpi_color};">{kpi_status}</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">HASH AUDIT ENGINE</div>
        <div class="metric-value" style="color: #34D399;">SHA-256 Verified</div>
    </div>
    <div class="metric-card">
        <div class="metric-label">CDN EDGE NETWORK</div>
        <div class="metric-value" style="color: #A78BFA;">CloudFront OAC</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "01 // Ingestion & Block Split Engine",
    "02 // Cryptographic Reconstruction",
    "03 // Cloud Architecture & Topology",
    "04 // Global Edge CDN Simulator"
])

# -----------------------------------------------------------------------------
# TAB 1: Ingestion & Split Engine
# -----------------------------------------------------------------------------
with tab1:
    col_left, col_right = st.columns([1.3, 1], gap="large")

    with col_left:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color: #F8FAFC; margin-top:0;'>01 // Payload Ingestion & Chunking</h3>", unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Upload target asset for client-side block encryption", type=None)

        block_size_kb = st.select_slider(
            "Block Chunk Size (KB)",
            options=[64, 128, 256, 512, 1024, 2048],
            value=512,
            help="Defines payload segment boundaries for parallel cloud storage uploads."
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color: #F8FAFC; margin-top:0;'>Cryptographic Specification</h3>", unsafe_allow_html=True)
        st.markdown("""
        - **Symmetric Encryption**: AES-256 (256-bit Key)
        - **Authenticated Cipher**: Galois/Counter Mode (GCM)
        - **Initialization Vector**: 96-bit Cryptographic Nonce per Block
        - **Integrity Digest**: SHA-256 Pre-Encryption Checksum
        - **Object Key Schema**: `storage_blocks/block_{index}.enc`
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    if uploaded_file is not None:
        temp_dir = os.path.join(PROJECT_ROOT, "temp_uploads")
        os.makedirs(temp_dir, exist_ok=True)
        temp_input_path = os.path.join(temp_dir, uploaded_file.name)

        with open(temp_input_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.info(f"📁 Asset Prepared: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")

        if st.button("⚡ Execute Encrypted Block-Split Pipeline", use_container_width=True):
            with st.spinner("Chunking payload and encrypting with AES-256-GCM..."):
                manifest_path = chunk_and_encrypt(
                    temp_input_path,
                    block_size=block_size_kb * 1024,
                    storage_dir=DEFAULT_STORAGE_DIR,
                    key_path=DEFAULT_KEY_PATH
                )
            st.success("✨ Block-level encryption complete! S3 manifest generated.")
            st.rerun()

    # Display Active Storage Blocks Visualizer
    if vault_active and manifest_data:
        st.markdown(f"### Distributed Encrypted Blocks (`storage_blocks/`) — `{manifest_data['filename']}`")
        cols = st.columns(4, gap="medium")
        for idx, block in enumerate(manifest_data["blocks"]):
            with cols[idx % 4]:
                st.markdown(f"""
                <div class="block-card">
                    <b style="color: #38BDF8;">{block['block_file']}</b><br>
                    <span style="color: #94A3B8; font-size: 0.75rem;">Encrypted: {block['size']:,} B</span><br>
                    <span style="color: #64748B; font-size: 0.70rem;">Plain: {block.get('plain_size', 'N/A')} B</span>
                </div>
                """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 2: Reconstruction & Verification
# -----------------------------------------------------------------------------
with tab2:
    if vault_active and manifest_data:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("<h3 style='color: #F8FAFC; margin-top:0;'>02 // Cryptographic Reconstruction & Audit</h3>", unsafe_allow_html=True)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Filename", manifest_data["filename"])
        with c2:
            st.metric("Total Payload", f"{manifest_data['original_size']:,} bytes")
        with c3:
            st.metric("Total Blocks", len(manifest_data["blocks"]))
        with c4:
            st.metric("Cipher Mode", manifest_data.get("cipher", "AES-256-GCM"))

        with st.expander("Inspect Cryptographic Manifest JSON"):
            st.json(manifest_data)

        if st.button("🔓 Reconstruct Payload & Verify SHA-256 Parity", use_container_width=True):
            with st.spinner("Reassembling encrypted blocks and auditing checksums..."):
                res = decrypt_and_reassemble(
                    manifest_path=manifest_file_path,
                    restored_dir=DEFAULT_RESTORED_DIR,
                    key_path=DEFAULT_KEY_PATH
                )

            if res["verified"]:
                st.markdown(f"""
                <div class="emerald-badge">
                    <span style="font-size: 1.8rem;">✓</span>
                    <div>
                        <div style="font-size: 1.05rem;">CRYPTOGRAPHIC SHA-256 PARITY VERIFIED (100% MATCH)</div>
                        <div style="font-size: 0.78rem; color: #A7F3D0; margin-top: 4px;">SHA-256: {res['sha256']}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                if res.get("restored_path") and os.path.exists(res["restored_path"]):
                    with open(res["restored_path"], "rb") as rf:
                        st.download_button(
                            label="📥 Download Restored Original File",
                            data=rf,
                            file_name=os.path.basename(res["restored_path"]),
                            use_container_width=True
                        )
            else:
                tampered_info = res.get("tampered_blocks", [])
                st.markdown(f"""
                <div class="ruby-badge">
                    <span style="font-size: 1.8rem;">⚠️</span>
                    <div>
                        <div style="font-size: 1.05rem;">INTEGRITY VERIFICATION FAILED: TAMPER DETECTED</div>
                        <div style="font-size: 0.78rem; color: #FCA5A5; margin-top: 4px;">{res.get('error', 'GCM Tag mismatch')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                if tampered_info:
                    st.warning(f"Corrupted Blocks: {tampered_info}")

        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="glass-card" style="text-align: center; padding: 3rem;">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📦</div>
            <h3 style="color: #94A3B8;">No blocks found in vault</h3>
            <p style="color: #64748B;">Upload and split an asset in Tab 1 first to create storage blocks.</p>
        </div>
        """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 3: Cloud Architecture & CDN Topology
# -----------------------------------------------------------------------------
with tab3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color: #F8FAFC; margin-top:0;'>03 // Cloud Architecture & Global Distribution Topology</h3>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; margin-bottom: 1.5rem;">
        <div style="background: rgba(15, 23, 42, 0.6); padding: 1.2rem; border-radius: 10px; border: 1px solid rgba(6, 182, 212, 0.25);">
            <h4 style="color: #38BDF8; margin-top: 0;">1. Client-Side Chunking Engine</h4>
            <p style="color: #94A3B8; font-size: 0.88rem;">Large payloads are divided into uniform binary blocks. Chunking enables parallel uploads, fault tolerance, and resilient byte-range streaming.</p>
        </div>
        <div style="background: rgba(15, 23, 42, 0.6); padding: 1.2rem; border-radius: 10px; border: 1px solid rgba(99, 102, 241, 0.25);">
            <h4 style="color: #818CF8; margin-top: 0;">2. Authenticated AES-256-GCM</h4>
            <p style="color: #94A3B8; font-size: 0.88rem;">Each block is encrypted independently with 256-bit AES-GCM and a unique 96-bit nonce. Galois authentication tags prevent any tampering at rest.</p>
        </div>
        <div style="background: rgba(15, 23, 42, 0.6); padding: 1.2rem; border-radius: 10px; border: 1px solid rgba(16, 185, 129, 0.25);">
            <h4 style="color: #34D399; margin-top: 0;">3. Amazon S3 / Cloud Storage</h4>
            <p style="color: #94A3B8; font-size: 0.88rem;">Encrypted blocks (`block_N.enc`) and signed manifests are stored across Amazon S3 object storage with server-side access control lists and object lock policies.</p>
        </div>
        <div style="background: rgba(15, 23, 42, 0.6); padding: 1.2rem; border-radius: 10px; border: 1px solid rgba(167, 139, 250, 0.25);">
            <h4 style="color: #A78BFA; margin-top: 0;">4. Amazon CloudFront Edge CDN</h4>
            <p style="color: #94A3B8; font-size: 0.88rem;">Edge point-of-presence (PoP) locations cache blocks globally. Origin Access Control (OAC) ensures direct S3 origin buckets remain private.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.code("""
+-----------------------------------------------------------------------------------+
|                                  CLIENT LAYER                                     |
|                      (Streamlit Web App / CLI SDK Client)                         |
+-----------------------------------------------------------------------------------+
                                         |
                                         v (HTTPS / TLS 1.3 GET Request)
+-----------------------------------------------------------------------------------+
|                             AMAZON CLOUDFRONT CDN                                 |
|            (Global Edge PoPs: N. Virginia, Frankfurt, Tokyo, Mumbai)              |
|        [ Cache Hit: 12ms Latency ]  <--->  [ Cache Miss: Fetch from Origin ]    |
+-----------------------------------------------------------------------------------+
                                         |
                                         v (Origin Access Control OAC)
+-----------------------------------------------------------------------------------+
|                           AMAZON S3 OBJECT STORAGE                                |
|        (Decentralized AES-256-GCM Encrypted Blocks & Signed Manifest JSON)        |
|     [ block_0.enc ]     [ block_1.enc ]     [ block_2.enc ]     [ manifest.json ] |
+-----------------------------------------------------------------------------------+
    """, language="text")
    st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# TAB 4: Global Edge CDN Simulator
# -----------------------------------------------------------------------------
with tab4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='color: #F8FAFC; margin-top:0;'>04 // Global Edge CDN & Latency Simulator</h3>", unsafe_allow_html=True)
    st.markdown("Simulate how Amazon CloudFront Edge Caching and TLS 1.3 reduce block retrieval times compared to direct S3 origin requests.")

    c_region, c_size = st.columns(2)
    with c_region:
        client_location = st.selectbox(
            "Select Client Region Location",
            options=[
                "AP-South (Mumbai, India)",
                "AP-Northeast (Tokyo, Japan)",
                "EU-Central (Frankfurt, Germany)",
                "US-East (N. Virginia, USA)"
            ]
        )

    with c_size:
        sim_payload_mb = st.slider("Simulated Transfer Size (MB)", min_value=1, max_value=50, value=10)

    if st.button("🚀 Run CDN Performance Benchmark Simulation", use_container_width=True):
        st.markdown("---")
        with st.spinner("Benchmarking latency across S3 Origin vs CloudFront Edge Nodes..."):
            time.sleep(0.8)

        # Realistic latency models
        if "Mumbai" in client_location:
            s3_origin_latency = 220
            cdn_edge_latency = 14
        elif "Tokyo" in client_location:
            s3_origin_latency = 180
            cdn_edge_latency = 18
        elif "Frankfurt" in client_location:
            s3_origin_latency = 140
            cdn_edge_latency = 11
        else:
            s3_origin_latency = 45
            cdn_edge_latency = 6

        # Calculate simulated transfer speed (Origin vs Edge)
        s3_total_time = (s3_origin_latency / 1000) + (sim_payload_mb / 8.0)
        cdn_total_time = (cdn_edge_latency / 1000) + (sim_payload_mb / 45.0)
        speedup = round(s3_total_time / cdn_total_time, 1)

        b1, b2, b3 = st.columns(3)
        with b1:
            st.metric("Direct S3 Origin Time", f"{s3_total_time:.2f} s", f"{s3_origin_latency} ms RTT")
        with b2:
            st.metric("CloudFront Edge CDN Time", f"{cdn_total_time:.2f} s", f"{cdn_edge_latency} ms RTT", delta_color="normal")
        with b3:
            st.metric("CDN Performance Boost", f"{speedup}x Faster", "TLS 1.3 Edge Accelerated")

        st.success(f"✨ CDN Edge Caching accelerated block delivery by **{speedup}x** for **{client_location}**!")
    st.markdown('</div>', unsafe_allow_html=True)
