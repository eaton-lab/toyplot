# Copyright 2014, Sandia Corporation. Under the terms of Contract
# DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government retains certain
# rights in this software.

import argparse
import os
import re
import shutil
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument("command", nargs="?", default="build", choices=["build", "clean"], help="Command to run.")
arguments = parser.parse_args()

root_dir = os.path.abspath(os.path.join(__file__, "..", ".."))
docs_dir = os.path.join(root_dir, "docs")
build_dir = os.path.join(docs_dir, "_build")
test_dir = os.path.join(docs_dir, "_test")

def convert_notebook(name):
    # If the Sphinx source is up-to-date, we're done.
    source = os.path.join(docs_dir, "%s.ipynb" % name)
    target = os.path.join(docs_dir, "%s.rst" % name)
    if os.path.exists(target) and os.path.getmtime(
            target) >= os.path.getmtime(source):
        return

    # Convert the notebook to pure Python, so we can run verify
    # that it runs without any errors.

    if not os.path.exists(test_dir):
        os.mkdir(test_dir)

    subprocess.check_call(["ipython",
                           "nbconvert",
                           "--execute",
                           "--to",
                           "python",
                           source,
                           "--output",
                           os.path.join(test_dir,
                                        name)])

    subprocess.check_call(["python", os.path.join(test_dir, "%s.py" % name)])

    # Convert the notebook into restructured text suitable for the
    # documentation.
    subprocess.check_call(["ipython",
                           "nbconvert",
                           "--execute",
                           "--to",
                           "rst",
                           source,
                           "--output",
                           os.path.join(docs_dir,
                                        name)])

    # Unmangle Sphinx cross-references in the tutorial that get mangled by
    # markdown.
    with open(target, "r") as file:
        content = file.read()
        content = re.sub(":([^:]+):``([^`]+)``", ":\\1:`\\2`", content)
        content = re.sub("[.][.].*(_[^:]+):", ".. \\1:", content)

        content = """
  .. image:: ../artwork/toyplot.png
    :width: 200px
    :align: right
  """ + content

    with open(target, "w") as file:
        file.write(content)

# Always build the documentation from scratch.
if os.path.exists(build_dir):
    shutil.rmtree(build_dir)

notebooks = [
        "canvas-layout",
        "cartesian-axes",
        "color",
        "convenience-api",
        "data-tables",
        "interaction",
        "labels-and-legends",
        "markers",
        "matrix-visualization",
        "null-data",
        "number-lines",
        "rendering",
        "table-axes",
        "text",
        "tick-locators",
        "tutorial",
        "units"]

# Clean the build.
if arguments.command == "clean":
    for name in notebooks:
        os.remove("%s.rst" % name)

# Generate the HTML documentation.
if arguments.command == "build":
    for name in notebooks:
        convert_notebook(name)
    subprocess.check_call(["make", "html"], cwd=docs_dir)
