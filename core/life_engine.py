import re


class LifeEngine:
    @staticmethod
    def get_advice(full_context: str):
        cat = full_context.lower().strip()

        numbers = [float(x) for x in re.findall(r"[-+]?\d*\.\d+|\d+", cat)]

        if (
            "spend" in cat
            or "budget" in cat
            or "plan" in cat
            or "income" in cat
            or "salary" in cat
            or "eater" in cat
            or "transport" in cat
        ) and numbers:
            # Extract the budget amount (look for the largest number or default to 1700 if found)
            total_amount = max(numbers) if max(numbers) > 50 else 1700.0

            # Check if user mentioned transport and data are covered
            if "transport" in cat and (
                "cover" in cat or "paid" in cat or "sorted" in cat
            ):
                # Reallocate: 0% transport/data, 75% heavy food/groceries, 25% emergency buffer
                groceries = round(total_amount * 0.75, 2)
                buffer = round(total_amount * 0.25, 2)

                return {
                    "state": f"Optimized Heavy-Eater Budget (Total: R{total_amount:,.2f})",
                    "focus": "Maximized Calorie Density & Zero Waste (Transport/Data Pre-Covered)",
                    "principles": [
                        f"1. Heavy Grocery Allocation (75%): R{groceries:,.2f} — Shifted entirely toward high-volume sustenance (maize meal, beans, peanut butter, eggs, bulk staples) to support high metabolic demand.",
                        f"2. Emergency Cash Buffer (25%): R{buffer:,.2f} — Retained strictly for unforeseen contingencies or medical needs.",
                    ],
                    "perspective": "By eliminating pre-covered overhead like transit, your entire capital stream channels directly into foundational sustenance and resilience.",
                }

            # Default standard budget split
            transport = round(total_amount * 0.25, 2)
            groceries = round(total_amount * 0.40, 2)
            data_airtime = round(total_amount * 0.15, 2)
            savings_buffer = round(total_amount * 0.20, 2)

            return {
                "state": f"Practical Budget Allocation (Total: R{total_amount:,.2f})",
                "focus": "Localized Survival, Zero Waste, and Essential Asset Protection",
                "principles": [
                    f"1. Transport / Commuting (25%): R{transport:,.2f} — Allocated strictly for local transit.",
                    f"2. Food & Groceries (40%): R{groceries:,.2f} — Focus on high-density energy staples.",
                    f"3. Data & Connectivity (15%): R{data_airtime:,.2f} — Essential for academic portals and job hunting.",
                    f"4. Emergency Buffer (20%): R{savings_buffer:,.2f} — Locked away for unforeseen costs.",
                ],
                "perspective": "Every rand must have a designated purpose before it leaves your hands.",
            }

        # Standard categorical intent matching
        adversity_keywords = [
            "poor",
            "broke",
            "struggl",
            "debt",
            "scarce",
            "hardship",
            "income",
            "money",
            "cash",
        ]
        wealth_keywords = [
            "rich",
            "wealth",
            "abundan",
            "invest",
            "capital",
            "million",
            "portfolio",
        ]
        grief_keywords = [
            "heart",
            "break",
            "grief",
            "loss",
            "pain",
            "breakup",
            "betray",
        ]
        joy_keywords = ["happy", "joy", "thriv", "excited", "success", "winning"]
        sad_keywords = [
            "sad",
            "depress",
            "overwhelm",
            "lost",
            "burnt",
            "stress",
            "anxiety",
            "exhaust",
        ]

        if any(w in cat for w in adversity_keywords):
            return {
                "state": "Financial Adversity / Resource-Constrained Phase",
                "focus": "Aggressive Expense Triage, High-Yield Skill Acquisition, and Capital Preservation",
                "principles": [
                    "Principle 1: Stop the bleeding. Isolate essential survival expenses from psychological wants immediately.",
                    "Principle 2: Shift from a consumer mindset to a producer mindset by directing zero-cost hours into mastering high-leverage skills.",
                    "Principle 3: Construct a micro-emergency fund and use zero-based budgeting to maximize every unit of income.",
                ],
                "perspective": "Financial scarcity is a temporary constraint when met with systematic discipline, rigorous budgeting, and relentless self-education.",
            }

        elif any(w in cat for w in wealth_keywords):
            return {
                "state": "Capital Abundance / Wealth Preservation",
                "focus": "Risk Asymmetry, Portfolio Diversification, and Generational Leverage",
                "principles": [
                    "Principle 1: Protect principal above all through strict asset allocation.",
                    "Principle 2: Diversify across uncorrelated asset classes to protect against systemic shocks.",
                    "Principle 3: Invest heavily in systems, code, and scalable assets rather than linear time.",
                ],
                "perspective": "True wealth is freedom of choice and time. Use abundance to build enduring structures.",
            }

        elif any(w in cat for w in grief_keywords):
            return {
                "state": "Emotional Recovery / Post-Loss Rebuilding",
                "focus": "Radical Acceptance, Physical Grounding, and Purpose Re-alignment",
                "principles": [
                    "Principle 1: Honor the psychological processing window rather than suppressing stress responses.",
                    "Principle 2: Channel raw emotional intensity into high-focus physical exertion or deep-work projects.",
                    "Principle 3: Protect personal boundaries fiercely while baseline stability resets.",
                ],
                "perspective": "Pain strips away distractions and forces you to discover your core self-reliance.",
            }

        elif any(w in cat for w in joy_keywords):
            return {
                "state": "Peak Momentum / Thriving",
                "focus": "Compound Habit Lock-In, Gratitude, and Strategic Scaling",
                "principles": [
                    "Principle 1: Lock in daily routines while energy is high; success stems from compounding habits.",
                    "Principle 2: Share momentum by lifting peers and building robust community structures.",
                    "Principle 3: Avoid lifestyle creep and use clear headspace for long-term targets.",
                ],
                "perspective": "Joy is operational fuel. Savor wins while keeping foundations anchored.",
            }

        elif any(w in cat for w in sad_keywords):
            return {
                "state": "Mental Fatigue / Overload",
                "focus": "Radical Simplification, Micro-Step Execution, and Radical Self-Compassion",
                "principles": [
                    "Principle 1: Reduce your operational horizon to the next single hour when facing a mountain.",
                    "Principle 2: Cut cognitive clutter, digital noise, and non-essential friction.",
                    "Principle 3: Prioritize core biological baselines: sleep consistency and hydration.",
                ],
                "perspective": "Low seasons are cyclical phases. Treat yourself with objective, patient strategy.",
            }

        else:
            return {
                "state": "General Strategic Navigation",
                "focus": "Systematic Clarity, First-Principles Breakdown, and Intentional Action",
                "principles": [
                    "Principle 1: Isolate variables and break complex problems into sequential components.",
                    "Principle 2: Build sustainable structural systems over relying on fleeting motivation.",
                    "Principle 3: Maintain absolute integrity across your personal, academic, and financial undertakings.",
                ],
                "perspective": "Sustainable progress is the product of disciplined, repeatable daily execution.",
            }
