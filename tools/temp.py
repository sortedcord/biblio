from tabulate import tabulate
from tabulate import TableFormat, Line, DataRow

table_ = [[1,2,3],[1,2,3],[1,2,3],[1,2,3],[1,2,3],[1,2,3]]

github = TableFormat(
        lineabove=Line("|", "-", "|", "|"),
        linebelowheader=Line("|", "-", "|", "|"),
        linebetweenrows=None,
        linebelow=None,
        headerrow=DataRow("|", "|", "|"),
        datarow=DataRow("|", "|", "|"),
        padding=0,
        with_header_hide=["lineabove"])

table = tabulate(table_, ["yet boi 123", "yet vboi 124", "S.No."], tablefmt=github, colalign=("left","left","left",))

print(table)