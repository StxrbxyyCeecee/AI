import speech_recognition as sr

recognizer = sr.Recognizer()
mic = sr.Microphone()

def record_voice(prompt="🎙 I'm listening, sir...", timeout=None, phrase_time_limit=None):
    with mic as source:
        print(prompt)
        recognizer.adjust_for_ambient_noise(source, duration=0.5) 
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("Listening timed out.")
            return None

    try:
        text = recognizer.recognize_google(audio, language="en-US")
        print("👤 You:", text)
        return text
    except sr.UnknownValueError:
        print("🤖 Couldn't recognize the voice")
        return None
    except sr.RequestError as e:
        print("🤖 Google Speech API Error:", e)
        return None