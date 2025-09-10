from fastapi import FastAPI
from pydantic import BaseModel
import subprocess
import tempfile
import os

app = FastAPI()

# Request schema
class TestCase(BaseModel):
    input: str
    expectedOutput: str

class CodeRequest(BaseModel):
    language: str
    code: str
    testCases: list[TestCase]

# Language command mapping
LANG_COMMANDS = {
    "python": ["python3", "Main.py"],
    "javascript": ["node", "main.js"],
    "java": ["java", "Main"],
    "cpp": ["./main"]
}

@app.post("/run")
def execute_code(req: CodeRequest):
    results = []

    with tempfile.TemporaryDirectory() as tempdir:
        filename = None
        compile_cmd = None

        # Save code file depending on language
        if req.language == "python":
            filename = os.path.join(tempdir, "Main.py")
        elif req.language == "javascript":
            filename = os.path.join(tempdir, "main.js")
        elif req.language == "java":
            filename = os.path.join(tempdir, "Main.java")
            compile_cmd = ["javac", filename]
        elif req.language == "cpp":
            filename = os.path.join(tempdir, "main.cpp")
            compile_cmd = ["g++", filename, "-o", os.path.join(tempdir, "main")]
        else:
            return {"error": f"Unsupported language {req.language}"}

        # Write code into file
        with open(filename, "w") as f:
            f.write(req.code)

        # Compile if needed
        if compile_cmd:
            compile_proc = subprocess.run(
                compile_cmd, cwd=tempdir,
                capture_output=True, text=True
            )
            if compile_proc.returncode != 0:
                return {"error": compile_proc.stderr}

        # Run test cases
        for tc in req.testCases:
            try:
                run_cmd = LANG_COMMANDS[req.language]
                proc = subprocess.run(
                    run_cmd,
                    input=tc.input.encode(),  # ✅ encode input properly
                    cwd=tempdir,
                    capture_output=True,
                    timeout=5
                )
                output = proc.stdout.decode().strip()
                results.append({
                    "input": tc.input,
                    "expected": tc.expectedOutput,
                    "output": output,
                    "passed": output == tc.expectedOutput
                })
            except Exception as e:
                results.append({
                    "input": tc.input,
                    "expected": tc.expectedOutput,
                    "output": str(e),
                    "passed": False
                })

    return {"results": results}
