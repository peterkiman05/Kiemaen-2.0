with open("core/router.py", "r") as f:
    code = f.read()

# Force Agg backend before importing pyplot
old_import = "import matplotlib.pyplot as plt"
new_import = "import matplotlib\nmatplotlib.use('Agg')\nimport matplotlib.pyplot as plt"

if old_import in code:
    code = code.replace(old_import, new_import)
    with open("core/router.py", "w") as f:
        f.write(code)
    print("[SUCCESS] Applied headless Matplotlib backend patch.")
else:
    print("[INFO] Patch already applied or import pattern changed.")
