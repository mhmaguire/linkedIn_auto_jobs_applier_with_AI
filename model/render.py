import uuid
import tempfile
from pathlib import Path

from page.util import html_to_pdf


html_template = """
<!DOCTYPE html>
<title>Resume</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<script src="{casual_markdown}"></script>
<script src="{reorganize_header}"></script>
<link rel="stylesheet" href="{resume_css}">
<body onload="document.body.innerHTML=md.html(document.body.innerHTML); document.body.style.display='block';">
"""


class PdfRenderer:
    def __init__(self, outdir="generated") -> None:
        self.template = html_template.format(
            casual_markdown=Path("resume_template/casual_markdown.js").absolute(),
            reorganize_header=Path("resume_template/reorganizeHeader.js").absolute(),
            resume_css=Path("resume_template/resume.css").absolute(),
        )

        self.outdir = Path(outdir)
        self.outdir.mkdir(parents=True, exist_ok=True)

    def __call__(self, content):
        content = self.template + content
        outpath = self.__filepath()

        with tempfile.NamedTemporaryFile(
            suffix=".html", mode="w", encoding="utf-8"
        ) as tmp:
            tmp_path = Path(tmp.name)
            tmp_path.write_text(content)
            pdf = html_to_pdf(tmp_path)
            outpath.write_bytes(pdf)

        return outpath

    def __filepath(self):
        return self.outdir / f"{uuid.uuid4().hex}.pdf"
