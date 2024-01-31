class DefaultApp:
    def __init__(self, *args, **kwargs):
        """
        test 123
        """
        print(kwargs)
        self.update_handlers = []
        if "update_handlers" in kwargs:
            self.update_handlers = kwargs["update_handlers"]

    def start(self):
        pass

    def exit(self):
        pass
