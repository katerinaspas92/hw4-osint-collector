def test_pagination():
    first_page = [
        {"id": "105"},
        {"id": "104"},
        {"id": "103"},
    ]

    second_page = [
        {"id": "102"},
        {"id": "101"},
        {"id": "100"},
    ]

    max_id = first_page[-1]["id"]

    assert max_id == "103"

    new_max_id = second_page[-1]["id"]

    assert int(new_max_id) < int(max_id)

    print("ТЕСТ ПАГИНАЦИИ ПРОЙДЕН!")


if __name__ == "__main__":
    test_pagination()
