import numpy as np
import pandas as pd
from scipy.sparse.linalg import svds

class Recommender:
    def __init__(self, visit_history):
        self.data = pd.DataFrame(visit_history, columns=['user_id', 'yelp_id', 'satisfaction'])

        R_df = pd.pivot_table(self.data, index='user_id', columns='yelp_id', values='satisfaction').fillna(0)
        R = R_df.as_matrix()
        user_satisfactions_mean = np.mean(R, axis=1)
        R_demeaned = R - user_satisfactions_mean.reshape(-1, 1)

        U, sigma, Vt = svds(R_demeaned, k=3)
        sigma = np.diag(sigma)
        all_user_predicted_ratings = np.dot(np.dot(U, sigma), Vt) + user_satisfactions_mean.reshape(-1, 1)
        self.predictions_df = pd.DataFrame(all_user_predicted_ratings, index=R_df.index.values, columns=R_df.columns)


    def recommend_visit_with_user_id(self, user_id, count = 5):
        rated_by_user = np.array(self.data[self.data['user_id'] == user_id]['yelp_id'])
        if rated_by_user:
            predictions = self.predictions_df.loc[user_id].sort_values(ascending=False).index.values
            return list(set(predictions) - set(rated_by_user))[:count]

          # TODO: recommend places near user.