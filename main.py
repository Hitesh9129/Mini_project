import tkinter as tk
from PIL import Image, ImageTk
from Quiz import Quiz  # Assuming the Quiz class is defined elsewhere

# Create the main window
root = tk.Tk()
root.title("Multitool Desktop App")
root.geometry("1920x1080")
root.configure(bg="#333333")

# Welcome Label
title_label = tk.Label(
    root,
    text="Welcome to our App!!",
    font=("Helvetica", 24, "bold"),
    fg="white",
    bg="lightblue",
    pady=10
)
title_label.pack(fill=tk.X)

# Load and resize quiz image
quiz_image = Image.open("C:\\Users\\User\\Downloads\\final mini project\\final mini project\\quizlogo.jpg").resize((180, 180), Image.LANCZOS)
quiz_icon = ImageTk.PhotoImage(quiz_image)

# Create a frame for the buttons
button_frame = tk.Frame(root, bg="#333333")
button_frame.pack(pady=50)  # Adds padding above and below the frame

# Function to open the quiz window
def open_quiz():
    quiz_window = tk.Toplevel(root)
    Quiz(quiz_window)

# Button for "Quizzes" app with image
quiz_button = tk.Button(
    button_frame,
    image=quiz_icon,
    text="Quizzes",
    compound="top",
    font=("Helvetica", 12),
    bg="black",
    fg="white",
    command=open_quiz
)
quiz_button.grid(row=0, column=0, padx=30, pady=20)

# Add a Quit button
quit_button = tk.Button(
    root,
    text="Quit",
    font=("Helvetica", 14, "bold"),
    bg="lightblue",
    fg="black",
    padx=10,
    pady=5,
    command=root.destroy  # Close the main window
)
quit_button.pack(pady=20)  # Position the quit button below other elements

# Keep reference to image to prevent garbage collection
quiz_button.image = quiz_icon

# Start the GUI event loop
root.mainloop()
