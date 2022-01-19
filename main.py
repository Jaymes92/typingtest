from tkinter import *
from tkinter import ttk
import requests
import time
import re
from difflib import ndiff


# Use API to request new random paragraph. Clear all text, update display with API response, set new timer start.
def new_test():
    global timer
    response = requests.get("http://metaphorpsum.com/paragraphs/2/8")
    target_text.configure(state=NORMAL)
    target_text.delete(1.0, END)
    target_text.insert("end", response.text)
    target_text.configure(state=DISABLED)
    typed_text.delete(1.0, END)
    typed_text.focus_set()
    timer = time.perf_counter()


# Stops timer then performs all relevant calculations and updates the display fields.
def stop_timer():
    global timer
    timer = time.perf_counter() - timer
    total_time_label.configure(text=f"Total Time: {timer:.2f} sec")
    # Find any multiple consecutive spaces and count it as just one and remove all new lines.
    typed = typed_text.get(1.0, END).replace("\n", "")
    typed = re.sub("[ ]{2,}", " ", typed)
    total_char_label.configure(text=f"Total Char: {len(typed)}")
    # Use gross_WPM = (All Entries/5) / (Time[minutes])
    gross_wpm = len(typed)/5 / (timer/60)
    gross_wpm_label.configure(text=f"Gross WPM: {gross_wpm:.1f}")

    # First pass at an algorithm to count incorrect characters. For each typed word use pop() to remove and compare to
    # next target word. Use ndiff from difflib module to look at missing characters (returned with a "+") and
    # excess characters (returned with a "-"). Count 'errors' as the max of either the + or - for a word. Not summing
    # because replacing a letter generates both a "+" and a "-" and looking at max of the two is a rough way to avoid
    # this (I want replacements to only add one error).
    correct = 0
    incorrect = 0
    target = target_text.get(1.0, END).replace("\n", "")
    typed = typed.split(" ")
    target = target.split(" ")
    for word in typed:
        target_word = target.pop(0)
        print(f"Comparing typed: {word} to target: {target_word}")
        diff = ndiff(word, target_word)
        plus = 0
        minus = 0
        for c in diff:
            if c[0] == "+":
                plus += 1
            elif c[0] == "-":
                minus += 1
        errors = max([plus, minus])
        incorrect += errors
        # +1 to account for spaces at the end of every word that were removed during splitting.
        correct += len(word) - errors + 1
        print(f"Correct characters: {len(word) - errors}. Incorrect characters: {errors}")
    # Subtract extra space counted on the last word of the loop.
    correct -= 1
    correct_label.configure(text=f"Correct Char: {correct}")
    incorrect_label.configure(text=f"Incorrect Char: {incorrect}")
    # Calculate net WPM with Net WPM = Gross WPM - (Uncorrected Errors/Time[Minutes])
    # Or "Words per minute typed minus errors per minute made."
    net_wpm = gross_wpm - incorrect / (timer/60)
    net_wpm_label.configure(text=f"Net WPM: {net_wpm:.1f}")


FONT = ("Times New Roman", 16, "bold")
timer = 0

root = Tk()
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
root.title("Typing Test")

frame = ttk.Frame(root)
frame.grid(row=0, column=0, sticky="nsew")
frame.columnconfigure(0, weight=1)
frame.rowconfigure(0, weight=1)

target_text = Text(frame, wrap=WORD, pady=10, padx=10)
target_text.insert("end", "Welcome to my mediocre typing test. Press the 'New Test' button to generate new words.")
target_text.configure(state=DISABLED)
target_text.grid(row=0, column=0, sticky="nsew")

typed_text = Text(frame, height=10)
typed_text.grid(row=1, column=0, sticky="ew")

bottom_frame = ttk.Frame(frame)
bottom_frame.grid(row=2, column=0, stick="ew")
bottom_frame.columnconfigure(0, weight=1)
bottom_frame.columnconfigure(1, weight=1)

new_button = ttk.Button(bottom_frame, text="New Test", command=new_test)
new_button.grid(column=0, row=0, sticky="ew", padx=5, pady=5)
stop_button = ttk.Button(bottom_frame, text="Stop Timer", command=stop_timer)
stop_button.grid(column=1, row=-0, sticky="ew", padx=5, pady=5)
total_char_label = ttk.Label(bottom_frame, text="Total Char: ---", anchor="w", font=FONT)
total_char_label.grid(column=0, row=1, sticky="ew", padx=5, pady=5)
total_time_label = ttk.Label(bottom_frame, text="Total Time: ---", anchor="w", font=FONT)
total_time_label.grid(column=1, row=1, sticky="ew", padx=5, pady=5)
correct_label = ttk.Label(bottom_frame, text="Correct Char: ---", anchor="w", font=FONT)
correct_label.grid(column=0, row=2, sticky="ew", padx=5, pady=5)
gross_wpm_label = ttk.Label(bottom_frame, text="Gross WPM: ---", anchor="w", font=FONT)
gross_wpm_label.grid(column=1, row=2, sticky="ew", padx=5, pady=5)
incorrect_label = ttk.Label(bottom_frame, text="Incorrect Char: ---", anchor="w", font=FONT)
incorrect_label.grid(column=0, row=3, sticky="ew", padx=5, pady=5)
net_wpm_label = ttk.Label(bottom_frame, text="Net WPM: ---", anchor="w", font=FONT)
net_wpm_label.grid(column=1, row=3, sticky="ew", padx=5, pady=5)

root.mainloop()
