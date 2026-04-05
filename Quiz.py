import tkinter as tk
from tkinter import messagebox
import json
import openai
import threading

openai.api_type = "open_ai"
openai.api_base = "http://127.0.0.1:1234/v1"
openai.api_key = "NULL"

class Quiz:
    def __init__(self, master):
        self.master = master
        self.master.title("Quiz Application")
        self.master.geometry("1920x1080")
        self.master.configure(bg="#333333")
        
        # Title Label
        self.title_label = tk.Label(master, text="Enter Quiz Details", font=("Amasis MT Pro Black", 36, "bold"),fg="#ffffff",bg="#333333",)
        self.title_label.pack(pady=20)

        # Topic Entry Field
        self.topic_var = tk.StringVar()  # Store user input for topic
        self.topic_label = tk.Label(master, text="Enter Topic (e.g., General Knowledge,History,Programming):", font=("Helvetica", 18),fg="#ffffff",bg="#333333",)
        self.topic_label.pack(pady=10)
        self.topic_entry = tk.Entry(master, textvariable=self.topic_var, font=("Helvetica", 14))
        self.topic_entry.pack(pady=10)

        # Age Entry Field
        self.age_var = tk.StringVar()  # Store user input for age
        self.age_label = tk.Label(master, text="Enter Your Age:", font=("Helvetica", 14),fg="#ffffff",bg="#333333")
        self.age_label.pack(pady=10)
        self.age_entry = tk.Entry(master, textvariable=self.age_var, font=("Helvetica", 14))
        self.age_entry.pack(pady=10)

        # Start Quiz Button
        self.start_button = tk.Button(master, text="Start Quiz", font=("Amasis MT Pro Black", 18), command=self.start_quiz_threaded,bg="lightblue")
        self.start_button.pack(pady=20)

        self.user_answers = []  # List to store user answers and correct answers

    def start_quiz_threaded(self):
        thread = threading.Thread(target=self.start_quiz)
        thread.start()

    def start_quiz(self):
        try:
            age = int(self.age_var.get())
        except ValueError:
            messagebox.showwarning("Warning", "Please enter a valid age.")
            return

        topic = self.topic_var.get().strip()
        if not topic:
            messagebox.showwarning("Warning", "Please enter a valid topic.")
            return

        # Hide the topic and age input fields once the quiz starts
        self.hide_input_fields()

        # Show Loading message
        self.show_loading_message()

        # Fetch questions from LM Studio API based on age and topic
        self.questions = self.fetch_questions_from_api(age, topic)

        # Close the Loading message
        self.close_loading_message()

        if not self.questions:
            messagebox.showerror("Error", "Could not fetch questions.")
            return

        # Log the number of questions fetched
        print(f"Number of questions fetched: {len(self.questions)}")

        self.score = 0
        self.question_index = 0
        self.display_question()

    def hide_input_fields(self):
        # Hide the topic, age labels and entry fields, and start button
        self.topic_label.pack_forget()
        self.topic_entry.pack_forget()
        self.age_label.pack_forget()
        self.age_entry.pack_forget()
        self.start_button.pack_forget()

    def show_loading_message(self):
        # Create a Toplevel window for the loading message
        self.loading_window = tk.Toplevel(self.master)
        self.loading_window.title("Loading...")
        self.loading_window.geometry("400x200")
        label = tk.Label(self.loading_window, text="Generating questions... Please wait..", font=("Helvetica", 14))
        label.pack(pady=20)

    def close_loading_message(self):
        # Close the loading window once the questions are fetched
        if hasattr(self, 'loading_window') and self.loading_window:
            self.loading_window.destroy()

    def fetch_questions_from_api(self, age, topic):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4-0613",
                messages=[{
                    "role": "user",
                    "content": (f"You are a quiz generator for a man or kid aged {age}. Create 5 logical and correct age-appropriate multiple-choice questions on the topic '{topic}'. "
                                "Each question must have 4 answer options in which one should be correct answer (A, B, C, D), with one correct answer. Ensure questions are simple, clear, and correct. "
                                "Provide output in JSON format: "
                                "\"{\\\"questions\\\": ["
                                "{"
                                "\\\"question\\\": \\\"<question_text>\\\","
                                "\\\"options\\\": [\\\"<option1>\\\", \\\"<option2>\\\", \\\"<option3>\\\", \\\"<option4>\\\"],"
                                "\\\"answer\\\": \\\"<correct_answer_In_text>\\\""
                                "}"
                                "]}\""
                        )
                }]
            )
            response_text = response['choices'][0]['message']['content'].strip()
            json_start_index = response_text.find("{")
            json_end_index = response_text.rfind("}") + 1
            json_str = response_text[json_start_index:json_end_index]

            try:
                data = json.loads(json_str)
                questions = data.get("questions", [])

                # Log number of questions
                print(f"Total questions fetched from API: {len(questions)}")

                # Ensure each question has the required "answer" field
                for question in questions:
                    if "answer" not in question:
                        print(f"Warning: Missing 'answer' in question: {question['question']}")
                        continue  # Skip questions with missing answers

                return questions

            except json.JSONDecodeError as e:
                messagebox.showerror("JSON Error", f"Failed to parse JSON: {e}")
                return None
        except Exception as e:
            messagebox.showerror("API Error", f"Failed to fetch questions: {e}")
            return None

    def display_question(self):
        if self.question_index >= len(self.questions):
            self.show_score()
            return

        question_data = self.questions[self.question_index]
        question_text = question_data.get("question", "No question available")
        
        # Clear any existing question
        self.clear_question()

        # Question Label
        self.question_label = tk.Label(self.master, text=question_text, font=("Amasis MT Pro Black", 18),fg="#ffffff",bg="#333333")
        self.question_label.pack(pady=20)

        # Option Buttons
        self.option_buttons = []
        for option in question_data.get("options", []):
            button = tk.Button(self.master, text=option, font=("Amasis MT Pro Black", 14),
                               command=lambda selected_option=option: self.check_answer(selected_option))
            button.pack(pady=5)
            self.option_buttons.append(button)

    def check_answer(self, selected_option):
        correct_answer = self.questions[self.question_index].get("answer")
        
        # Track the user's answer for the current question
        user_answer = selected_option
        self.user_answers.append({
            "question": self.questions[self.question_index].get("question"),
            "user_answer": user_answer,
            "correct_answer": correct_answer
        })

        if correct_answer and selected_option == correct_answer:
            self.score += 1
        
        self.question_index += 1
        self.display_question()

    def clear_question(self):
        # Clear the previous question and options
        for widget in self.master.winfo_children():
            if isinstance(widget, tk.Label) or isinstance(widget, tk.Button):
                widget.destroy()

    def show_score(self):
        # Show the final score
        messagebox.showinfo("Quiz Complete", f"Your final score is: {self.score}/{len(self.questions)}")

        # Display full quiz results (questions, user's answers, and correct answers)
        self.show_full_results()

        # Close the window after displaying score
        self.master.quit()

    def show_full_results(self):
    # Create a new window to show the full results
        results_window = tk.Toplevel(self.master)
        results_window.title("Quiz Results")
        results_window.geometry("1920x1080")

        result_text = ""
        for answer in self.user_answers:
            result_text += f"Q: {answer['question']}\n"
            result_text += f"Your answer: {answer['user_answer']}\n (Correct answer: {answer['correct_answer']})\n\n"
        
        # Display the results in the results window
        result_label = tk.Label(results_window, text=result_text, font=("Helvetica", 12), justify="left")
        result_label.pack(padx=20, pady=20)

        # Quit Button to close the results window
        quit_button = tk.Button(results_window, text="Close", command=results_window.destroy)
        quit_button.pack(pady=20)

        # Make sure the results window is destroyed properly
        results_window.protocol("WM_DELETE_WINDOW", results_window.destroy)

