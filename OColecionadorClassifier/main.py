from fastapi import FastAPI, File, UploadFile
import subprocess
import json
import tempfile

app = FastAPI()

@app.post("/api/classify")
async def classify(file: UploadFile = File(...)):
    image_bytes = await file.read()

    with tempfile.NamedTemporaryFile(delete=False) as temp:
        temp.write(image_bytes)
        temp.flush()

        result = subprocess.run(
            ["python", "worker.py"],
            input=image_bytes,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    if result.returncode != 0:
        return {"erro": result.stderr.decode()}

    output = json.loads(result.stdout.decode())
    threshold = 0.9
    if output["confianca"] < threshold:
        output["classe"] = "Indefinido"
    return output
