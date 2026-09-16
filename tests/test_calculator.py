from app.models import CostBreakdownRequest
from app.services.calculator_service import RentalCalculatorService


def test_rental_calculator_basic():
    req = CostBreakdownRequest(
        rent_monthly=25000,
        deposit=125000,
        maintenance=2000,
        brokerage=0,
        agreement_charges=1500,
        other_charges=0
    )
    res = RentalCalculatorService.calculate_deal(req)

    assert res.total_monthly_burn == 27000
    assert res.total_initial_move_in_cost == 153500
    assert res.deposit_to_rent_ratio == 5.0
    assert res.is_deposit_high is False
    assert res.savings_vs_market_avg > 0


def test_rental_calculator_high_deposit():
    req = CostBreakdownRequest(
        rent_monthly=30000,
        deposit=250000,  # > 8x rent
        maintenance=3000,
        brokerage=30000,
        agreement_charges=2000,
        other_charges=0
    )
    res = RentalCalculatorService.calculate_deal(req)

    assert res.deposit_to_rent_ratio == 8.33
    assert res.is_deposit_high is True
    assert res.total_initial_move_in_cost == 315000
