# Duchas_Task
This is a Python-based voice-interactive quiz assistant that uses speech recognition and text-to-speech to engage users in a spoken quiz session. Users can choose categories, answer multiple-choice questions by voice, and get their results stored locally.


#Installations
pip install pyttsx3 speechrecognition pyaudio

#Run the file
python quiz_assistant.py
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Flow of Execution
i) Initialization
Loads TTS (pyttsx3) and STT (speech_recognition)

ii) Ensures folders exist (categories/, results/)
Category Selection
Lists available quiz categories from categories/

iii) Uses microphone input to choose one via voice
Quiz Loading

iv) Loads selected JSON file
Validates format: question, options[], answer

v) Quiz Session
Reads each question and options aloud

vi) Accepts user's spoken number (e.g., "one", "2")
Checks correctness and provides feedback

vii) Result Handling
Calculates score and accuracy
Saves result in a timestamped entry to results/quiz_results.txt
