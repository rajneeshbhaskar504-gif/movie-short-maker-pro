import streamlit as st
import subprocess
import os

# Streamlit Page Design
st.set_page_config(page_title="Rajneesh Movie Pro", layout="wide", page_icon="🎬")
st.title("🎬 Rajneesh Bhaskar - Professional Shorts Creator")
st.write("Apni video upload karein aur purane logos ko remove karke professional layout banayein.")

LOGO_FILE = "1642.jpg"

uploaded_file = st.file_uploader("Video File Upload Karein", type=['mp4', 'mkv'])

if uploaded_file:
    st.sidebar.header("✍️ Text Customization")
    # Yahan aap apni movie ke hisab se text likh sakte hain
    line1 = st.sidebar.text_input("Top Line (Yellow Text)", "Pehli Line Likhein")
    line2 = st.sidebar.text_input("Bottom Line (White Text)", "Doosri Line Likhein")
    
    if st.button("🚀 Process & Remove Old Logos"):
        input_p = "input_temp.mp4"
        output_p = "rajneesh_final_clean.mp4"
        
        # Uploaded file ko local disk par save karna
        with open(input_p, "wb") as f:
            f.write(uploaded_file.read())
        
        with st.spinner("Processing... Purane logos ko kaat kar naya layout banaya ja raha hai..."):
            # Linux server par standard font path
            font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
            
            # MASTER LOGIC FOR CLEANING:
            # - hflip: Copyright shield ke liye video mirror karega
            # - crop=iw:ih-240:0:120: Upar aur niche se 120-120px permanently cut (Purana logo gayab!)
            # - scale=720:-1: Video width ko 720px sharp karega
            # - pad=720:1280...: Nayi solid black patti lagayega shorts ke liye
            clean_vf = (
                f"hflip,crop=iw:ih-240:0:120,scale=720:-1,pad=720:1280:(ow-iw)/2:(oh-ih)/2:black,"
                f"drawtext=text='{line1}':fontfile={font_path}:fontcolor=yellow:fontsize=45:x=(w-text_w)/2:y=140:shadowcolor=black:shadowx=2:shadowy=2,"
                f"drawtext=text='{line2}':fontfile={font_path}:fontcolor=white:fontsize=45:x=(w-text_w)/2:y=200:shadowcolor=black:shadowx=2:shadowy=2"
            )
            
            # Niche ka watermark
            footer_text = f"drawtext=text='Rajneesh Bhaskar':fontfile={font_path}:fontcolor=white@0.4:fontsize=28:x=(w-text_w)/2:y=h-130"

            # Check if your logo exists
            if os.path.exists(LOGO_FILE):
                logo_proc = "scale=85:85,format=rgba,geq=r='r(X,Y)':a='if(gt(hypot(X-W/2,Y-H/2),W/2),0,255)'"
                cmd = [
                    'ffmpeg', '-y', '-i', input_p, '-i', LOGO_FILE,
                    '-filter_complex', f"[0:v]{clean_vf},{footer_text}[v1];[1:v]{logo_proc}[logo];[v1][logo]overlay=W-w-35:35",
                    '-af', "atempo=1.06",
                    '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '18', '-pix_fmt', 'yuv420p',
                    output_p
                ]
            else:
                cmd = ['ffmpeg', '-y', '-i', input_p, '-vf', f"{clean_vf},{footer_text}", '-af', "atempo=1.06", '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '18', output_p]
            
            # Running FFmpeg command safely
            res = subprocess.run(cmd, capture_output=True, text=True)
            
            if os.path.exists(output_p):
                st.success("✅ Video Taiyar! Purane saare logos hat chuke hain.")
                with open(output_p, "rb") as f:
                    st.download_button("📥 Download Clean Video", f, "rajneesh_pro_short.mp4")
            else:
                st.error("Processing mein dikkat aayi! FFmpeg Log niche dekhein:")
                st.code(res.stderr)
        
        # Temp files clear karna taaki server crash na ho
        if os.path.exists(input_p): os.remove(input_p)

