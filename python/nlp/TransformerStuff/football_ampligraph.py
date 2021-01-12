import numpy as np
import pandas as pd
import ampligraph

ampligraph.__version__

#import requests
#url = 'https://ampligraph.s3-eu-west-1.amazonaws.com/datasets/football_graph.csv'
#open('football_results.csv', 'wb').write(requests.get(url).content)

df = pd.read_csv("/home/stefan/PycharmProjects/Distinctiopus4/football_results.csv").sort_values("date")

print (df.isna().sum())

df = df.dropna()
df["train"] = df.date < "2014-01-01"
print (df.train.value_counts())

# Entities naming
df["match_id"] = df.index.values.astype(str)
df["match_id"] =  "Match" + df.match_id
df["city_id"] = "City" + df.city.str.title().str.replace(" ", "")
df["country_id"] = "Country" + df.country.str.title().str.replace(" ", "")
df["home_team_id"] = "Team" + df.home_team.str.title().str.replace(" ", "")
df["away_team_id"] = "Team" + df.away_team.str.title().str.replace(" ", "")
df["tournament_id"] = "Tournament" + df.tournament.str.title().str.replace(" ", "")
df["neutral"] = df.neutral.astype(str)

triples = []
for _, row in df[df["train"]].iterrows():
    # Home and away information
    home_team = (row["home_team_id"], "isHomeTeamIn", row["match_id"])
    away_team = (row["away_team_id"], "isAwayTeamIn", row["match_id"])

    # Match results
    if row["home_score"] > row["away_score"]:
        score_home = (row["home_team_id"], "winnerOf", row["match_id"])
        score_away = (row["away_team_id"], "loserOf", row["match_id"])
    elif row["home_score"] < row["away_score"]:
        score_away = (row["away_team_id"], "winnerOf", row["match_id"])
        score_home = (row["home_team_id"], "loserOf", row["match_id"])
    else:
        score_home = (row["home_team_id"], "draws", row["match_id"])
        score_away = (row["away_team_id"], "draws", row["match_id"])
    home_score = (row["match_id"], "homeScores", np.clip(int(row["home_score"]), 0, 5))
    away_score = (row["match_id"], "awayScores", np.clip(int(row["away_score"]), 0, 5))

    # Match characteristics
    tournament = (row["match_id"], "inTournament", row["tournament_id"])
    city = (row["match_id"], "inCity", row["city_id"])
    country = (row["match_id"], "inCountry", row["country_id"])
    neutral = (row["match_id"], "isNeutral", row["neutral"])
    year = (row["match_id"], "atYear", row["date"][:4])

    triples.extend((home_team, away_team, score_home, score_away,
                    tournament, city, country, neutral, year, home_score, away_score))

triples_df = pd.DataFrame(triples, columns=["subject", "predicate", "object"])
triples_df[(triples_df.subject=="Match3129") | (triples_df.object=="Match3129")]

from ampligraph.evaluation import train_test_split_no_unseen

X_train, X_valid = train_test_split_no_unseen(np.array(triples), test_size=10000)

print('Train set size: ', X_train.shape)
print('Test set size: ', X_valid.shape)

from ampligraph.latent_features import ComplEx

import os
from ampligraph.utils import save_model, restore_model

import tensorflow as tf
tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
from ampligraph.evaluation import evaluate_performance

ke_model_path = "./models/football_ke.amplimodel"
if not os.path.isfile(ke_model_path):
    model = ComplEx(batches_count=50,
                    epochs=1,
                    k=1,
                    eta=20,
                    optimizer='adam',
                    optimizer_params={'lr':1e-3},
                    loss='multiclass_nll',
                    regularizer='LP',
                    regularizer_params={'p':3, 'lambda':1e-5},
                    seed=0,
                    verbose=True)


    print ("Training...")
    model.fit(X_train)
    save_model(model, model_name_path=ke_model_path)

    filter_triples = np.concatenate((X_train, X_valid))
else:
    model = restore_model(model_name_path=ke_model_path)

from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from adjustText import adjust_text
from incf.countryutils import transformations

print("Extracting Embeddings..")

id_to_name_map = {**dict(zip(df.home_team_id, df.home_team)), **dict(zip(df.away_team_id, df.away_team))}

teams = pd.concat((df.home_team_id[df["train"]], df.away_team_id[df["train"]])).unique()
team_embeddings = dict(zip(teams, model.get_embeddings(teams)))


embeddings_2d = PCA(n_components=2).fit_transform(np.array([i for i in team_embeddings.values()]))

print (embeddings_2d)
first_embeddings = list(team_embeddings.values())[0]
print (first_embeddings)
print (first_embeddings.shape)
print (embeddings_2d.shape)
from ampligraph.discovery import find_clusters
from sklearn.cluster import KMeans

print("Clustering..")

clustering_algorithm = KMeans(n_clusters=6, n_init=50, max_iter=500, random_state=0)
clusters = find_clusters(teams, model, clustering_algorithm, mode='entity')

print (clusters)
print("Visualize..")

def cn_to_ctn(country):
    try:
        return transformations.cn_to_ctn(id_to_name_map[country])
    except KeyError:
        return "unk"

plot_df = pd.DataFrame({"teams": teams,
                        "embedding1": embeddings_2d[:, 0],
                        "embedding2": embeddings_2d[:, 1],
                        "continent": pd.Series(teams).apply(cn_to_ctn),
                        "cluster": "cluster" + pd.Series(clusters).astype(str)})

top20teams = ["TeamBelgium", "TeamFrance", "TeamBrazil", "TeamEngland", "TeamPortugal", "TeamCroatia", "TeamSpain",
              "TeamUruguay", "TeamSwitzerland", "TeamDenmark", "TeamArgentina", "TeamGermany", "TeamColombia",
              "TeamItaly", "TeamNetherlands", "TeamChile", "TeamSweden", "TeamMexico", "TeamPoland", "TeamIran"]

def plot_clusters(hue):
    print(hue)

    np.random.seed(0)
    plt.figure(figsize=(12, 12))
    plt.title("{} embeddings".format(hue).capitalize())
    ax = sns.scatterplot(data=plot_df[plot_df.continent!="unk"], x="embedding1", y="embedding2", hue=hue)
    texts = []
    for i, point in plot_df.iterrows():
        if point["teams"] in top20teams or np.random.random() < 0.1:
            texts.append(plt.text(point['embedding1']+0.02, point['embedding2']+0.01, str(point["teams"])))
    adjust_text(texts)
    plt.show()

plot_clusters("continent")


plot_clusters("cluster")


from sklearn import metrics
metrics.adjusted_rand_score(plot_df.continent, plot_df.cluster)

df["results"] = (df.home_score > df.away_score).astype(int) + \
                (df.home_score == df.away_score).astype(int)*2 + \
                (df.home_score < df.away_score).astype(int)*3 - 1

df.results.value_counts(normalize=True)


def get_features_target(mask):
    def get_embeddings(team):
        return team_embeddings.get(team, np.full(list(team_embeddings.values())[0].shape[0], np.nan))

    X = np.hstack((np.vstack(df[mask].home_team_id.apply(get_embeddings).values),
                   np.vstack(df[mask].away_team_id.apply(get_embeddings).values)))
    y = df[mask].results.values
    return X, y

clf_X_train, y_train = get_features_target((df["train"]))
clf_X_test, y_test = get_features_target((~df["train"]))

clf_X_train.shape, clf_X_test.shape

np.isnan(clf_X_test).sum()/clf_X_test.shape[1]

from xgboost import XGBClassifier

clf_model = XGBClassifier(n_estimators=550, max_depth=5, objective="multi:softmax")

clf_model.fit(clf_X_train, y_train)

print (df[~df["train"]].results.value_counts(normalize=True))

print (metrics.accuracy_score(y_test, clf_model.predict(clf_X_test)))




