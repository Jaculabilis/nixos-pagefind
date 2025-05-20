{
  lib,
  python3Packages,
}:
python3Packages.buildPythonApplication rec {
    pname = "staticgen";
    version = "0.0.0";
    pyproject = true;

    src = ./.;

    build-system = with python3Packages; [ hatchling ];

    dependencies = with python3Packages; [ hatchling jinja2 ];
}