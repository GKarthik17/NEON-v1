import msvcrt

class NonBlockingInput:
    def __init__(self):
        self.buffer = ""

    def poll(self):
        if not msvcrt.kbhit():
            return None

        ch = msvcrt.getwch()

        if ch == '\r':   # Enter
            line = self.buffer.strip()
            self.buffer = ""
            print()
            return line

        elif ch == '\b':  # Backspace
            self.buffer = self.buffer[:-1]
            print('\b \b', end='', flush=True)

        else:
            self.buffer += ch
            print(ch, end='', flush=True)

        return None
