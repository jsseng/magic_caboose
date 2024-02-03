import subprocess

APPS = {
    "Magic Caboose": ["env/bin/python3", "magic_caboose/magic_caboose.py"],
    "Example App": ["env/bin/python3", "example_app/example_app.py"],
}


def main():
    next_app = "App Selector"
    while next_app is not None:
        if next_app == "App Selector":
            print("App Selector launched")
            app_selector_cmd = ["env/bin/python3", "app_selector/app_selector.py"]
            app_selector_cmd.extend(list(APPS.keys()))
            process = subprocess.run(app_selector_cmd, capture_output=True)
            print("App Selector exited")
            process_stdout = str(process.stdout, encoding="utf-8").strip().split("\n")
            if len(process_stdout) < 0 or process_stdout[-1] not in APPS:
                break
            else:
                next_app = process_stdout[-1]
        else:
            print(f"{next_app} launched")
            process = subprocess.run(APPS[next_app])
            next_app = "App Selector"
            print(f"{next_app} exited")


if __name__ == "__main__":
    main()
