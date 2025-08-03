import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from collections import defaultdict
from feature_engineering import calculate_spread
from prepayment_models import generate_psa_cashflows
from statistical_model import StatisticalPrepaymentModel

# --- FRED Series Codes ---
FRED_SERIES = {
    "10-Year Treasury (DGS10)": "DGS10",
    "2-Year Treasury (DGS2)": "DGS2",
    "30-Year Mortgage (MORTGAGE30US)": "MORTGAGE30US",
    "15-Year Mortgage (MORTGAGE15US)": "MORTGAGE15US",
    "Case-Shiller HPI (CSUSHPINSA)": "CSUSHPINSA"
}

class MBSDataHubApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Project 1: MBS Data Hub")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")

        self.data_df = None
        self.stat_model = StatisticalPrepaymentModel()

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_data_hub_tab()
        self.create_prepayment_modeler_tab()

    def create_data_hub_tab(self):
        data_hub_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(data_hub_frame, text="Data Hub")
        # ... (rest of the data hub tab creation code is the same)
        # --- Controls Frame (Left Side) ---
        controls_frame = ttk.LabelFrame(data_hub_frame, text="Controls", padding="10")
        controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # --- Date Entry ---
        date_frame = ttk.Frame(controls_frame)
        date_frame.pack(fill=tk.X, pady=10)
        ttk.Label(date_frame, text="Start Date (YYYY-MM-DD):").pack(pady=(0, 5))
        self.start_date_entry = ttk.Entry(date_frame)
        self.start_date_entry.pack(fill=tk.X)
        self.start_date_entry.insert(0, "2010-01-01")

        ttk.Label(date_frame, text="End Date (YYYY-MM-DD):").pack(pady=(10, 5))
        self.end_date_entry = ttk.Entry(date_frame)
        self.end_date_entry.pack(fill=tk.X)
        self.end_date_entry.insert(0, datetime.now().strftime('%Y-%m-%d'))

        # --- Series Selection ---
        series_frame = ttk.LabelFrame(controls_frame, text="Select Data Series & Plot Group", padding="10")
        series_frame.pack(fill=tk.X, pady=10)
        self.series_vars = {}
        self.series_groups = {}

        header_frame = ttk.Frame(series_frame)
        header_frame.pack(fill=tk.X, anchor="w", pady=(0,5))
        ttk.Label(header_frame, text="Series", font="-weight bold").pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Label(header_frame, text="Group", font="-weight bold").pack(side=tk.RIGHT, padx=(10,0))

        for i, (name, code) in enumerate(FRED_SERIES.items()):
            row_frame = ttk.Frame(series_frame)
            row_frame.pack(fill=tk.X, anchor="w", pady=2)

            var = tk.BooleanVar(value=True)
            self.series_vars[code] = var
            cb = ttk.Checkbutton(row_frame, text=name, variable=var)
            cb.pack(side=tk.LEFT, expand=True, fill=tk.X)

            group_entry = ttk.Entry(row_frame, width=5)
            if 'Treasury' in name or 'Mortgage' in name:
                group_entry.insert(0, "1")
            else:
                group_entry.insert(0, str(i + 2))
            group_entry.pack(side=tk.RIGHT)
            self.series_groups[code] = group_entry

        # --- Action Buttons ---
        buttons_frame = ttk.Frame(controls_frame)
        buttons_frame.pack(fill=tk.X, pady=20, side=tk.BOTTOM)

        self.fetch_button = ttk.Button(buttons_frame, text="Fetch & Plot Data", command=self.fetch_and_plot)
        self.fetch_button.pack(fill=tk.X, pady=5)

        self.spread_button = ttk.Button(buttons_frame, text="Plot Mortgage-Treasury Spread", command=self.plot_spread)
        self.spread_button.pack(fill=tk.X, pady=5)

        self.save_button = ttk.Button(buttons_frame, text="Save Data to CSV", command=self.save_to_csv)
        self.save_button.pack(fill=tk.X, pady=5)

        # --- Plot Frame (Right Side) ---
        plot_frame = ttk.LabelFrame(data_hub_frame, text="Data Visualization", padding="10")
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig = plt.Figure(facecolor="#f0f0f0")
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        ax = self.fig.add_subplot(111)
        ax.set_title("Select data and click 'Fetch & Plot'")
        ax.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()


    def create_prepayment_modeler_tab(self):
        modeler_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(modeler_frame, text="Prepayment Modeler")

        # --- PSA Modeler (Top) ---
        psa_frame = ttk.LabelFrame(modeler_frame, text="PSA Model", padding="10")
        psa_frame.pack(fill=tk.X, pady=5)

        # Inputs
        ttk.Label(psa_frame, text="Balance:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.balance_entry = ttk.Entry(psa_frame)
        self.balance_entry.grid(row=0, column=1, sticky=tk.EW, pady=2)
        self.balance_entry.insert(0, "1000000")

        ttk.Label(psa_frame, text="WAC (%):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.wac_entry = ttk.Entry(psa_frame)
        self.wac_entry.grid(row=1, column=1, sticky=tk.EW, pady=2)
        self.wac_entry.insert(0, "5.0")

        ttk.Label(psa_frame, text="WAM (Months):").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.wam_entry = ttk.Entry(psa_frame)
        self.wam_entry.grid(row=2, column=1, sticky=tk.EW, pady=2)
        self.wam_entry.insert(0, "360")

        ttk.Label(psa_frame, text="PSA Speed:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.psa_entry = ttk.Entry(psa_frame)
        self.psa_entry.grid(row=3, column=1, sticky=tk.EW, pady=2)
        self.psa_entry.insert(0, "100")

        # Button
        self.run_psa_button = ttk.Button(psa_frame, text="Run PSA Model", command=lambda: self.run_prepayment_model(model_type='psa'))
        self.run_psa_button.grid(row=4, column=0, columnspan=2, pady=10)

        # --- Statistical Modeler (Middle) ---
        stat_frame = ttk.LabelFrame(modeler_frame, text="Statistical Model", padding="10")
        stat_frame.pack(fill=tk.X, pady=5)

        self.train_button = ttk.Button(stat_frame, text="Train Model", command=self.train_stat_model)
        self.train_button.pack(pady=5)

        self.model_score_label = ttk.Label(stat_frame, text="Model Score: Not Trained")
        self.model_score_label.pack(pady=5)

        self.run_stat_button = ttk.Button(stat_frame, text="Run Statistical Model", command=lambda: self.run_prepayment_model(model_type='stat'), state=tk.DISABLED)
        self.run_stat_button.pack(pady=5)

        # --- Cash Flow Table (Bottom) ---
        table_frame = ttk.LabelFrame(modeler_frame, text="Cash Flow Projections", padding="10")
        table_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.tree = ttk.Treeview(table_frame)
        self.tree.pack(fill=tk.BOTH, expand=True)

    def train_stat_model(self):
        try:
            score = self.stat_model.train('synthetic_loan_data.csv')
            self.model_score_label.config(text=f"Model Score (R^2): {score:.4f}")
            self.run_stat_button.config(state=tk.NORMAL)
            messagebox.showinfo("Training Complete", "The statistical model has been successfully trained.")
        except Exception as e:
            messagebox.showerror("Training Error", f"Failed to train model: {e}")

    def run_prepayment_model(self, model_type: str):
        try:
            balance = float(self.balance_entry.get())
            wac = float(self.wac_entry.get()) / 100.0
            wam = int(self.wam_entry.get())

            if model_type == 'psa':
                psa_speed = float(self.psa_entry.get())
                cashflows_df = generate_psa_cashflows(balance, wac, wam, psa_speed)
            elif model_type == 'stat':
                # For the stat model, we need to generate features for each month
                # This is a simplification; a real model would use a scenario for future rates, HPA, etc.
                features_df = pd.DataFrame({
                    'refinance_incentive': [0.5] * wam, # Assuming a constant refi incentive for simplicity
                    'seasonality': [0.0] * wam,
                    'hpa': [2.0] * wam
                })

                smm_predictions = self.stat_model.model.predict(features_df)

                # We need a cashflow generation function that accepts a vector of SMMs
                # For now, we will just use the first predicted smm for all months
                # This is a simplification to get the UI working
                cashflows_df = self.generate_stat_model_cashflows(balance, wac, wam, smm_predictions)

            self.display_cashflows(cashflows_df)

        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numbers in all fields.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def generate_stat_model_cashflows(self, balance, wac, wam, smm_vector):
        # This is a simplified cashflow generator for the stat model
        # A more robust implementation is needed
        cashflows = []
        monthly_interest_rate = wac / 12.0
        for month_idx, smm in enumerate(smm_vector):
            if balance <= 0: break
            payment = balance * (monthly_interest_rate * (1 + monthly_interest_rate)**(wam - month_idx)) / \
                      ((1 + monthly_interest_rate)**(wam - month_idx) - 1)
            interest_due = balance * monthly_interest_rate
            scheduled_principal = payment - interest_due
            prepayment = (balance - scheduled_principal) * smm
            total_principal = scheduled_principal + prepayment
            cashflows.append({
                "Month": month_idx + 1, "Beginning Balance": balance, "Interest": interest_due,
                "Scheduled Principal": scheduled_principal, "Prepayment": prepayment,
                "Total Principal": total_principal, "Ending Balance": balance - total_principal, "SMM": smm
            })
            balance -= total_principal
        return pd.DataFrame(cashflows)

    def display_cashflows(self, df):
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = list(df.columns)
        self.tree["show"] = "headings"
        for col in df.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=80)
        for index, row in df.iterrows():
            self.tree.insert("", "end", values=list(row.round(2)))

    # ... (rest of the methods are the same: fetch_data, fetch_and_plot, etc.)
    def fetch_data(self):
        """
        Fetches selected data series from FRED based on user input.
        Returns True on success, False on failure.
        """
        selected_codes = [code for code, var in self.series_vars.items() if var.get()]
        if not selected_codes:
            messagebox.showwarning("No Selection", "Please select at least one data series.")
            return False

        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()

        try:
            self.data_df = web.DataReader(selected_codes, 'fred', start_date, end_date)
            self.data_df.ffill(inplace=True)
            messagebox.showinfo("Success", f"Successfully fetched {len(selected_codes)} series.")
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data: {e}")
            self.data_df = None
            return False

    def fetch_and_plot(self):
        """
        Wrapper function to fetch data and then plot it.
        """
        if self.fetch_data():
            self.plot_all_data()

    def plot_all_data(self):
        """
        Plots all columns from the fetched DataFrame, grouping them into subplots
        based on the user-defined group numbers.
        """
        if self.data_df is None or self.data_df.empty:
            messagebox.showwarning("No Data", "No data to plot. Please fetch data first.")
            return

        plot_groups = defaultdict(list)
        for code, var in self.series_vars.items():
            if var.get() and code in self.data_df.columns:
                group_key = self.series_groups[code].get().strip()
                if not group_key:
                    group_key = code
                plot_groups[group_key].append(code)

        self.fig.clear()

        num_groups = len(plot_groups)
        if num_groups == 0:
            ax = self.fig.add_subplot(111)
            ax.set_title("No data columns to plot.")
            self.canvas.draw()
            return

        axes = self.fig.subplots(nrows=num_groups, ncols=1, sharex=True)
        if num_groups == 1:
            axes = [axes]

        self.fig.suptitle("Selected Economic Data from FRED", fontsize=14)

        for i, (group_name, codes_in_group) in enumerate(plot_groups.items()):
            ax = axes[i]
            for code in codes_in_group:
                series_name = next((name for name, c in FRED_SERIES.items() if c == code), code)
                self.data_df[code].plot(ax=ax, label=series_name)

            ax.set_ylabel("Value")
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(loc='best')

        axes[-1].set_xlabel("Date")

        self.fig.tight_layout(rect=[0, 0, 1, 0.96])
        self.canvas.draw()

    def plot_spread(self):
        """
        Calculates and plots the spread between the 30-Year Mortgage Rate
        and the 10-Year Treasury yield on a single, dedicated plot.
        """
        required_codes = ['MORTGAGE30US', 'DGS10']
        start_date = self.start_date_entry.get()
        end_date = self.end_date_entry.get()

        try:
            spread_df = web.DataReader(required_codes, 'fred', start_date, end_date)
            spread_df.ffill(inplace=True)

            spread_df = calculate_spread(spread_df, 'MORTGAGE30US', 'DGS10')
            spread_name = 'MORTGAGE30US-DGS10_Spread'

            self.fig.clear()
            ax = self.fig.add_subplot(111)

            spread_df[spread_name].plot(ax=ax, color='purple', label='30Y Mortgage / 10Y Treasury Spread')
            ax.set_title("Mortgage-to-Treasury Spread")
            ax.set_xlabel("Date")
            ax.set_ylabel("Spread (%)")
            ax.grid(True, linestyle='--', alpha=0.6)
            ax.legend(loc='best')
            ax.axhline(0, color='black', linewidth=0.5, linestyle='--')

            self.fig.tight_layout()
            self.canvas.draw()

        except Exception as e:
            messagebox.showerror("Error", f"Could not calculate or plot spread: {e}")

    def save_to_csv(self):
        """
        Saves the currently held DataFrame to a CSV file.
        """
        if self.data_df is None or self.data_df.empty:
            messagebox.showwarning("No Data", "No data available to save. Please fetch data first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save Data As..."
        )

        if not file_path:
            return

        try:
            self.data_df.to_csv(file_path)
            messagebox.showinfo("Success", f"Data successfully saved to:\n{file_path}")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = MBSDataHubApp(root)
    root.mainloop()
