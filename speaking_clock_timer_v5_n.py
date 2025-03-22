#speaking clock

#import libraries
import streamlit as st
import datetime
### import pyttsx3
import time
from gtts import gTTS
import os
from playsound import playsound
import tempfile
import base64

st.set_page_config(page_title="Speaking Clock & Safety Timer", layout="wide")

# Function to autoplay audio when timer reaches 2 hours
def get_audio_html(audio_path):
    try:
        audio_file = open(audio_path, "rb").read()
        audio_bytes = base64.b64encode(audio_file).decode()
        return f"""
            <audio autoplay>
                <source src="data:audio/mp3;base64,{audio_bytes}" type="audio/mp3">
                Your browser does not support the audio element.
            </audio>
        """
    except FileNotFoundError:
        st.error(f"Audio file not found: {audio_path}")
        return ""

def autoplay_audio(file_path: str):
    with open(file_path, "rb") as f:
        data = f.read()
        b64 = base64.b64encode(data).decode()
        md = f"""
            <audio controls autoplay="true">
            <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
            </audio>
            """
        st.markdown(
            md,
            unsafe_allow_html=True,
        )


# Initialize session state variables
if 'running' not in st.session_state:
    st.session_state.running = True
if 'stopwatch_running' not in st.session_state:
    st.session_state.stopwatch_running = False
if 'stopwatch_start' not in st.session_state:
    st.session_state.stopwatch_start = None
if 'alert_shown' not in st.session_state:
    st.session_state.alert_shown = False
if 'last_announcement_time' not in st.session_state:
    st.session_state.last_announcement_time = None

def on_text_change():
    st.session_state.alert_shown = False

#variables
time_str=""
#alert_string = "Yo people! It's time to have a pause, pee and check pressure areas."
#tts = gTTS(text=alert_string, lang='en')
#tts.save("alert_string_audio.mp3")

# create sting of current time for audio 
current_time = datetime.datetime.now()
hour = current_time.hour
period = "AM" if hour < 12 else "PM"
minute = current_time.minute
time_str = f"The time, sponsored by xxx , is {hour} : {minute} {period}."

st.title("Speaking Clock & Safety Timer")

# Create two columns for current time and stopwatch
col1, col2 = st.columns(2)

#column ONE for current time speaking clock
with col1:
    st.subheader("Current Time")
# Create a placeholder for the time display
    time_placeholder = st.empty()

    if st.button("Announce the time"):
#modify button states
                st.session_state.button_clicked = True
                st.session_state.audio_played = False
#converting time string into audio
# Convert text to speech and save to file
                text = time_str # + interest_str
                tts = gTTS(text=text, lang='en')
                tts.save("time_str.mp3")
# Display audio only if button was clicked and audio hasn't played yet
                if st.session_state.button_clicked and not st.session_state.audio_played:
                    st.audio("time_str.mp3", format="audio/mpeg", loop=False, autoplay=True)
                    st.session_state.audio_played = True
    # Force a rerun to hide the audio element
    
#radio button to choose timing of announcements
    speaking_freq = st.radio("When do you want the spoken time:", ["only on demand","9am, 12pm, 4pm", "every 2 hours","every hour"])

#tick box for humourous annoucnements
## funny_mode = st.checkbox("Light heart mode ON")

# Function to check if we already announced this time
def need_to_announce(hour, minute):
    now = datetime.datetime.now()
    current_time = (now.hour, now.minute)
    
    # If we haven't announced yet, or if we're in a new minute
    if st.session_state.last_announcement_time is None or current_time != st.session_state.last_announcement_time:
        st.session_state.last_announcement_time = current_time
        return True
    return False

# Function to check if it's time to speak. Return True if current time == speaking_freq AND need_to_announce = True
def should_speak_now(speaking_freq):
    now = datetime.datetime.now()
    current_hour = now.hour
    current_minute = now.minute
    
    # Parse the selected option and check if we should speak now
    if speaking_freq == "9am, 12pm, 4pm":
        specific_times = [(9, 0), (12, 0), (16, 0)]
        for hour, minute in specific_times:
            if current_hour == hour and current_minute == minute and need_to_announce(hour, minute):
                return True
    
    elif speaking_freq == "every 2 hours":
        if current_minute == 0 and current_hour % 2 == 0 and need_to_announce(current_hour, current_minute):
            return True
    
    elif speaking_freq == "every hour":
        if current_minute == 0 and need_to_announce(current_hour, current_minute):
            return True
    
    return False


def is_alert(alert_time):
    elapsed = datetime.datetime.now() - st.session_state.stopwatch_start
    if elapsed >= datetime.timedelta(minutes=alert_time):
        return True
    else:
        return False


def alert_string_audio(alert_string):
    tts = gTTS(text=alert_string, lang='en')
    return tts.save("alert_string_audio.mp3")



with col2:
    st.subheader("Timer")
# Create a placeholder for the stopwatch display
    timer_placeholder = st.empty()

    #user inputs of weight and height
    user_alert_time = st.number_input("When do you want the alarm (in minutes):", step = 10, value = 160, min_value = 0, max_value = 300)
    user_alert_text  = st.text_input(
        "What do you want the alarm to say:",
        value = "Yo people! It's time to have a pause, pee and check pressure areas.",
        key = "alert_text",
        on_change=on_text_change()
        )

    alert_time = user_alert_time

    # Start/Stop Stopwatch button
    if not st.session_state.stopwatch_running:
        if st.button("Start"):
            st.session_state.stopwatch_running = True
            st.session_state.stopwatch_start = datetime.datetime.now()
            st.session_state.alert_shown = False
            st.rerun()

    if st.session_state.stopwatch_running == True:
        if st.button("Pause"):
            st.session_state.stopwatch_running = False
            st.rerun()
    
    # Reset button (always available)
    if st.button("Reset"):
        st.session_state.stopwatch_running = False
        st.session_state.stopwatch_start = None
        st.session_state.alert_shown = False
        st.rerun()
    
# Audio file path - replace with your actual path
## audio_file_path = alert_string_audio.mp3  # Replace with your actual file path

# Function to display the stopwatch
def display_stopwatch():
    if (st.session_state.stopwatch_running == True) and (st.session_state.stopwatch_start != 0) :
        # Calculate elapsed time
        elapsed = datetime.datetime.now() - st.session_state.stopwatch_start
        
        # Format elapsed time
        hours, remainder = divmod(elapsed.total_seconds(), 3600)
        minutes, seconds = divmod(remainder, 60)
        timer_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
        
        # Check if elapsed time is at or past 2 hours mark
        is_alert = elapsed >= datetime.timedelta(minutes=alert_time)
        
        #if is_alert and not st.session_state.alert_shown:
            # Play sound when elapsed time reaches 2 hours
            #st.session_state.alert_shown = True
            ## st.markdown(get_audio_html(audio_file_path), unsafe_allow_html=True)
        
        # Display stopwatch with red background if alert condition is met
        if is_alert:
            timer_placeholder.markdown(
                f"<div style='background-color: #ff5555; padding: 20px; border-radius: 10px;'>"
                f"<h1 style='text-align: center; color: white;'>{timer_str}</h1>"
                f"<p style='text-align: center; color: white;'>{alert_time} minutes have elapsed!</p>"
                f"</div>",
                unsafe_allow_html=True
            )
            if st.session_state.alert_shown == False:                
                user_alert_tts = gTTS(text=user_alert_text, lang='en')
                user_alert_tts.save("user_alert_audio.mp3")
                autoplay_audio("user_alert_audio.mp3")
            st.session_state.alert_shown = True
            #st.rerun()
            ##st.audio("user_alert_audio.mp3", format="audio/mpeg", loop=False, autoplay=True)
            #time.sleep(61)
            
        else:
            timer_placeholder.markdown(
                f"<h1 style='text-align: center; font-size: 48px;'>{timer_str}</h1>",
                unsafe_allow_html=True
            )
    else:
        # Display zeros when not running
        if st.session_state.stopwatch_start is None:
            timer_placeholder.markdown(
                "<h1 style='text-align: center; font-size: 48px;'>00:00:00</h1>", 
                unsafe_allow_html=True
            )
        else:
            # Display the last time when paused
            elapsed = st.session_state.stopwatch_start - st.session_state.stopwatch_start
            if st.session_state.stopwatch_running == False:
                elapsed = datetime.datetime.now() - st.session_state.stopwatch_start
            
            hours, remainder = divmod(elapsed.total_seconds(), 3600)
            minutes, seconds = divmod(remainder, 60)
            timer_str = f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
            
            is_alert = elapsed >= datetime.timedelta(minutes=alert_time)
            
            if is_alert:
                timer_placeholder.markdown(
                    f"<div style='background-color: #ff5555; padding: 20px; border-radius: 10px;'>"
                    f"<h1 style='text-align: center; color: white;'>{timer_str}</h1>"
                    f"<p style='text-align: center; color: white;'>2 hours elapsed!</p>"
                    f"</div>",
                    unsafe_allow_html=True
                )
            else:
                timer_placeholder.markdown(
                    f"<h1 style='text-align: center; font-size: 48px;'>{timer_str}</h1>",
                    unsafe_allow_html=True
                )

# Main app loop
try:
    while True:
        # Update current time
        if st.session_state.running:
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M:%S %p")
            time_placeholder.markdown(f"<h1 style='text-align: center; font-size: 48px;'>{time_str}</h1>", unsafe_allow_html=True)
        #check if its time make an announcement
            if should_speak_now(speaking_freq):
                time_string_auto = f"The time, sponsored by Accurist, is {hour} : {period}."
                text = time_string_auto  # + interest_str
                tts = gTTS(text=text, lang='en')
                tts.save("time_str_auto.mp3")
                st.audio("time_str_auto.mp3", format="audio/mpeg", loop=False, autoplay=True)
                time.sleep(15)


### funny / light heart mode string string add-on
            #interest_str = ""
            #if funny_mode == True:
            #    if hour < 9:
            #        interest_str = "I hope we've all had our Weetabix"
            #    elif hour < 10:
            #        interest_str = "I need a coffee"
            #    elif hour < 12:
            #        interest_str = "I'm getting peckish"
            #    elif hour < 14:
            #        interest_str = "I hope everybody has had their lunch"
            #    elif hour < 16:
            #        interest_str = "Time for a cup of tea."
            #    else:
            #        interest_str = "Don't even THINK about sending for the next one"



        # Update stopwatch
        display_stopwatch()
        
        # Wait before updating
        time.sleep(0.1)
except st.runtime.scriptrunner.StopException:
    # Handle Streamlit script execution stopping
    pass

# Display current date at the bottom
st.markdown("---")
st.write("Date: ", datetime.datetime.now().strftime("%A, %B %d, %Y"))