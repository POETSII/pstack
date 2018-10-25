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

header = ["Process", "User", "CPU", "Time", "Schema", "Devices", "Edges"]

palette = [
    ('engine', 'dark cyan', 'light gray'),
    ('meter', 'dark green', ''),
    ('brack', 'bold', ''),
    ('usage', 'dark gray, bold', ''),
    ('header', 'dark blue, bold', ''),
    ('section', 'bold', ''),
    ('help', '', ''),
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


def update_meter(meter, usage_perc):
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
    meter.set_text(parts)


def make_engines_section(engines, meters):
    """Create LineBox with engine usage meters."""
    titles = [Text(("engine", name), align="right") for name in engines]
    title_len = max(len(engine) for engine in engines)
    columns = Columns([(title_len, Pile(titles)), Pile(meters)])
    return LineBox(columns, **{arg: " " for arg in linebox_args})


def get_table_piles(rows):
    get_header = lambda items: [("header", item) for item in items]
    rows[0] = get_header(rows[0])
    ncols = len(rows[0])
    get_col = lambda col: [row[col] for row in rows]
    cols = map(get_col, range(ncols))
    col_piles = [
        (Pile(Text(item) for item in col), ('weight', 1, False))
        for col in cols
    ]
    return col_piles


def get_padded(items):
    """Wrap items in a Fillter with left and right margins."""
    pad = Padding(Pile(items), left=1, right=1)
    return Filler(pad, 'top')


def get_state_demo():
    """Return dummy information for demonstration."""
    engines = [
        "byron.cl.cam.ac.uk",
        "aesop.cl.cam.ac.uk",
        "coleridge.cl.cam.ac.uk",
    ]
    usage = [randint(0, 100) for _ in engines]
    processes = [
        ["process-123", "user-123", "30.2%", "0:03", "ro", "4", "16"],
        ["process-123", "user-123", "30.2%", "0:03", "ro", "4", "16"],
        ["process-123456", "user-123", "30.2%", "0:03", "ro", "4", "16"],
        ["process-123", "user-123", "30.2%", "0:03", "ro", "4", "16"],
        ["process-123", "user-123", "30.2%", "0:03", "ro", "4", "65535"],
    ]
    nproc = randint(1, len(processes))
    return engines, usage, sample(processes, nproc)


def top(period=1, get_state=get_state_demo):
    """Display process information.

    Arguments:
      - period (float)       : update period
      - get_state (callable) : function to generate state information
    """

    def make_text(title, attr="", align="left"):
        """Create a Text object with given content, style and alignment."""
        return Text((attr, " %s" % title), align=align)

    def make_separator():
        """Create a separator."""
        return make_text("")

    engines, usage, processes = get_state()
    meters = [Text(" ", align="left") for _ in engines]
    process_table = LineBox(Columns([]))

    def update_process_table(processes):
        new_contents = get_table_piles([header] +processes)
        process_table.base_widget.contents = new_contents

    def update():
        engines, usage, processes = get_state()
        update_process_table(processes)
        for meter, perc in zip(meters, usage):
            update_meter(meter, perc)

    update()

    items = [
        make_separator(),
        make_text("POETS Process Viewer", attr="section", align="center"),
        make_text("Engine Usage:"),
        make_engines_section(engines, meters),
        make_text("Process Table:"),
        make_separator(),
        process_table,
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
    loop.set_alarm_in(period, on_timer)
    loop.run()

if __name__ == '__main__':
    top()
