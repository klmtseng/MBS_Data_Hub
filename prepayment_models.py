import numpy as np
import pandas as pd

def get_psa_cpr(month: int, psa_speed: float = 100.0) -> float:
    """
    Calculates the Conditional Prepayment Rate (CPR) based on the PSA model.

    Args:
        month: The age of the mortgage in months.
        psa_speed: The PSA speed (e.g., 100 for 100% PSA).

    Returns:
        The CPR for the given month and PSA speed.
    """
    if month <= 0:
        return 0.0

    cpr_base = 0.06  # 6% CPR is the baseline for 100% PSA

    if month <= 30:
        cpr = cpr_base * (month / 30.0)
    else:
        cpr = cpr_base

    return cpr * (psa_speed / 100.0)

def generate_psa_cashflows(
    balance: float,
    wac: float,
    wam: int,
    psa_speed: float = 100.0
) -> pd.DataFrame:
    """
    Generates a cash flow table for a mortgage pool based on the PSA model.

    Args:
        balance: The current balance of the mortgage pool.
        wac: The Weighted Average Coupon of the pool (as a decimal, e.g., 0.05 for 5%).
        wam: The Weighted Average Maturity of the pool in months.
        psa_speed: The PSA speed to assume for prepayments.

    Returns:
        A pandas DataFrame with the projected cash flows for each month.
    """
    cashflows = []

    monthly_interest_rate = wac / 12.0

    for month in range(1, wam + 1):
        if balance <= 0:
            break

        # Calculate monthly payment using the standard formula
        payment = balance * (monthly_interest_rate * (1 + monthly_interest_rate)**(wam - month + 1)) / \
                  ((1 + monthly_interest_rate)**(wam - month + 1) - 1)

        # 1. Interest Due for the month
        interest_due = balance * monthly_interest_rate

        # 2. Scheduled Principal
        scheduled_principal = payment - interest_due

        # 3. Prepayments
        cpr = get_psa_cpr(month, psa_speed)
        smm = 1 - (1 - cpr)**(1/12)  # Convert CPR to SMM (Single Monthly Mortality)
        prepayment = (balance - scheduled_principal) * smm

        # Total Principal and updating balance
        total_principal = scheduled_principal + prepayment

        cashflows.append({
            "Month": month,
            "Beginning Balance": balance,
            "Monthly Payment": payment,
            "Interest": interest_due,
            "Scheduled Principal": scheduled_principal,
            "Prepayment": prepayment,
            "Total Principal": total_principal,
            "Ending Balance": balance - total_principal,
            "CPR": cpr,
            "SMM": smm
        })

        balance -= total_principal

    return pd.DataFrame(cashflows)
