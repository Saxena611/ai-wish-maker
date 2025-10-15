import streamlit as st
import os, tempfile, time, requests, re
from pathlib import Path
from gtts import gTTS
from pydub import AudioSegment
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import io

st.set_page_config(page_title="AI Diwali Wish Maker", page_icon="🪔", layout="wide")

# Configuration - Load from environment variables or Streamlit secrets
def get_config(key, default):
    """Get config from env var or Streamlit secrets"""
    return os.getenv(key, default)
    # if value == default and hasattr(st, 'secrets') and key in st.secrets:
    #     value = st.secrets[key]
    # return value

OLLAMA_HOST = get_config("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = get_config("OLLAMA_MODEL", "llama3.2")
OPENAI_API_KEY = get_config("OPENAI_API_KEY", "")

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 'home'

def generate_wish_with_ai(recipient, sender, personality, tone, language, wish_type="voice"):
    """Generate wish text using Ollama or OpenAI"""
    if wish_type == "voice":
        prompt = f"""You are a warm, heartfelt voice message creator for Diwali celebrations.
Create a SPOKEN voice message that sounds natural when read aloud.
Requirements:
- Address {recipient} by name warmly
- Use conversational language
- Reflect their {personality.lower()} personality
- Use a {tone.lower()} tone
- Include vivid Diwali imagery (diyas, lights, joy)
- End with "Happy Diwali!"
- Language: {language}
- Length: 50-70 words maximum
Sender: {sender}
Recipient: {recipient}"""
    else:  # card
        prompt = f"""Write a short, heart-touching Diwali wish for {recipient}.
Make it {personality} in tone and use {language} style.
Include friendly Diwali emojis like ✨🪔🌈
Make it sound natural, not robotic.
Keep it under 40 words.
Example Hinglish: "Iss Diwali, tension ko jala do aur khushiyon ki roshni badha do! ✨"
From: {sender}"""
    
    # Try Ollama first
    try:
        response = requests.post(f"{OLLAMA_HOST}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}, timeout=30)
        if response.status_code == 200:
            return response.json()["response"].strip()
    except Exception as e:
        st.warning(f"Ollama unavailable ({str(e)[:50]}...), trying OpenAI fallback...")
    
    # Try OpenAI if Ollama fails
    if OPENAI_API_KEY:
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            st.warning(f"OpenAI also failed: {str(e)[:50]}...")
    
    # Final fallback
    if wish_type == "voice":
        return f"Hey {recipient}! It's {sender} here... wishing you a wonderful Diwali! May your life be filled with light, laughter, and endless joy! Happy Diwali! 🪔✨"
    else:
        return f"Dear {recipient},\nMay this Diwali bring you joy, prosperity, and endless happiness! ✨🪔\nWith love, {sender}"

# ==================== HOME PAGE ====================
def show_home():
    st.markdown("<h1 style='text-align: center; color: #FF6B35;'>🪔 AI Diwali Wish Maker ✨</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #666;'>Choose Your Magic</h3>", unsafe_allow_html=True)
    st.write("")
    st.write("")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Voice Wish Card
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0;'>🎙️ Voice Wish Generator</h2>
            <p style='color: #f0f0f0; margin: 10px 0;'>Create personalized AI voice greetings</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎙️ Create Voice Wish", use_container_width=True, type="primary"):
            st.session_state.page = 'voice'
            st.rerun()
        
        st.write("")
        st.write("")
        
        # Card Generator Card
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 20px;'>
            <h2 style='color: white; margin: 0;'>🎨 Card Generator</h2>
            <p style='color: #f0f0f0; margin: 10px 0;'>Design beautiful AI-powered greeting cards</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎨 Create Greeting Card", use_container_width=True, type="secondary"):
            st.session_state.page = 'card'
            st.rerun()

# ==================== VOICE WISH PAGE ====================
def show_voice_wish():
    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("← Back"):
            st.session_state.page = 'home'
            st.rerun()
    with col_title:
        st.title("🎙️ AI Diwali Voice Wish")
    
    st.markdown("*Create personalized voice greetings with AI magic!*")
    
    col1, col2 = st.columns(2)
    with col1:
        sender = st.text_input("Your Name", placeholder="Priya")
    with col2:
        recipient = st.text_input("Recipient's Name", placeholder="Rahul")
    
    personality = st.selectbox("Recipient's Personality", 
        ["Cheerful", "Caring", "Ambitious", "Funny", "Traditional"])
    tone = st.radio("Tone of Message", ["Warm", "Poetic", "Funny", "Formal"], horizontal=True)
    
    col_lang, col_music = st.columns(2)
    with col_lang:
        language = st.selectbox("Language", ["English", "Hindi", "Hinglish"])
    with col_music:
        add_music = st.checkbox("🎵 Background Music")
    
    st.info("🎙️ Voice enhanced with faster, energetic pacing and emotional delivery!")
    
    music_file_path = os.path.join(os.getcwd(), "background_music.mp3")
    if add_music and not os.path.exists(music_file_path):
        st.warning("⚠️ No background_music.mp3 file found.")
    
    if st.button("✨ Generate Wish", type="primary", use_container_width=True):
        if not sender or not recipient:
            st.error("Please enter both sender and recipient names!")
        else:
            with st.spinner("🪔 Lighting the diya... crafting your wish ✨"):
                wish_text = generate_wish_with_ai(recipient, sender, personality, tone, language, "voice")
                wish_text = re.sub(r'^(\w+),', r'\1...', wish_text)
                wish_text = wish_text.replace('!', '! ').replace('.', '... ').replace(',', ', ')
                wish_text = re.sub(r'\s+', ' ', wish_text).strip()
                st.session_state.wish_text = wish_text
                st.session_state.generated = True
                st.session_state.add_music = add_music
                st.session_state.language = language
    
    if st.session_state.get("generated"):
        st.markdown("### 📝 Your Wish")
        edited_text = st.text_area("Edit if needed:", value=st.session_state.wish_text, height=120)
        
        if st.button("🎙️ Generate Voice", type="primary", use_container_width=True):
            with st.spinner("Converting to voice... 🎤"):
                temp_dir = tempfile.gettempdir()
                voice_file = os.path.join(temp_dir, f"wish_{int(time.time())}.mp3")
                
                # Generate TTS
                lang_map = {'English': 'en', 'Hindi': 'hi', 'Hinglish': 'en'}
                tts = gTTS(text=edited_text, lang=lang_map.get(st.session_state.get('language', 'English'), 'en'), slow=False, tld='co.in')
                temp_path = voice_file.replace('.mp3', '_temp.mp3')
                tts.save(temp_path)
                
                try:
                    audio = AudioSegment.from_file(temp_path)
                    audio = audio._spawn(audio.raw_data, overrides={"frame_rate": int(audio.frame_rate * 1.15)}).set_frame_rate(audio.frame_rate)
                    audio = audio.normalize()
                    audio.export(voice_file, format="mp3", bitrate="192k")
                    os.remove(temp_path)
                except:
                    if os.path.exists(temp_path):
                        os.rename(temp_path, voice_file)
                
                final_audio = voice_file
                if st.session_state.get('add_music', False) and os.path.exists(music_file_path):
                    with st.spinner("🎵 Adding background music..."):
                        mixed_file = os.path.join(temp_dir, f"mixed_{int(time.time())}.mp3")
                        voice = AudioSegment.from_file(voice_file)
                        music = AudioSegment.from_file(music_file_path) - 15
                        if len(music) < len(voice):
                            music = music * (len(voice) // len(music) + 1)
                        mixed = voice.overlay(music[:len(voice)])
                        mixed.export(mixed_file, format="mp3")
                        final_audio = mixed_file
                        st.info("✨ Background music added!")
                
                st.session_state.audio_file = final_audio
                st.session_state.voice_generated = True
    
    if st.session_state.get("voice_generated"):
        st.success("✅ Your wish is ready!")
        with open(st.session_state.audio_file, "rb") as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format="audio/mp3")
        st.download_button(label="⬇️ Download MP3", data=audio_bytes,
            file_name=f"diwali_wish_{int(time.time())}.mp3", mime="audio/mp3", use_container_width=True)

# ==================== CARD GENERATOR PAGE ====================
def create_diwali_card(text, theme, recipient):
    """Generate a stunning Diwali card with beautiful effects"""
    import math
    import random
    
    # Card dimensions
    width, height = 800, 600
    
    # Enhanced theme colors with glow colors
    themes = {
        "Traditional": {
            "bg": [(255, 140, 0), (220, 90, 20), (139, 0, 0)],
            "text": (255, 255, 255),
            "accent": (255, 215, 0),
            "glow": (255, 200, 100),
            "stars": (255, 255, 150)
        },
        "Modern": {
            "bg": [(147, 51, 234), (109, 40, 217), (67, 20, 120)],
            "text": (255, 255, 255),
            "accent": (236, 72, 153),
            "glow": (192, 132, 252),
            "stars": (253, 224, 71)
        },
        "Minimal": {
            "bg": [(250, 250, 250), (220, 220, 220), (180, 180, 180)],
            "text": (40, 40, 40),
            "accent": (255, 140, 0),
            "glow": (255, 180, 100),
            "stars": (255, 200, 120)
        }
    }
    
    theme_colors = themes.get(theme, themes["Traditional"])
    
    # Create radial gradient background
    img = Image.new('RGB', (width, height), color=theme_colors["bg"][0])
    pixels = img.load()
    
    # Radial gradient from center
    center_x, center_y = width // 2, height // 2
    max_dist = math.sqrt(center_x**2 + center_y**2)
    
    for y in range(height):
        for x in range(width):
            dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
            ratio = dist / max_dist
            ratio = min(1.0, ratio)
            
            r = int(theme_colors["bg"][0][0] * (1 - ratio) + theme_colors["bg"][2][0] * ratio)
            g = int(theme_colors["bg"][0][1] * (1 - ratio) + theme_colors["bg"][2][1] * ratio)
            b = int(theme_colors["bg"][0][2] * (1 - ratio) + theme_colors["bg"][2][2] * ratio)
            pixels[x, y] = (r, g, b)
    
    draw = ImageDraw.Draw(img)
    
    # Add decorative sparkles/stars
    random.seed(42)  # Consistent pattern
    for _ in range(40):
        x = random.randint(20, width - 20)
        y = random.randint(20, height - 20)
        size = random.randint(2, 5)
        brightness = random.randint(100, 255)
        star_color = tuple(min(255, c + brightness - 150) for c in theme_colors["stars"])
        
        # Draw star shape
        draw.ellipse([x-size, y-size, x+size, y+size], fill=star_color)
        # Cross lines for twinkle effect
        draw.line([(x-size-2, y), (x+size+2, y)], fill=star_color, width=1)
        draw.line([(x, y-size-2), (x, y+size+2)], fill=star_color, width=1)
    
    # Draw enhanced diyas with glow effect
    diya_positions = [(120, 520), (680, 520), (120, 80), (680, 80)]
    for pos in diya_positions:
        # Outer glow layers
        for glow_r in range(30, 10, -3):
            alpha = int(150 - (glow_r - 10) * 5)
            glow_color = tuple(int(c * alpha / 255) for c in theme_colors["glow"])
            draw.ellipse([pos[0]-glow_r, pos[1]-glow_r, pos[0]+glow_r, pos[1]+glow_r], 
                        fill=glow_color)
        
        # Diya base (bowl)
        draw.ellipse([pos[0]-18, pos[1]-15, pos[0]+18, pos[1]+15], fill=theme_colors["accent"])
        # Inner bowl shadow
        draw.ellipse([pos[0]-14, pos[1]-11, pos[0]+14, pos[1]+11], fill=(180, 140, 0))
        
        # Flame
        flame_x, flame_y = pos[0], pos[1] - 20
        # Outer flame (orange)
        draw.ellipse([flame_x-8, flame_y-12, flame_x+8, flame_y+2], fill=(255, 140, 0))
        # Inner flame (yellow)
        draw.ellipse([flame_x-5, flame_y-8, flame_x+5, flame_y], fill=(255, 255, 100))
        # Bright core
        draw.ellipse([flame_x-2, flame_y-4, flame_x+2, flame_y], fill=(255, 255, 200))
    
    # Decorative corner patterns
    def draw_corner_pattern(x, y, flip_x=1, flip_y=1):
        for i in range(3):
            offset = i * 15
            x1 = x + offset * flip_x
            y1 = y + offset * flip_y
            x2 = x + (offset + 30) * flip_x
            y2 = y + (offset + 30) * flip_y
            
            # Ensure coordinates are in correct order (min, min, max, max)
            bbox = [min(x1, x2), min(y1, y2), max(x1, x2), max(y1, y2)]
            draw.arc(bbox, 0, 90, fill=theme_colors["accent"], width=2)
    
    # Draw patterns in corners
    draw_corner_pattern(15, 15, 1, 1)
    draw_corner_pattern(width - 45, 15, -1, 1)
    draw_corner_pattern(15, height - 45, 1, -1)
    draw_corner_pattern(width - 45, height - 45, -1, -1)
    
    # Elegant border with double line
    border_width = 8
    draw.rectangle([border_width, border_width, width-border_width, height-border_width], 
                   outline=theme_colors["accent"], width=border_width)
    draw.rectangle([border_width+15, border_width+15, width-border_width-15, height-border_width-15], 
                   outline=theme_colors["glow"], width=2)
    
    # Add text with shadows
    try:
        # Try to use a nice font (fallback to default if not available)
        title_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 56)
        text_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 26)
        name_font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial Bold.ttf", 36)
    except:
        title_font = ImageFont.load_default()
        text_font = ImageFont.load_default()
        name_font = ImageFont.load_default()
    
    # Helper function to draw text with shadow
    def draw_text_with_shadow(pos, text, font, fill_color, shadow_color=(0, 0, 0)):
        x, y = pos
        # Draw shadow (multiple layers for softer effect)
        for offset in range(3, 0, -1):
            shadow_alpha = int(100 - offset * 20)
            draw.text((x + offset, y + offset), text, fill=shadow_color, font=font)
        # Draw main text
        draw.text((x, y), text, fill=fill_color, font=font)
    
    # Title with glow effect
    title = "✨ Happy Diwali ✨"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) / 2
    # Draw glow
    for i in range(5, 0, -1):
        glow_alpha = int(150 - i * 25)
        glow_col = tuple(min(255, int(c * glow_alpha / 255)) for c in theme_colors["glow"])
        draw.text((title_x + i, 48 + i), title, fill=glow_col, font=title_font)
    draw.text((title_x, 48), title, fill=theme_colors["accent"], font=title_font)
    
    # Recipient name with shadow
    name_text = f"Dear {recipient},"
    name_bbox = draw.textbbox((0, 0), name_text, font=name_font)
    name_width = name_bbox[2] - name_bbox[0]
    draw_text_with_shadow(((width - name_width) / 2, 140), name_text, name_font, theme_colors["text"])
    
    # Main message (word wrap with shadows)
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=text_font)
        if bbox[2] - bbox[0] < width - 140:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    
    y_text = 210
    for line in lines[:5]:  # Max 5 lines
        bbox = draw.textbbox((0, 0), line, font=text_font)
        line_width = bbox[2] - bbox[0]
        line_x = (width - line_width) / 2
        draw_text_with_shadow((line_x, y_text), line, text_font, theme_colors["text"])
        y_text += 44
    
    # Apply subtle blur for professional look
    img = img.filter(ImageFilter.SMOOTH_MORE)
    
    # Add a semi-transparent overlay in the center for better text readability
    overlay = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([100, 120, width-100, y_text + 20], 
                          fill=(0, 0, 0, 30))  # Semi-transparent black
    img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')
    
    return img

def show_card_generator():
    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("← Back"):
            st.session_state.page = 'home'
            st.rerun()
    with col_title:
        st.title("🎨 AI Diwali Card Generator")
    
    st.markdown("*Design beautiful AI-powered greeting cards!*")
    
    col1, col2 = st.columns(2)
    with col1:
        sender = st.text_input("Your Name", placeholder="Priya", key="card_sender")
    with col2:
        recipient = st.text_input("Recipient's Name", placeholder="Rahul", key="card_recipient")
    
    col3, col4 = st.columns(2)
    with col3:
        personality = st.selectbox("Personality", ["Cheerful", "Calm", "Romantic", "Funny", "Traditional"], key="card_personality")
    with col4:
        language = st.selectbox("Language Style", ["English", "Hindi", "Hinglish"], key="card_language")
    
    theme = st.selectbox("Visual Theme", ["Traditional", "Modern", "Minimal"])
    
    st.info("🎨 Your card will feature AI-generated text on a beautiful Diwali-themed background!")
    
    if st.button("✨ Generate My Diwali Card", type="primary", use_container_width=True):
        if not sender or not recipient:
            st.error("Please enter both sender and recipient names!")
        else:
            with st.spinner("🪔 Creating your magical card... ✨"):
                # Generate wish text
                wish_text = generate_wish_with_ai(recipient, sender, personality, "Warm", language, "card")
                st.session_state.card_text = wish_text
                st.session_state.card_theme = theme
                st.session_state.card_recipient_name = recipient  # Use different key name
                st.session_state.card_generated = True
    
    if st.session_state.get("card_generated"):
        st.markdown("### 📝 Your Card Message")
        edited_text = st.text_area("Edit your message:", value=st.session_state.card_text, height=100, key="card_text_edit")
        
        if st.button("🎨 Generate Card Image", type="primary", use_container_width=True):
            with st.spinner("Creating your beautiful card... 🎨"):
                card_img = create_diwali_card(edited_text, st.session_state.card_theme, st.session_state.card_recipient_name)
                st.session_state.card_image = card_img
                st.session_state.final_card_ready = True
    
    if st.session_state.get("final_card_ready"):
        st.success("✅ Your card is ready!")
        st.image(st.session_state.card_image, use_container_width=True)
        
        # Convert PIL image to bytes for download
        buf = io.BytesIO()
        st.session_state.card_image.save(buf, format='PNG')
        byte_im = buf.getvalue()
        
        st.download_button(
            label="⬇️ Download Card (PNG)",
            data=byte_im,
            file_name=f"diwali_card_{int(time.time())}.png",
            mime="image/png",
            use_container_width=True
        )

# ==================== MAIN ROUTER ====================
def main():
    page = st.session_state.page
    
    if page == 'home':
        show_home()
    elif page == 'voice':
        show_voice_wish()
    elif page == 'card':
        show_card_generator()
    
    # Footer
    st.markdown("---")
    st.markdown("<p style='text-align: center; color: #888;'>Made with ❤️ for Diwali 2025</p>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()
