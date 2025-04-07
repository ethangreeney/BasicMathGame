import tkinter as tk
from tkinter import ttk # For themed widgets (nicer look)
from tkinter import simpledialog, messagebox
import random
import time
import json
import os

NUM_QUESTIONS = 10
LEADERBOARD_FILE = "math_game_leaderboard.json"
LEADERBOARD_SIZE = 10

class MathGameGUI:
    def __init__(self, master):
        self.master = master
        master.title("Quick Math Challenge!")
        master.geometry("400x450") # Adjusted size for leaderboard display later
        master.resizable(False, False)

        # Styling
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 14))
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("Header.TLabel", font=("Arial", 18, "bold"))
        self.style.configure("Question.TLabel", font=("Arial", 24, "bold"))
        self.style.configure("Score.TLabel", font=("Arial", 12, "italic"))

        # --- Game State Variables ---
        self.questions = []
        self.current_question_index = 0
        self.start_time = 0
        self.final_time = 0
        self.current_correct_answer = 0

        # --- GUI Widgets ---
        self.header_label = ttk.Label(master, text="Quick Math Challenge!", style="Header.TLabel")
        self.header_label.pack(pady=10)

        self.question_label = ttk.Label(master, text="", style="Question.TLabel", width=20, anchor="center")
        self.question_label.pack(pady=20)

        self.answer_entry = ttk.Entry(master, font=("Arial", 18), width=10, justify="center")
        self.answer_entry.pack(pady=10)
        # Bind Enter key to submit answer
        self.answer_entry.bind("<Return>", self.check_answer_event)

        self.submit_button = ttk.Button(master, text="Submit", command=self.check_answer, width=15)
        self.submit_button.pack(pady=5)

        self.status_label = ttk.Label(master, text="", style="Score.TLabel", foreground="red")
        self.status_label.pack(pady=5)

        self.score_label = ttk.Label(master, text="", style="Score.TLabel")
        self.score_label.pack(pady=5)

        self.leaderboard_display = tk.Text(master, height=11, width=35, font=("Courier", 10), state=tk.DISABLED, wrap=tk.WORD, borderwidth=1, relief="solid")
        self.leaderboard_display.pack(pady=10)

        self.play_again_button = ttk.Button(master, text="Play Again", command=self.start_game, state=tk.DISABLED)
        self.play_again_button.pack(pady=5)

        # --- Initial Setup ---
        self.load_leaderboard_display() # Show leaderboard initially
        self.start_game()

    def generate_questions(self):
        """Generates a list of NUM_QUESTIONS problems."""
        self.questions = []
        for _ in range(NUM_QUESTIONS):
            num1 = random.randint(10, 99)
            num2 = random.randint(10, 99)
            operation = random.choice(['+', '-'])

            if operation == '+':
                question_text = f"{num1} + {num2} = ?"
                answer = num1 + num2
            else:
                # Ensure non-negative result for simplicity
                if num1 < num2:
                    num1, num2 = num2, num1 # Swap them
                question_text = f"{num1} - {num2} = ?"
                answer = num1 - num2
            self.questions.append({"text": question_text, "answer": answer})

    def display_question(self):
        """Updates the GUI to show the current question."""
        if self.current_question_index < NUM_QUESTIONS:
            question_data = self.questions[self.current_question_index]
            self.question_label.config(text=question_data["text"])
            self.current_correct_answer = question_data["answer"]
            self.status_label.config(text="") # Clear status
            self.answer_entry.delete(0, tk.END) # Clear previous answer
            self.answer_entry.focus_set() # Set focus to entry field
            self.score_label.config(text=f"Question {self.current_question_index + 1} of {NUM_QUESTIONS}")
        else:
            self.end_game()

    def start_game(self):
        """Resets the game state and starts a new game."""
        self.generate_questions()
        self.current_question_index = 0
        self.final_time = 0
        self.answer_entry.config(state=tk.NORMAL)
        self.submit_button.config(state=tk.NORMAL)
        self.play_again_button.config(state=tk.DISABLED)
        self.status_label.config(text="")
        self.score_label.config(text="")
        self.display_question()
        self.start_time = time.time() # Start timer when first question is displayed

    def check_answer_event(self, event):
        """Callback for the Enter key press."""
        self.check_answer()

    def check_answer(self):
        """Checks the user's answer against the correct answer."""
        try:
            user_answer = int(self.answer_entry.get())
        except ValueError:
            self.status_label.config(text="Please enter a valid number.", foreground="red")
            return # Don't proceed if input is not a number

        if user_answer == self.current_correct_answer:
            self.current_question_index += 1
            self.status_label.config(text="Correct!", foreground="green")
            # Use after to delay moving to next question slightly so user sees "Correct!"
            self.master.after(500, self.display_question)
        else:
            self.status_label.config(text="Incorrect. Try again.", foreground="red")
            self.answer_entry.delete(0, tk.END) # Clear wrong answer


    def end_game(self):
        """Ends the game, calculates score, and handles leaderboard."""
        self.final_time = time.time() - self.start_time
        self.question_label.config(text="Finished!")
        self.score_label.config(text=f"Your time: {self.final_time:.2f} seconds")
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.DISABLED)
        self.play_again_button.config(state=tk.NORMAL)
        self.status_label.config(text="")

        # Ask for name and update leaderboard
        self.update_leaderboard()
        self.load_leaderboard_display() # Refresh display


    def load_leaderboard(self):
        """Loads leaderboard data from the JSON file."""
        if not os.path.exists(LEADERBOARD_FILE):
            return []
        try:
            with open(LEADERBOARD_FILE, 'r') as f:
                # Handle empty file case
                content = f.read()
                if not content:
                    return []
                return json.loads(content)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading leaderboard: {e}")
            messagebox.showerror("Leaderboard Error", f"Could not load leaderboard file: {e}")
            return []

    def save_leaderboard(self, leaderboard):
        """Saves leaderboard data to the JSON file."""
        try:
            with open(LEADERBOARD_FILE, 'w') as f:
                json.dump(leaderboard, f, indent=4)
        except IOError as e:
            print(f"Error saving leaderboard: {e}")
            messagebox.showerror("Leaderboard Error", f"Could not save leaderboard file: {e}")

    def update_leaderboard(self):
        """Adds the current score to the leaderboard if it's good enough."""
        leaderboard = self.load_leaderboard()

        # Prompt for name only if the game was successfully completed
        if self.final_time > 0:
             name = simpledialog.askstring("Leaderboard Entry", "Enter your name:", parent=self.master)
             if not name:
                 name = "Anonymous" # Default name if none entered

             leaderboard.append({"name": name, "score": self.final_time})
             # Sort by score (time), lowest first
             leaderboard.sort(key=lambda x: x["score"])
             # Keep only top scores
             leaderboard = leaderboard[:LEADERBOARD_SIZE]
             self.save_leaderboard(leaderboard)


    def load_leaderboard_display(self):
        """Loads and displays the leaderboard in the Text widget."""
        leaderboard = self.load_leaderboard()
        self.leaderboard_display.config(state=tk.NORMAL) # Enable writing
        self.leaderboard_display.delete('1.0', tk.END) # Clear existing content

        if not leaderboard:
            self.leaderboard_display.insert(tk.END, "Leaderboard is empty.")
        else:
            self.leaderboard_display.insert(tk.END, "--- Leaderboard (Top {} Scores) ---\n".format(LEADERBOARD_SIZE))
            self.leaderboard_display.insert(tk.END, "{:<4} {:<20} {:<10}\n".format("Rank", "Name", "Time (s)"))
            self.leaderboard_display.insert(tk.END, "-"*36 + "\n")
            for i, entry in enumerate(leaderboard):
                rank = i + 1
                name = entry['name'][:18] # Truncate long names
                score = f"{entry['score']:.2f}"
                self.leaderboard_display.insert(tk.END, f"{rank:<4} {name:<20} {score:<10}\n")

        self.leaderboard_display.config(state=tk.DISABLED) # Make read-only again


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    game_gui = MathGameGUI(root)
    root.mainloop()