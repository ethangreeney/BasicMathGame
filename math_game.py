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

        self.leaderboard_display = tk.Text(self.game_frame, height=8, width=45, font=("Courier", 10), state=tk.DISABLED, wrap=tk.WORD, borderwidth=1, relief="solid") # Increased width slightly
        self.leaderboard_display.pack(pady=5)

        # --- Combined Start / Play Again Button ---
        # Initial state: "Start Game", command=self.start_game
        self.start_button = ttk.Button(self.game_frame, text="Start Game", command=self.start_game, style="Start.TButton", width=15)
        self.start_button.pack(pady=10) # Added more padding

        # Removed the separate play_again_button

        # --- Initial Setup ---
        self.load_leaderboard_display() # Show leaderboard initially
        self.setup_game(show_welcome=True) # Setup the initial screen

    def setup_options_frame(self):
        """Set up the options frame with game settings."""
        # Number of operands (numbers in the equation)
        operands_frame = ttk.Frame(self.options_frame)
        operands_frame.pack(fill=tk.X, pady=5)

        ttk.Label(operands_frame, text="Number of operands:").pack(side=tk.LEFT, padx=5)
        operands_spinbox = ttk.Spinbox(operands_frame, from_=2, to=4, width=5,
                                       textvariable=self.num_operands, state="readonly") # Use readonly state
        operands_spinbox.pack(side=tk.RIGHT, padx=5)

        # Number of digits
        digits_frame = ttk.Frame(self.options_frame)
        digits_frame.pack(fill=tk.X, pady=5)

        ttk.Label(digits_frame, text="Number of digits:").pack(side=tk.LEFT, padx=5)
        digits_spinbox = ttk.Spinbox(digits_frame, from_=1, to=3, width=5,
                                     textvariable=self.num_digits, state="readonly") # Use readonly state
        digits_spinbox.pack(side=tk.RIGHT, padx=5)

        # Operation types - checkboxes
        operations_frame = ttk.Frame(self.options_frame)
        operations_frame.pack(fill=tk.X, pady=5)

        ttk.Label(operations_frame, text="Operations:").pack(side=tk.LEFT, padx=5)

        operations_checks_frame = ttk.Frame(operations_frame)
        operations_checks_frame.pack(side=tk.RIGHT)

        cb_add_sub = ttk.Checkbutton(operations_checks_frame, text="Addition & Subtraction (+ -)",
                       variable=self.use_add_sub)
        cb_add_sub.pack(anchor=tk.W)
        cb_mul_div = ttk.Checkbutton(operations_checks_frame, text="Multiplication & Division (× ÷)",
                       variable=self.use_mul_div)
        cb_mul_div.pack(anchor=tk.W)

        # Validator to ensure at least one operation type is selected
        def validate_operations(*args): # Added *args to handle trace callback arguments
            if not self.use_add_sub.get() and not self.use_mul_div.get():
                # Use 'after' to show messagebox slightly later, avoiding potential issues
                self.master.after(10, lambda: messagebox.showwarning("Invalid Selection", "At least one operation type must be selected!"))
                # Re-enable Add/Sub if both get unchecked
                self.use_add_sub.set(True)

        # Bind the checkers to the validation function
        self.use_add_sub.trace_add("write", validate_operations)
        self.use_mul_div.trace_add("write", validate_operations)

    def generate_questions(self):
        """Generates a list of NUM_QUESTIONS problems based on selected options."""
        print("Generating questions with options:", # Debug print
              f"Operands={self.num_operands.get()},",
              f"Digits={self.num_digits.get()},",
              f"AddSub={self.use_add_sub.get()},",
              f"MulDiv={self.use_mul_div.get()}")

        self.questions = []

        # Get current option values
        operands = self.num_operands.get()
        digits = self.num_digits.get()
        operations = []

        if self.use_add_sub.get():
            operations.extend(['+', '-'])
        if self.use_mul_div.get():
            operations.extend(['×', '÷'])  # Using × and ÷ for display

        # Default to addition if somehow no operations are selected (validator should prevent this)
        if not operations:
            print("Warning: No operations selected, defaulting to '+'")
            operations = ['+']
            self.use_add_sub.set(True) # Ensure the checkbox reflects the default

        # Generate digit ranges based on selected digit count
        min_value = 10**(digits-1)
        max_value = (10**digits) - 1
        if digits == 1:  # Handle single digit (1-9)
            min_value = 1

        for i in range(NUM_QUESTIONS):
            # Select operation *for this question*
            operation = random.choice(operations)

             # Generate the operands, handling constraints
            nums = []
            while True: # Loop to ensure valid numbers are generated (esp. for division)
                nums = [random.randint(min_value, max_value) for _ in range(operands)]

                if operation == '-':
                    # Sort numbers in descending order for subtraction to avoid negative results mostly
                    nums.sort(reverse=True)
                    # Ensure result isn't negative (simple check for 2 operands)
                    if operands == 2 and nums[0] < nums[1]:
                        nums[0], nums[1] = nums[1], nums[0] # Swap if needed
                    # For more operands, it gets complex, just sort for now
                    break # Exit while loop

                elif operation == '÷':
                    # Ensure clean division (no remainder)
                    # Pick first number
                    dividend = random.randint(min_value * 2, max_value) # Start with a larger dividend
                    current_result = dividend
                    divisors = []

                    valid_division_found = True
                    for _ in range(operands - 1):
                         # Find divisors within the digit range
                        possible_divisors = [
                            n for n in range(max(2, min_value), min(current_result, max_value) + 1)
                            if current_result % n == 0
                            and (current_result // n >= 1 if operands - len(divisors) == 2 else True) # Ensure next result is >=1
                        ]

                        if not possible_divisors:
                            valid_division_found = False
                            break # Cannot find suitable divisor, retry number generation

                        divisor = random.choice(possible_divisors)
                        divisors.append(divisor)
                        current_result //= divisor

                    if valid_division_found and current_result >= 1: # Check final result is valid
                        nums = [dividend] + divisors
                        break # Exit while loop - found valid sequence
                    # If loop finishes without break, it retries generating numbers

                elif operation == '×':
                     # Optional: check if product exceeds a reasonable limit to avoid huge numbers
                     # temp_answer = nums[0]
                     # for num in nums[1:]: temp_answer *= num
                     # if temp_answer > 100000: continue # Retry if product too large
                     break # Exit while loop

                else: # Addition
                    break # Exit while loop

            # Build question text
            question_text = str(nums[0])
            for j in range(1, len(nums)):
                question_text += f" {operation} {nums[j]}"
            question_text += " = ?"

            # Calculate the correct answer
            answer = nums[0]
            try: # Added try-except for safety, esp. division by zero (should be prevented by logic above)
                if operation == '+':
                    for num in nums[1:]: answer += num
                elif operation == '-':
                    for num in nums[1:]: answer -= num
                elif operation == '×':
                    for num in nums[1:]: answer *= num
                elif operation == '÷':
                    for num in nums[1:]:
                        if num == 0: raise ZeroDivisionError # Safety check
                        answer //= num
            except ZeroDivisionError:
                 print(f"Error: Division by zero avoided for question generation. Retrying.")
                 # This should ideally not happen with the generation logic, but good to handle.
                 # We might want to regenerate this specific question if it occurs.
                 # For simplicity now, we might get an 'invalid' question if this rare case hits.
                 answer = 0 # Assign a default answer or handle differently


            self.questions.append({"text": question_text, "answer": answer})
        # print("Generated questions:", self.questions) # Debug print

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
        """
        Sets up the game state for a new game or prepares the initial screen.
        Resets state variables, enables options, disables game controls,
        and sets the start button to 'Start Game'.
        """
        print("Running setup_game...") # Debug print
        # *** Do NOT generate questions here anymore ***
        # self.generate_questions()
        self.current_question_index = 0
        self.final_time = 0
        self.game_in_progress = False

        # Enable the options frame widgets
        for child in self.options_frame.winfo_children():
            for widget in child.winfo_children():
                 # Check widget type more carefully
                widget_type = widget.winfo_class()
                if widget_type in ('TSpinbox', 'TCheckbutton'):
                    try:
                        widget.config(state=tk.NORMAL)
                    except tk.TclError: # Handle potential errors if widget state is complex
                         pass
                elif isinstance(widget, ttk.Spinbox): # Fallback for Spinbox if style changes class name
                    try:
                         widget.config(state="readonly") # Spinboxes should be readonly
                    except tk.TclError:
                         pass

        # Disable game-play widgets
        self.answer_entry.delete(0, tk.END) # Clear potentially leftover answer
        self.answer_entry.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.DISABLED)

        # Configure the main action button for starting a new game
        self.start_button.config(text="Start Game", command=self.start_game, state=tk.NORMAL)

        # Clear display labels
        self.status_label.config(text="")

        if show_welcome:
            self.question_label.config(text="Ready?")
            self.score_label.config(text="Configure options and click 'Start Game'!")
        else:
            # This case happens when 'Play Again' was clicked
            self.question_label.config(text="Configure & Start!")
            self.score_label.config(text="Options enabled. Click 'Start Game' when ready.")

    def start_game(self):
        """Starts the game, generates questions based on current options, and starts timer."""
        print("Running start_game...") # Debug print

        # --- FIX 1: Generate questions *using current options* ---
        self.generate_questions()
        # Check if question generation failed (e.g., invalid options somehow)
        if not self.questions:
             messagebox.showerror("Error", "Could not generate questions. Please check options.")
             self.setup_game() # Go back to setup state
             return

        # Disable options during gameplay
        for child in self.options_frame.winfo_children():
            for widget in child.winfo_children():
                widget_type = widget.winfo_class()
                if widget_type in ('TSpinbox', 'TCheckbutton') or isinstance(widget, (ttk.Spinbox, ttk.Checkbutton)):
                    try:
                        widget.config(state=tk.DISABLED)
                    except tk.TclError:
                         pass


        self.game_in_progress = True
        self.current_question_index = 0 # Ensure index is reset
        self.start_button.config(state=tk.DISABLED)  # Disable start button during gameplay
        self.answer_entry.config(state=tk.NORMAL)
        self.submit_button.config(state=tk.NORMAL)

        self.start_time = time.time()  # Start timer
        self.display_question() # Display the first question
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
            user_answer_str = self.answer_entry.get().strip()
            if not user_answer_str: # Handle empty input
                self.status_label.config(text="Please enter an answer.", foreground="orange")
                return
            user_answer = int(user_answer_str)
        except ValueError:
            self.status_label.config(text="Please enter a valid number.", foreground="red")
            return # Don't proceed if input is not a number

        if user_answer == self.current_correct_answer:
            self.current_question_index += 1
            self.status_label.config(text="Correct!", foreground="green")
            # Use after to delay moving to next question slightly so user sees "Correct!"
            self.master.after(400, self.display_question) # Reduced delay slightly
        else:
            self.status_label.config(text=f"Incorrect. Please try again", foreground="red")
            self.answer_entry.delete(0, tk.END) # Clear wrong answer
            # Maybe add a small delay before they can try again or move to next? Optional.
            # For now, let them try the same question again immediately.

    def end_game(self):
        """Ends the game, calculates score, handles leaderboard, sets up for 'Play Again'."""
        print("Running end_game...") # Debug print
        self.game_in_progress = False
        self.final_time = time.time() - self.start_time
        self.question_label.config(text="Finished!")
        self.score_label.config(text=f"Your time: {self.final_time:.2f} seconds")
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.config(state=tk.DISABLED)
        self.submit_button.config(state=tk.DISABLED)

        # --- FIX 2: Configure start_button for "Play Again" ---
        # It should call setup_game when clicked next
        self.start_button.config(text="Play Again", command=self.setup_game, state=tk.NORMAL)

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
                content = f.read()
                if not content.strip(): # Check if file is empty or whitespace only
                    return []
                return json.loads(content)
        except (IOError) as e:
             print(f"Warning: Could not read leaderboard file {LEADERBOARD_FILE}: {e}")
             # Don't show popup for read error, just return empty
             return []
        except json.JSONDecodeError as e:
            print(f"Error loading leaderboard: Invalid JSON in {LEADERBOARD_FILE}. {e}")
            messagebox.showerror("Leaderboard Error", f"Leaderboard file '{LEADERBOARD_FILE}' is corrupted.\nA new one will be created if you save a score.")
            # Optionally backup/rename the corrupted file here
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
        settings.append(f"{self.num_operands.get()}op") # Shorter description
        settings.append(f"{self.num_digits.get()}dig")

        ops = []
        if self.use_add_sub.get(): ops.append("+-")
        if self.use_mul_div.get(): ops.append("×÷")
        settings.append("".join(ops))

        settings_str = " ".join(settings)

        # Prompt for name only if the game was successfully completed (time > 0)
        if self.final_time > 0:
             # Check if score is good enough BEFORE asking for name
             is_top_score = len(leaderboard) < LEADERBOARD_SIZE or self.final_time < leaderboard[-1]["score"]

             if is_top_score:
                 name = simpledialog.askstring("Leaderboard Entry",
                                               f"Top {LEADERBOARD_SIZE} score!\nYour time: {self.final_time:.2f}s\nEnter your name:",
                                               parent=self.master)
                 if not name:
                     name = "Anonymous" # Default name if none entered
                 elif len(name) > 12:
                     name = name[:12] # Truncate long names

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
             else:
                 print("Score not in top", LEADERBOARD_SIZE) # Debug print


    def load_leaderboard_display(self):
        """Loads and displays the leaderboard in the Text widget."""
        leaderboard = self.load_leaderboard()
        self.leaderboard_display.config(state=tk.NORMAL) # Enable writing
        self.leaderboard_display.delete('1.0', tk.END) # Clear existing content

        if not leaderboard:
            self.leaderboard_display.insert(tk.END, "Leaderboard is empty.")
        else:
            title = f"--- Leaderboard (Top {min(len(leaderboard), LEADERBOARD_SIZE)}) ---\n"
            header = "{:<4} {:<13} {:<9} {:<15}\n".format("Rank", "Name", "Time(s)", "Settings")
            separator = "-" * 44 + "\n" # Adjust separator length

            self.leaderboard_display.insert(tk.END, title)
            self.leaderboard_display.insert(tk.END, header)
            self.leaderboard_display.insert(tk.END, separator)

            for i, entry in enumerate(leaderboard):
                rank = i + 1
                name = entry.get('name', '???')[:12] # Max 12 chars for name
                score = f"{entry.get('score', 0.0):.2f}"
                settings = entry.get('settings', 'N/A')[:14] # Max 14 chars for settings
                line = f"{rank:<4} {name:<13} {score:<9} {settings:<15}\n"
                self.leaderboard_display.insert(tk.END, line)

        self.leaderboard_display.config(state=tk.DISABLED) # Make read-only again


# --- Main Execution ---
if __name__ == "__main__":
    root = tk.Tk()
    # Apply theme before creating widgets if possible
    try:
        ttk.Style().theme_use('clam') # Or 'alt', 'default', 'classic'
    except tk.TclError:
        print("Themes not available, using default.")
    game_gui = MathGameGUI(root)
    root.mainloop()