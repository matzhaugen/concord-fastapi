from src import db


def test_db():
    end_date = "2012-11-26"
    data = db.get_data(["AA", "AXP"], end_date=end_date)
    assert data[end_date:].shape[0] == 1
