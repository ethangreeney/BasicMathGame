# Quick Math Challenge!

A fast-paced arithmetic game to test and improve your mental math skills.

## Overview

Quick Math Challenge is an interactive math game where you solve a series of 10 arithmetic problems as quickly as possible. The game tracks your time and keeps a leaderboard of the fastest players.

## Features

- Customizable difficulty settings
- Timed gameplay
- Persistent leaderboard system
- Clean, user-friendly interface
- Support for various operation types

## Installation

### Requirements
- Python 3.6 or higher
- Tkinter (usually comes with Python installation)

### Steps
1. Clone or download this repository
2. Navigate to the directory containing the files
3. Run the game:
   ```python
   python math_game.py
   ```

## How to Play

1. Configure your preferred difficulty settings
2. Click "Start Game" or press Enter
3. For each question, type your answer in the input field
4. Press Enter or click "Submit" to check your answer
5. If correct, you'll move to the next question; if incorrect, try again
6. After completing all 10 questions, your total time will be displayed
7. If your time is fast enough, you'll be prompted to enter your name for the leaderboard

## Game Options

### Number of Operands (2-4)
Controls how many numbers appear in each equation.
- 2 operands: "17 + 25 = ?"
- 3 operands: "17 + 25 - 8 = ?"
- 4 operands: "17 + 25 - 8 + 12 = ?"

### Number of Digits (1-3)
Controls the size of the numbers.
- 1 digit: Numbers from 1-9
- 2 digits: Numbers from 10-99
- 3 digits: Numbers from 100-999

### Operation Types
- Addition & Subtraction (+ -)
- Multiplication & Division (× ÷)
- Both can be selected for mixed operations

## Benchmark Times

Based on the current leaderboard and estimated difficulty scaling, here are some benchmark times to aim for:

| Difficulty | Settings | Excellent | Good | Average |
|------------|----------|-----------|------|---------|
| Beginner | 2op, 1dig, +- | < 20s | 20-30s | 30-40s |
| Easy | 2op, 2dig, +- | < 30s | 30-40s | 40-50s |
| Medium | 3op, 2dig, +- | < 40s | 40-55s | 55-70s |
| Hard | 3op, 2dig, +-×÷ | < 55s | 55-70s | 70-85s |
| Expert | 4op, 3dig, +-×÷ | < 80s | 80-100s | 100-120s |

### Current Record Holder
The current record for the standard mode is (2op, 2dig, +-) is **31.97 seconds** by Ethan.

## Tips for Faster Times

1. Practice mental math techniques like breaking down numbers
2. For addition/subtraction, try rounding up and then subtracting the difference
3. For multiplication, learn shortcuts for multiplying certain numbers
4. Use the number keys at the top of your keyboard rather than the numpad for faster input
5. Focus on accuracy first - incorrect answers cost more time than careful calculation

## Future Enhancements

- Bonus points for streak of correct answers
- Practice mode without time pressure
- More detailed statistics tracking
- Sound effects and visual feedback
- Additional operation types (exponents, percentages, etc.)