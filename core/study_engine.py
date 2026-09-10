class StudyEngine:
    @staticmethod
    def get_study_strategy(module_name: str):
        mod = module_name.lower().strip()
        
        # 1. Environmental Management
        if "environ" in mod or "management" in mod or "sustain" in mod:
            return {
                "module": "Environmental Management",
                "proven_theory": "ISO 14001 Environmental Management Systems (EMS) & The Mitigation Hierarchy",
                "core_strategy": "Environmental Impact Assessment (EIA) Matrix Analysis & Statutory Compliance Mapping",
                "steps": [
                    "Step 1: Dissect project lifecycles against South African National Environmental Management Act (NEMA) regulations and environmental authorizations.",
                    "Step 2: Construct Leopold Interaction Matrices to quantitatively cross-reference project activities (e.g., earthworks, trenching) against environmental receptors (water tables, local fauna).",
                    "Step 3: Apply the strict Mitigation Hierarchy sequence—first design to **Avoid**, then **Minimize**, then **Restore**, and only use **Offsets** as a last resort."
                ],
                "benefits": "Why this is the superior strategy: It prevents catastrophic statutory non-compliance penalties, ensures your EIA reports withstand rigorous public scrutiny, and provides a bulletproof framework for sustainable infrastructure planning."
            }
            
        # 2. Strength of Materials
        elif "strength" in mod or "materials" in mod:
            return {
                "module": "Strength of Materials",
                "proven_theory": "Euler-Bernoulli Beam Theory & Mohr's Circle Principal Stress Transformation",
                "core_strategy": "Free-Body Diagram (FBD) Superposition & Continuous Load Integration",
                "steps": [
                    "Step 1: Derive internal shear force ($V$) and bending moment ($M$) distributions directly via continuous calculus integration ($V = \\int w(x)dx$) rather than relying on memorized formulas.",
                    "Step 2: Plot Mohr's Circle geometrically to determine absolute maximum in-plane shear stresses and principal stresses ($\\sigma_1, \\sigma_2$) under combined axial and torsional loads.",
                    "Step 3: Apply boundary and compatibility equations rigorously to solve statically indeterminate beam deflections."
                ],
                "benefits": "Why this is the superior strategy: It eliminates sign-convention errors during multi-axis loading calculations and mirrors professional Eurocode/SANS structural design codes."
            }

        # 3. Numerical Methods
        elif "numerical" in mod or "methods" in mod:
            return {
                "module": "Numerical Methods",
                "proven_theory": "Taylor Series Truncation Error Bounds & Matrix Conditioning",
                "core_strategy": "Algorithmic Convergence Tracing & Iterative Residual Minimization",
                "steps": [
                    "Step 1: Map the Lipschitz condition geometrically for root-finding algorithms (Newton-Raphson vs. Secant method) to predict divergence before coding.",
                    "Step 2: Perform manual LU decomposition and Gauss-Seidel matrix iterations on 3x3 systems to verify diagonal dominance requirements.",
                    "Step 3: Track absolute and relative truncation error bounds across iterations to ensure precision thresholds are met."
                ],
                "benefits": "Why this is the superior strategy: It eliminates black-box programming errors and guarantees mathematical stability in finite-element pre-processing."
            }

        # 4. Structural Analysis
        elif "structural" in mod or "analysis" in mod:
            return {
                "module": "Structural Analysis",
                "proven_theory": "Principle of Virtual Work & Stiffness Matrix Transformations",
                "core_strategy": "Energy-Based Deflection Formulation & Castigliano's Second Theorem",
                "steps": [
                    "Step 1: Formulate internal strain energy storage equations ($U = \\int \\frac{M^2}{2EI} dx$) to resolve complex frame deflections efficiently.",
                    "Step 2: Assemble global structural stiffness matrices ($[K]\{d\} = \{F\}$) by applying local-to-global coordinate transformation matrices.",
                    "Step 3: Leverage structural symmetry and anti-symmetry boundaries to halve matrix dimensions and simplify manual computations."
                ],
                "benefits": "Why this is the superior strategy: It forms the exact mathematical foundation used by commercial Finite Element Analysis (FEA) software packages."
            }

        # 5. Geotechnical Engineering
        elif "geotechnical" in mod or "soil" in mod:
            return {
                "module": "Geotechnical Engineering",
                "proven_theory": "Terzaghi's 1D Consolidation Theory & Mohr-Coulomb Shear Failure Criterion",
                "core_strategy": "Effective Stress Principle ($\sigma' = \sigma - u$) & Orthogonal Flow Net Sketching",
                "steps": [
                    "Step 1: Separate total vertical stress vectors from pore water pressure ($u$) fluctuations in multi-layered clay and sand profiles.",
                    "Step 2: Construct orthogonal seepage flow nets obeying Laplace's equation to evaluate uplift pressures and piping risks.",
                    "Step 3: Plot triaxial shear test stress paths against the Mohr-Coulomb envelope to compute cohesion ($c'$) and friction angle ($\\phi'$)."
                ],
                "benefits": "Why this is the superior strategy: Prevents catastrophic foundation settlement errors and ensures accurate retaining wall stability designs."
            }

        # 6. Professional Communication / Technical Writing
        elif "comm" in mod or "writing" in mod or "report" in mod:
            return {
                "module": "Professional Communication",
                "proven_theory": "Shannon-Weaver Transmission Model & The Rhetorical Situation Framework",
                "core_strategy": "Top-Down Pyramid Principle & Plain English Technical Clause Reduction",
                "steps": [
                    "Step 1: Define audience technical baselines before drafting (separating project stakeholders, regulatory authorities, and lay clients).",
                    "Step 2: Structure formal engineering reports using the Pyramid Principle—placing executive summaries and key findings upfront.",
                    "Step 3: Purge passive voice bloat, nominalizations, and ambiguity to ensure unambiguous contractual and site specifications."
                ],
                "benefits": "Why this is the superior strategy: It eradicates contractual misunderstandings on-site, secures professional report approvals, and maximizes technical writing marks."
            }

        # Catch-all fallback if a completely unlisted module name is provided
        else:
            return {
                "module": module_name.upper(),
                "proven_theory": "First-Principles Phenomenological Modeling & System Boundary Analysis",
                "core_strategy": "Core Axiom Decomposition & Structured Problem Mapping",
                "steps": [
                    f"Step 1: Identify the primary governing laws and baseline definitions specific to {module_name.upper()}.",
                    "Step 2: Break complex problems down into fundamental boundary constraints and functional components.",
                    "Step 3: Execute targeted past-paper simulations coupled with active recall error logging."
                ],
                "benefits": f"Why this is the superior strategy: It forces deep conceptual mastery over surface-level memorization, ensuring adaptability across any exam question format for {module_name.upper()}."
            }
