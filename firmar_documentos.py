#!/usr/bin/env python3
"""
Estampa una imagen de firma en lote sobre archivos PDF, Word (.docx) y Excel (.xlsx).

La posicion se calcula con un TEXTO ANCLA (p. ej. "REPRESENTANTE DEL INEI"):
la firma se coloca justo encima del texto encontrado.

Uso (interfaz grafica):   python firmar_documentos.py
Uso (linea de comandos):  python firmar_documentos.py --cli CARPETA_ENTRADA CARPETA_SALIDA \
                              --firma firma.png --ancla "REPRESENTANTE DEL INEI"

Dependencias:  pip install pymupdf python-docx openpyxl pillow
(tkinter viene con Python; en Linux: sudo apt install python3-tk)

IMPORTANTE: usar solo con la autorizacion de la persona titular de la firma.
"""
from __future__ import annotations

import argparse
import io
import sys
from dataclasses import dataclass
from pathlib import Path

from PIL import Image

EXTENSIONES = {".pdf", ".docx", ".xlsx"}


@dataclass
class Opciones:
    firma: Path
    ancla: str = "REPRESENTANTE DEL INEI"
    ocurrencia: int = 1          # 1 = primera coincidencia del ancla
    alto_pt: float = 50.0        # alto de la firma en puntos (el ancho se calcula)
    desplazamiento_y: float = 14.0  # puntos extra hacia arriba (para saltar la etiqueta "(Firma)")
    quitar_fondo: bool = True    # vuelve transparente el papel blanco de la firma
    # Respaldo para PDFs escaneados (sin texto buscable): posicion relativa de la base
    # de la firma como fraccion de la pagina (0-1). None = desactivado.
    respaldo_x: float | None = 0.63
    respaldo_y: float | None = 0.70


# --------------------------------------------------------------------------- imagen
def preparar_firma(ruta: Path, quitar_fondo: bool) -> bytes:
    """Devuelve la firma como PNG (opcionalmente con fondo transparente y recortada)."""
    img = Image.open(ruta).convert("RGB")
    if quitar_fondo:
        gris = img.convert("L")
        alfa = gris.point(lambda v: max(0, min(255, (235 - v) * 4)))
        img = img.convert("RGBA")
        img.putalpha(alfa)
        caja = alfa.getbbox()
        if caja:
            img = img.crop(caja)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


def _dimensiones(png: bytes) -> tuple[int, int]:
    return Image.open(io.BytesIO(png)).size


# --------------------------------------------------------------------------- PDF
def firmar_pdf(origen: Path, destino: Path, png: bytes, op: Opciones) -> int:
    import fitz  # PyMuPDF

    w, h = _dimensiones(png)
    alto = op.alto_pt
    ancho = alto * w / h
    colocadas = 0
    doc = fitz.open(origen)
    visto = 0
    for pagina in doc:
        for r in pagina.search_for(op.ancla):
            visto += 1
            if visto != op.ocurrencia:
                continue
            cx = (r.x0 + r.x1) / 2
            y1 = r.y0 - op.desplazamiento_y
            rect = fitz.Rect(cx - ancho / 2, y1 - alto, cx + ancho / 2, y1)
            pagina.insert_image(rect, stream=png, keep_proportion=True, overlay=True)
            colocadas += 1
    if not colocadas and op.respaldo_x is not None and op.respaldo_y is not None and len(doc):
        pagina = doc[len(doc) - 1]  # el escaneo suele tener la firma en la ultima pagina
        W, H = pagina.rect.width, pagina.rect.height
        cx, y1 = W * op.respaldo_x, H * op.respaldo_y
        rect = fitz.Rect(cx - ancho / 2, y1 - alto, cx + ancho / 2, y1)
        pagina.insert_image(rect, stream=png, keep_proportion=True, overlay=True)
        colocadas = 1
    if colocadas:
        doc.save(destino, garbage=3, deflate=True)
    doc.close()
    return colocadas


# --------------------------------------------------------------------------- Word
def _parrafos(doc):
    """Itera parrafos del cuerpo y de las tablas (incluye tablas anidadas)."""
    def desde_tabla(t):
        for fila in t.rows:
            for celda in fila.cells:
                yield from celda.paragraphs
                for sub in celda.tables:
                    yield from desde_tabla(sub)

    yield from doc.paragraphs
    for t in doc.tables:
        yield from desde_tabla(t)


def firmar_docx(origen: Path, destino: Path, png: bytes, op: Opciones) -> int:
    import copy

    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.shared import Pt

    doc = Document(origen)
    visto = 0
    for p in _parrafos(doc):
        if op.ancla.lower() not in p.text.lower():
            continue
        visto += 1
        if visto != op.ocurrencia:
            continue
        # Parrafo nuevo, centrado, justo antes del ancla, con la imagen
        nuevo = copy.deepcopy(p._p)
        for hijo in list(nuevo):
            if hijo.tag != nuevo.tag.replace("}p", "}pPr"):
                nuevo.remove(hijo)
        p._p.addprevious(nuevo)
        from docx.text.paragraph import Paragraph
        par = Paragraph(nuevo, p._parent)
        par.alignment = WD_ALIGN_PARAGRAPH.CENTER
        par.paragraph_format.space_after = Pt(0)
        par.add_run().add_picture(io.BytesIO(png), height=Pt(op.alto_pt))
        doc.save(destino)
        return 1
    return 0


# --------------------------------------------------------------------------- Excel
def firmar_xlsx(origen: Path, destino: Path, png: bytes, op: Opciones) -> int:
    from openpyxl import load_workbook
    from openpyxl.drawing.image import Image as XLImage

    wb = load_workbook(origen)
    visto = 0
    for hoja in wb.worksheets:
        for fila in hoja.iter_rows():
            for celda in fila:
                if isinstance(celda.value, str) and op.ancla.lower() in celda.value.lower():
                    visto += 1
                    if visto != op.ocurrencia:
                        continue
                    w, h = _dimensiones(png)
                    img = XLImage(io.BytesIO(png))
                    img.height = int(op.alto_pt * 96 / 72)      # puntos -> pixeles
                    img.width = int(img.height * w / h)
                    fila_dest = max(1, celda.row - 1)           # una fila encima del ancla
                    hoja.add_image(img, f"{celda.column_letter}{fila_dest}")
                    wb.save(destino)
                    return 1
    return 0


PROCESADORES = {".pdf": firmar_pdf, ".docx": firmar_docx, ".xlsx": firmar_xlsx}


# --------------------------------------------------------------------------- lote
def procesar_carpeta(entrada: Path, salida: Path, op: Opciones, log=print) -> tuple[int, int]:
    salida.mkdir(parents=True, exist_ok=True)
    png = preparar_firma(op.firma, op.quitar_fondo)
    ok = fallos = 0
    archivos = sorted(p for p in entrada.iterdir()
                      if p.suffix.lower() in EXTENSIONES and not p.name.startswith("~$"))
    if not archivos:
        log("No hay archivos PDF, DOCX o XLSX en la carpeta.")
    for f in archivos:
        destino = salida / f"{f.stem}_firmado{f.suffix.lower()}"
        try:
            n = PROCESADORES[f.suffix.lower()](f, destino, png, op)
            if n:
                log(f"OK      {f.name} -> {destino.name}")
                ok += 1
            else:
                log(f"SIN ANCLA  {f.name}: no se encontro '{op.ancla}' (ocurrencia {op.ocurrencia})")
                fallos += 1
        except Exception as e:  # un archivo malo no detiene el lote
            log(f"ERROR   {f.name}: {e}")
            fallos += 1
    log(f"\nTerminado: {ok} firmados, {fallos} con problemas.")
    return ok, fallos


# --------------------------------------------------------------------------- GUI
def lanzar_gui() -> None:
    import threading
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext, ttk

    root = tk.Tk()
    root.title("Firmar documentos en lote")
    root.geometry("660x640")

    v = {k: tk.StringVar() for k in ("entrada", "salida", "firma")}
    v["ancla"] = tk.StringVar(value="REPRESENTANTE DEL INEI")
    v["ocurrencia"] = tk.StringVar(value="1")
    v["alto"] = tk.StringVar(value="50")
    v["dy"] = tk.StringVar(value="14")
    v["rx"] = tk.StringVar(value="0.63")
    v["ry"] = tk.StringVar(value="0.70")

    def fila(r, texto, var, buscar=None):
        ttk.Label(root, text=texto).grid(row=r, column=0, sticky="e", padx=6, pady=4)
        ttk.Entry(root, textvariable=var, width=52).grid(row=r, column=1, pady=4)
        if buscar:
            ttk.Button(root, text="...", width=3, command=buscar).grid(row=r, column=2)

    fila(0, "Carpeta de entrada:", v["entrada"], lambda: v["entrada"].set(filedialog.askdirectory() or v["entrada"].get()))
    fila(1, "Carpeta de salida:", v["salida"], lambda: v["salida"].set(filedialog.askdirectory() or v["salida"].get()))
    fila(2, "Imagen de la firma:", v["firma"], lambda: v["firma"].set(
        filedialog.askopenfilename(filetypes=[("Imagen", "*.png *.jpg *.jpeg *.gif")]) or v["firma"].get()))
    fila(3, "Texto ancla:", v["ancla"])
    fila(4, "Ocurrencia (1, 2...):", v["ocurrencia"])
    fila(5, "Alto firma (pt):", v["alto"])
    fila(6, "Subir firma (pt):", v["dy"])

    fila(7, "PDF escaneado: X (0-1):", v["rx"])
    fila(8, "PDF escaneado: Y (0-1):", v["ry"])
    quitar = tk.BooleanVar(value=True)
    ttk.Checkbutton(root, text="Quitar fondo blanco de la firma", variable=quitar).grid(row=9, column=1, sticky="w")

    log = scrolledtext.ScrolledText(root, height=14, width=76, state="disabled")
    log.grid(row=11, column=0, columnspan=3, padx=6, pady=8)

    def escribir(msg):
        def _w():
            log.configure(state="normal")
            log.insert("end", msg + "\n")
            log.see("end")
            log.configure(state="disabled")
        root.after(0, _w)

    def ejecutar():
        try:
            op = Opciones(Path(v["firma"].get()), v["ancla"].get().strip(), int(v["ocurrencia"].get()),
                          float(v["alto"].get()), float(v["dy"].get()), quitar.get(),
                          float(v["rx"].get()), float(v["ry"].get()))
            ent, sal = Path(v["entrada"].get()), Path(v["salida"].get())
            if not (ent.is_dir() and op.firma.is_file() and op.ancla and v["salida"].get()):
                raise ValueError("Completa carpeta de entrada, salida, firma y texto ancla.")
        except ValueError as e:
            messagebox.showerror("Datos incompletos", str(e))
            return
        if not messagebox.askyesno("Confirmar", "¿Tienes autorización de la titular para estampar esta firma?"):
            return
        boton.configure(state="disabled")

        def tarea():
            try:
                procesar_carpeta(ent, sal, op, escribir)
            finally:
                root.after(0, lambda: boton.configure(state="normal"))
        threading.Thread(target=tarea, daemon=True).start()

    boton = ttk.Button(root, text="Firmar documentos", command=ejecutar)
    boton.grid(row=10, column=1, pady=8)
    root.mainloop()


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cli", nargs=2, metavar=("ENTRADA", "SALIDA"), help="modo sin interfaz")
    ap.add_argument("--firma", type=Path)
    ap.add_argument("--ancla", default="REPRESENTANTE DEL INEI")
    ap.add_argument("--ocurrencia", type=int, default=1)
    ap.add_argument("--alto", type=float, default=50)
    ap.add_argument("--subir", type=float, default=14)
    ap.add_argument("--conservar-fondo", action="store_true")
    ap.add_argument("--sin-respaldo", action="store_true",
                    help="no usar posicion relativa en PDFs escaneados")
    ap.add_argument("--respaldo", nargs=2, type=float, metavar=("X", "Y"), default=(0.63, 0.70),
                    help="posicion relativa (0-1) de la base de la firma en PDFs escaneados")
    a = ap.parse_args()
    if a.cli:
        if not a.firma:
            sys.exit("Falta --firma")
        op = Opciones(a.firma, a.ancla, a.ocurrencia, a.alto, a.subir, not a.conservar_fondo,
                      None if a.sin_respaldo else a.respaldo[0], None if a.sin_respaldo else a.respaldo[1])
        procesar_carpeta(Path(a.cli[0]), Path(a.cli[1]), op)
    else:
        lanzar_gui()


if __name__ == "__main__":
    main()
