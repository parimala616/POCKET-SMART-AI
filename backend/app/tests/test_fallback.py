from app.ai import home

from app.schemas import HomeBudgetInput


def test_home_fallback():

    data = HomeBudgetInput(
        total_budget=10000,
        num_lights=2,
        num_fans=1,
        num_furniture=1,
        num_dining_tables=0,
        has_living_room=True,
        has_kitchen=False,
        has_bedroom=False
    )

    result = home(data)

    assert result["planner"] == "home"

    assert result["total_budget"] == 10000

    assert "budget_breakdown" in result

    assert "remaining_budget" in result

    assert len(
        result["budget_breakdown"]
    ) > 0