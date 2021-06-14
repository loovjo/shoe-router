from collections import defaultdict

NUMERALS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]

class GeorgeLink:
    def __init__(self, prev, next):
        self.prev = prev
        self.next = next

    def __str__(self):
        return f"GeorgeLink(prev={self.prev!r}, next={self.next!r})"

class AnalysisResult:
    def __init__(self, wrong_links, no_links):
        self.wrong_links = wrong_links # set(name)
        self.no_links = no_links # set(name)

    def __str__(self):
        return f"AnalysisResult(wrong_links={self.wrong_links!r}, no_links={self.no_links!r})"

    def into_name(self):
        if len(self.wrong_links) == 0:
            if len(self.no_links) == 0:
                return "a webring", False
            elif len(self.no_links) == 1:
                return "a webline", True
            elif len(self.no_links) < len(NUMERALS):
                return f"{NUMERALS[len(self.no_links)]} weblines", True
            elif len(self.no_links) < len(NUMERALS):
                return "many weblines", True
            else:
                return "many weblines", True
        else:
            return "a webgraph", True

    def into_html(self):
        name, do_strike = self.into_name()

        if do_strike:
            name = f"<strike>a webring</strike> {name}"

        return f'<span class="george">{name}</span>'

class GeorgeState:
    def __init__(self, proper_order, links):
        self.proper_order = proper_order
        self.links = links # defaultdict(λ. None, {name: (prev_user, next_user)})

    def from_data(users, stati):
        proper_order = [user.name for user in users]
        link2name = defaultdict(lambda: None, {u.link: u.name for u in users})

        links = {
            user: (link2name[status.prev_link], link2name[status.next_link])
            for user, status in stati.items()
        }
        links = defaultdict(lambda: (None, None), links)

        return GeorgeState(proper_order, links)

    def analyze(self):
        wrong_links = set()
        no_links = set()

        for i, user in enumerate(self.proper_order):
            prev = self.proper_order[i - 1]
            next = self.proper_order[(i + 1) % len(self.proper_order)]

            if None in self.links[user]:
                no_links.add(user)
            elif self.links[user] != (prev, next):
                wrong_links.add(user)

        return AnalysisResult(wrong_links, no_links)