import glob, importlib.util, inspect, os

def test_template(f):
    spec = importlib.util.spec_from_file_location("mod", f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    
    if not hasattr(mod, "compute_totals"):
        return "No compute_totals"
        
    items = [("Test Item", 2, 100.0)]
    
    sig = inspect.signature(mod.compute_totals)
    kwargs = {}
    for param_name in sig.parameters:
        if param_name == "items":
            kwargs["items"] = items
            continue
            
        var_name = param_name.upper()
        potential_vars = [var_name]
        if var_name.endswith("_PCT"):
            potential_vars.append(var_name.replace("_PCT", "_PERCENT"))
            
        val_found = False
        for pv in potential_vars:
            if hasattr(mod, pv):
                kwargs[param_name] = getattr(mod, pv)
                val_found = True
                break
                
        if not val_found:
            kwargs[param_name] = 0.0
            
    try:
        res = mod.compute_totals(**kwargs)
        if isinstance(res, tuple):
            return res[-1]
        return res
    except Exception as e:
        return f"Error: {e}"

for f in glob.glob("/home/aditya/Desktop/UFLP/streamlit_app/templates/*.py"):
    res = test_template(f)
    print(f"{os.path.basename(f)}: {res}")
