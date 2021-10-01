from importlib.resources import files
import json

import digi4k.data.charts.tutorial
from digi4k.lib.objects.note import Chart


def test_parse():
    j = json.loads(files(digi4k.data.charts.tutorial).joinpath("tutorial-hard.json").read_text())
    chart = Chart.from_json(j)
    assert chart is not None
