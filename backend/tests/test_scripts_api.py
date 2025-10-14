"""
Integration Tests für Scripts API
"""
import io

import pytest


class TestUploadEndpoint:
    """Tests für /api/v1/scripts/upload Endpoint."""

    def test_upload_fountain_script(self, client, sample_fountain_content):
        """Test: Fountain-Script hochladen."""
        files = {"file": ("test.fountain", io.BytesIO(sample_fountain_content), "text/plain")}

        response = client.post("/api/v1/scripts/upload", files=files)

        assert response.status_code == 201

        data = response.json()
        assert "script_id" in data
        assert data["filename"] == "test.fountain"
        assert data["format"] == "fountain"
        assert data["scenes_count"] == 4  # Sample hat 4 Szenen
        assert data["pages"] >= 1
        assert "upload_time" in data

    def test_upload_unsupported_format(self, client, invalid_content):
        """Test: Nicht unterstütztes Format."""
        files = {"file": ("invalid.txt", io.BytesIO(invalid_content), "text/plain")}

        response = client.post("/api/v1/scripts/upload", files=files)

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert data["detail"]["error"] == "unsupported_format"
        assert "supported_formats" in data["detail"]

    def test_upload_file_too_large(self, client):
        """Test: Datei zu groß (>50 MB)."""
        # Erstelle großen Content (51 MB)
        large_content = b"x" * (51 * 1024 * 1024)
        files = {"file": ("large.fountain", io.BytesIO(large_content), "text/plain")}

        response = client.post("/api/v1/scripts/upload", files=files)

        assert response.status_code == 413
        assert "too large" in response.json()["detail"].lower()

    def test_upload_simple_scene(self, client, simple_fountain_content):
        """Test: Einfache Szene hochladen."""
        files = {"file": ("simple.fountain", io.BytesIO(simple_fountain_content), "text/plain")}

        response = client.post("/api/v1/scripts/upload", files=files)

        assert response.status_code == 201
        data = response.json()
        assert data["scenes_count"] == 1

    def test_upload_multi_scene(self, client, multi_scene_fountain):
        """Test: Multi-Scene Script hochladen."""
        files = {"file": ("multi.fountain", io.BytesIO(multi_scene_fountain), "text/plain")}

        response = client.post("/api/v1/scripts/upload", files=files)

        assert response.status_code == 201
        data = response.json()
        assert data["scenes_count"] == 3


class TestHealthEndpoint:
    """Tests für Health-Check Endpoint."""

    def test_health_check(self, client):
        """Test: Health-Check funktioniert."""
        response = client.get("/api/v1/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        assert "services" in data


class TestRootEndpoint:
    """Tests für Root-Endpoint."""

    def test_root(self, client):
        """Test: Root-Endpoint gibt Info zurück."""
        response = client.get("/")

        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "Scene Analyzer" in data["message"]
        assert "docs" in data
