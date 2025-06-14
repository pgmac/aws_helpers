import subprocess
import os
import sys

def get_base_prefix_compat():
    """Get base/real prefix, or sys.prefix if there is none."""
    return (
        getattr(sys, "base_prefix", None)
        or getattr(sys, "real_prefix", None)
        or sys.prefix
    )

def in_virtualenv():
    return sys.prefix != get_base_prefix_compat()

def activate(env_name):
    if not in_virtualenv():
        python_ver = f"python{sys.version_info.major}.{sys.version_info.minor}"
        subprocess.run(f"source {os.path.abspath(os.path.join(os.path.dirname(__file__),
                            env_name,
                            "bin",
                            "activate"))}", shell = True)
        pypath = os.path.abspath(os.path.join(os.path.dirname(__file__),
                            env_name,
                            "lib",
                            python_ver,
                            "site-packages"))
        sys.path.insert(0, pypath)
