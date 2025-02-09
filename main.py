import json

import customtkinter as ctk

from ai_predictor import predict_match
from team_rater import create_rating_file

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def open_create_match():
    root.withdraw()  # Hide the main menu window
    match_window = ctk.CTk()
    match_window.title("Pick Teams for the Match")
    match_window.geometry("500x400")

    # Red Alliance Section
    red_label = ctk.CTkLabel(match_window, text="Red Alliance", font=("Arial", 16))
    red_label.pack(pady=10)
    red_teams = []
    for i in range(3):
        red_team_entry = ctk.CTkEntry(match_window, placeholder_text=f"Red Team {i + 1}")
        red_team_entry.pack(side="left", padx=5)
        red_teams.append(red_team_entry)

    # Blue Alliance Section
    blue_label = ctk.CTkLabel(match_window, text="Blue Alliance", font=("Arial", 16))
    blue_label.pack(pady=20)
    blue_teams = []
    for i in range(3):
        blue_team_entry = ctk.CTkEntry(match_window, placeholder_text=f"Blue Team {i + 1}")
        blue_team_entry.pack(side="left", padx=5)
        blue_teams.append(blue_team_entry)

    # Predict Button
    predict_button = ctk.CTkButton(match_window, text="Predict", state="disabled",
                                   command=lambda: predict_match(red_teams, blue_teams))
    predict_button.pack(pady=20)

    # Function to enable button when all fields are filled
    def check_fields():
        if all(entry.get() != "" for entry in red_teams + blue_teams):
            predict_button.configure(state="normal")
        else:
            predict_button.configure(state="disabled")

    # Bind the check_fields function to monitor changes in all entries
    for entry in red_teams + blue_teams:
        entry.bind("<KeyRelease>", lambda event: check_fields())

    match_window.protocol("WM_DELETE_WINDOW", lambda: root.quit())  # Close the program when the window is closed
    match_window.mainloop()


def rate_team(team_key, rating_label):
    try:
        with open("teams_rating_2024.json", "r") as file:
            ratings = json.load(file)
    except FileNotFoundError:
        create_rating_file("2024_statbotics_ratings.csv", "2024_statbotics_ratings.json")
        with open("worlds_teams_2024.json", "r") as file:
            ratings = json.load(file)
    try:
        team = "frc" + team_key.strip()
        text = f'team {team} are rated: {ratings[team][0]} world wide with an ATR of {ratings[team][1]}'

    except KeyError:
        text = f'team not found'
    rating_label.configure(text=text)


def open_rate_team():
    root.withdraw()
    rate_window = ctk.CTk()
    rate_window.title("Rate Team")
    rate_window.geometry("600x600")

    menu_btn = ctk.CTkButton(rate_window, text="Menu", command=lambda: main_menu(rate_window))
    menu_btn.pack(pady=10, anchor="w", padx=10)

    label = ctk.CTkLabel(rate_window, text="Write the team you wish to rate", font=("Arial", 16))
    label.pack(pady=20)

    entry = ctk.CTkEntry(rate_window, placeholder_text="Enter team number")
    entry.pack(pady=10)

    rating_label = ctk.CTkLabel(rate_window, text="", font=("Arial", 14))
    rating_label.pack(pady=20)

    rate_btn = ctk.CTkButton(rate_window, text="Rate", command=lambda: rate_team(entry.get(), rating_label))
    rate_btn.pack(pady=10)

    rate_window.bind("<Return>", lambda event: rate_team(entry.get(), rating_label))
    rate_window.protocol("WM_DELETE_WINDOW", lambda: root.quit())
    rate_window.mainloop()


def open_window(title):
    root.destroy()
    new_window = ctk.CTk()
    new_window.title(title)
    new_window.geometry("600x600")

    menu_btn = ctk.CTkButton(new_window, text="Menu", command=lambda: main_menu(new_window))
    menu_btn.pack(pady=10, anchor="w", padx=10)

    label = ctk.CTkLabel(new_window, text=f"{title} Page", font=("Arial", 18))
    label.pack(pady=40)

    new_window.mainloop()


def main_menu(current_window=None):
    if current_window:
        current_window.withdraw()  # Hide the current window instead of destroying

    global root
    root = ctk.CTk()
    root.title("FRC AI Menu")
    root.geometry("600x600")

    frame = ctk.CTkFrame(root)
    frame.pack(expand=True, padx=20, pady=20)

    buttons = [
        ("Rate Team", lambda: open_rate_team()),
        ("Predict Event", lambda: open_window("Predict Event")),
        ("Create Match", lambda: open_create_match()),
        ("Make Event", lambda: open_window("Make Event")),
        ("Show All Ratings", lambda: open_window("Show All Ratings"))
    ]

    for text, command in buttons:
        btn = ctk.CTkButton(frame, text=text, command=command)
        btn.pack(pady=5, fill="x")

    root.protocol("WM_DELETE_WINDOW", lambda: root.quit())

    root.mainloop()


main_menu()
