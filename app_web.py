#!/usr/bin/env python3
"""
Interfaz web para firmar documentos: sube la firma y los PDF/Word/Excel,
y descarga los archivos firmados (un ZIP si son varios).

    pip install -r requirements.txt
    python app_web.py          ->  abre http://localhost:5000

Usar solo con la autorizacion de la persona titular de la firma.
"""
import io
import tempfile
import webbrowser
import zipfile
from pathlib import Path

from flask import Flask, Response, request

from firmar_documentos import EXTENSIONES, PROCESADORES, Opciones, preparar_firma

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 200 * 1024 * 1024

PAGINA = """<!doctype html><html lang="es"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Firmar documentos</title>
<style>
body{font-family:system-ui,sans-serif;max-width:640px;margin:32px auto;padding:0 16px;color:#222}
h1{font-size:1.4rem} .zona{border:2px dashed #888;border-radius:10px;padding:22px;text-align:center;
margin:12px 0;background:#fafafa;cursor:pointer} .zona.on{background:#e8f0ff;border-color:#2b6cff}
.zona small{display:block;color:#666;margin-top:6px} label{display:block;margin:10px 0 4px;font-weight:600}
input[type=text],input[type=number]{width:100%;padding:8px;box-sizing:border-box}
.fila{display:flex;gap:12px}.fila>div{flex:1} button{margin-top:18px;padding:12px 22px;font-size:1rem;
background:#2b6cff;color:#fff;border:0;border-radius:8px;cursor:pointer} button:disabled{opacity:.5}
#msg{margin-top:14px;white-space:pre-wrap} .ok{color:#127a2e}.err{color:#b00020}
</style>
<h1>Firmar documentos en lote</h1>
<form id="f">
 <div class="zona" id="zf"><b>1. Imagen de la firma</b> (PNG/JPG)<small id="nf">Arrastra aquí o haz clic</small>
  <input type="file" id="firma" name="firma" accept="image/*" hidden required></div>
 <div class="zona" id="zd"><b>2. Documentos</b> (PDF, Word, Excel)<small id="nd">Arrastra aquí o haz clic</small>
  <input type="file" id="docs" name="docs" multiple accept=".pdf,.docx,.xlsx" hidden required></div>
 <label>Texto ancla (la firma va encima)</label>
 <input type="text" name="ancla" value="REPRESENTANTE DEL INEI" required>
 <div class="fila">
  <div><label>Ocurrencia</label><input type="number" name="ocurrencia" value="1" min="1"></div>
  <div><label>Alto firma (pt)</label><input type="number" name="alto" value="50" step="1"></div>
  <div><label>Subir (pt)</label><input type="number" name="subir" value="14" step="1"></div>
 </div>
 <div class="fila">
  <div><label>PDF escaneado: X (0-1)</label><input type="number" name="rx" value="0.63" step="0.01"></div>
  <div><label>PDF escaneado: Y (0-1)</label><input type="number" name="ry" value="0.70" step="0.01"></div>
 </div>
 <label><input type="checkbox" name="auth" required> Tengo autorización de la titular para estampar esta firma</label>
 <button id="b">Firmar y descargar</button>
 <div id="msg"></div>
</form>
<script>
function zona(z,i,n){const inp=document.getElementById(i),nom=document.getElementById(n),el=document.getElementById(z);
 const show=()=>nom.textContent=[...inp.files].map(f=>f.name).join(', ')||'Arrastra aquí o haz clic';
 el.onclick=()=>inp.click();inp.onchange=show;
 el.ondragover=e=>{e.preventDefault();el.classList.add('on')};el.ondragleave=()=>el.classList.remove('on');
 el.ondrop=e=>{e.preventDefault();el.classList.remove('on');inp.files=e.dataTransfer.files;show()}}
zona('zf','firma','nf');zona('zd','docs','nd');
f.onsubmit=async e=>{e.preventDefault();b.disabled=true;msg.className='';msg.textContent='Procesando…';
 const r=await fetch('/firmar',{method:'POST',body:new FormData(f)});
 const resumen=decodeURIComponent(r.headers.get('X-Resumen')||'');
 if(!r.ok){msg.className='err';msg.textContent=await r.text();b.disabled=false;return}
 const blob=await r.blob(),a=document.createElement('a');a.href=URL.createObjectURL(blob);
 a.download=decodeURIComponent(r.headers.get('X-Nombre'));a.click();msg.className='ok';msg.textContent=resumen;b.disabled=false}
</script></html>"""


@app.get("/")
def inicio():
    return PAGINA


@app.post("/firmar")
def firmar():
    firma = request.files.get("firma")
    docs = [d for d in request.files.getlist("docs") if d.filename]
    if not firma or not docs or not request.form.get("auth"):
        return Response("Faltan la firma, los documentos o la confirmación de autorización.", 400)
    try:
        op = Opciones(
            Path("firma"), request.form["ancla"].strip(), int(request.form["ocurrencia"]),
            float(request.form["alto"]), float(request.form["subir"]), True,
            float(request.form["rx"]), float(request.form["ry"]))
        png = preparar_firma(io.BytesIO(firma.read()), True)
    except Exception as e:
        return Response(f"Datos o firma no válidos: {e}", 400)

    salida, log = [], []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for i, d in enumerate(docs):
            nombre = Path(d.filename).name
            ext = Path(nombre).suffix.lower()
            if ext not in EXTENSIONES:
                log.append(f"IGNORADO {nombre}: formato no soportado")
                continue
            origen, destino = tmp / f"in{i}{ext}", tmp / f"out{i}{ext}"
            d.save(origen)
            try:
                n = PROCESADORES[ext](origen, destino, png, op)
            except Exception as e:
                log.append(f"ERROR {nombre}: {e}")
                continue
            if n:
                salida.append((f"{Path(nombre).stem}_firmado{ext}", destino.read_bytes()))
                log.append(f"OK {nombre}")
            else:
                log.append(f"SIN ANCLA {nombre}")

    resumen = "; ".join(log)
    cab = {"X-Resumen": resumen.encode("ascii", "ignore").decode().replace("\n", " ")}
    from urllib.parse import quote
    cab["X-Resumen"] = quote(resumen)
    if not salida:
        return Response("No se firmó ningún archivo. " + resumen, 422)
    if len(salida) == 1:
        nombre, datos = salida[0]
        cab["X-Nombre"] = quote(nombre)
        return Response(datos, headers=cab, mimetype="application/octet-stream")
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for nombre, datos in salida:
            z.writestr(nombre, datos)
    cab["X-Nombre"] = "documentos_firmados.zip"
    return Response(buf.getvalue(), headers=cab, mimetype="application/zip")


if __name__ == "__main__":
    webbrowser.open("http://localhost:5000")
    app.run(host="127.0.0.1", port=5000)
