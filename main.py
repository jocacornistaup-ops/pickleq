"""
main.py
-------
PICKLEQ - A Pickleball Court Queue Assistance System
Entry point: run this file to launch the app.

    python main.py

Flow: init the SQLite database -> show the login/register screen ->
on a successful login, open the main dashboard.
"""

import database
from login_window import LoginWindow
from dashboard import launch_dashboard


def main():
    database.init_db()
    app = LoginWindow(on_success=launch_dashboard)
    app.mainloop()


if __name__ == "__main__":
    main()
