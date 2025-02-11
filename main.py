import json
import re
import tkinter
from tkinter import ttk
import customtkinter as ctk

from ai_predictor import predict_match
from event_maker import simulate_event
from team_rater import create_rating_file

with open("teams.json", "r") as file:
    all_teams = json.load(file)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def result_label_update(red_teams, blue_teams):
    red_alliance = [entry.get().strip() for entry in red_teams]
    blue_alliance = [entry.get().strip() for entry in blue_teams]
    for i in range(3):
        red_alliance[i] = "frc" + red_alliance[i]
        blue_alliance[i] = "frc" + blue_alliance[i]

    predicted_winner, confidence = predict_match(red_alliance, blue_alliance)
    result_label.configure(
        text=f'{predicted_winner} is predicted to win with {"{:.2f}".format((float(confidence) * 100))}% chance')


def open_create_match():
    root.withdraw()
    match_window = ctk.CTk()
    match_window.title("Pick Teams for the Match")
    match_window.geometry("500x350")

    menu_btn = ctk.CTkButton(match_window, text="Main Menu", command=lambda: main_menu(match_window))
    menu_btn.pack(pady=10, anchor="w", padx=10)

    title_label = ctk.CTkLabel(match_window, text="Pick Teams for the Match", font=("Arial", 18, "bold"))
    title_label.pack(pady=10)

    def validate_entries():
        all_filled = all(entry.get().strip() for entry in red_teams + blue_teams)
        predict_button.configure(state="normal" if all_filled else "disabled")

    red_label = ctk.CTkLabel(match_window, text="Red Alliance", font=("Arial", 16))
    red_label.pack(pady=5)

    red_frame = ctk.CTkFrame(match_window)
    red_frame.pack(pady=5)
    red_teams = []
    for i in range(3):
        red_team_entry = ctk.CTkEntry(red_frame, placeholder_text=f"Red Team {i + 1}", width=100)
        red_team_entry.pack(side="left", padx=5)
        red_team_entry.bind("<KeyRelease>", lambda event: validate_entries())
        red_teams.append(red_team_entry)

    blue_label = ctk.CTkLabel(match_window, text="Blue Alliance", font=("Arial", 16))
    blue_label.pack(pady=10)

    blue_frame = ctk.CTkFrame(match_window)
    blue_frame.pack(pady=5)
    blue_teams = []
    for i in range(3):
        blue_team_entry = ctk.CTkEntry(blue_frame, placeholder_text=f"Blue Team {i + 1}", width=100)
        blue_team_entry.pack(side="left", padx=5)
        blue_team_entry.bind("<KeyRelease>", lambda event: validate_entries())
        blue_teams.append(blue_team_entry)

    predict_button = ctk.CTkButton(match_window, text="Predict", state="disabled",
                                   command=lambda: result_label_update(red_teams, blue_teams))
    predict_button.pack(pady=20)

    global result_label
    result_label = ctk.CTkLabel(match_window, text="", font=("Arial", 14))
    result_label.pack(pady=10)

    match_window.protocol("WM_DELETE_WINDOW", lambda: root.quit())
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

    menu_btn = ctk.CTkButton(rate_window, text="Main Menu", command=lambda: main_menu(rate_window))
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


def open_make_event():
    root.withdraw()
    make_event_window = ctk.CTk()
    make_event_window.title("Predict Event")
    make_event_window.geometry("600x600")

    menu_btn = ctk.CTkButton(make_event_window, text="Main Menu", command=lambda: main_menu(make_event_window))
    menu_btn.pack(pady=10, anchor="w", padx=10)

    title = ctk.CTkLabel(make_event_window,
                         text="Write the list of the teams you wish to play an event\n the list must be at least 6 teams long and comma separated",
                         font=("Arial", 16))
    title.pack(pady=20)

    event_text = ctk.CTkTextbox(make_event_window, width=580, height=200)  # Large Textbox
    event_text.pack(fill="both", expand=True, padx=10, pady=5)

    error_label = ctk.CTkLabel(make_event_window, text="", text_color="red", font=("Arial", 12))
    error_label.pack(pady=5)

    def validate_event_text(text):
        text = text.replace(" ", "")
        pattern = r"^\d{1,5}(,\d{1,5})*$"
        if not bool(re.fullmatch(pattern, text)):
            return False, "invalid teams list, the format is 1111,2222,3333,4444,5555,6666"
        teams = [f"frc{num}" for num in text.replace(" ", "").split(",")]
        if len(teams) < 6:
            return False, "not enough teams"
        if len(teams) != len(set(teams)):
            return False, "repetition of team"

        for team in teams:
            if team not in all_teams:
                return False, f'team {team[3:]} not found'
        return True, ""

    def create_event_data(text):
        teams = [f"frc{num}" for num in text.replace(" ", "").split(",")]
        # event table format: [rp_average, average_rank, top_rank, bottom_rank, median_rank]
        return simulate_event(teams)

    def open_data_window(data):
        table_window = tkinter.Toplevel()
        table_window.title("Event Data Table")
        table_window.geometry("800x400")

        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 14))
        style.configure("Treeview.Heading", font=("Arial", 14, "bold"))
        frame = ttk.Frame(table_window)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        tree_scroll = ttk.Scrollbar(frame, orient="vertical")
        tree_scroll.pack(side="right", fill="y")

        columns = (
            "Predicted Rank", "Team Key", "Average RP", "Mean Rank", "5th Percentile", "95th Percentile", "Median Rank")
        tree = ttk.Treeview(frame, columns=columns, show="headings", yscrollcommand=tree_scroll.set)

        tree_scroll.config(command=tree.yview)

        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)

        tree.pack(fill="both", expand=True)

        sorted_data = sorted(data.items(), key=lambda item: item[1][0], reverse=True)
        for rank, (team_key, values) in enumerate(sorted_data, start=1):
            tree.insert("", "end", values=(rank, team_key, *values))

        def find_in_table(event=None):
            search_query = search_entry.get().strip().lower()
            for item in tree.get_children():
                values = tree.item(item, "values")
                if any(search_query in str(value).lower() for value in values):
                    tree.selection_set(item)
                    tree.see(item)
                    break

        search_frame = ttk.Frame(table_window)
        search_frame.pack(fill="x", padx=10, pady=5)

        search_label = ttk.Label(search_frame, text="Search:")
        search_label.pack(side="left", padx=5)

        search_entry = ttk.Entry(search_frame)
        search_entry.pack(side="left", fill="x", expand=True, padx=5)

        search_button = ttk.Button(search_frame, text="Find", command=find_in_table)
        search_button.pack(side="left", padx=5)

        table_window.bind("<Control-f>", find_in_table)
        table_window.mainloop()

    def adjust_textbox_height(_):
        lines = event_text.get("1.0", "end").count("\n")
        new_height = min(400, max(200, lines * 20))
        event_text.configure(height=new_height)

    event_text.bind("<KeyRelease>", adjust_textbox_height)

    def make_event():
        event_content = event_text.get("1.0", "end").strip()

        valid, error = validate_event_text(event_content)
        if not valid:
            error_label.configure(text=error)
            return
        else:
            error_label.configure(text="")
        event_data = create_event_data(event_content)

        open_data_window(event_data)

    make_event_button = ctk.CTkButton(make_event_window, text="Make Event", command=make_event)
    make_event_button.pack(pady=10)

    make_event_window.protocol("WM_DELETE_WINDOW", lambda: root.quit())
    make_event_window.mainloop()


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
        current_window.withdraw()

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
        ("Make Event", lambda: open_make_event()),
        ("Show All Ratings", lambda: open_window("Show All Ratings"))
    ]

    for text, command in buttons:
        btn = ctk.CTkButton(frame, text=text, command=command)
        btn.pack(pady=5, fill="x")

    root.protocol("WM_DELETE_WINDOW", lambda: root.quit())

    root.mainloop()


main_menu()
