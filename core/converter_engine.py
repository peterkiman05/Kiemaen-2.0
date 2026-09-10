import re

class ConverterEngine:
    @staticmethod
    def convert_units(prompt: str):
        query = prompt.lower()
        numbers = [float(x) for x in re.findall(r"[-+]?\d*\.\d+|\d+", prompt)]
        
        if not numbers:
            return "No numerical value provided for conversion."
        
        val = numbers[0]
        
        if "mm" in query and "m" in query:
            if "mm to m" in query:
                return f"{val} mm = {val / 1000} m"
            else:
                return f"{val} m = {val * 1000} mm"
        elif "mpa" in query and "kpa" in query:
            if "mpa to kpa" in query:
                return f"{val} MPa = {val * 1000} kPa"
            else:
                return f"{val} kPa = {val / 1000} MPa"
        elif "deg" in query or "radian" in query:
            import math
            if "deg to rad" in query:
                return f"{val}° = {round(math.radians(val), 4)} rad"
            else:
                return f"{val} rad = {round(math.degrees(val), 4)}°"
        else:
            return f"Conversion pattern not recognized. Try: 'convert 500 mm to m' or 'convert 40 mpa to kpa'."
