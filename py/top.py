from urwid import (
    Text,
    Pile,
    Filler,
    Columns,
    LineBox,
    Padding,
    MainLoop,
    ListBox,
    ExitMainLoop
)

from random import randint
from random import sample

header = [
    "PID",
    "Status",
    "Regions",
    "User",
    "CPU",
    "Time",
    "Graph",
    "Devices",
    "Edges"
]

palette = [
    ('engine', 'dark cyan', 'light gray'),
    ('meter', 'dark green', ''),
    ('brack', 'bold', ''),
    ('usage', 'dark gray, bold', ''),
    ('header', 'bold', ''),
    ('section', 'bold', ''),
    ('help', '', ''),
    ('running', 'dark green, bold', ''),
    ('waiting', 'dark gray, bold', ''),
]

linebox_args = [
    "tlcorner",
    "tline",
    "lline",
    "trcorner",
    "blcorner",
    "rline",
    "bline",
    "brcorner"
]


def get_meter_parts(usage_perc):
    """Update the value of a progress meter Text."""
    usage_str = " %5.1f%%" % usage_perc
    meter_w = 40
    meter_pos = int(usage_perc / 100.0 * meter_w)
    strokes = meter_pos
    spaces = meter_w - strokes
    parts = [
        ("", " "),
        ("brack", "["),
        ("meter", "|" * strokes + " " * spaces),
        ("usage", usage_str),
        ("brack", "]")
    ]
    return parts


def get_engine_table_content(engines):
    titles = [Text(("engine", name), align="right") for name, _ in engines]
    meters = [Text(get_meter_parts(perc), align="right") for _, perc in engines]
    title_len = max(len(name) for name, _ in engines) if engines else 1
    return [
        (Pile(titles), ('given', title_len, False)),
        (Pile(meters), ('weight', 1, False))
    ]


def get_process_table_content(rows):
    get_header = lambda items: [("header", item) for item in items]
    rows[0] = get_header(rows[0])
    ncols = len(rows[0])
    get_col = lambda col: [row[col] for row in rows]
    cols = map(get_col, range(ncols))
    weights = [10, 10, 10, 10, 8, 8, 8, 8, 8]
    return [
        (Pile(Text(item) for item in col), ('weight', weight, False))
        for col, weight in zip(cols, weights)
    ]


def get_padded(items):
    """Wrap items in a Fillter with left and right margins."""
    pad = Padding(Pile(items), left=1, right=1)
    return Filler(pad, 'top')


def get_demo_state():
    """Return demo state information."""
    engines = [("engine%d" % ind, randint(0, 100)) for ind in range(9)]
    processes = [
        ["123", ("running", "Running"), "3", "user-123", "30.2%", "1:10", "ro", "4", "16"],
        ["456", ("waiting", "Waiting"), "1", "user-345", "78.1%", "0:01", "ro", "8", "16"],
        ["789", ("waiting", "Waiting"), "6", "user-783", "46.9%", "0:22", "ro", "8", "16"],
        ["111", ("running", "Running"), "2", "user-843", "21.3%", "0:15", "ro", "4", "16"],
        ["001", ("running", "Running"), "4", "user-103", "58.2%", "0:17", "ro", "2", "65"],
    ]
    nproc = randint(1, len(processes))
    nengines = randint(1, len(engines))
    return sample(engines, nengines), sample(processes, nproc)


def top(period=1, get_state=get_demo_state):
    """Display process information.

    Arguments:
      - period (float)       : update period
      - get_state (callable) : function to generate state information
    """

    engine_table = Columns([])
    process_table = Columns([])

    def make_text(title, attr="", align="left"):
        """Create a Text object with given content, style and alignment."""
        return Text((attr, " %s" % title), align=align)

    def make_separator():
        """Create a separator."""
        return make_text("")

    def update():
        engines, processes = get_state()
        engine_table.contents = get_engine_table_content(engines)
        process_table.contents = get_process_table_content([header] + processes)

    items = [
        make_separator(),
        make_text("Process Viewer", attr="section", align="center"),
        make_text("Engine Usage:"),
        LineBox(engine_table, **{arg: " " for arg in linebox_args}),
        make_text("Process Table:"),
        make_separator(),
        LineBox(process_table),
        make_separator(),
        make_text("Press (q) to quit.")
    ]

    def on_timer(loop, user_data):
        update()
        loop.set_alarm_in(period, on_timer)

    def on_key(key):
        if key in ('q', 'Q'):
            raise ExitMainLoop()

    loop = MainLoop(get_padded(items), palette, unhandled_input=on_key)
    on_timer(loop, None)  # Start timer
    loop.run()

if __name__ == '__main__':
    top()
