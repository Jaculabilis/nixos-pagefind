import argparse
import json
from pathlib import Path
from typing import Any

parser = argparse.ArgumentParser()
parser.add_argument("out", help="out dir")
parser.add_argument("files", nargs="+", help="input files, .json list of objects")
args = parser.parse_args()

out_dir: Path = Path(args.out)
packages = out_dir / "package"

input_files: list[str] = args.files
for _, input_file in enumerate(input_files):
    with open(input_file) as f:
        file_data: list[dict[str, Any]] = json.load(f)
    for i, data in enumerate(file_data):
        type_: str = data.get("type", "")
        attr_name: str = data.get("package_attr_name", "")
        if type_ != "package":
            continue
        if not (attr_name in ("android-tools", "hello", "hello-cpp") or i % 100 == 0):
            continue  # pare down packages while testing

        attr_set: str = data.get("package_attr_set") or ""
        pname: str = data.get("package_pname") or ""
        pversion: str = data.get("package_pversion") or ""
        platforms: list[str] = data.get("package_platforms") or []
        outputs: list[str] = data.get("package_outputs") or []
        default_output: str = data.get("package_default_output") or ""
        programs: list[str] = data.get("package_programs") or []
        license_: list[dict] = data.get("package_license") or []
        maintainers: list[dict] = data.get("package_maintainers") or []
        teams: list[dict] = data.get("package_teams") or []
        description: str = data.get("package_description") or ""
        long_description: str = data.get("package_longDescription") or ""
        homepage: list[str] = data.get("package_homepage") or []
        position: str = data.get("package_position") or ""

        file_name = f"{attr_name}.html"
        file_path = packages / file_name
        file_path.parent.mkdir(parents=True, exist_ok=True)

        content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{attr_name}</title>
</head>
<body>"""
        indicator = '<span data-pagefind-filter="type:package">[P]</span>'
        content += f"""
    <h2 data-pagefind-filter="package set:{attr_set}">{indicator} {attr_name}</h2>
    <p data-pagefind-meta="description">{description}</p>
    <ul>
    """
        content += f"\n<li>{attr_name}</li>" if attr_name else ""
        content += f"\n<li>{pversion}</li>" if pversion else ""
        content += f'\n<li><a href="{homepage[0]}">Homepage</a></li>' if homepage else ""
        content += f'\n<li><a href="{position}">Source</a></li>' if position else ""
        for lic in license_:
            content += f'\n<li>License: <a href="{lic["url"]}">{lic["fullName"]}</a></li>'
        content += '</ul>'
        content += "<details>"
        content += "<summary>Package details</summary>"
        content += long_description
        content += "<h4>Programs provided</h4>"
        if programs:
            content += f'<p>{", ".join(programs)}</p>'
        else:
            content += "<p>This package provides no programs.</p>"
        content += "<h4>Maintainers</h4>"
        if maintainers:
            content += "<ul>"
            for maintainer in maintainers:
                mname = maintainer.get("name", "Anonymous")
                mgithub = maintainer.get("github", "")
                memail = maintainer.get("email", "")
                name_span = f'<span data-pagefind-filter="maintainer">{mname}</span>'
                content += "\n<li>"
                content += f'<a href="https://github.com/{mgithub}">{name_span}</a>' if mgithub else mname
                if memail:
                    content += f' &lt<a href="mailto:{memail}">{memail}</a>&gt;'
                content += "</li>"
            content += "</ul>"
        else:
            content += '<p data-pagefind-filter="maintainer:Unmaintained">This package has no maintainers. If you find it useful, please consider becoming a maintainer!</p>'
        if platforms:
            content += "\n<h4>Platforms</h4>"
            content += "<ul>"
            for platform in sorted(platforms):
                content += f'\n<li data-pagefind-filter="platform">{platform}</li>'
            content += "</ul>"
        content += "</details>"
        content += """
</body>
</html>
"""
        file_path.write_text(content)

index = Path("index.html")
(out_dir / "index.html").write_text(index.read_text())
