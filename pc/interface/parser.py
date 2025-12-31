class Command:
    def __init__(self, domain, action, params=None):
        self.domain = domain
        self.action = action
        self.params = params or []

    def __repr__(self):
        return f"<Command {self.domain}:{self.action} {self.params}>"

class CommandParser:
    def parse(self, raw: str):
        if ":" not in raw:
            raise ValueError("Invalid command format (missing domain)")

        domain_part, rest = raw.split(":", 1)
        tokens = rest.strip().split()

        if not tokens:
            raise ValueError("Missing action")

        domain = domain_part.upper()
        action = tokens[0].upper()
        params = tokens[1:]

        return Command(domain, action, params)
