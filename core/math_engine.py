import math


class MathEngine:
    @staticmethod
    def solve_beam_deflection(load, length, e, i):
        delta = (float(load) * (float(length) ** 3)) / (48 * float(e) * float(i))
        return round(delta, 4)

    @staticmethod
    def calculate_trade_risk(balance, risk_percent, stop_loss_pips):
        # Risk amount in currency = Account Balance * (Risk % / 100)
        risk_amount = float(balance) * (float(risk_percent) / 100)

        # Standard lot size calculation for standard forex/gold lots (approx value per pip)
        # Lot Size = Risk Amount / (Stop Loss in Pips * Pip Value multiplier)
        lot_size = risk_amount / (float(stop_loss_pips) * 10)

        return {"risk_amount": round(risk_amount, 2), "lot_size": round(lot_size, 2)}
