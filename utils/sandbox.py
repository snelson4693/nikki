import os
import tempfile
import traceback
import subprocess

def run_code_sandbox(code: str) -> dict:
    """
    Executes the given code in a temporary isolated Python sandbox environment.
    Returns a dictionary with execution results or error trace.
    """
    result = {
        "success": False,
        "output": "",
        "error": ""
    }

    try:
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as temp_file:
            temp_file.write(code)
            temp_file_path = temp_file.name

        # Run the file using a subprocess with limited resources
        process = subprocess.run(
            ["python", temp_file_path],
            capture_output=True,
            text=True,
            timeout=10  # prevent hanging
        )

        result["output"] = process.stdout
        result["error"] = process.stderr

        if process.returncode == 0:
            result["success"] = True
        else:
            result["success"] = False

    except subprocess.TimeoutExpired:
        result["error"] = "Execution timed out."
        result["success"] = False
    except Exception:
        result["error"] = traceback.format_exc()
        result["success"] = False
    finally:
        try:
            os.remove(temp_file_path)
        except Exception:
            pass  # If cleanup fails, ignore

    return result
