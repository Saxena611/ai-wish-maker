import streamlit as st
import streamlit.components.v1 as components
import os, time, requests, re, json, sys, random
from urllib.parse import quote

# Debug logging function that works with systemd
def debug_log(message):
    """Print to stderr so it appears in journalctl"""
    print(f"[DEBUG] {message}", file=sys.stderr, flush=True)

# Promotional taglines for wishkarle.online
PROMO_TAGLINES = [
    "🪔 Dil se likha, AI ne roshan kar diya ✨",
    "🎆 Mere emotions, AI ka expression 💫",
    "✨ Khayaal mera, andaaz AI ka 😄",
    "💫 Thoda pyaar mera, thoda magic AI ka 🪔",
    "🌟 Main socha, AI ne likh diya 😉",
    "🎇 Mera jazbaat, AI ka likha hua andaaz ✨",
    "🪔 Dil se socha, AI ne diya roop 💛",
    "🌈 Pyar mera, presentation AI ka 🎁",
    "💥 Emotion mera, expression AI ka ✨",
    "🎊 Feeling human wali, likhawat AI wali 😄",
    "🪔 Soch meri, likhavat AI ki 💫",
    "🌸 Dil ke jazbaat, AI ke alfaaz 🪔",
    "✨ Mujhse likha gaya, AI se nikha gaya 🎇",
    "💫 Mere shabd, AI ka touch ✨",
    "🎆 Mann se bana, AI se sajaa diya 🪔"
]

st.set_page_config(
    page_title="AI Diwali Wish Maker", 
    page_icon="🪔", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Google Analytics Integration
def inject_ga():
    """Inject Google Analytics tracking code"""
    ga_code = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-0QSZXW3BKD"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-0QSZXW3BKD');
      
      // Custom event tracking function
      window.trackWishGeneration = function(relationship, language) {
        gtag('event', 'generate_wish', {
          'event_category': 'Wish',
          'event_label': relationship,
          'language': language
        });
      };
    </script>
    """
    components.html(ga_code, height=0)

# Inject GA on page load
inject_ga()

# Configuration - Load from environment variables
def get_config(key, default):
    """Get config from env var or Streamlit secrets"""
    return os.getenv(key, default)

OLLAMA_HOST = get_config("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = get_config("OLLAMA_MODEL", "llama3.2")
OPENAI_API_KEY = get_config("OPENAI_API_KEY", "")

# Initialize session state
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'wish_generated' not in st.session_state:
    st.session_state.wish_generated = False
if 'wish_text' not in st.session_state:
    st.session_state.wish_text = ""

# Custom CSS for minimalist design
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=5, user-scalable=yes">

<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', -apple-system, sans-serif;
        -webkit-tap-highlight-color: transparent;
    }
    
    html {
        -webkit-text-size-adjust: 100%;
        touch-action: manipulation;
    }
    
    .main {
        background: linear-gradient(135deg, #FFF5E6 0%, #FFE4CC 50%, #FFD4A3 100%);
        position: relative;
        overflow-x: hidden;
    }
    
    /* Festive decorations */
    .diya-decoration {
        position: fixed;
        font-size: 40px;
        animation: float 3s ease-in-out infinite;
        z-index: 0;
        opacity: 0.6;
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-20px); }
    }
    
    @keyframes sparkle {
        0%, 100% { opacity: 0.4; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.3); }
    }
    
    @keyframes twinkle {
        0%, 100% { opacity: 0.3; }
        50% { opacity: 1; }
    }
    
    .firecracker {
        position: fixed;
        font-size: 30px;
        animation: sparkle 2s ease-in-out infinite;
        z-index: 0;
    }
    
    .sparkle-dot {
        position: fixed;
        width: 8px;
        height: 8px;
        background: radial-gradient(circle, #FFD700, #FFA500);
        border-radius: 50%;
        animation: twinkle 1.5s ease-in-out infinite;
        z-index: 0;
    }
    
    /* Compact header */
    .compact-header {
        text-align: center;
        margin: 20px 0 30px 0;
        position: relative;
        z-index: 1;
        background: rgba(255, 255, 255, 0.9);
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(255, 107, 53, 0.2);
    }
    
    .compact-title {
        font-size: 36px;
        font-weight: 700;
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 50%, #FF6B35 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(255, 107, 53, 0.1);
    }
    
    .compact-subtitle {
        font-size: 14px;
        color: #FF8C42;
        margin-top: 8px;
        font-weight: 600;
    }
    
    /* Colorful progress bar */
    .progress-bar-container {
        width: 100%;
        height: 5px;
        background: linear-gradient(90deg, #FFE4CC, #FFD4A3);
        border-radius: 10px;
        margin: 20px 0;
        overflow: hidden;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        position: relative;
        z-index: 1;
    }
    
    .progress-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #FF6B35, #F7931E, #FFD700, #FF6B35);
        background-size: 200% 100%;
        transition: width 0.4s ease;
        border-radius: 10px;
        animation: shimmer 2s linear infinite;
    }
    
    @keyframes shimmer {
        0% { background-position: 0% 0%; }
        100% { background-position: 200% 0%; }
    }
    
    /* Clean input container */
    .input-container {
        padding: 10px 0;
        margin: 15px 0;
        animation: slideIn 0.3s ease-out;
        position: relative;
        z-index: 1;
    }
    
    /* Reduce spacing before generate button */
    #step-6 {
        margin-top: 10px !important;
    }
    
    #step-6 + div {
        margin-top: 0 !important;
    }
    
    /* Reduce Streamlit's default spacing after language radio */
    .stRadio {
        margin-bottom: 5px !important;
    }
    
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Compact labels */
    .stTextInput label, .stSelectbox label, .stMultiselect label, .stRadio label {
        font-size: 13px !important;
        font-weight: 600 !important;
        color: #333 !important;
        margin-bottom: 8px !important;
    }
    
    /* Clean inputs */
    .stTextInput input, .stSelectbox select {
        border: 1px solid #E0E0E0 !important;
        border-radius: 8px !important;
        padding: 10px 12px !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput input:focus, .stSelectbox select:focus {
        border-color: #FF6B35 !important;
        box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.1) !important;
    }
    
    /* Colorful buttons */
    .stButton>button {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 50%, #FF8C42 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 14px;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4), 0 0 20px rgba(255, 215, 0, 0.2);
        position: relative;
        z-index: 1;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(255, 107, 53, 0.5), 0 0 30px rgba(255, 215, 0, 0.3);
        background: linear-gradient(135deg, #FF8C42 0%, #F7931E 50%, #FF6B35 100%);
    }
    
    /* Compact multiselect */
    .stMultiselect {
        margin-bottom: 0 !important;
    }
    
    /* Vibrant wish card */
    .wish-card-modern {
        background: linear-gradient(135deg, #FF6B35 0%, #F7931E 50%, #FFD700 100%);
        color: white;
        padding: 35px;
        border-radius: 20px;
        box-shadow: 0 15px 40px rgba(255, 107, 53, 0.4), 0 0 50px rgba(255, 215, 0, 0.3);
        margin: 20px 0;
        line-height: 1.8;
        font-size: 16px;
        animation: slideIn 0.4s ease-out, glow 2s ease-in-out infinite;
        position: relative;
        z-index: 1;
        border: 3px solid rgba(255, 255, 255, 0.3);
        overflow: hidden;
        max-width: 100%;
        box-sizing: border-box;
    }
    
    .wish-card-modern > div {
        overflow-wrap: break-word !important;
        word-wrap: break-word !important;
        word-break: break-word !important;
        white-space: pre-line !important;
        overflow-x: hidden !important;
        overflow-y: auto !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }
    
    .wish-card-modern * {
        max-width: 100% !important;
        box-sizing: border-box !important;
    }
    
    @keyframes glow {
        0%, 100% { box-shadow: 0 15px 40px rgba(255, 107, 53, 0.4), 0 0 50px rgba(255, 215, 0, 0.3); }
        50% { box-shadow: 0 15px 40px rgba(255, 107, 53, 0.5), 0 0 70px rgba(255, 215, 0, 0.5); }
    }
    
    /* Colorful share section */
    .share-section {
        background: linear-gradient(135deg, #FFFFFF 0%, #FFF8F0 100%);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(255, 140, 0, 0.2);
        margin: 15px 0;
        border: 2px solid rgba(255, 215, 0, 0.3);
        position: relative;
        z-index: 1;
    }
    
    /* Hide alerts */
    .stAlert {
        display: none !important;
    }
    
    div[data-testid="stNotification"] {
        display: none !important;
    }
    
    /* Step indicator */
    .step-text {
        text-align: center;
        color: #999;
        font-size: 12px;
        font-weight: 500;
        margin: 10px 0;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Radio buttons horizontal */
    .stRadio > div {
        flex-direction: row !important;
        gap: 15px !important;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Mobile responsive styles */
    @media (max-width: 768px) {
        .compact-title {
            font-size: 28px !important;
        }
        
        .compact-subtitle {
            font-size: 12px !important;
        }
        
        .compact-header {
            padding: 15px !important;
            margin: 10px 0 20px 0 !important;
        }
        
        .input-container {
            padding: 15px !important;
            margin: 10px 0 !important;
        }
        
        .wish-card-modern {
            padding: 20px !important;
            font-size: 14px !important;
            margin: 15px 0 !important;
        }
        
        .share-section {
            padding: 15px !important;
        }
        
        /* Reduce decoration size on mobile */
        .diya-decoration {
            font-size: 30px !important;
        }
        
        .firecracker {
            font-size: 24px !important;
        }
        
        .sparkle-dot {
            width: 6px !important;
            height: 6px !important;
        }
        
        /* Adjust button sizes */
        .stButton>button {
            padding: 10px 20px !important;
            font-size: 13px !important;
        }
        
        /* Better input sizing */
        .stTextInput input, .stSelectbox select {
            font-size: 13px !important;
        }
        
        .stTextInput label, .stSelectbox label, .stMultiselect label, .stRadio label {
            font-size: 12px !important;
        }
        
        /* Progress bar */
        .progress-bar-container {
            height: 4px !important;
        }
        
        .step-text {
            font-size: 11px !important;
        }
    }
    
    @media (max-width: 480px) {
        .compact-title {
            font-size: 24px !important;
        }
        
        .compact-subtitle {
            font-size: 11px !important;
        }
        
        .input-container {
            padding: 12px !important;
        }
        
        .wish-card-modern {
            padding: 18px !important;
            font-size: 13px !important;
            line-height: 1.6 !important;
            overflow: hidden !important;
        }
        
        .wish-card-modern > div {
            overflow-wrap: break-word !important;
            word-wrap: break-word !important;
            word-break: break-word !important;
            white-space: pre-line !important;
            overflow-x: hidden !important;
            overflow-y: auto !important;
        }
        
        /* Hide some decorations on very small screens */
        .diya-decoration:nth-child(3),
        .diya-decoration:nth-child(4),
        .firecracker:nth-child(7),
        .firecracker:nth-child(8) {
            display: none;
        }
        
        .sparkle-dot {
            width: 5px !important;
            height: 5px !important;
        }
    }
    
    /* Landscape mobile */
    @media (max-width: 768px) and (orientation: landscape) {
        .compact-header {
            margin: 10px 0 15px 0 !important;
            padding: 12px !important;
        }
        
        .input-container {
            padding: 12px !important;
            margin: 8px 0 !important;
        }
    }
</style>

""", unsafe_allow_html=True)

def add_promo_tagline(wish_text):
    """Add a random promotional tagline to the wish"""
    tagline = random.choice(PROMO_TAGLINES)
    return f"{wish_text}\n\n{tagline}\n(wishkarle.online)"

def generate_wish_with_ai(sender_name, recipient_name, relationship, traits, life_thing, language):
    """Generate wish text using Ollama or OpenAI"""
    traits_str = ", ".join(traits) if traits else "wonderful"
    
    # Language-specific strict instructions (anti-hallucination)
    lang_instruction = {
        "English": "MUST write in ENGLISH only.",
        "Hindi": "MUST write in pure HINDI (हिंदी) Devanagari script. NOT Punjabi. NOT Urdu. Use: दिवाली, शुभकामनाएं, खुशियाँ, प्रकाश, जीवन.",
        "Hinglish": "MUST write in HINGLISH (Hindi+English mixed). Example: 'Aapko Diwali ki shubhkamnayein' NOT pure Hindi/English."
    }
    
    prompt = f"""Write a Diwali wish in {language}.

LANGUAGE RULE: {lang_instruction.get(language, lang_instruction['English'])}

GIVEN INFORMATION (USE ONLY THIS):
- From: {sender_name}
- To: {recipient_name}
- Relationship: {relationship}
- Their traits: {traits_str}
- Their passion: {life_thing}

STRICT RULES:
1. Use ONLY the information provided above
2. Write in {language} language only
3. Length: 2-4 sentences maximum
4. Include 6-8 Diwali emojis (🪔✨🎆💫🌟🎇)
5. Address {recipient_name} by name
6. Mention their {traits_str} traits
7. Reference their {life_thing} passion
8. End with wishes from {sender_name}

FORMAT: Short greeting + personal line + wish + signature

DO NOT invent facts. DO NOT add information not provided. Output ONLY the wish text."""
    
    # Try Ollama first
    ollama_error = None
    try:
        debug_log(f"Attempting Ollama connection to: {OLLAMA_HOST}")
        debug_log(f"Using model: {OLLAMA_MODEL}")
        response = requests.post(f"{OLLAMA_HOST}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False}, timeout=120)
        debug_log(f"Ollama response status: {response.status_code}")
        if response.status_code == 200:
            debug_log("✓ Ollama success!")
            wish = response.json()["response"].strip()
            return add_promo_tagline(wish)
        else:
            ollama_error = f"Status code: {response.status_code}, Response: {response.text[:200]}"
    except requests.exceptions.Timeout as e:
        ollama_error = f"Timeout error: {str(e)}"
    except requests.exceptions.ConnectionError as e:
        ollama_error = f"Connection error: {str(e)}"
    except Exception as e:
        ollama_error = f"Unexpected error: {type(e).__name__} - {str(e)}"
    
    if ollama_error:
        debug_log(f"✗ Ollama failed: {ollama_error}")
        st.warning(f"⚠️ Ollama unavailable, using fallback...")
    
    # Try OpenAI if Ollama fails
    if OPENAI_API_KEY:
        try:
            import openai
            openai.api_key = OPENAI_API_KEY
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            wish = response.choices[0].message.content.strip()
            return add_promo_tagline(wish)
        except Exception as e:
            pass  # Silently use fallback
    
    # Final fallback
    fallback_wish = f"""Dear {recipient_name} 🪔✨

This Diwali, may your life be filled with endless joy, prosperity, and beautiful moments! 🌟🎆 
Your {traits_str} spirit lights up every room, just like these diyas! 🕯️💫
May your passion for {life_thing} grow brighter than ever! 🌈🎉

Happy Diwali! 🪔✨
With love, {sender_name} ❤️"""
    return add_promo_tagline(fallback_wish)

def show_progress_bar(current_step, total_steps):
    """Show a minimal progress bar"""
    progress_percent = (current_step / total_steps) * 100
    st.markdown(f"""
    <div class="progress-bar-container">
        <div class="progress-bar-fill" style="width: {progress_percent}%"></div>
        </div>
    <div class="step-text">Step {current_step} of {total_steps}</div>
        """, unsafe_allow_html=True)
        
def main():
    # Festive decorations
    st.markdown("""
    <!-- Floating Diyas -->
    <div class="diya-decoration" style="top: 10%; left: 5%;">🪔</div>
    <div class="diya-decoration" style="top: 20%; right: 8%; animation-delay: 0.5s;">🪔</div>
    <div class="diya-decoration" style="top: 60%; left: 3%; animation-delay: 1s;">🪔</div>
    <div class="diya-decoration" style="top: 75%; right: 5%; animation-delay: 1.5s;">🪔</div>
    
    <!-- Firecrackers -->
    <div class="firecracker" style="top: 15%; left: 15%; animation-delay: 0.3s;">🎆</div>
    <div class="firecracker" style="top: 35%; right: 12%; animation-delay: 0.8s;">✨</div>
    <div class="firecracker" style="top: 50%; left: 10%; animation-delay: 1.2s;">🎇</div>
    <div class="firecracker" style="top: 70%; right: 15%; animation-delay: 1.6s;">🎆</div>
    
    <!-- Sparkle dots -->
    <div class="sparkle-dot" style="top: 25%; left: 20%; animation-delay: 0.2s;"></div>
    <div class="sparkle-dot" style="top: 45%; right: 18%; animation-delay: 0.6s;"></div>
    <div class="sparkle-dot" style="top: 65%; left: 12%; animation-delay: 1s;"></div>
    <div class="sparkle-dot" style="top: 80%; right: 20%; animation-delay: 1.4s;"></div>
    <div class="sparkle-dot" style="top: 30%; left: 25%; animation-delay: 0.4s;"></div>
    <div class="sparkle-dot" style="top: 55%; right: 22%; animation-delay: 0.9s;"></div>
    """, unsafe_allow_html=True)
    
    # Compact header
    st.markdown("""
    <div class="compact-header">
    <h1 class="compact-title">🪔✨ Diwali Wish Maker ✨🎆</h1>
    <p class="compact-subtitle">🎇 AI-powered personalized wishes in seconds 🎇</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Total steps
    total_steps = 6
    
    # Show progress
    if not st.session_state.wish_generated:
        show_progress_bar(st.session_state.current_step, total_steps)
    
    # Auto-advance logic: check if fields are filled
    def advance_step_0():
        if st.session_state.get('sender_name') and st.session_state.current_step == 0:
            st.session_state.current_step = 1
    
    def advance_step_1():
        if st.session_state.get('recipient_name') and st.session_state.current_step == 1:
            st.session_state.current_step = 2
    
    def advance_step_2():
        if st.session_state.current_step == 2:
            st.session_state.current_step = 3
    
    def advance_step_3():
        if st.session_state.get('traits') and st.session_state.current_step == 3:
            st.session_state.current_step = 4
    
    def advance_step_4():
        if st.session_state.get('life_thing') and st.session_state.current_step == 4:
            st.session_state.current_step = 5
    
    def advance_step_5():
        if st.session_state.current_step == 5:
            st.session_state.current_step = 6
    
    # Track step before rendering
    step_before = st.session_state.current_step
    
    # Step 1: Your Name
    if st.session_state.current_step >= 0 and not st.session_state.wish_generated:
        st.markdown('<div class="input-container" id="step-0">', unsafe_allow_html=True)
        sender_name = st.text_input(
            "🎁 Your Name",
            placeholder="Enter your name",
            key="sender_name",
            on_change=advance_step_0
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Scroll to this step if it's the current one
        if st.session_state.current_step == 0:
            components.html("""
                <script>
                    setTimeout(function() {
                        const element = window.parent.document.getElementById('step-0');
                        if (element) {
                            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }, 100);
                </script>
            """, height=0)
        
        # Check if step changed and rerun
        if st.session_state.current_step != step_before:
            st.rerun()
    
    # Step 2: Recipient Name
    if st.session_state.current_step >= 1 and not st.session_state.wish_generated:
        st.markdown('<div class="input-container" id="step-1">', unsafe_allow_html=True)
        recipient_name = st.text_input(
            "🪔 Recipient's Name",
            placeholder="Who will receive this wish?",
            key="recipient_name",
            on_change=advance_step_1
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Scroll to this step if it's the current one
        if st.session_state.current_step == 1:
            components.html("""
                <script>
                    setTimeout(function() {
                        const element = window.parent.document.getElementById('step-1');
                        if (element) {
                            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }, 100);
                </script>
            """, height=0)
        
        if st.session_state.current_step != step_before:
            st.rerun()
    
    # Step 3: Relationship
    if st.session_state.current_step >= 2 and not st.session_state.wish_generated:
        st.markdown('<div class="input-container" id="step-2">', unsafe_allow_html=True)
        relationship = st.selectbox(
            "❤️ Relationship",
            options=["Friend", "Family", "Colleague", "Lover", "Mentor"],
            key="relationship",
            on_change=advance_step_2
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Scroll to this step if it's the current one
        if st.session_state.current_step == 2:
            components.html("""
                <script>
                    setTimeout(function() {
                        const element = window.parent.document.getElementById('step-2');
                        if (element) {
                            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }, 100);
                </script>
            """, height=0)
            # Auto-advance if relationship has a value (including default)
            if st.session_state.get('relationship'):
                st.session_state.current_step = 3
                st.rerun()
        
        if st.session_state.current_step != step_before:
            st.rerun()
    
    # Step 4: Personality Traits
    if st.session_state.current_step >= 3 and not st.session_state.wish_generated:
        st.markdown('<div class="input-container" id="step-3">', unsafe_allow_html=True)
        traits = st.multiselect(
            "✨ Their Personality (choose 1-3)",
            options=["Creative", "Funny", "Caring", "Ambitious", "Calm", "Energetic", 
                    "Thoughtful", "Kind", "Smart", "Cheerful"],
            key="traits",
            max_selections=3,
            on_change=advance_step_3
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Scroll to this step if it's the current one
        if st.session_state.current_step == 3:
            components.html("""
                <script>
                    setTimeout(function() {
                        const element = window.parent.document.getElementById('step-3');
                        if (element) {
                            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }, 100);
                </script>
            """, height=0)
            # Auto-advance if traits are selected
            if st.session_state.get('traits'):
                st.session_state.current_step = 4
                st.rerun()
        
        if st.session_state.current_step != step_before:
            st.rerun()
    
    # Step 5: Life Thing
    if st.session_state.current_step >= 4 and not st.session_state.wish_generated:
        st.markdown('<div class="input-container" id="step-4">', unsafe_allow_html=True)
        life_thing = st.text_input(
            "🎨 Their Passion",
            placeholder="e.g., Music, Travel, Cooking",
            key="life_thing",
            on_change=advance_step_4
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Scroll to this step if it's the current one
        if st.session_state.current_step == 4:
            components.html("""
                <script>
                    setTimeout(function() {
                        const element = window.parent.document.getElementById('step-4');
                        if (element) {
                            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }, 100);
                </script>
            """, height=0)
            # Auto-advance if life_thing is filled
            if st.session_state.get('life_thing'):
                st.session_state.current_step = 5
                st.rerun()
        
        if st.session_state.current_step != step_before:
            st.rerun()
    
    # Step 6: Language
    if st.session_state.current_step >= 5 and not st.session_state.wish_generated:
        st.markdown('<div class="input-container" id="step-5">', unsafe_allow_html=True)
        language = st.radio(
            "🌍 Language",
            options=["English", "Hindi", "Hinglish"],
            horizontal=True,
            key="language",
            on_change=advance_step_5
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Scroll to this step if it's the current one
        if st.session_state.current_step == 5:
            components.html("""
                <script>
                    setTimeout(function() {
                        const element = window.parent.document.getElementById('step-5');
                        if (element) {
                            element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                        }
                    }, 100);
                </script>
            """, height=0)
        
        if st.session_state.current_step != step_before:
            st.rerun()
    
    # Always show Generate button at step 5 if language is selected (including default)
    if st.session_state.current_step >= 5 and not st.session_state.wish_generated and st.session_state.get('language'):
        st.markdown('<div id="step-6">', unsafe_allow_html=True)
        
        # Scroll to generate button
        components.html("""
            <script>
                setTimeout(function() {
                    const element = window.parent.document.getElementById('step-6');
                    if (element) {
                        element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }, 300);
            </script>
        """, height=0)
        
        if st.button("✨ Generate Wish", type="primary", use_container_width=True):
            sender = st.session_state.get('sender_name')
            recipient = st.session_state.get('recipient_name')
            rel = st.session_state.get('relationship')
            traits_list = st.session_state.get('traits', [])
            life = st.session_state.get('life_thing')
            lang = st.session_state.get('language', 'English')
            
            if all([sender, recipient, traits_list, life]):
                with st.spinner("🪔 Crafting your wish..."):
                    wish_text = generate_wish_with_ai(sender, recipient, rel, traits_list, life, lang)
                    st.session_state.wish_text = wish_text
                    st.session_state.wish_generated = True
                    
                    # Track wish generation in Google Analytics
                    components.html(f"""
                    <script>
                        if (typeof window.parent.trackWishGeneration === 'function') {{
                            window.parent.trackWishGeneration('{rel}', '{lang}');
                        }}
                    </script>
                    """, height=0)
                    
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display Generated Wish
    if st.session_state.wish_generated and st.session_state.wish_text:
        st.markdown("---")
        
        # Wish card
        st.markdown(f"""
        <div class="wish-card-modern">
            <div>{st.session_state.wish_text}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Balloons effect
        st.balloons()
        
        # Share buttons below the wish card
        st.markdown("")
        col1, col2, col3 = st.columns(3)
            
        with col1:
            # Create a copy button with JavaScript using components
            copy_text = json.dumps(st.session_state.wish_text)
            components.html(f"""
                <div style="width: 100%;">
                    <button id="copy-btn" onclick="copyToClipboard()" 
                            style="width: 100%; padding: 10px; font-size: 14px; 
                            border-radius: 8px; border: none; cursor: pointer; 
                            background: linear-gradient(135deg, #FF6B35 0%, #F7931E 50%, #FF8C42 100%);
                            color: white; font-weight: 600;
                            transition: all 0.2s ease; 
                            box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4), 0 0 20px rgba(255, 215, 0, 0.2);
                            -webkit-tap-highlight-color: transparent; touch-action: manipulation;">
                        <span id="copy-text">📋 Copy</span>
                    </button>
                </div>
                <script>
                    const textToCopy = {copy_text};
                    
                    function copyToClipboard() {{
                        // Try modern clipboard API first
                        if (navigator.clipboard && window.isSecureContext) {{
                            navigator.clipboard.writeText(textToCopy).then(function() {{
                                showSuccess();
                            }}).catch(function(err) {{
                                fallbackCopy();
                            }});
                        }} else {{
                            fallbackCopy();
                        }}
                    }}
                    
                    function fallbackCopy() {{
                        const textArea = document.createElement('textarea');
                        textArea.value = textToCopy;
                        textArea.style.position = 'fixed';
                        textArea.style.left = '-999999px';
                        textArea.style.top = '-999999px';
                        document.body.appendChild(textArea);
                        textArea.focus();
                        textArea.select();
                        try {{
                            document.execCommand('copy');
                            showSuccess();
                        }} catch (err) {{
                            document.getElementById('copy-text').textContent = '❌ Failed';
                        }}
                        document.body.removeChild(textArea);
                    }}
                    
                    function showSuccess() {{
                        document.getElementById('copy-text').textContent = '✓ Copied!';
                        setTimeout(function() {{
                            document.getElementById('copy-text').textContent = '📋 Copy';
                        }}, 2000);
                    }}
                    
                    // Add hover effects
                    const btn = document.getElementById('copy-btn');
                    btn.addEventListener('mouseover', function() {{
                        this.style.transform = 'translateY(-2px)';
                        this.style.boxShadow = '0 6px 16px rgba(255, 107, 53, 0.5), 0 0 30px rgba(255, 215, 0, 0.3)';
                    }});
                    btn.addEventListener('mouseout', function() {{
                        this.style.transform = 'translateY(0)';
                        this.style.boxShadow = '0 4px 12px rgba(255, 107, 53, 0.4), 0 0 20px rgba(255, 215, 0, 0.2)';
                    }});
                </script>
            """, height=50)
            
        with col2:
            whatsapp_text = quote(st.session_state.wish_text)
            whatsapp_url = f"https://wa.me/?text={whatsapp_text}"
            st.markdown(f"""
                <a href="{whatsapp_url}" target="_blank" rel="noopener noreferrer" 
                   style="text-decoration: none; display: block;">
                    <button style="width: 100%; padding: 10px; font-size: 14px; 
                            border-radius: 8px; border: none; cursor: pointer; 
                            background: #25D366; color: white; font-weight: 600;
                            transition: all 0.2s ease; box-shadow: 0 2px 8px rgba(37, 211, 102, 0.3);
                            -webkit-tap-highlight-color: transparent; touch-action: manipulation;"
                            onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(37, 211, 102, 0.4)';"
                            onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 2px 8px rgba(37, 211, 102, 0.3)';">
                        📱 WhatsApp
                    </button>
                </a>
            """, unsafe_allow_html=True)
        
        with col3:
            if st.button("🔄 Create Another", type="secondary", use_container_width=True):
                # Reset all
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.session_state.current_step = 0
                st.session_state.wish_generated = False
                st.rerun()
    
    # Beautiful footer with LinkedIn
    st.markdown("")
    st.markdown("""
    <div style="text-align: center; margin-top: 50px; padding: 20px;">
        <p style="color: #999; font-size: 12px; margin-bottom: 8px;">Made with ❤️ for Diwali 2025 🪔 • by Animesh</p>
        <a href="https://www.linkedin.com/in/animeshsaxena6111/" target="_blank" 
           style="display: inline-flex; align-items: center; gap: 8px; 
                  text-decoration: none; color: #0077B5; font-size: 13px;
                  padding: 8px 16px; border-radius: 20px; 
                  background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
                  border: 1px solid #0077B5; transition: all 0.3s ease;
                  font-weight: 500;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="#0077B5">
                <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
            </svg>
            Connect on LinkedIn
        </a>
        <p style="color: #BBB; font-size: 10px; margin-top: 15px;">✨ Powered by AI • Built with Streamlit & Ollama</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()