import json
from pathlib import Path
import pytest
from pytest_mock import MockerFixture
from client import data

def test_extract_content_from_ipynb_success(mocker: MockerFixture):
    """Test extract_content_from_ipynb with valid notebook."""
    mock_file = mocker.mock_open(read_data=json.dumps({
        "cells": [
            {"cell_type": "markdown", "source": ["# Title\n", "Text"]},
            {"cell_type": "code", "source": ["print('Hello')"]},
            {"cell_type": "unknown", "source": ["Other"]}
        ]
    }))
    mocker.patch("pathlib.Path.read_text", mock_file)

    content = data.extract_content_from_ipynb(Path("test.ipynb"))

    expected = (
        "### Cell 1: Markdown\n"
        "# Title\nText\n\n"
        "### Cell 2: Code\n"
        "print('Hello')\n\n"
        "### Cell 3: unknown\n"
        "Other\n\n"
    )
    assert content == expected

def test_extract_content_from_ipynb_empty(mocker: MockerFixture):
    """Test extract_content_from_ipynb with empty notebook."""
    mock_file = mocker.mock_open(read_data=json.dumps({"cells": []}))
    mocker.patch("pathlib.Path.read_text", mock_file)

    content = data.extract_content_from_ipynb(Path("test.ipynb"))

    assert content == ""

def test_extract_content_from_ipynb_error(mocker: MockerFixture):
    """Test extract_content_from_ipynb with invalid JSON."""
    mocker.patch("pathlib.Path.read_text", side_effect=Exception("File error"))

    content = data.extract_content_from_ipynb(Path("test.ipynb"))

    assert content == "# Error reading test.ipynb: File error"

def test_export_code_and_directory_list_success(mocker: MockerFixture, tmp_path):
    """Test export_code_and_directory_list with .py and .ipynb files."""
    py_file = tmp_path / "test.py"
    py_file.write_text("print('Hello')", encoding="utf-8")
    ipynb_file = tmp_path / "test.ipynb"
    ipynb_file.write_text(json.dumps({
        "cells": [{"cell_type": "code", "source": ["print('World')"]}]
    }), encoding="utf-8")

    mocker.patch("pathlib.Path.rglob", return_value=[py_file, ipynb_file])
    mock_code = mocker.mock_open()
    mock_list = mocker.mock_open()
    mocker.patch("builtins.open", side_effect=[mock_code(), mock_list()])

    data.export_code_and_directory_list(root_directory=tmp_path, code_file="code.txt", list_file="dirs.txt")

    list_calls = mock_list().write.call_args_list
    assert str(py_file) in list_calls[0][0][0]
    assert str(ipynb_file) in list_calls[1][0][0]

    code_calls = mock_code().write.call_args_list
    assert f"# {py_file}" in code_calls[0][0][0]
    assert "print('Hello')" in code_calls[1][0][0]
    assert f"# {ipynb_file}" in code_calls[3][0][0]
    assert "### Cell 1: Code\nprint('World')" in code_calls[4][0][0]

def test_export_code_and_directory_list_error(mocker: MockerFixture, tmp_path):
    """Test export_code_and_directory_list with file read error."""
    py_file = tmp_path / "test.py"
    mocker.patch("pathlib.Path.rglob", return_value=[py_file])
    mocker.patch("pathlib.Path.read_text", side_effect=Exception("Read error"))
    mock_code = mocker.mock_open()
    mock_list = mocker.mock_open()
    mocker.patch("builtins.open", side_effect=[mock_code(), mock_list()])

    data.export_code_and_directory_list(root_directory_path=tmp_path, code_file="code.txt", list_file="dirs.txt")

    code_calls = mock_code().write.call_args_list
    assert f"# {py_file}" in code_calls[0][0]
    assert "# Error reading" in code_calls[1][0][0]