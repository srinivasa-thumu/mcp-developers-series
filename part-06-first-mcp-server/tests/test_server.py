import pytest

from server import find_customer


def test_find_customer_returns_john() -> None:
    assert find_customer(101) == {
        "name": "John",
        "email": "john@example.com",
        "city": "Hyderabad",
    }


def test_find_customer_returns_sarah() -> None:
    assert find_customer(102)["name"] == "Sarah"


def test_find_customer_raises_for_unknown_id() -> None:
    with pytest.raises(ValueError, match="Customer with ID 999 was not found"):
        find_customer(999)


@pytest.mark.parametrize("customer_id", [0, -1])
def test_find_customer_rejects_non_positive_id(customer_id: int) -> None:
    with pytest.raises(ValueError, match="positive integer"):
        find_customer(customer_id)
