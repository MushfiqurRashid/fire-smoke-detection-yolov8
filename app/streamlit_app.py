"""
Streamlit dashboard for fire and smoke detection.

Beautiful, professional UI for real-time detection and safety recommendations.
"""

import streamlit as st
from streamlit_option_menu import option_menu
from PIL import Image, ImageDraw
import numpy as np
import cv2
from pathlib import Path
import io
import logging

from app.predictor import get_predictor
from app.recommender import SafetyRecommender
from app.utils import draw_detections, resize_image, calculate_statistics, generate_report
from src.config import get_config
from src.logger import setup_logger

# Setup logging
logger = setup_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="Fire & Smoke Detection",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main {
        padding-top: 2rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .alert-critical {
        background-color: #ffcccc;
        border-left: 4px solid #ff0000;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    .alert-warning {
        background-color: #fff3cd;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
    .alert-safe {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        border-radius: 0.25rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


def init_predictor():
    """Initialize predictor with caching."""
    if 'predictor' not in st.session_state:
        try:
            st.session_state.predictor = get_predictor()
            return True
        except Exception as e:
            st.error(f"Failed to load model: {e}")
            return False
    return True


def display_hero():
    """Display hero section."""
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://img.icons8.com/color/96/000000/fire.png", width=80)
    
    with col2:
        st.title("🔥 Fire & Smoke Detection System")
        st.markdown(
            "**Advanced Real-time Detection for Industrial Safety**\n\n"
            "Powered by YOLOv8 | Detect hazards instantly | Get actionable recommendations"
        )


def display_metrics():
    """Display key metrics."""
    st.subheader("📊 System Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Model", "YOLOv8n", "1.3M parameters")
    
    with col2:
        st.metric("Dataset", "D-Fire", "21,000+ images")
    
    with col3:
        st.metric("Classes", "2", "Fire + Smoke")
    
    with col4:
        if st.session_state.predictor:
            model_info = st.session_state.predictor.get_model_info()
            st.metric("Status", "✅ Ready", "Online")


def page_home():
    """Home page."""
    display_hero()
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### ✨ Key Features")
        st.markdown("""
        - 🎯 Real-time fire and smoke detection
        - 📸 Support for images and videos
        - 🎥 Live webcam streaming
        - ⚡ Lightning-fast inference
        - 🚨 Intelligent alert system
        - 💡 Automated safety recommendations
        - 📊 Comprehensive analytics
        - 🔒 Enterprise-grade reliability
        """)
    
    with col2:
        st.markdown("### 🔍 How It Works")
        st.markdown("""
        1. **Upload** your image or video
        2. **Process** using advanced YOLOv8 model
        3. **Detect** fire and smoke hazards
        4. **Analyze** severity and risks
        5. **Recommend** safety actions
        6. **Report** comprehensive findings
        """)
    
    st.divider()
    display_metrics()


def page_detection():
    """Detection page."""
    st.header("🎯 Detection & Analysis")
    
    tab1, tab2, tab3 = st.tabs(["Image Detection", "Video Detection", "Webcam Stream"])
    
    # Image Detection Tab
    with tab1:
        st.subheader("Upload Image for Detection")
        
        uploaded_file = st.file_uploader(
            "Choose an image (JPG, PNG)",
            type=["jpg", "jpeg", "png"],
            key="image_upload"
        )
        
        confidence = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.25,
            step=0.05
        )
        
        if uploaded_file is not None:
            with st.spinner("🔄 Processing image..."):
                # Save and process
                image = Image.open(uploaded_file)
                
                # Resize for display
                display_image = resize_image(image, max_size=800)
                
                # Run prediction
                result = st.session_state.predictor.predict_image(image, confidence)
                
                # Display results
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 📷 Original Image")
                    st.image(display_image, use_column_width=True)
                
                with col2:
                    st.markdown("### 🎯 Detections")
                    
                    if result.get("status") == "success":
                        detections = result.get("detections", [])
                        alerts = result.get("alerts", [])
                        
                        # Draw detections
                        annotated = draw_detections(image, detections, confidence)
                        annotated = resize_image(annotated, max_size=800)
                        st.image(annotated, use_column_width=True)
                        
                        # Detection count
                        st.metric("Detections Found", len(detections))
                        
                        if detections:
                            st.markdown("**Detection Details:**")
                            for i, det in enumerate(detections, 1):
                                st.write(
                                    f"  {i}. **{det['class'].upper()}** "
                                    f"(Confidence: {det['confidence']:.2%})"
                                )
                    else:
                        st.error(f"Detection failed: {result.get('error', 'Unknown error')}")
                
                # Safety Analysis
                st.divider()
                st.markdown("### 🚨 Safety Analysis")
                
                safety_report = SafetyRecommender.generate_safety_report(result)
                
                # Overall Status
                status = safety_report.get("overall_status", "UNKNOWN")
                
                if "CRITICAL" in status:
                    st.markdown(
                        f'<div class="alert-critical"><strong>🚨 {status}</strong></div>',
                        unsafe_allow_html=True
                    )
                elif "WARNING" in status:
                    st.markdown(
                        f'<div class="alert-warning"><strong>⚠️ {status}</strong></div>',
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f'<div class="alert-safe"><strong>✅ {status}</strong></div>',
                        unsafe_allow_html=True
                    )
                
                # Recommendations
                recommendations = safety_report.get("recommendations", [])
                if recommendations:
                    st.markdown("**📋 Safety Recommendations:**")
                    for i, rec in enumerate(recommendations, 1):
                        st.write(f"{i}. {rec}")
    
    # Video Detection Tab
    with tab2:
        st.subheader("Upload Video for Detection")
        st.info("⚠️ Video processing may take a few minutes depending on file size and duration")
        
        uploaded_video = st.file_uploader(
            "Choose a video (MP4, AVI)",
            type=["mp4", "avi", "mov"],
            key="video_upload"
        )
        
        confidence = st.slider(
            "Confidence Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.25,
            step=0.05,
            key="video_conf"
        )
        
        if uploaded_video is not None:
            with st.spinner("🔄 Processing video... This may take a while"):
                # Save video temporarily
                import tempfile
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
                    tmp.write(uploaded_video.getbuffer())
                    tmp_path = tmp.name
                
                try:
                    # Run detection
                    output_path = tmp_path.replace(".mp4", "_detected.mp4")
                    result = st.session_state.predictor.detector.detect_video(
                        tmp_path,
                        confidence,
                        output_path
                    )
                    
                    if result.get("status") == "success":
                        st.success("✅ Video processing completed!")
                        st.metric("Total Frames", result.get("total_frames", 0))
                        
                        # Show download button
                        with open(output_path, 'rb') as f:
                            st.download_button(
                                label="📥 Download Detected Video",
                                data=f.read(),
                                file_name="detected_video.mp4",
                                mime="video/mp4"
                            )
                    else:
                        st.error(f"Processing failed: {result.get('error')}")
                
                except Exception as e:
                    st.error(f"Error processing video: {e}")
    
    # Webcam Tab
    with tab3:
        st.subheader("Live Webcam Detection")
        st.info("Click 'Start Detection' to begin capturing from your webcam")
        
        duration = st.slider(
            "Capture Duration (seconds)",
            min_value=10,
            max_value=60,
            value=30,
            step=10,
            key="webcam_duration"
        )
        
        if st.button("🎥 Start Webcam Detection"):
            with st.spinner("📹 Capturing from webcam..."):
                try:
                    result = st.session_state.predictor.detector.detect_webcam(
                        duration=duration,
                        conf=0.25
                    )
                    
                    if result.get("status") == "success":
                        st.success("✅ Capture completed!")
                        st.metric("Frames Captured", result.get("total_frames", 0))
                    else:
                        st.error(f"Capture failed: {result.get('error')}")
                
                except Exception as e:
                    st.error(f"Webcam error: {e}")


def page_about():
    """About page."""
    st.header("ℹ️ About This System")
    
    st.markdown("""
    ## Fire and Smoke Detection Using YOLOv8 for Industrial Safety Monitoring
    
    ### Overview
    This advanced detection system leverages the power of YOLOv8, a state-of-the-art object detection model,
    to identify fire and smoke hazards in real-time across images, videos, and live camera feeds.
    
    ### Technology Stack
    - **Detection Model**: YOLOv8 (nano variant for edge deployment)
    - **Dataset**: D-Fire with 21,000+ annotated images
    - **Classes**: Fire and Smoke
    - **Framework**: Ultralytics YOLOv8
    - **APIs**: FastAPI for REST endpoints
    - **Dashboard**: Streamlit for interactive UI
    - **Deployment**: Docker containerization
    
    ### Key Features
    ✨ Real-time fire and smoke detection
    🎯 High accuracy on diverse industrial environments
    ⚡ Fast inference (GPU and CPU support)
    🚨 Intelligent alert thresholds
    💡 Automated safety recommendations
    📊 Comprehensive metrics and analytics
    
    ### Model Performance
    - Trained on D-Fire dataset (21,000+ images)
    - Optimized for industrial safety applications
    - Support for various lighting conditions
    - Robust to occlusions and partial detections
    
    ### Use Cases
    - 🏭 Manufacturing facilities
    - 🌳 Forest fire detection
    - 🏢 Building safety monitoring
    - 🛢️ Chemical plants and refineries
    - ⚙️ Data centers and server rooms
    
    ### Safety Thresholds
    - **Fire**: Confidence > 60% triggers CRITICAL alert
    - **Smoke**: Confidence > 50% triggers WARNING alert
    
    ### Deployment Options
    - Streamlit Dashboard (this interface)
    - FastAPI REST API
    - Docker containers
    - Local installation
    
    ---
    
    **Built by**: AI Engineer | Computer Vision Specialist
    **Version**: 1.0.0
    **License**: MIT
    """)


def main():
    """Main application."""
    # Initialize predictor
    if not init_predictor():
        st.stop()
    
    # Sidebar navigation
    st.sidebar.title("🔥 Fire & Smoke Detection")
    st.sidebar.divider()
    
    page = option_menu(
        menu_title=None,
        options=["Home", "Detection", "About"],
        icons=["house", "eye", "info-circle"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"padding": "0!important"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "0px",
                "--hover-color": "#eee"
            }
        }
    )
    
    st.sidebar.divider()
    st.sidebar.markdown("### ⚙️ System Info")
    
    try:
        model_info = st.session_state.predictor.get_model_info()
        st.sidebar.write(f"**Model**: {model_info['model_name']}")
        st.sidebar.write(f"**Classes**: {', '.join(model_info['classes'])}")
        st.sidebar.write(f"**Status**: ✅ Ready")
    except Exception as e:
        st.sidebar.error(f"Model error: {e}")
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        "Made with ❤️ for industrial safety\n\n"
        "[GitHub](https://github.com) | [Docs](https://docs)"
    )
    
    # Route to pages
    if page == "Home":
        page_home()
    elif page == "Detection":
        page_detection()
    elif page == "About":
        page_about()


if __name__ == "__main__":
    main()
