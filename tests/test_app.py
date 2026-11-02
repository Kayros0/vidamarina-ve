"""Pruebas de humo y de flujo con el cliente de pruebas de Flask."""
import re
import unittest

from app import create_app
from app.extensions import db
from app.models import Species, User
from config import Config


class TestConfig(Config):
    TESTING = True
    SECRET_KEY = "clave-de-pruebas"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    ADMIN_USERNAME = "admin"
    ADMIN_EMAIL = "admin@test.local"
    ADMIN_PASSWORD = "Admin1234!"


class VidaMarinaTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TestConfig)

    def setUp(self):
        self.client = self.app.test_client()

    # ---------------------------- Catálogo ----------------------------
    def test_home_loads_with_catalog(self):
        response = self.client.get("/")
        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Vida marina y de ríos", body)
        self.assertIn("Delfín rosado", body)
        self.assertIn('class="species-card', body)

    def test_search_is_accent_insensitive(self):
        response = self.client.get("/?q=delfin")
        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Delfín rosado", body)
        self.assertIn("Delfín nariz de botella", body)
        self.assertNotIn("Tortuga carey", body)

    def test_filter_by_region(self):
        response = self.client.get("/?region=rios")
        body = response.get_data(as_text=True)
        self.assertIn("Delfín rosado", body)
        self.assertIn("Caimán del Orinoco", body)
        self.assertNotIn("Tortuga carey", body)

    def test_sort_by_rarity_starts_with_critically_endangered(self):
        response = self.client.get("/?orden=rareza")
        body = response.get_data(as_text=True)
        cards = re.findall(r'class="species-card.*?</article>', body, re.S)
        self.assertTrue(cards)
        self.assertIn("badge-CR", cards[0])

    def test_species_detail(self):
        with self.app.app_context():
            species = Species.query.filter_by(scientific_name="Inia geoffrensis").first()
            species_id = species.id
        response = self.client.get(f"/especie/{species_id}")
        body = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Delfín rosado", body)
        self.assertIn("Inia geoffrensis", body)

    def test_map_and_sources(self):
        self.assertEqual(self.client.get("/mapa").status_code, 200)
        self.assertEqual(self.client.get("/fuentes").status_code, 200)

    def test_api_returns_json(self):
        response = self.client.get("/api/especies?q=tortuga")
        data = response.get_json()
        self.assertEqual(response.status_code, 200)
        self.assertGreater(data["count"], 0)
        self.assertTrue(all("tortuga" in item["common_name"].lower() for item in data["results"]))

    def test_unknown_page_returns_404(self):
        self.assertEqual(self.client.get("/no-existe").status_code, 404)

    # --------------------------- Autenticación ---------------------------
    def test_register_then_login(self):
        response = self.client.post(
            "/cuenta/registro",
            data={
                "username": "estudiante",
                "email": "estudiante@example.com",
                "password": "ClaveSegura123",
                "confirm": "ClaveSegura123",
            },
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("Tu cuenta fue creada", response.get_data(as_text=True))

        self.client.post("/cuenta/salir", follow_redirects=True)
        response = self.client.post(
            "/cuenta/entrar",
            data={"identity": "estudiante", "password": "ClaveSegura123"},
            follow_redirects=True,
        )
        self.assertIn("Bienvenido de nuevo", response.get_data(as_text=True))

    def test_admin_area_requires_admin(self):
        self.client.post(
            "/cuenta/registro",
            data={
                "username": "visitante",
                "email": "visitante@example.com",
                "password": "ClaveSegura123",
                "confirm": "ClaveSegura123",
            },
            follow_redirects=True,
        )
        self.assertEqual(self.client.get("/admin/").status_code, 403)

    def test_admin_can_open_panel(self):
        response = self.client.post(
            "/cuenta/entrar",
            data={"identity": "admin", "password": "Admin1234!"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get("/admin/").status_code, 200)

    def test_admin_crud_flow(self):
        self.client.post(
            "/cuenta/entrar",
            data={"identity": "admin", "password": "Admin1234!"},
        )

        payload = {
            "common_name": "Especie de prueba",
            "scientific_name": "Testus probatus",
            "group": "pez",
            "region": "caribe",
            "habitat": "Arrecife de prueba",
            "description": "Descripción de prueba para el CRUD.",
            "iucn_status": "LC",
            "iucn_year": "2020",
            "described_year": "2000",
            "image_url": "",
            "image_author": "",
            "image_license": "",
            "source_url": "",
            "map_lat": "10.0",
            "map_lng": "-64.0",
            "map_label": "Lugar de prueba",
        }

        response = self.client.post("/admin/nueva", data=payload, follow_redirects=True)
        self.assertIn("se agregó al catálogo", response.get_data(as_text=True))

        with self.app.app_context():
            species = Species.query.filter_by(scientific_name="Testus probatus").first()
            self.assertIsNotNone(species)
            species_id = species.id

        payload["common_name"] = "Especie editada"
        response = self.client.post(
            f"/admin/{species_id}/editar", data=payload, follow_redirects=True
        )
        self.assertIn("se actualizó correctamente", response.get_data(as_text=True))

        with self.app.app_context():
            species = db.session.get(Species, species_id)
            self.assertEqual(species.common_name, "Especie editada")

        response = self.client.post(
            f"/admin/{species_id}/eliminar", follow_redirects=True
        )
        self.assertIn("se eliminó del catálogo", response.get_data(as_text=True))

        with self.app.app_context():
            self.assertIsNone(db.session.get(Species, species_id))

    def test_password_is_hashed(self):
        with self.app.app_context():
            admin = User.query.filter_by(username="admin").first()
            self.assertNotEqual(admin.password_hash, "Admin1234!")
            self.assertTrue(admin.check_password("Admin1234!"))


if __name__ == "__main__":
    unittest.main()
