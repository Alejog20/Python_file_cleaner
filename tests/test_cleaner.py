import unittest
import os
import shutil
import tempfile
import datetime
from unittest import mock
from cleaner import DirectoryCleaner, DownloadsCleaner

class TestDirectoryCleaner(unittest.TestCase):
    """Testing for DirectoryCleaner class"""
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        # Crear directorios temporales para las pruebas
        self.test_dir = tempfile.mkdtemp()
        self.archive_dir = tempfile.mkdtemp()
        
        # Crear instancia de DirectoryCleaner para las pruebas
        self.cleaner = DirectoryCleaner(target_directory=self.test_dir, 
                                        archive_base_dir=self.archive_dir)
        
        # Deshabilitar logging para las pruebas
        self.cleaner.logger.handlers = []
        
    def tearDown(self):
        """Limpieza después de cada prueba"""
        # Eliminar directorios temporales
        shutil.rmtree(self.test_dir, ignore_errors=True)
        shutil.rmtree(self.archive_dir, ignore_errors=True)
    
    def create_test_file(self, filename, content="test content"):
        """Crea un archivo de prueba en el directorio de prueba"""
        filepath = os.path.join(self.test_dir, filename)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath
    
    def test_init(self):
        """Prueba la inicialización de DirectoryCleaner"""
        self.assertEqual(self.cleaner.target_directory, self.test_dir)
        self.assertEqual(self.cleaner.archive_base_dir, self.archive_dir)
        
        # Verificar que se hayan creado las reglas predeterminadas
        self.assertIn(".csv", self.cleaner.rules)
        self.assertIn(".txt", self.cleaner.rules)
        
        # Verificar que el directorio de archivo exista
        self.assertTrue(os.path.exists(self.archive_dir))
    
    def test_add_rule(self):
        """Prueba la función add_rule"""
        # Agregar una nueva regla
        self.cleaner.add_rule(".test", "delete")
        self.assertEqual(self.cleaner.rules[".test"], "delete")
        
        # Actualizar una regla existente
        self.cleaner.add_rule(".csv", "delete")
        self.assertEqual(self.cleaner.rules[".csv"], "delete")
    
    def test_add_name_rule(self):
        """Prueba la función add_name_rule"""
        # Agregar una regla por nombre
        dest_dir = os.path.join(self.archive_dir, "TestDir")
        self.cleaner.add_name_rule(r"test", "move", dest_dir)
        
        # Verificar que la regla se haya agregado
        self.assertEqual(len(self.cleaner.name_rules), 2)  # La predeterminada EPAY + la nueva
        self.assertEqual(self.cleaner.name_rules[1]["action"], "move")
        self.assertEqual(self.cleaner.name_rules[1]["destination"], dest_dir)
        
        # Verificar que el directorio destino exista
        self.assertTrue(os.path.exists(dest_dir))
    
    def test_get_file_info(self):
        """Prueba la función _get_file_info"""
        # Crear un archivo de prueba
        filepath = self.create_test_file("test.txt")
        
        # Obtener información del archivo
        file_info = self.cleaner._get_file_info(filepath)
        
        # Verificar la información
        self.assertEqual(file_info["path"], filepath)
        self.assertEqual(file_info["name"], "test.txt")
        self.assertEqual(file_info["extension"], ".txt")
        self.assertIsInstance(file_info["size"], int)
        self.assertIsInstance(file_info["modified"], datetime.datetime)
        self.assertIsInstance(file_info["created"], datetime.datetime)
        
        # Probar con un archivo que no existe
        self.assertIsNone(self.cleaner._get_file_info("no_existe.txt"))
    
    @mock.patch.object(DirectoryCleaner, '_archive_file')
    def test_process_file_archive(self, mock_archive):
        """Prueba la función _process_file con una regla de archivo"""
        # Configurar una regla para archivar .txt
        self.cleaner.rules[".txt"] = "archive"
        
        # Crear información de archivo simulada
        file_info = {
            "path": "/path/to/test.txt",
            "name": "test.txt",
            "extension": ".txt"
        }
        
        # Procesar el archivo
        result = self.cleaner._process_file(file_info)
        
        # Verificar que se llamó a _archive_file
        mock_archive.assert_called_once_with(file_info)
        self.assertEqual(result, "archived")
    
    @mock.patch.object(DirectoryCleaner, '_delete_file')
    def test_process_file_delete(self, mock_delete):
        """Prueba la función _process_file con una regla de eliminación"""
        # Configurar una regla para eliminar .txt
        self.cleaner.rules[".txt"] = "delete"
        
        # Crear información de archivo simulada
        file_info = {
            "path": "/path/to/test.txt",
            "name": "test.txt",
            "extension": ".txt"
        }
        
        # Procesar el archivo
        result = self.cleaner._process_file(file_info)
        
        # Verificar que se llamó a _delete_file
        mock_delete.assert_called_once_with(file_info)
        self.assertEqual(result, "deleted")
    
    @mock.patch.object(DirectoryCleaner, '_move_file')
    def test_process_file_name_rule(self, mock_move):
        """Prueba la función _process_file con una regla de nombre"""
        # Configurar una regla por nombre
        dest_dir = os.path.join(self.archive_dir, "TestDir")
        self.cleaner.add_name_rule(r"test", "move", dest_dir)
        
        # Crear información de archivo simulada
        file_info = {
            "path": "/path/to/test_file.doc",
            "name": "test_file.doc",
            "extension": ".doc"
        }
        
        # Procesar el archivo
        result = self.cleaner._process_file(file_info)
        
        # Verificar que se llamó a _move_file
        mock_move.assert_called_once_with(file_info, dest_dir)
        self.assertEqual(result, "moved")
    
    def test_archive_file(self):
        """Prueba la función _archive_file"""
        # Crear un archivo de prueba
        filepath = self.create_test_file("test.txt")
        
        # Crear información de archivo
        file_info = self.cleaner._get_file_info(filepath)
        
        # Crear directorio de archivo para la extensión
        txt_dir = os.path.join(self.archive_dir, "TXT")
        os.makedirs(txt_dir, exist_ok=True)
        
        # Archivar el archivo
        with mock.patch('shutil.move') as mock_move:
            self.cleaner._archive_file(file_info)
            # Verificar que se llamó a shutil.move con los argumentos correctos
            mock_move.assert_called_once()
            self.assertEqual(mock_move.call_args[0][0], filepath)
            self.assertTrue(mock_move.call_args[0][1].startswith(txt_dir))
    
    def test_move_file(self):
        """Prueba la función _move_file"""
        # Crear un archivo de prueba
        filepath = self.create_test_file("test.txt")
        
        # Crear información de archivo
        file_info = self.cleaner._get_file_info(filepath)
        
        # Crear directorio destino
        dest_dir = os.path.join(self.archive_dir, "Destination")
        os.makedirs(dest_dir, exist_ok=True)
        
        # Mover el archivo
        with mock.patch('shutil.move') as mock_move:
            self.cleaner._move_file(file_info, dest_dir)
            # Verificar que se llamó a shutil.move con los argumentos correctos
            mock_move.assert_called_once()
            self.assertEqual(mock_move.call_args[0][0], filepath)
            self.assertEqual(mock_move.call_args[0][1], os.path.join(dest_dir, "test.txt"))
    
    def test_delete_file(self):
        """Prueba la función _delete_file"""
        # Crear un archivo de prueba
        filepath = self.create_test_file("test.txt")
        
        # Crear información de archivo
        file_info = self.cleaner._get_file_info(filepath)
        
        # Eliminar el archivo
        with mock.patch('os.remove') as mock_remove:
            self.cleaner._delete_file(file_info)
            # Verificar que se llamó a os.remove con el archivo correcto
            mock_remove.assert_called_once_with(filepath)
    
    @mock.patch('os.listdir')
    @mock.patch.object(DirectoryCleaner, '_get_file_info')
    @mock.patch.object(DirectoryCleaner, '_process_file')
    def test_clean_directory(self, mock_process, mock_get_info, mock_listdir):
        """Prueba la función clean_directory"""
        # Configurar mocks
        mock_listdir.return_value = ["file1.txt", "file2.csv", "folder"]
        
        def get_info_side_effect(path):
            if path.endswith("folder"):
                return None
            base = os.path.basename(path)
            return {
                "path": path,
                "name": base,
                "extension": os.path.splitext(base)[1],
                "modified": datetime.datetime.now(),
                "size": 100
            }
        
        mock_get_info.side_effect = get_info_side_effect
        mock_process.side_effect = ["archived", "deleted"]
        
        # Ejecutar limpieza
        stats = self.cleaner.clean_directory()
        
        # Verificar que se procesaron los archivos
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["archived"], 1)
        self.assertEqual(stats["deleted"], 1)
        
        # Verificar que se llamó a _process_file para cada archivo
        self.assertEqual(mock_process.call_count, 2)
    
    @mock.patch('os.listdir')
    @mock.patch.object(DirectoryCleaner, '_get_file_info')
    def test_get_directory_stats(self, mock_get_info, mock_listdir):
        """Prueba la función get_directory_stats"""
        # Configurar mocks
        mock_listdir.return_value = ["file1.txt", "file2.csv", "folder"]
        
        def get_info_side_effect(path):
            if path.endswith("folder"):
                return None
            base = os.path.basename(path)
            ext = os.path.splitext(base)[1]
            return {
                "path": path,
                "name": base,
                "extension": ext,
                "size": 1024 * 1024 if ext == ".txt" else 2 * 1024 * 1024
            }
        
        mock_get_info.side_effect = get_info_side_effect
        
        # Obtener estadísticas
        stats = self.cleaner.get_directory_stats()
        
        # Verificar estadísticas
        self.assertEqual(stats["total_files"], 2)
        self.assertEqual(stats["total_size"], 3 * 1024 * 1024)
        self.assertEqual(stats["total_size_mb"], 3.0)
        self.assertEqual(len(stats["by_extension"]), 2)
        self.assertEqual(stats["by_extension"][".txt"]["count"], 1)
        self.assertEqual(stats["by_extension"][".txt"]["size_mb"], 1.0)
        self.assertEqual(stats["by_extension"][".csv"]["count"], 1)
        self.assertEqual(stats["by_extension"][".csv"]["size_mb"], 2.0)


class TestDownloadsCleaner(unittest.TestCase):
    """Pruebas para la clase DownloadsCleaner"""
    
    @mock.patch('os.path.expanduser')
    @mock.patch('os.makedirs')
    def test_init(self, mock_makedirs, mock_expanduser):
        """Prueba la inicialización de DownloadsCleaner"""
        # Configurar mock para expanduser
        mock_expanduser.return_value = "/mock/home/Downloads"
        
        # Crear instancia de DownloadsCleaner
        cleaner = DownloadsCleaner()
        
        # Verificar que se usó la ruta correcta
        mock_expanduser.assert_called_once_with("~/Downloads")
        self.assertEqual(cleaner.target_directory, "/mock/home/Downloads")
        
        # Verificar que se crearon las reglas predefinidas
        self.assertIn(".csv", cleaner.rules)
        self.assertIn(".txt", cleaner.rules)
        self.assertIn(".xml", cleaner.rules)
        self.assertIn(".pdf", cleaner.rules)
        self.assertIn(".jpg", cleaner.rules)
        self.assertIn(".png", cleaner.rules)
        self.assertIn(".exe", cleaner.rules)
        
        # Verificar regla EPAY
        self.assertEqual(len(cleaner.name_rules), 1)
        self.assertTrue(cleaner.name_rules[0]["pattern"].search("EPAY_report.xlsx"))
        self.assertEqual(cleaner.name_rules[0]["action"], "move")


if __name__ == '__main__':
    unittest.main()
