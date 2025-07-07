import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import pandas_datareader.data as web
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from collections import defaultdict

# --- FRED Series Codes ---
# This dictionary holds the series we are interested in.
# It makes the code cleaner and easier to expand later.
FRED_SERIES = {
    "10-Year Treasury (DGS10)": "DGS10",
    "2-Year Treasury (DGS2)": "DGS2",
    "30-Year Mortgage (MORTGAGE30US)": "MORTGAGE30US",
    "15-Year Mortgage (MORTGAGE15US)": "MORTGAGE15US",
    "Case-Shiller HPI (CSUSHPINSA)": "CSUSHPINSA"
}

class MBSDataHubApp:
    """
    An application for fetching, visualizing, and exporting key economic data
    for Mortgage-Backed Securities (MBS) analysis from the FRED database.
    """
    def __init__(self, root):
        """
        Initializes the application's user interface and state.
        """
        self.root = root
        self.root.title("Project 1: MBS Data Hub")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f0f0")

        # This will hold the fetched data as a pandas DataFrame
        self.data_df = None

        # --- Main Frame ---
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Controls Frame (Left Side) ---
        controls_frame = ttk.LabelFrame(main_frame, text="Controls", padding="10")
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
        
        # Add Header
        header_frame = ttk.Frame(series_frame)
        header_frame.pack(fill=tk.X, anchor="w", pady=(0,5))
        ttk.Label(header_frame, text="Series", font="-weight bold").pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Label(header_frame, text="Group", font="-weight bold").pack(side=tk.RIGHT, padx=(10,0))

        # Add Series with Grouping Entry
        for i, (name, code) in enumerate(FRED_SERIES.items()):
            row_frame = ttk.Frame(series_frame)
            row_frame.pack(fill=tk.X, anchor="w", pady=2)
            
            var = tk.BooleanVar(value=True)
            self.series_vars[code] = var
            cb = ttk.Checkbutton(row_frame, text=name, variable=var)
            cb.pack(side=tk.LEFT, expand=True, fill=tk.X)

            group_entry = ttk.Entry(row_frame, width=5)
            # Default grouping: 1 for rates, 2 for HPI
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
        plot_frame = ttk.LabelFrame(main_frame, text="Data Visualization", padding="10")
        plot_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.fig = plt.Figure(facecolor="#f0f0f0")
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        ax = self.fig.add_subplot(111)
        ax.set_title("Select data and click 'Fetch & Plot'")
        ax.grid(True, linestyle='--', alpha=0.6)
        plt.tight_layout()


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

        # --- Grouping Logic ---
        # defaultdict simplifies adding new keys
        plot_groups = defaultdict(list)
        for code, var in self.series_vars.items():
            if var.get() and code in self.data_df.columns:
                group_key = self.series_groups[code].get().strip()
                # If group is empty, give it a unique group based on its own code
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
            
        # Create subplots, one for each group, sharing the x-axis
        axes = self.fig.subplots(nrows=num_groups, ncols=1, sharex=True)
        if num_groups == 1:
            axes = [axes] # Make it iterable for consistency
            
        self.fig.suptitle("Selected Economic Data from FRED", fontsize=14)

        # Plot each group on its own subplot
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

            spread_df['Spread'] = spread_df['MORTGAGE30US'] - spread_df['DGS10']

            self.fig.clear()
            ax = self.fig.add_subplot(111)
            
            spread_df['Spread'].plot(ax=ax, color='purple', label='30Y Mortgage / 10Y Treasury Spread')
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
