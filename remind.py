class Reminder:
    def __init__(self, message_obj):
        args = message_obj.content.split(" ")
        self.args = args
        self.time_arg = False

    def remind(self):
        if self.args[0] == "min" or self.args[0] == "mins" or self.args[0] == "minute" or self.args[0] == "minutes" or self.args[0] == "m":
            self.time *= 60
            self.time_arg = True
        elif self.args[0] == "hour" or self.args[0] == "hours" or self.args[0] == "hr" or self.args[0] == "hrs" or self.args[0] == "h":
            self.time *= 3600
            self.time_arg = True
        elif self.args[0] == "day" or self.args[0] == "days" or self.args[0] == "d":
            self.time *= 86400
            self.time_arg = True

        t = Timer(self.time, self.handle_command)
        t.start()


    def handle_command(self):
        reponse_str = " ".join(self.args)
        print(response_str)
        return reponse_str