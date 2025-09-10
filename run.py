import os
import subprocess
import tempfile
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/run", methods=["POST"])
def run_code():
    data = request.get_json()
    language = data.get("language")
    code = data.get("code")
    test_cases = data.get("testCases", [])

    results = []

    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            if language == "python":
                file_path = os.path.join(temp_dir, "solution.py")
                with open(file_path, "w") as f:
                    f.write(code)
                for case in test_cases:
                    output = subprocess.run(
                        ["python3", file_path],
                        input=case.encode(),
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    results.append({"input": case, "output": output.stdout.strip(), "error": output.stderr.strip()})

            elif language == "cpp":
                file_path = os.path.join(temp_dir, "solution.cpp")
                exe_path = os.path.join(temp_dir, "a.out")
                with open(file_path, "w") as f:
                    f.write(code)
                compile_process = subprocess.run(["g++", file_path, "-o", exe_path], capture_output=True, text=True)
                if compile_process.returncode != 0:
                    return jsonify({"error": compile_process.stderr}), 400
                for case in test_cases:
                    output = subprocess.run(
                        [exe_path],
                        input=case.encode(),
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    results.append({"input": case, "output": output.stdout.strip(), "error": output.stderr.strip()})

            elif language == "java":
                file_path = os.path.join(temp_dir, "Solution.java")
                with open(file_path, "w") as f:
                    f.write(code)
                compile_process = subprocess.run(["javac", file_path], capture_output=True, text=True)
                if compile_process.returncode != 0:
                    return jsonify({"error": compile_process.stderr}), 400
                for case in test_cases:
                    output = subprocess.run(
                        ["java", "-cp", temp_dir, "Solution"],
                        input=case.encode(),
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    results.append({"input": case, "output": output.stdout.strip(), "error": output.stderr.strip()})

            elif language == "javascript":
                file_path = os.path.join(temp_dir, "solution.js")
                with open(file_path, "w") as f:
                    f.write(code)
                for case in test_cases:
                    output = subprocess.run(
                        ["node", file_path],
                        input=case.encode(),
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    results.append({"input": case, "output": output.stdout.strip(), "error": output.stderr.strip()})

            else:
                return jsonify({"error": "Unsupported language"}), 400

            return jsonify({"results": results})

        except subprocess.TimeoutExpired:
            return jsonify({"error": "Execution timed out"}), 408
        except Exception as e:
            return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
