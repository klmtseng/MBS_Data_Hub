import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

class StatisticalPrepaymentModel:
    """
    A simple statistical prepayment model using linear regression.
    """
    def __init__(self):
        self.model = LinearRegression()
        self.features = ['refinance_incentive', 'seasonality', 'hpa']
        self.target = 'smm'
        self.is_trained = False

    def train(self, data_path: str):
        """
        Trains the linear regression model on the provided data.

        Args:
            data_path: The path to the CSV file containing the training data.
        """
        try:
            df = pd.read_csv(data_path)
            X = df[self.features]
            y = df[self.target]

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

            self.model.fit(X_train, y_train)
            self.is_trained = True

            # Return the score for display purposes
            return self.model.score(X_test, y_test)

        except FileNotFoundError:
            raise Exception(f"Training data not found at {data_path}")
        except Exception as e:
            raise Exception(f"An error occurred during training: {e}")

    def predict_smm(self, features: pd.DataFrame) -> float:
        """
        Predicts the SMM for a given set of features.

        Args:
            features: A DataFrame with the same features used for training.

        Returns:
            The predicted SMM.
        """
        if not self.is_trained:
            raise Exception("Model has not been trained yet.")

        prediction = self.model.predict(features)
        return prediction[0]
