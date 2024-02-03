import subprocess
import os
import sys
import pathlib

APPS = {
    "Magic Caboose": ["env/bin/python3", "magic_caboose/magic_caboose.py"],
    "Example App": ["env/bin/python3", "example_app/example_app.py"],
}


def main():
    log_file_path = os.path.expanduser("~/main.log")
    log_file = open(log_file_path, "w")
    next_app = "App Selector"
    while next_app is not None:
        if next_app == "App Selector":
            print("App Selector launched", file=log_file)
            project_root_path = str(pathlib.Path(__file__).parent)
            app_selector_cmd = [
                f"{project_root_path}/env/bin/python3",
                "app_selector/app_selector.py",
            ]
            app_selector_cmd.extend(list(APPS.keys()))
            process = subprocess.run(app_selector_cmd, capture_output=True)
            print("App Selector exited", file=log_file)
            process_stdout = str(process.stdout, encoding="utf-8").strip().split("\n")
            if len(process_stdout) < 0 or process_stdout[-1] not in APPS:
                break
            else:
                next_app = process_stdout[-1]
        else:
            print(f"{next_app} launched", file=log_file)
            process = subprocess.run(APPS[next_app])
            next_app = "App Selector"
            print(f"{next_app} exited", file=log_file)


if __name__ == "__main__":
    main()
