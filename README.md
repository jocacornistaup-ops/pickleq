# PICKLEQ — Pickleball Court Queue Assistance System

A desktop app built with **Python + Tkinter + SQLite** that solves disorganized
court queuing and unclear play rotation on pickleball courts.

## Features
- **User Authentication** — login & registration for players, separate staff login
- **Digital Queue Joining** — join the queue with your name/team
- **Real-Time Queue Display** — live-updating queue table
- **Automated Rotation Timer** — per-court countdown that signals when a session ends
- **Group/Team Queuing** — queue solo, as a pair, or as a team
- **Notification Alerts** — pop-up alerts when a court is about to free up / time's up
- **Court Usage Log** — history of every completed session

## Project structure
```
pickleq/
├── main.py            # entry point — run this
├── database.py         # all SQLite access (schema + queries)
├── login_window.py     # first screen: login / register (gradient UI)
├── dashboard.py         # main app: queue, courts/timer, usage log tabs
├── styles.py            # shared blue/white color palette + widget styles
├── requirements.txt
├── .gitignore
└── README.md
```

`pickleq.db` (the SQLite database file) is created automatically the first
time you run the app, in the same folder.

---

## 1. Requirements

- **Python 3.9+** (comes with `tkinter` and `sqlite3` already built in —
  nothing to `pip install`)
- On **Windows/macOS**, the standard python.org installer already includes Tkinter.
- On **Linux (Ubuntu/Debian)**, if you get `ModuleNotFoundError: No module named 'tkinter'`, install it with:
  ```bash
  sudo apt-get install python3-tk
  ```

## 2. Run it in VS Code

1. Open the `pickleq` folder in VS Code: `File → Open Folder…`
2. Make sure the **Python extension** (by Microsoft) is installed.
3. Select an interpreter: press `Ctrl+Shift+P` (`Cmd+Shift+P` on Mac) →
   type **Python: Select Interpreter** → choose your Python 3 install.
4. Open `main.py`, then run it either by:
   - Clicking the ▶ **Run** button in the top-right of the editor, or
   - Opening a terminal in VS Code (`` Ctrl+` ``) and typing:
     ```bash
     python main.py
     ```
5. The login window should appear.

### Default account to try immediately
| Role | Username | Password |
|---|---|---|
| Staff | `admin` | `admin123` |

Or click **Register** on the login screen to create your own player account.

### Staff vs. Player
- **Players** can join the queue and watch courts/log in real time.
- **Staff** additionally get the "Send Next Party to Available Court" and
  "End Session" buttons to actually run the rotation.
- The login screen has a **Player / Court Staff** radio button — pick the
  one matching the account you're logging into.

## 3. Uploading to GitHub

From inside the `pickleq` folder:

```bash
git init
git add .
git commit -m "Initial commit: PICKLEQ Tkinter + SQLite app"
git branch -M main
git remote add origin https://github.com/<your-username>/<your-repo-name>.git
git push -u origin main
```

(Create the empty repo on github.com first — "New repository", no README/
.gitignore, since you already have them locally — then copy its URL into
the `git remote add` command above.)

Because of the included `.gitignore`, the generated `pickleq.db` file and
`__pycache__/` folders won't be pushed — anyone who clones the repo gets a
clean database seeded automatically on first run.

## 4. Notes / things you can extend later
- Add password-reset / "forgot password" flow
- Export the Usage Log to CSV or PDF
- Add more courts by inserting rows into the `courts` table
- Turn the desktop app into a kiosk-mode fullscreen build for an actual
  court-side tablet
