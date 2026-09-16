from app.models import CostBreakdownRequest, CostBreakdownResponse


class RentalCalculatorService:
    @staticmethod
    def calculate_deal(req: CostBreakdownRequest) -> CostBreakdownResponse:
        monthly_burn = req.rent_monthly + req.maintenance
        
        # Initial Move-in = Deposit + First Month Rent + First Month Maintenance + Brokerage + Legal/Agreement + Other
        move_in_cost = (
            req.deposit + 
            req.rent_monthly + 
            req.maintenance + 
            req.brokerage + 
            req.agreement_charges + 
            req.other_charges
        )
        
        deposit_ratio = round(req.deposit / max(1, req.rent_monthly), 2)
        is_high = deposit_ratio > 6.0  # Alert if deposit exceeds 6 months
        
        # 1-Year Total Cost = Initial Move-in - Refundable Deposit + (11 * monthly_burn)
        # Or simpler: Deposit + (12 * monthly_burn) + Brokerage + Agreement
        annual_projection = req.deposit + (12 * monthly_burn) + req.brokerage + req.agreement_charges
        
        # Benchmark market average for 2BHK in tech corridor (~38k/mo)
        benchmark_monthly = 36000
        potential_monthly_savings = max(0, benchmark_monthly - monthly_burn)
        annual_savings = potential_monthly_savings * 12
        
        return CostBreakdownResponse(
            total_monthly_burn=monthly_burn,
            total_initial_move_in_cost=move_in_cost,
            deposit_to_rent_ratio=deposit_ratio,
            annual_cost_projection=annual_projection,
            is_deposit_high=is_high,
            savings_vs_market_avg=annual_savings
        )
