This is the AI predictor I made to prove a point about the FIRST Robotics Competition.

For those who don't know, the FIRST Robotics Competition or FRC for short is a robotics competition played by teams of high school students. Each team builds a robot based on this year's game. Each match 3 robots form an alliance and play against another alliance 
of 3 teams, during the match robots score points by completing tasks based on that year's challenge and the alliance that scores the most points wins the match.

The veteran participents of the FRC competition know that there are good robots and bad robots, from the veterans those who know the game side of the competiton really well after watching the diffrent robots play a few matches can predict which alliance will win
in the next match and which will lose and from those the extremely skilled who knows the teams really well can predict with shockingly high accuracy who will win and who will lose before seeing even a single robot play. 

The goal of this project was to prove that most of the teams' fates are sealed even before the season had started and the challange was revealed. To do that we need to make a prediction module of a match without knowing the robots.

There are some projects with the same aim but the most influential and popular one is Statbotics.io

Statbotics takes the teams and gives them an inital rating called EPA, then it uses a very clever adaptation of the Elo module to update the rating of the teams after each match. This solution is very elegant and it gives a fair and somewhat accurate 
evaluation of each team's strength while having a 72% accuracy in predictions but it doesn't fulfill the goal of this project as Statbotics achives their high prediction rate by updating their rating after every match meaning they don't predict the whole
season with a 72% accuracy they predict the next match with 72% accuracy which we can not have.

There is a wonderful website call The Blue Alliance which is a database of all the matches ever played in FRC, not only does it have every match but it also has more data about the competiton itself, by using this data we can create measure teams on multiple
metrics and create the following JSON 

     "team_key": {
        "rookie_year": int,
        "epa": float,
        "winrate": 0 <= x <= 1,
        "average_rank": float,
        "average_pick": float,
        "number_of_events": int,
        "average_match_score": 0 <= x <= 1,
        "worlds_rate": 0 <= x <= 1,
        "number_of_matches": int,
        "average_opponent_epa": float,
        "average_alliance_epa": float
      }
      
here is a short breakdown of every stat and it's importance:

* rookie_year: the year in which the team was founded, on average older teams are better
* epa: the ranking Statbotics gave the team based on their last match from last season
* winrate: out of all the matches the team played in the last 5 seasons how many did they win
* average_rank: in FRC competition at every match a win gives a certain amount of Ranking Points (RP) and during the match completing spacial missions gains additional RP, by the end of the qualification matches the teams are ranked by their RP teams who usually
  end up higher in the ranking not only won more matches but also scored more RP during the matches proving they are better
* average_pick: after the qualification matches are done the highest ranked teams gets to pick their alliances for the finals, as such the better teams get picked first so lower is better
* number_of_events: the amount of competitions or "events" a team played in the last 5 years. The more a team played the better trained they are, also playing a lot of events means they got to the next stages of the competition
* average_match_score: Each year has a highest scored match, based on that each match score is calculated as score/max score, that way we can normalize all the scores from all the diffrent challenges with diffrent scoring and calculate the avergae, better teams
  score more points on an average match even if they lose it
* worlds_rate: there are two diffrent systems to get to the world championship, in both it's very hard to get a ticket as such the more a team got to world in the past 5 seasons the better
* number_of_matches: the amount of matches a team played in the last five years, more matches means the team reached higher in the finals stage of the competition and also more matches = more training which makes teams better
* average_opponent_epa: the average EPA of a robot in the apposing alliance, winning against strong teams means the team is strong
* average_alliance_epa: the average EPA of the robots in the team's alliance, winning with weaker alliance partners means the team is strong

Because teams do not stay the same every year as students leave and join every year, mentors leave and join and so on there was a need for a cut off point as some of the older data is just not relevent anymore. As such we decided that the most distant season we 
will take data from is 2018 as for reasons which are not relevent for the code itself we belive is the oldest data we can still use

Using this structure we can take the data from the matches played between 2018 and 2023 to train a neural network to predict who will win, using the keras sequantial module with two hidden layers we trained the module and let it predict the outcome of the matches
in 2024. It got an accuracy of 74% meaning that in the season of 2024 3/4 matches were over the moment the match schedule was released.

Using this prediction power we made some useful features: 
* We created an "average team" which has the average stat of every metric and made the AI give a prediction of how each alliance with 3 average teams will fair against an alliance of 3 times every team which gave us a rating of all the teams
* We made a function that takes teams from an event and rans a simulation of said event giving predictions on the ranking of the teams by the end of the qualification matches

For those intrested in trying the code themselves here are the discription of each scripts:
event_fetcher: gets all the relevent data from the all the events, takes a long time
team_fetcher: takes the data from the events and Statbotics to create the teams JSON
data_preperations: takes the data from the teams and events JSONs and change it to .npy files the AI can use
ai_creator: creates a module based on the data that was prepared and saves it to file
event_maker: creates simulations of events based on the teams that will play them and prints the resualts
team_rater: rates all the teams based on the average team


As I said the reason I made this project is to prove a point so here it is: teams repeat their performances, good teams mostly remain good and bad teams remain bad. For a team to change their position in the competition they can't keep their old ways, every team by
the end of the season have a meeting in which they discuss what went well and what didn't to get better for the next year but most of the time very little changes are made and as such the team gets only marginally better and since all the teams gets marginally 
better they end up effectively in the same place they started. That is not to say that teams should just give up but to say that teams which aims to beat the competition needs to take it as seriously as possible and not revert to old patterns

