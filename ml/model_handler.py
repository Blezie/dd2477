import pickle
import os
from xgboost import XGBRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import json
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler


# def convert_json_to_df(json_data):
#     df = pd.json_normalize(json_data)
#     return df


def get_onehot_encoded_data(data, column):
    print("get_onehot_encoded_data", data[column].head())
    one_hot = pd.get_dummies(data[column].apply(pd.Series).stack()).groupby(level=0).sum()
    data = data.drop(columns=[column])
    return pd.concat([data, one_hot], axis=1)


class ModelHandler:
    model = None
    path = "../ml/models/"
    # scaler = StandardScaler()
    # pca = PCA()
    X_columns = None

    def __init__(self, model_type="XGB", prereviewed_data=None):
        self.get_model(model_type, prereviewed_data)

    def get_model(self, model_type, prereviewed_data=None):
        self.path = self.path + model_type

        if os.path.isfile(self.path + ".pkl"):
            print("Loading model")
            self.load_model()
        else:
            if model_type == "XGB":
                self.model = XGBRegressor(enable_categorical=True)
            elif model_type == "RF":
                self.model = RandomForestRegressor()
            elif model_type == "LR":
                self.model = LinearRegression()
            X, y = self.preprocess(prereviewed_data, training=True)
            self.train_model(X, y)
            self.save_model()

    def train_model(self, X, y):
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        score = self.model.score(X_test, y_test)
        print(f"Model score: {score}")

    def predict_rating(self, data):
        # print(data.dtypes)
        data, nan_indeces = self.preprocess(data)
        return self.model.predict(data), nan_indeces

    def save_model(self):

        with open(self.path + ".pkl", 'wb') as file:
            pickle.dump(self.model, file)
        with open(self.path + "_columns.pkl", 'wb') as file:
            pickle.dump(self.X_columns, file)

    def load_model(self):
        print("Loading model")
        print(self.path + ".pkl")
        with open(self.path + ".pkl", 'rb') as file:
            self.model = pickle.load(file)
            print("Model loaded")
        with open(self.path + "_columns.pkl", 'rb') as file:
            self.X_columns = pickle.load(file)

    # def preprocess_data(self, data, training=False):
    #     if training:
    #         self.scaler.fit(data)
    #         data = self.scaler.transform(data)
    #         self.pca.fit(data)
    #     else:
    #         data = self.scaler.transform(data)
    #     return self.pca.transform(data)

    def preprocess(self, data, training=False):
        # df = convert_json_to_df(data)
        df = pd.DataFrame(data)
        columns = ["genres", "averageRating", "numPages", "ratingsCount"]
        if training:
            columns.append("user_score")
        df = df[columns]
        dropped_indexes = df.index[df.isna().any(axis=1)].tolist()
        df.dropna(inplace=True)
        if df.empty:
            return None
        encoded = get_onehot_encoded_data(df, "genres")
        if training:
            y = encoded["user_score"]
            X = encoded.drop(columns=["user_score"])
            self.X_columns = X.columns
            return X, y
        else:
            encoded = encoded.reindex(columns=self.X_columns, fill_value=0)
            return encoded, dropped_indexes


if __name__ == "__main__":

    with open('./bookUserReviews.ndjson', 'r', encoding="utf-8") as file:
         # Read each line (JSON object) from the file
         json_objects = []
         for line in file.readlines():
             # Parse the JSON object
             data = json.loads(line)

             # Process the data as needed
             json_objects.append(data)

    model = ModelHandler("XGB", json_objects)

    # test = model.preprocess(json.loads(
    #     """{"genres": ["Fantasy", "Young Adult", "Fiction", "Magic", "Audiobook", "Adventure", "Science Fiction 
    #     Fantasy"], "numPages": 200, "averageRating": 1.58 }"""
    # ))
    # res = model.predict_rating(test)
    # print(res) 
