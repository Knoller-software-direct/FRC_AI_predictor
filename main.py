import json
import tkinter
import customtkinter

from team_rater import create_rating_file


def rate_team():

    try:
        with open("teams_rating_2024.json", "r") as file:
            ratings = json.load(file)
    except FileNotFoundError:
        create_rating_file("2024_statbotics_ratings.csv", "2024_statbotics_ratings.csv")
        with open("worlds_teams_2024.json", "r") as file:
            ratings = json.load(file)
    try:
        team = "frc" + team_field.get()
        rating.configure(text=f'team {team} are rated: {ratings[team][0]} world wide with a score of {ratings[team][1]}')
    except KeyError:
        rating.configure(text=f'team not found')

customtkinter.set_appearance_mode("System")
customtkinter.set_default_color_theme("blue")

app = customtkinter.CTk()
app.geometry("1080X1920")
app.title("FRC AI predictor")

#team rating label
title = customtkinter.CTkLabel(app, text="which team would you like to rate")
title.pack(padx=10, pady=10)

#team rating field
team = tkinter.StringVar()
team_field = customtkinter.CTkEntry(app, width=350, height=40, textvariable=team)
team_field.pack()

#rate button
rate_button = customtkinter.CTkButton(app, text="Rate", command=rate_team)
rate_button.pack()

#rating label
rating = customtkinter.CTkLabel(app, text="")
rating.pack(padx=10, pady=10)

app.mainloop()




