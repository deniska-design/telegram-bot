```
# Activity Tracker Bot

> A simple Telegram bot to track your daily activities (like sleep, workouts, and study) and generate visual weekly statistics.

---

## Demo

<img width="536" height="517" alt="photo_2026-09-17_17-32-36" src="https://github.com/user-attachments/assets/780a55e2-b97b-4307-b54c-796936fd8129" />

<img width="577" height="747" alt="photo_2026-09-17_17-32-05" src="https://github.com/user-attachments/assets/a8168dc2-83e9-47fc-9738-57302c871c9b" />

* **Try the Bot on Telegram:** [@MySimpleAssistentBot](https://t.me/MySimpleAssistentBot)

---

## Features

The bot uses conversation handlers to manage multi-step inputs and interactive menus:

| Command | Description |
| :--- | :--- |
| `/start` | Initializes user memory, sets up daily reminders, and resets daily trackers. |
| `/help` | Displays a complete list of available commands and their usage. |
| `/log` | Logs data for a selected activity for today (multi-step process). |
| `/get` | Shows the activity data you logged for today. |
| `/cancel` | Cancels the current multi-step conversation flow at any point. |
| `/getstatistic` | Generates and sends a weekly matplotlib progress chart for a chosen activity. |
| `/revoke` | Resets/clears your logged data for a specific activity for today. |

---

## Tech Stack & Software

* **Language:** Python
* **Libraries & Frameworks:** `python-telegram-bot`, `python-dotenv`, `matplotlib`
* **Tools:** Visual Studio Code, Git

---

## How to Run

### Option 1: Use the Live Bot
Simply open Telegram, navigate to [@MySimpleAssistentBot](https://t.me/MySimpleAssistentBot), and press **Start** to begin tracking.

### Option 2: Run Locally (Development Setup)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/deniska-design/telegram-bot.git
   cd telegram-bot
   ```
```
2. **Set up Virtual Environment & Install Dependencies:**
   ```bash
   # Create a virtual environment
   python -m venv venv

   # Activate it (Linux / macOS)
   source venv/bin/activate

   # On Windows:
   # venv\Scripts\activate

   # Install required packages
   pip install -r requirements.txt
   ```
```
3. **Configure Environment Variables:**
   Create a `.env` file in the root directory and add your Telegram bot token:
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   ```
```
4. **Run the Bot:**
   ```bash
   python main.py
   ```
```
---

## What I Learned & Challenges

* **Learning Python on the Go:** Since this was my first Python project, my main goal was to learn the language while building a real-world application. **Because of this, I made extensive use of AI, but strictly as a research and learning assistant—to search for information, discover libraries, explore command syntax, and get clear conceptual explanations.**
* **C++ to Python Transition:** Coming from a C++ background, I was constantly surprised by how concise and straightforward Python makes complex operations that would otherwise require significantly more boilerplate in C++. I learned core Python syntax alongside fundamental data structures like tuples, dictionaries, lists, and sets.
* **Key Achievements:** I learned how to handle asynchronous Telegram bot handlers, implement timed reminders, and build visual charts dynamically.
* **Main Challenges:**
  * **Multi-step Conversations:** At first, implementing the `/log` command was difficult because it required chaining multiple sequential functions (asking for the activity, getting duration/value, and saving the entry). Once I understood conversation handlers, it became natural.
  * **Data & Statistics:** The biggest challenge was figuring out how to store and structure data for multiple users, activities, and days without setting up a heavy database. I managed to resolve this by designing an efficient internal data structure to feed data directly into `matplotlib` for generating charts.

---

## License

Distributed under the MIT License. See `LICENSE` for more information.
