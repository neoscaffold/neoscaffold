from ray.data import from_items

from server import Evaluator, Source, ColumnMax


def test_basic():
    ds = from_items( [{"col1": i, "col2": i * 2} for i in range(10)] )
    assert (ds.max('col1')) == 9

def test_evaluator():
    datasource = from_items( [{"col1": i, "col2": i * 2} for i in range(10)] )

    evl = Evaluator(
        ColumnMax(
            column="col1",
            max_numeric=8,
        )
    )
    result = evl.evaluate(Source(
        datasource
    ))

    print(result.passed)
    print(result)

    evl = Evaluator()

    evl.set_rules(
        ColumnMax(
            column="col1",
            max_numeric=11,
        )
    )

    result = evl.evaluate(Source(
        datasource
    ))

    print(result.passed)
    print(result)