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
        master.geometry("500x600") # Increased size for options menu
        master.resizable(False, False)

        # Styling
        self.style = ttk.Style()
        self.style.configure("TLabel", font=("Arial", 14))
        self.style.configure("TButton", font=("Arial", 12))
        self.style.configure("Header.TLabel", font=("Arial", 18, "bold"))
        self.style.configure("Question.TLabel", font=("Arial", 24, "bold"))
        self.style.configure("Score.TLabel", font=("Arial", 12, "italic"))
        self.style.configure("Start.TButton", font=("Arial", 16, "bold"))
        self.style.configure("Options.TLabelframe", font=("Arial", 12))
        self.style.configure("Options.TLabelframe.Label", font=("Arial", 12, "bold"))

        # --- Game State Variables ---
        self.questions = []
        self.current_question_index = 0
        self.start_time = 0
        self.final_time = 0
        self.current_correct_answer = 0
        self.game_in_progress = False
        
        # --- Game Options Variables ---
        self.num_operands = tk.IntVar(value=2)  # Default: 2 numbers in equation
        self.num_digits = tk.IntVar(value=2)    # Default: 2-digit numbers
        self.use_add_sub = tk.BooleanVar(value=True)  # Addition/Subtraction
        self.use_mul_div = tk.BooleanVar(value=False) # Multiplication/Division

        # --- Main Layout Frames ---
        self.options_frame = ttk.LabelFrame(master, text="Game Options", style="Options.TLabelframe")
        self.options_frame.pack(fill=tk.BOTH, padx=20, pady=10)
        
        self.game_frame = ttk.Frame(master)
        self.game_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # --- Setup Options Frame ---
        self.setup_options_frame()
        
        # --- GUI Widgets for Game ---
        self.header_label = ttk.Label(self.game_frame, text="Quick Math Challenge!", style="Header.TLabel")
        self.header_label.pack(pady=10)

        self.question_label = ttk.Label(self.game_frame, text="", style="Question.TLabel", width=20, anchor="center")
        self.question_label.pack(pady=20)

        self.answer_entry = ttk.Entry(self.game_frame, font=("Arial", 18), width=10, justify="center")
        self.answer_entry.pack(pady=10)
        # Bind Enter key to submit answer
        self.answer_entry.bind("<Return>", self.check_answer_event)

        self.submit_button = ttk.Button(self.game_frame, text="Submit", command=self.check_answer, width=15)
        self.submit_button.pack(pady=5)

        self.status_label = ttk.Label(self.game_frame, text="", style="Score.TLabel", foreground="red")
        self.status_label.pack(pady=5)

        self.score_label = ttk.Label(self.game_frame, text="", style="Score.TLabel")
        self.score_label.pack(pady=5)

        self.leaderboard_display = tk.Text(self.game_frame, height=8, width=35, font=("Courier", 10), state=tk.DISABLED, wrap=tk.WORD, borderwidth=1, relief="solid")
        self.leaderboard_display.pack(pady=5)

        # Add Start Button
        self.start_button = ttk.Button(self.game_frame, text="Start Game", command=self.start_game, style="Start.TButton", width=15)
        self.start_button.pack(pady=5)

        self.play_again_button = ttk.Button(self.game_frame, text="Play Again", command=self.setup_game, state=tk.DISABLED)
        self.play_again_button.pack(pady=5)

        # --- Initial Setup ---
        self.load_leaderboard_display() # Show leaderboard initially
        self.setup_game(show_welcome=True) # Setup the game but don't start the timer

    def setup_options_frame(self):
        """Set up the options frame with game settings."""
        # Number of operands (numbers in the equation)
        operands_frame = ttk.Frame(self.options_frame)
        operands_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(operands_frame, text="Number of operands:").pack(side=tk.LEFT, padx=5)
        operands_spinbox = ttk.Spinbox(operands_frame, from_=2, to=4, width=5, 
                                       textvariable=self.num_operands)
        operands_spinbox.pack(side=tk.RIGHT, padx=5)
        
        # Number of digits
        digits_frame = ttk.Frame(self.options_frame)
        digits_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(digits_frame, text="Number of digits:").pack(side=tk.LEFT, padx=5)
        digits_spinbox = ttk.Spinbox(digits_frame, from_=1, to=3, width=5, 
                                     textvariable=self.num_digits)
        digits_spinbox.pack(side=tk.RIGHT, padx=5)
        
        # Operation types - checkboxes
        operations_frame = ttk.Frame(self.options_frame)
        operations_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(operations_frame, text="Operations:").pack(side=tk.LEFT, padx=5)
        
        operations_checks_frame = ttk.Frame(operations_frame)
        operations_checks_frame.pack(side=tk.RIGHT)
        
        ttk.Checkbutton(operations_checks_frame, text="Addition & Subtraction", 
                       variable=self.use_add_sub).pack(anchor=tk.W)
        ttk.Checkbutton(operations_checks_frame, text="Multiplication & Division", 
                       variable=self.use_mul_div).pack(anchor=tk.W)
        
        # Validator to ensure at least one operation type is selected
        def validate_operations():
            if not self.use_add_sub.get() and not self.use_mul_div.get():
                messagebox.showwarning("Invalid Selection", "At least one operation type must be selected!")
                self.use_add_sub.set(True)
            
        # Bind the checkers to the validation function
        for var in [self.use_add_sub, self.use_mul_div]:
            var.trace_add("write", lambda *args: validate_operations())

    def generate_questions(self):
        """Generates a list of NUM_QUESTIONS problems based on selected options."""
        self.questions = []
        
        # Get current option values
        operands = self.num_operands.get()
        digits = self.num_digits.get()
        operations = []
        
        if self.use_add_sub.get():
            operations.extend(['+', '-'])
        if self.use_mul_div.get():
            operations.extend(['×', '÷'])  # Using × and ÷ for display
            
        # Default to addition if somehow no operations are selected
        if not operations:
            operations = ['+']
            
        # Generate digit ranges based on selected digit count
        min_value = 10**(digits-1)
        max_value = (10**digits) - 1
        if digits == 1:  # Handle single digit (1-9)
            min_value = 1
            
        for _ in range(NUM_QUESTIONS):
            # Generate the operands
            nums = [random.randint(min_value, max_value) for _ in range(operands)]
            
            # Select operation
            operation = random.choice(operations)
            
            # For subtraction, ensure non-negative result
            if operation == '-':
                # Sort numbers in descending order for subtraction
                nums.sort(reverse=True)
                
            # For division, ensure clean division (no remainder)
            if operation == '÷':
                # Pick first number, then make subsequent numbers factors
                nums = [random.randint(min_value, max_value)]
                # Get all possible divisors within the valid range
                for _ in range(operands - 1):
                    possible_divisors = [n for n in range(2, min(nums[0], max_value) + 1) 
                                         if nums[0] % n == 0 and n >= min_value]
                    if possible_divisors:
                        nums.append(random.choice(possible_divisors))
                    else:
                        # If no valid divisors, use 1 (always valid)
                        nums.append(1)
                
                # Sort numbers for clean division
                nums.sort(reverse=True)
                
            # Build question text
            question_text = str(nums[0])
            for i in range(1, len(nums)):
                question_text += f" {operation} {nums[i]}"
            question_text += " = ?"
            
            # Calculate the correct answer
            if operation == '+':
                answer = sum(nums)
            elif operation == '-':
                answer = nums[0]
                for num in nums[1:]:
                    answer -= num
            elif operation == '×':
                answer = nums[0]
                for num in nums[1:]:
                    answer *= num
            elif operation == '÷':
                answer = nums[0]
                for num in nums[1:]:
                    answer //= num
                    
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

    def setup_game(self, show_welcome=False):
        """Sets up the game state but doesn't start the timer."""
        self.generate_questions()
        self.current_question_index = 0
        self.final_time = 0
        self.game_in_progress = False
        
        # Enable the options frame
        for child in self.options_frame.winfo_children():
            for widget in child.winfo_children():
                if isinstance(widget, (ttk.Spinbox, ttk.Checkbutton)):
                    widget.config(state=tk.NORMAL)
        
        # Enable/disable appropriate widgets
        self.answer_entry.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.DISABLED)
        self.play_again_button.config(state=tk.DISABLED)
        self.start_button.config(state=tk.NORMAL)
        
        # Clear display
        self.status_label.config(text="")
        
        if show_welcome:
            self.question_label.config(text="Ready to play?")
            self.score_label.config(text="Configure options and click 'Start Game'!")
        else:
            self.question_label.config(text="Play again?")
            self.score_label.config(text="Configure options and click 'Start Game'!")

    def start_game(self):
        """Starts the game and timer."""
        # Disable options during gameplay
        for child in self.options_frame.winfo_children():
            for widget in child.winfo_children():
                if isinstance(widget, (ttk.Spinbox, ttk.Checkbutton)):
                    widget.config(state=tk.DISABLED)
                    
        self.game_in_progress = True
        self.start_button.config(state=tk.DISABLED)  # Disable start button during gameplay
        self.answer_entry.config(state=tk.NORMAL)
        self.submit_button.config(state=tk.NORMAL)
        self.display_question()
        self.start_time = time.time()  # Start timer only when the game actually starts
        self.answer_entry.focus_set()  # Set focus to entry field

    def check_answer_event(self, event):
        """Callback for the Enter key press."""
        if self.game_in_progress:
            self.check_answer()

    def check_answer(self):
        """Checks the user's answer against the correct answer."""
        if not self.game_in_progress:
            return
            
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
        self.game_in_progress = False
        self.final_time = time.time() - self.start_time
        self.question_label.config(text="Finished!")
        self.score_label.config(text=f"Your time: {self.final_time:.2f} seconds")
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.DISABLED)
        self.play_again_button.config(state=tk.NORMAL)
        self.start_button.config(state=tk.NORMAL)  # Enable start button for new game
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

        # Create a description of the game settings
        settings = []
        settings.append(f"{self.num_operands.get()} operands")
        settings.append(f"{self.num_digits.get()}-digit")
        
        ops = []
        if self.use_add_sub.get():
            ops.append("+-")
        if self.use_mul_div.get():
            ops.append("×÷")
        settings.append("".join(ops))
        
        settings_str = " ".join(settings)

        # Prompt for name only if the game was successfully completed
        if self.final_time > 0:
             name = simpledialog.askstring("Leaderboard Entry", "Enter your name:", parent=self.master)
             if not name:
                 name = "Anonymous" # Default name if none entered

             leaderboard.append({
                 "name": name, 
                 "score": self.final_time,
                 "settings": settings_str  # Store game settings with the score
             })
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
            self.leaderboard_display.insert(tk.END, "{:<4} {:<15} {:<10} {:<15}\n".format("Rank", "Name", "Time (s)", "Settings"))
            self.leaderboard_display.insert(tk.END, "-" * 50 + "\n")
            for i, entry in enumerate(leaderboard):
                rank = i + 1
                name = entry['name'][:12] # Truncate long names
                score = f"{entry['score']:.2f}"
                settings = entry.get('settings', 'classic')  # Default for older scores
                self.leaderboard_display.insert(tk.END, f"{rank:<4} {name:<15} {score:<10} {settings:<15}\n")

        self.leaderboard_display.config(state=tk.DISABLED) # Make read-only again


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    game_gui = MathGameGUI(root)
    root.mainloop()