import pandas as pd
import numpy as np

def generate_synthetic_data(num_months: int = 240, filename: str = "synthetic_loan_data.csv"):
    """
    Generates a synthetic dataset for prepayment modeling and saves it to a CSV file.

    Args:
        num_months: The number of months of data to generate.
        filename: The name of the CSV file to save the data to.
    """
    np.random.seed(42)

    # --- Generate Features ---
    # 1. Refinance Incentive (as a random walk)
    refi_incentive = np.random.randn(num_months).cumsum() * 0.1

    # 2. Seasonality (sine wave to represent summer/winter effects)
    seasonality = np.sin(np.linspace(0, (num_months / 12) * 2 * np.pi, num_months))

    # 3. Housing Price Appreciation (HPA) (as another random walk)
    hpa = np.random.randn(num_months).cumsum() * 0.05 + 2.0 # Start with a positive trend

    # --- Generate Target Variable (SMM) ---
    # SMM is a function of the features plus some noise
    smm = 0.01 + \
          0.02 * refi_incentive + \
          0.005 * seasonality + \
          0.002 * hpa + \
          np.random.randn(num_months) * 0.005 # Noise

    # Clip SMM to be between 0 and 1
    smm = np.clip(smm, 0, 1)

    # --- Create DataFrame ---
    df = pd.DataFrame({
        'month': range(1, num_months + 1),
        'refinance_incentive': refi_incentive,
        'seasonality': seasonality,
        'hpa': hpa,
        'smm': smm
    })

    # --- Save to CSV ---
    df.to_csv(filename, index=False)
    print(f"Synthetic data generated and saved to {filename}")

if __name__ == "__main__":
    generate_synthetic_data()
