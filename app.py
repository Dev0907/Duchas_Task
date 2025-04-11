import speech_recognition as sr
import pyttsx3
import json
import os
from datetime import datetime
import time

class Assistant:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", 150)
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.0  # Longer pause threshold
        self.quiz_questions = []
        self.correct_answers = 0
        self.total_questions = 0
        self.results_dir = "results"
        self.results_file = os.path.join(self.results_dir, "quiz_results.txt")
        self.categories_dir = "categories"
        
        # Create necessary directories if they don't exist
        os.makedirs(self.results_dir, exist_ok=True)
        os.makedirs(self.categories_dir, exist_ok=True)

    def speak(self, text):
        """Convert text to speech and print it"""
        print("Assistant:", text)
        self.engine.say(text)
        self.engine.runAndWait()

    def listen(self, timeout=5, retries=3):
        """Listen to user voice input with retries and timeout"""
        with sr.Microphone() as source:
            for attempt in range(retries):
                try:
                    print(f"Listening (attempt {attempt + 1}/{retries})...")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = self.recognizer.listen(source, timeout=timeout)
                    text = self.recognizer.recognize_google(audio).lower()
                    print("You said:", text)
                    return text
                except sr.WaitTimeoutError:
                    if attempt < retries - 1:
                        self.speak("I didn't hear anything. Please try again.")
                        continue
                    self.speak("No speech detected. Moving on.")
                    return None
                except sr.UnknownValueError:
                    if attempt < retries - 1:
                        self.speak("I didn't understand that. Please repeat.")
                        continue
                    self.speak("Sorry, I still didn't understand that.")
                    return None
                except sr.RequestError as e:
                    self.speak(f"Could not request results from speech recognition service: {e}")
                    return None
        return None

    def list_categories(self):
        """List all available quiz categories"""
        categories = []
        try:
            categories = [f.replace(".json", "") for f in os.listdir(self.categories_dir) 
                         if f.endswith(".json")]
        except Exception as e:
            self.speak(f"Error accessing categories: {e}")
        return categories

    def choose_category(self):
        """Let user select a quiz category by voice"""
        categories = self.list_categories()
        if not categories:
            self.speak("No quiz categories found in the categories directory.")
            return None

        self.speak("Available quiz categories are: " + ", ".join(categories))
        self.speak("Please say the name of the category you want to take.")

        while True:
            response = self.listen()
            if not response:
                continue

            # Find best matching category
            matched_category = None
            for category in categories:
                if category.lower() in response:
                    matched_category = category
                    break

            if matched_category:
                category_path = os.path.join(self.categories_dir, f"{matched_category}.json")
                self.speak(f"You selected {matched_category}.")
                return category_path
            else:
                self.speak("I didn't recognize that category. Please try again or say 'exit' to cancel.")
                if response and 'exit' in response:
                    return None

    def load_quiz_questions(self, file_path):
        """Load quiz questions from JSON file"""
        try:
            with open(file_path, 'r') as f:
                self.quiz_questions = json.load(f)
            
            # Validate the loaded questions
            valid_questions = []
            for q in self.quiz_questions:
                if ('question' in q and 'options' in q and 'answer' in q and 
                    isinstance(q['options'], list) and len(q['options']) >= 2):
                    valid_questions.append(q)
            
            self.quiz_questions = valid_questions
            self.total_questions = len(self.quiz_questions)
            
            if self.total_questions == 0:
                self.speak("No valid questions found in the file.")
                return False
            
            self.speak(f"Loaded {self.total_questions} questions.")
            return True
        except Exception as e:
            self.speak(f"Failed to load quiz questions: {str(e)}")
            self.quiz_questions = []
            self.total_questions = 0
            return False

    def start_quiz(self):
        """Start the quiz session"""
        if not self.quiz_questions:
            self.speak("No questions available to start the quiz.")
            return

        self.speak(f"Starting quiz with {self.total_questions} questions. Let's begin!")
        self.correct_answers = 0
        
        for idx, q_data in enumerate(self.quiz_questions, 1):
            self.ask_question(idx, q_data)
            time.sleep(1)  # Brief pause between questions

        accuracy = (self.correct_answers / self.total_questions) * 100
        self.speak(f"Quiz completed. You got {self.correct_answers} out of {self.total_questions} correct. That's {accuracy:.1f}% accuracy.")
        self.save_results()

    def ask_question(self, number, q_data):
        """Ask a single question and check the answer"""
        self.speak(f"Question {number}: {q_data['question']}")
        
        # Speak options with numbers
        for i, opt in enumerate(q_data['options'], 1):
            self.speak(f"Option {i}: {opt}")
        
        self.speak("Please say the number of your answer.")
        
        while True:
            response = self.listen()
            if not response:
                continue

            # Try to extract a number from the response
            try:
                # Handle both "one" and "1" formats
                word_to_num = {
                    'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
                    'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10
                }
                
               
                selected_num = None
                for word, num in word_to_num.items():
                    if word in response:
                        selected_num = num
                        break
                
                # If no word number found, try to extract digit
                if selected_num is None:
                    # Extract first digit from response
                    for char in response:
                        if char.isdigit():
                            selected_num = int(char)
                            break
                
                if selected_num is None:
                    raise ValueError("No number detected")

                # Validate the selected option
                if 1 <= selected_num <= len(q_data['options']):
                    selected_option = q_data['options'][selected_num - 1]
                    correct = selected_option.lower() == q_data['answer'].lower()
                    
                    if correct:
                        self.speak("Correct!")
                        self.correct_answers += 1
                    else:
                        self.speak(f"Sorry, the correct answer is: {q_data['answer']}")
                    break
                else:
                    self.speak(f"Please say a number between 1 and {len(q_data['options'])}.")
            except Exception as e:
                self.speak("I didn't catch the option number. Please try again.")

    def save_results(self):
        """Save quiz results to file"""
        if self.total_questions == 0:
            return

        accuracy = (self.correct_answers / self.total_questions) * 100
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        result_entry = (
            f"\n[{timestamp}]\n"
            f"Score: {self.correct_answers}/{self.total_questions}\n"
            f"Accuracy: {accuracy:.2f}%\n"
            f"{'-'*30}\n"
        )

        try:
            with open(self.results_file, 'a') as file:
                file.write(result_entry)
            self.speak("Your results have been saved.")
        except Exception as e:
            self.speak(f"Could not save results: {str(e)}")

if __name__ == "__main__":
    assistant = Assistant()
    assistant.speak("Welcome to the Quiz Assistant!")
    
    while True:
        selected_file = assistant.choose_category()
        if not selected_file:
            assistant.speak("No category selected. Exiting.")
            break
        
        if assistant.load_quiz_questions(selected_file):
            assistant.start_quiz()
        
        assistant.speak("Would you like to take another quiz? Say yes or no.")
        response = assistant.listen()
        if not response or 'no' in response:
            assistant.speak("Thank you for using the Quiz Assistant. Goodbye!")
            break