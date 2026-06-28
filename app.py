import os
import whisper
from gtts import gTTS
from moviepy import VideoFileClip, AudioFileClip
from transformers import pipeline
import gradio as gr

def video_to_text(video_path):
    print("1. Video se audio aur text nikal raha hai...")
    video = VideoFileClip(video_path)
    audio_path = "temp_audio.mp3"
    video.audio.write_audiofile(audio_path, bitrate="64k", logger=None)
    
    model = whisper.load_model("tiny", device="cpu")
    result = model.transcribe(audio_path, language="hi")
    return result["text"]

def generate_viral_script(full_transcript):
    print("2. AI Script generate kar raha hai...")
    if not full_transcript.strip():
        return "Dosto, aaj ki video bohot mazaedar hone wali hai, ise poora dekhein!"
        
    pipe = pipeline("text-generation", model="Qwen/Qwen1.5-0.5B-Chat", device="cpu")
    prompt = f"<|im_start|>system\nAap ek Reels creator hain. Niche di gayi movie transcript se ek lamba, suspenseful aur viral Hindi voiceover script likhein jo lagbhag 80 se 90 seconds tak chale.<|im_end|>\n<|im_start|>user\nTranscript: {full_transcript}<|im_end|>\n<|im_start|>assistant\n"
    
    outputs = pipe(prompt, max_new_tokens=300, do_sample=True, temperature=0.7)
    generated_text = outputs[0]["generated_text"].split("<|im_start|>assistant\n")[-1]
    return generated_text

def text_to_voice(hindi_text):
    print("3. Voiceover taiyar ho raha hai...")
    tts = gTTS(text=hindi_text, lang='hi', slow=False)
    voice_path = "ai_voiceover.mp3"
    tts.save(voice_path)
    return voice_path

def make_final_short(video_path, ai_voice_path):
    print("4. Video cutting aur Copyright Shield apply ho raha hai...")
    clip = VideoFileClip(video_path)
    audio_clip = AudioFileClip(ai_voice_path)
    
    duration = min(90, audio_clip.duration, clip.duration)
    short_clip = clip.subclip(0, duration)
    
    w, h = short_clip.size
    target_w = int(h * 9 / 16)
    x_center = w / 2
    crop_clip = short_clip.crop(x_center=x_center, width=target_w, height=h)
    
    # Copyright Shield (Zoom 5% + Mirror)
    final_clip = crop_clip.fx(lambda c: c.resize(1.05)).fx(lambda c: c.mirrorx())
    
    final_clip = final_clip.set_audio(audio_clip.set_duration(duration))
    output_path = "viral_short_output.mp4"
    
    final_clip.write_videofile(output_path, codec="libx264", audio_codec="aac", preset="ultrafast", logger=None, threads=2)
    print("🎯 Video Taiyar Hai!")
    return output_path

def start_processing(video_file):
    try:
        transcript = video_to_text(video_file)
        hindi_script = generate_viral_script(transcript)
        voice_path = text_to_voice(hindi_script)
        final_video = make_final_short(video_file, voice_path)
        return final_video
    except Exception as e:
        print(f"Error: {e}")
        return None

with gr.Blocks() as demo:
    gr.Markdown("# 🎬 GitHub Codespaces Powered - AI Movie Explainer")
    with gr.Row():
        input_video = gr.Video(label="6 Minute Tak Ki Movie Clip Dalein")
        output_video = gr.Video(label="Aapka AI 90-Sec Video Taiyar Hai")
    btn = gr.Button("Generate Viral Video 🚀")
    btn.click(fn=start_processing, inputs=input_video, outputs=output_video)

demo.queue().launch(share=True)
