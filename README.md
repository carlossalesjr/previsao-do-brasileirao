# ⚽ Brasileirão Simulator

![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

> A Python script that runs a simulation of the remainder of the Brazilian Football Championship season, projecting a possible final league table. This project uses web scraping to gather up-to-date data from Wikipedia and applies a statistical model based on the Poisson Distribution to predict the outcome of each remaining match.

---

## ✨ Features

- [x] **Automated Data Scraping:** Scrapes league tables and match results from Wikipedia.
- [x] **Weighted Statistical Model:** Uses data from the current and previous seasons to calculate team strength.
- [x] **Poisson Distribution for Predictions:** Simulates match scores based on offensive and defensive stats.
- [x] **Single, Randomized Simulation:** Executes one full simulation of the remaining season.
- [x] **Terminal-Based Display:** Presents the final projected league table in the command line.

---

## 🛠️ Tech Stack

| Category | Technology / Library |
| :--- | :--- |
| **Language** | `Python 3.9+` |
| **Data Analysis** | `pandas`, `numpy` |
| **Web Scraping** | `requests` |
| **Statistical Modeling** | `scipy` |
| **Virtual Environment**| `venv` |

---

## ⚙️ Setup and Installation

Follow the steps below to run this project locally.

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/your-repository.git](https://github.com/your-username/your-repository.git)
    cd your-repository
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # Create the environment
    python -m venv venv

    # Activate on Windows
    .\venv\Scripts\activate

    # Activate on macOS/Linux
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    This command reads the `requirements.txt` file and installs all necessary libraries.
    ```bash
    pip install -r requirements.txt
    ```

---

## ▶️ How to Run

With the virtual environment activated, run the main script with this single command:

```bash
python previsao.py
