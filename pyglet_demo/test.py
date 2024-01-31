import pyglet


# Define a window class
class MyWindow(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super(MyWindow, self).__init__(*args, **kwargs)


pyglet.app.run()
for i in range(10):
    # Create multiple instances of the window class
    window = MyWindow(width=400, height=300, caption=f"Window {i}")
    # Start the event loop
    # pyglet.app.exit()
