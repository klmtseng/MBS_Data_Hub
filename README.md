Project 1: MBS Data HubThis application provides a user-friendly interface to fetch, visualize, and export key economic time-series data relevant to Mortgage-Backed Securities (MBS) analysis. It sources its data directly from the Federal Reserve Economic Data (FRED) database via their public API.FeaturesDynamic Data Fetching: Select from a list of key economic indicators, including Treasury yields, mortgage rates, and housing price indexes.Custom Date Ranges: Specify the exact time period you want to analyze.Advanced Visualization:Plot multiple data series on the same chart for direct comparison.Group series onto separate, stacked subplots to handle different scales and units effectively.Dedicated function to plot the crucial 30-Year Mortgage to 10-Year Treasury spread.Data Export: Save the fetched data to a .csv file for use in other applications, such as spreadsheet software or other analysis scripts.User-Friendly Interface: All controls are managed through a simple graphical user interface (GUI) with adjustable font sizes for readability.Setup and InstallationTo run this application on your local machine, follow these steps.PrerequisitesPython 3.6 or newerPip (Python's package installer)1. Clone the Repository (or Download the Files)If you're using Git, clone the repository to your local machine:git clone <your-repository-url>
cd <repository-folder>
Alternatively, download the mbs_data_hub_app.py, requirements.txt, and .gitignore files into a new folder on your computer.2. Create a Virtual Environment (Recommended)It's best practice to create a virtual environment to keep project dependencies isolated.# For Windows
python -m venv venv
.\venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate
3. Install DependenciesThe required Python libraries are listed in the requirements.txt file. Install them using pip:pip install -r requirements.txt
How to Run the ApplicationOnce the dependencies are installed, you can run the application by executing the main Python script:python mbs_data_hub_app.py
The application window should appear, and you can start fetching and plotting data.

## Project Roadmap

This project is currently a data extraction and visualization tool. The long-term goal is to transform it into a comprehensive platform for analyzing and evaluating Mortgage-Backed Securities (MBS). The planned development is divided into several phases:

### Phase 1: Foundational Enhancements & Prepayment Modeling
-   **Expand Data Sources & Feature Engineering:** Integrate more granular data sources (e.g., Ginnie Mae, Fannie Mae) and build a feature engineering pipeline.
-   **Implement Prepayment Models:** Start with a baseline PSA model and then develop a more sophisticated statistical prepayment model based on key drivers like interest rates and housing market dynamics.

### Phase 2: Cash Flow Generation and Valuation
-   **Build a Cash Flow Generator:** Project monthly cash flows (interest, scheduled principal, prepayments) based on the prepayment models.
-   **Implement Valuation Models:** Introduce static valuation methods (e.g., Z-spread) and scenario analysis capabilities.

### Phase 3: Advanced Modeling & User Interface
-   **Implement Option-Adjusted Spread (OAS) Analysis:** Build a Monte Carlo simulation for more robust, industry-standard MBS valuation.
-   **Refactor and Enhance the User Interface:** Transition from a desktop application to a more accessible format, such as a web application or a Jupyter/Colab notebook.

## Note on Google Colab

The current version of this application is built with Tkinter, a desktop GUI toolkit, and **cannot be run directly in Google Colab**.

Making the project compatible with Colab is a key part of the **Phase 3** roadmap. This will involve separating the core logic from the UI, allowing the analysis to be run in a notebook environment with interactive controls.