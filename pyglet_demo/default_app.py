class DefaultApp:
    """A simple default app which has all the functions required by main for an App"""

    name = "Default App"

    def __init__(self, update_handlers=[], *args, **kwargs):
        """Default App init

        Keywords Arguments:
            update_handlers (list): provide update_handlers that should be called on every refresh
              cycle of App. Defaults to [].
        """
        self.update_handlers = update_handlers

    def start(self):
        """This function is run by main on app startup
        It should be blocking as long as the app is running
        """
        pass

    def exit(self):
        """This function is run by main on app exit.
        App is responsible to clean after itself"""
        pass
