#!/usr/bin/env python3
"""
Codebase Mapper - Creates a concise markdown map of the codebase for LLM consumption.
Filters out unnecessary files and extracts key structural information.
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict
from typing import NamedTuple

class FunctionSig(NamedTuple):
    name: str
    kind: str
    params: List[str]
    line: int
    is_async: bool

@dataclass
class FileInfo:
    path: str
    type: str  # 'controller', 'model', 'route', 'validator', 'helper', 'config', 'migration', 'other'
    exports: List[str]
    imports: List[str]
    summary: str
    lines: int

@dataclass
class FuncSig:
    name: str
    line: int
    kind: str  # 'function', 'async_function', 'arrow', 'method', 'class', 'getter', 'setter'

class CodebaseMapper:
    def __init__(self, root: str):
        self.root = Path(root)
        self.ignore_dirs = {
            'node_modules', '.git', 'dist', 'build', '.next', '.turbo',
            'coverage', '.nyc_output', 'tmp', 'temp', 'logs', '.vscode',
            '.idea', '__pycache__', '.pytest_cache', '.venv', 'env',
            'vendor', 'storage', 'bootstrap/cache', 'public/build',
            'migrations', 'database/migrations', 'tests', '.phpunit',
        }
        self.ignore_files = {
            '.gitignore', '.eslintrc', '.prettierrc', '.npmrc', '.nvmrc',
            'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'tsconfig.json',
            'webpack.config.js', 'jest.config.js', '.env', '.env.example',
            '.dockerignore', 'Dockerfile', 'docker-compose.yml', 'docker-compose.yaml',
            'README.md', 'CHANGELOG.md', 'LICENSE', 'CONTRIBUTING.md',
            'composer.json', 'composer.lock', 'artisan', 'phpunit.xml', 'phpunit.xml.dist',
            'pyproject.toml', 'requirements.txt', 'requirements-dev.txt', 'Pipfile', 'Pipfile.lock',
            'poetry.lock', 'setup.py', 'setup.cfg', 'pytest.ini', 'mypy.ini',
        }
        self.ignore_extensions = {
            '.log', '.map', '.min.js', '.min.css', '.woff', '.woff2',
            '.ttf', '.eot', '.svg', '.png', '.jpg', '.jpeg', '.gif',
            '.ico', '.pdf', '.zip', '.tar', '.gz', '.sqlite', '.db',
            '.phtml', '.blade.php',
        }
        
        # Keywords to categorize files
        self.type_patterns = {
            # JS/TS patterns
            'controller': ['controllers/', 'Controller.js', 'Controller.ts'],
            'model': ['models/', 'Model.js', 'Model.ts'],
            'route': ['routes/', 'Route.js', 'Route.ts'],
            'validator': ['validators/', 'Validator.js', 'Validator.ts'],
            'helper': ['helpers/', 'Helper.js', 'Helper.ts'],
            'config': ['config/', 'Config.js', 'Config.ts'],
            'migration': ['migrations/', 'Migration.js', 'Migration.ts'],
            'service': ['services/', 'Service.js', 'Service.ts'],
            'middleware': ['middleware/', 'Middleware.js', 'Middleware.ts'],
            'utility': ['utils/', 'utils.js', 'utils.ts', 'utility.js'],
            # Laravel patterns
            'laravel_controller': ['app/Http/Controllers/', 'Controller.php'],
            'laravel_model': ['app/Models/', 'app/Model.php'],
            'laravel_migration': ['database/migrations/', 'Migration.php'],
            'laravel_request': ['app/Http/Requests/', 'Request.php'],
            'laravel_resource': ['app/Http/Resources/', 'Resource.php'],
            'laravel_service': ['app/Services/', 'Service.php'],
            'laravel_repository': ['app/Repositories/', 'Repository.php'],
            'laravel_middleware': ['app/Http/Middleware/', 'Middleware.php'],
            'laravel_provider': ['app/Providers/', 'ServiceProvider.php'],
            'laravel_policy': ['app/Policies/', 'Policy.php'],
            'laravel_observer': ['app/Observers/', 'Observer.php'],
            'laravel_job': ['app/Jobs/', 'Job.php'],
            'laravel_event': ['app/Events/', 'Event.php'],
            'laravel_listener': ['app/Listeners/', 'Listener.php'],
            'laravel_notification': ['app/Notifications/', 'Notification.php'],
            'laravel_mail': ['app/Mail/', 'Mailable.php'],
            'laravel_seeder': ['database/seeders/', 'Seeder.php'],
            'laravel_factory': ['database/factories/', 'Factory.php'],
            'laravel_config': ['config/', '.php'],
            # FastAPI patterns
            'fastapi_router': ['routers/', 'router.py', 'routes.py'],
            'fastapi_model': ['models/', 'schemas/', 'Model.py', 'Schema.py'],
            'fastapi_service': ['services/', 'service.py'],
            'fastapi_repository': ['repositories/', 'repository.py'],
            'fastapi_dependency': ['dependencies/', 'depends.py'],
            'fastapi_middleware': ['middleware/', 'middleware.py'],
            'fastapi_config': ['config/', 'settings.py', 'config.py'],
            'fastapi_exception': ['exceptions/', 'exception.py'],
            'fastapi_main': ['main.py', 'app.py'],
            
            # Django patterns
            'django_model': ['models.py', 'models/'],
            'django_view': ['views.py', 'views/'],
            'django_serializer': ['serializers.py', 'serializers/'],
            'django_url': ['urls.py'],
            'django_admin': ['admin.py'],
            'django_form': ['forms.py'],
            'django_migration': ['migrations/'],
            'django_app': ['apps.py'],
            
            # Flask patterns
            'flask_model': ['models.py', 'models/'],
            'flask_view': ['views.py', 'views/'],
            'flask_blueprint': ['blueprints/', 'bp.py'],
            'flask_form': ['forms.py'],
            
            # Python generic
            'py_config': ['config.py', 'settings.py', 'constants.py'],
            'py_util': ['utils.py', 'helpers.py', 'common.py'],
            
            # Spring Boot patterns
            'spring_controller': ['controller/', 'Controller.java'],
            'spring_service': ['service/', 'Service.java'],
            'spring_repository': ['repository/', 'Repository.java', 'dao/', 'Dao.java'],
            'spring_entity': ['entity/', 'model/', 'domain/', 'Entity.java'],
            'spring_dto': ['dto/', 'Dto.java', 'request/', 'response/'],
            'spring_config': ['config/', 'Configuration.java'],
            'spring_security': ['security/', 'SecurityConfig.java'],
            'spring_main': ['Application.java', 'SpringBootApplication.java'],
            'spring_exception': ['exception/', 'ExceptionHandler.java'],
            'spring_filter': ['filter/', 'Filter.java'],
            'spring_util': ['util/', 'Util.java', 'helper/', 'Helper.java'],
            
            # C#/.NET patterns
            'csharp_controller': ['Controllers/', 'Controller.cs'],
            'csharp_service': ['Services/', 'Service.cs'],
            'csharp_repository': ['Repositories/', 'Repository.cs', 'Data/', 'Dao.cs'],
            'csharp_model': ['Models/', 'Entities/', 'Domain/', 'Entity.cs', 'Model.cs'],
            'csharp_dto': ['DTOs/', 'ViewModels/', 'Dto.cs', 'ViewModel.cs'],
            'csharp_config': ['Configuration/', 'Config.cs', 'Startup.cs', 'Program.cs'],
            'csharp_middleware': ['Middleware/', 'Middleware.cs'],
            'csharp_filter': ['Filters/', 'Filter.cs'],
            'csharp_attribute': ['Attributes/', 'Attribute.cs'],
            'csharp_extension': ['Extensions/', 'Extension.cs'],
            'csharp_hub': ['Hubs/', 'Hub.cs'],
            'csharp_background': ['BackgroundServices/', 'HostedService.cs'],
        }

    def should_ignore(self, path: Path) -> bool:
        """Check if path should be ignored."""
        parts = path.parts
        if any(part in self.ignore_dirs for part in parts):
            return True
        if path.name in self.ignore_files:
            return True
        if path.suffix in self.ignore_extensions:
            return True
        if path.name.startswith('.'):
            return True
        return False

    def get_file_type(self, path: Path) -> str:
        """Determine file type based on path patterns."""
        path_str = str(path).replace('\\', '/')
        for ftype, patterns in self.type_patterns.items():
            for pattern in patterns:
                if pattern in path_str:
                    return ftype
        return 'other'

    def extract_js_info(self, content: str) -> tuple:
        """Extract exports, imports, and summary from JS/TS file."""
        exports = []
        imports = []
        
        # Extract module.exports
        export_patterns = [
            r'module\.exports\s*=\s*\{([^}]+)\}',
            r'module\.exports\s*=\s*(\w+)',
            r'exports\.(\w+)\s*=',
            r'export\s+(?:default\s+)?(?:function\s+)?(\w+)',
            r'export\s+\{([^}]+)\}',
        ]
        
        for pattern in export_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                if isinstance(match, str):
                    items = [x.strip() for x in match.split(',')]
                    exports.extend([x for x in items if x and not x.startswith('//')])
        
        # Extract require/import statements
        import_patterns = [
            r'require\([\'"]([^\'"]+)[\'"]\)',
            r'import\s+.*from\s+[\'"]([^\'"]+)[\'"]',
            r'import\s+[\'"]([^\'"]+)[\'"]',
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content)
            imports.extend(matches)
        
        # Filter imports to relevant ones (relative or known packages)
        imports = [imp for imp in imports if not imp.startswith('@') and imp not in 
                  ['express', 'sequelize', 'lodash', 'moment', 'bcrypt', 'jsonwebtoken',
                   'multer', 'cors', 'helmet', 'morgan', 'dotenv', 'nodemailer']]
        
        # Generate summary from comments or first function
        summary = self.generate_summary(content)
        
        return exports[:10], imports[:15], summary

    def generate_summary(self, content: str) -> str:
        """Generate a brief summary of the file."""
        lines = content.split('\n')
        
        # Look for JSDoc or block comments at top
        for i, line in enumerate(lines[:30]):
            line = line.strip()
            if line.startswith('/**') or line.startswith('/*'):
                # Extract comment block
                comment_lines = []
                for j in range(i, min(i+10, len(lines))):
                    comment_lines.append(lines[j].strip())
                    if '*/' in lines[j]:
                        break
                comment_text = ' '.join(comment_lines).replace('/**', '').replace('*/', '').replace('*', '').strip()
                if len(comment_text) > 20:
                    return comment_text[:200]
        
        # Look for descriptive function names
        func_patterns = [
            r'(?:async\s+)?function\s+(\w+)',
            r'const\s+(\w+)\s*=\s*(?:async\s+)?\(',
            r'(\w+)\s*:\s*(?:async\s+)?function',
        ]
        
        functions = []
        for pattern in func_patterns:
            matches = re.findall(pattern, content[:2000])
            functions.extend(matches)
        
        if functions:
            return f"Exports: {', '.join(functions[:5])}"
        
        # Fallback: first non-empty non-comment line
        for line in lines[:20]:
            line = line.strip()
            if line and not line.startswith('//') and not line.startswith('*'):
                return line[:150]
        
        return "No summary available"

    def extract_functions(self, content: str) -> List[FunctionSig]:
        """Extract function signatures with params and line numbers for JS/TS, PHP, Python."""
        funcs = []
        lines = content.split('\n')
        
        patterns = [
            # JS/TS patterns
            (r'(?:export\s+)?(?:async\s+)?function\s+(\w+)\s*\(([^)]*)\)', 'function'),
            (r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?\(([^)]*)\)\s*=>', 'arrow'),
            (r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?function\s*\(([^)]*)\)', 'function_expr'),
            (r'(\w+)\s*:\s*(?:async\s+)?function\s*\(([^)]*)\)', 'method'),
            (r'(\w+)\s*:\s*(?:async\s+)?\(([^)]*)\)\s*=>', 'arrow_method'),
            (r'async\s+(\w+)\s*\(([^)]*)\)', 'async_function'),
            # PHP patterns
            (r'(?:public|protected|private|static|final\s+)?\s*(?:abstract\s+)?function\s+(\w+)\s*\(([^$)]*(?:\$[^$)]*)*)\)', 'function'),
            # Python patterns
            (r'(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)', 'function'),
            (r'class\s+(\w+)', 'class'),
        ]
        
        for i, line in enumerate(lines):
            for pattern, kind in patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    if isinstance(match, tuple):
                        name, params_str = match
                    elif isinstance(match, str) and match:
                        name, params_str = match, ''
                    else:
                        continue
                    params = [p.strip().split(':')[0].split('=')[0].strip() 
                             for p in params_str.split(',') if p.strip()]
                    funcs.append(FunctionSig(
                        name=name, kind=kind, params=params, 
                        line=i+1, is_async='async' in line
                    ))
        return funcs

    def compact_tree(self, max_depth: int = 2) -> str:
        """Generate a compact directory tree with file counts and line counts."""
        lines = []
        prefix_map = {}
        
        for path in self.root.rglob('*'):
            if not path.is_file() or self.should_ignore(path):
                continue
            rel = str(path.relative_to(self.root)).replace('\\', '/')
            parts = rel.split('/')
            if len(parts) > max_depth:
                key = '/'.join(parts[:max_depth])
                if key not in prefix_map:
                    prefix_map[key] = {'dirs': set(), 'files': 0, 'lines': 0}
                prefix_map[key]['files'] += 1
                try:
                    prefix_map[key]['lines'] += len(path.read_text(encoding='utf-8', errors='ignore').split('\n'))
                except Exception:
                    pass
            else:
                key = rel
        
        lines.append(f"# Compact Tree (depth <={max_depth})")
        lines.append("")
        
        for path in sorted(self.root.iterdir()):
            if path.is_dir() and path.name not in self.ignore_dirs:
                total_files = 0
                total_lines = 0
                for f in path.rglob('*'):
                    if f.is_file() and not self.should_ignore(f):
                        total_files += 1
                        try:
                            total_lines += len(f.read_text(encoding='utf-8', errors='ignore').split('\n'))
                        except Exception:
                            pass
                lines.append(f"{path.name}/\t{total_files} files\t{total_lines} lines")
        
        for path in sorted(self.root.iterdir()):
            if path.is_file() and not self.should_ignore(path):
                try:
                    lc = len(path.read_text(encoding='utf-8', errors='ignore').split('\n'))
                    ftype = self.get_file_type(path)
                    lines.append(f"{path.name}\t{ftype}\t{lc} lines")
                except Exception:
                    pass
        
        if prefix_map:
            lines.append(f"\n# Aggregated (beyond depth {max_depth})")
            for key in sorted(prefix_map):
                info = prefix_map[key]
                lines.append(f"{key}/\t{info['files']} files\t{info['lines']} lines")
        
        return '\n'.join(lines)

    def find_dependents(self, target_file: str) -> List[str]:
        """Find all files that import the given file."""
        dependents = []
        target_normalized = target_file.replace('\\', '/')
        if target_normalized.endswith('.js') or target_normalized.endswith('.ts'):
            target_normalized = target_normalized[:-3]
        
        for path in self.root.rglob('*'):
            if not path.is_file() or self.should_ignore(path):
                continue
            if path.suffix not in ['.js', '.ts', '.json']:
                continue
            try:
                content = path.read_text(encoding='utf-8', errors='ignore')
                rel_path = str(path.relative_to(self.root)).replace('\\', '/')
                
                import_patterns = [
                    r'require\([\'"]([^\'"]+)[\'"]\)',
                    r'import\s+.*from\s+[\'"]([^\'"]+)[\'"]',
                    r'import\s+[\'"]([^\'"]+)[\'"]',
                ]
                
                for pattern in import_patterns:
                    matches = re.findall(pattern, content)
                    for imp in matches:
                        imp_norm = imp.replace('\\', '/')
                        if imp_norm.startswith('.'):
                            if imp_norm.endswith('.js') or imp_norm.endswith('.ts'):
                                imp_norm = imp_norm[:-3]
                            if imp_norm == target_normalized or imp_norm.endswith('/' + target_normalized):
                                dependents.append(rel_path)
                                break
            except Exception:
                pass
        
        return sorted(set(dependents))

    def search_pattern(self, pattern: str, ext: str = '.js', context: int = 2) -> List[Dict]:
        """Search for regex pattern across files, return structured matches with context."""
        results = []
        regex = re.compile(pattern, re.MULTILINE)
        
        for path in self.root.rglob(f'*{ext}'):
            if not path.is_file() or self.should_ignore(path):
                continue
            try:
                content = path.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if regex.search(line):
                        start = max(0, i - context)
                        end = min(len(lines), i + context + 1)
                        rel = str(path.relative_to(self.root)).replace('\\', '/')
                        results.append({
                            'file': rel,
                            'line': i + 1,
                            'match': line.strip(),
                            'context': [f"{j+1}: {lines[j].strip()}" for j in range(start, end)]
                        })
            except Exception:
                pass
        
        return results

    def process_file(self, path: Path) -> Optional[FileInfo]:
        """Process a single file and extract info."""
        try:
            content = path.read_text(encoding='utf-8', errors='ignore')
            lines = len(content.split('\n'))
            
            if lines == 0:
                return None
            
            file_type = self.get_file_type(path)
            
            # Dispatch to appropriate extractor based on extension
            if path.suffix in ['.js', '.ts', '.jsx', '.tsx']:
                exports, imports, summary = self.extract_js_info(content)
            elif path.suffix == '.php':
                exports, imports, summary = self.extract_php_info(content)
            elif path.suffix == '.py':
                exports, imports, summary = self.extract_python_info(content)
            elif path.suffix == '.java':
                exports, imports, summary = self.extract_java_info(content)
            elif path.suffix == '.cs':
                exports, imports, summary = self.extract_csharp_info(content)
            else:
                exports, imports, summary = [], [], self.generate_summary(content)
            
            return FileInfo(
                path=str(path.relative_to(self.root)),
                type=file_type,
                exports=exports,
                imports=imports,
                summary=summary,
                lines=lines
            )
        except Exception as e:
            return FileInfo(
                path=str(path.relative_to(self.root)),
                type='error',
                exports=[],
                imports=[],
                summary=f"Error reading file: {e}",
                lines=0
            )

    def extract_php_info(self, content: str) -> tuple:
        """Extract exports (classes/functions), imports (use statements), and summary from PHP file."""
        exports = []
        imports = []
        
        # Extract class names
        class_matches = re.findall(r'(?:abstract\s+|final\s+)?class\s+(\w+)', content)
        exports.extend(class_matches)
        
        # Extract interface names
        interface_matches = re.findall(r'interface\s+(\w+)', content)
        exports.extend(interface_matches)
        
        # Extract trait names
        trait_matches = re.findall(r'trait\s+(\w+)', content)
        exports.extend(trait_matches)
        
        # Extract function names (public/protected)
        func_matches = re.findall(r'(?:public|protected|private)\s+(?:static\s+)?function\s+(\w+)', content)
        exports.extend(func_matches)
        
        # Extract use statements (imports)
        use_matches = re.findall(r'use\s+([^;]+);', content)
        for use_stmt in use_matches:
            parts = use_stmt.strip().split(' ')
            imports.append(parts[-1])  # Get the last part (class name)
        
        # Extract namespace
        ns_match = re.search(r'namespace\s+([^;]+);', content)
        if ns_match:
            imports.append(f"namespace: {ns_match.group(1).strip()}")
        
        # Generate summary from docblock or first class/function
        summary = self.generate_php_summary(content, exports)
        
        return exports[:15], imports[:15], summary

    def extract_python_info(self, content: str) -> tuple:
        """Extract exports (classes/functions), imports, and summary from Python file."""
        exports = []
        imports = []
        
        # Extract class names
        class_matches = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)
        exports.extend(class_matches)
        
        # Extract function names (top-level and async)
        func_matches = re.findall(r'^(?:async\s+)?def\s+(\w+)', content, re.MULTILINE)
        exports.extend(func_matches)
        
        # Extract imports
        import_matches = re.findall(r'^(?:from\s+(\S+)\s+)?import\s+([^#\n]+)', content, re.MULTILINE)
        for match in import_matches:
            from_mod, imported = match
            for item in imported.split(','):
                item = item.strip().split(' as ')[0].strip()
                if from_mod:
                    imports.append(f"{from_mod}.{item}")
                else:
                    imports.append(item)
        
        # Filter out stdlib imports
        stdlib_modules = {'os', 'sys', 'json', 're', 'datetime', 'time', 'math', 'random',
                         'collections', 'itertools', 'functools', 'pathlib', 'typing',
                         'dataclasses', 'enum', 'abc', 'contextlib', 'hashlib', 'base64',
                         'urllib', 'http', 'email', 'html', 'xml', 'csv', 'sqlite3',
                         'logging', 'argparse', 'configparser', 'subprocess', 'threading',
                         'multiprocessing', 'asyncio', 'concurrent', 'queue', 'signal',
                         'statistics', 'decimal', 'fractions', 'numbers', 'string',
                         'textwrap', 'unicodedata', 'stringprep', 'readline', 'rlcompleter'}
        imports = [imp for imp in imports if not any(imp.startswith(m + '.') or imp == m for m in stdlib_modules)]
        
        # Generate summary from docstring or first class/function
        summary = self.generate_python_summary(content, exports)
        
        return exports[:15], imports[:15], summary

    def generate_php_summary(self, content: str, exports: List[str]) -> str:
        """Generate summary from PHP docblock or first export."""
        # Look for class/interface/trait docblock
        docblock_match = re.search(r'/\*\*(.*?)\*/\s*(?:class|interface|trait)\s+\w+', content, re.DOTALL)
        if docblock_match:
            doc = docblock_match.group(1)
            # Clean up docblock
            lines = [line.strip().lstrip('*').strip() for line in doc.split('\n') if line.strip()]
            summary = ' '.join([l for l in lines if l and not l.startswith('@')])[:200]
            if summary:
                return summary
        
        # Fallback to first export
        if exports:
            return f"Exports: {', '.join(exports[:5])}"
        
        return "PHP file"

    def generate_python_summary(self, content: str, exports: List[str]) -> str:
        """Generate summary from Python docstring or first export."""
        # Look for module docstring
        docstring_match = re.search(r'^(""".*?"""|\'\'\'.*?\'\'\')', content, re.DOTALL | re.MULTILINE)
        if docstring_match:
            doc = docstring_match.group(1)
            doc = doc.strip('"\'')
            summary = ' '.join(doc.split())[:200]
            if summary:
                return summary
        
        # Look for class docstring
        class_doc_match = re.search(r'class\s+\w+.*?(""".*?"""|\'\'\'.*?\'\'\')', content, re.DOTALL)
        if class_doc_match:
            doc = class_doc_match.group(1)
            doc = doc.strip('"\'')
            summary = ' '.join(doc.split())[:200]
            if summary:
                return summary
        
        # Fallback to exports
        if exports:
            return f"Exports: {', '.join(exports[:5])}"
        
        return "Python file"

    def extract_java_info(self, content: str) -> tuple:
        """Extract exports (classes/interfaces/enums), imports, and summary from Java file."""
        exports = []
        imports = []
        
        # Extract package declaration
        package_match = re.search(r'^package\s+([\w.]+);', content, re.MULTILINE)
        if package_match:
            imports.append(f"package: {package_match.group(1)}")
        
        # Extract imports
        import_matches = re.findall(r'^import\s+(?:static\s+)?([\w.]+);', content, re.MULTILINE)
        for imp in import_matches:
            # Filter out java.*, javax.*, jakarta.* stdlib imports
            if not (imp.startswith('java.') or imp.startswith('javax.') or imp.startswith('jakarta.')):
                imports.append(imp)
        
        # Extract class/interface/enum/record names
        type_matches = re.findall(r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?(class|interface|enum|record)\s+(\w+)', content)
        for type_kind, name in type_matches:
            exports.append(f"{type_kind}:{name}")
        
        # Extract method signatures (public/protected)
        method_matches = re.findall(r'(?:public|protected)\s+(?:static\s+)?(?:\w+\s+)*(\w+)\s*\([^)]*\)\s*(?:throws\s+[\w,\s]+)?\s*{', content)
        exports.extend([f"method:{m}" for m in method_matches])
        
        # Generate summary from Javadoc or first class
        summary = self.generate_java_summary(content, exports)
        
        return exports[:15], imports[:15], summary

    def generate_java_summary(self, content: str, exports: List[str]) -> str:
        """Generate summary from Java Javadoc or first export."""
        # Look for class/interface Javadoc
        javadoc_match = re.search(r'/\*\*(.*?)\*/\s*(?:public\s+)?(?:abstract\s+)?(?:final\s+)?(?:class|interface|enum|record)\s+\w+', content, re.DOTALL)
        if javadoc_match:
            doc = javadoc_match.group(1)
            lines = [line.strip().lstrip('*').strip() for line in doc.split('\n') if line.strip()]
            summary = ' '.join([l for l in lines if l and not l.startswith('@')])[:200]
            if summary:
                return summary
        
        # Fallback to first export
        if exports:
            return f"Exports: {', '.join(exports[:5])}"
        
        return "Java file"

    def extract_csharp_info(self, content: str) -> tuple:
        """Extract exports (classes/interfaces/records), imports, and summary from C# file."""
        exports = []
        imports = []
        
        # Extract namespace
        namespace_match = re.search(r'^namespace\s+([\w.]+)', content, re.MULTILINE)
        if namespace_match:
            imports.append(f"namespace: {namespace_match.group(1)}")
        
        # Extract using statements (imports)
        using_matches = re.findall(r'^using\s+(?:static\s+)?([\w.]+);', content, re.MULTILINE)
        for using in using_matches:
            # Filter out System.* stdlib imports
            if not using.startswith('System.'):
                imports.append(using)
        
        # Extract class/interface/record/struct names
        type_matches = re.findall(r'(?:public\s+)?(?:abstract\s+)?(?:sealed\s+)?(?:partial\s+)?(class|interface|record|struct)\s+(\w+)', content)
        for type_kind, name in type_matches:
            exports.append(f"{type_kind}:{name}")
        
        # Extract method signatures (public/protected/internal)
        method_matches = re.findall(r'(?:public|protected|internal)\s+(?:static\s+)?(?:async\s+)?(?:\w+\s+)*(\w+)\s*\([^)]*\)', content)
        exports.extend([f"method:{m}" for m in method_matches])
        
        # Generate summary from XML doc comments or first class
        summary = self.generate_csharp_summary(content, exports)
        
        return exports[:15], imports[:15], summary

    def generate_csharp_summary(self, content: str, exports: List[str]) -> str:
        """Generate summary from C# XML doc comments or first export."""
        # Look for class/interface XML doc comment
        xml_doc_match = re.search(r'///\s*<summary>(.*?)</summary>.*?(?:public\s+)?(?:abstract\s+)?(?:sealed\s+)?(?:partial\s+)?(?:class|interface|record|struct)\s+\w+', content, re.DOTALL)
        if xml_doc_match:
            doc = xml_doc_match.group(1)
            lines = [line.strip().lstrip('///').strip() for line in doc.split('\n') if line.strip()]
            summary = ' '.join([l for l in lines if l and not l.startswith('<')])[:200]
            if summary:
                return summary
        
        # Fallback to first export
        if exports:
            return f"Exports: {', '.join(exports[:5])}"
        
        return "C# file"

    def map_codebase(self) -> Dict:
        """Map the entire codebase."""
        files_by_type: Dict[str, List[FileInfo]] = {}
        total_files = 0
        total_lines = 0
        
        supported_extensions = {
            '.js', '.ts', '.jsx', '.tsx', '.json', '.md',
            '.php', '.py', '.java', '.cs',
        }
        
        for path in self.root.rglob('*'):
            if path.is_file() and not self.should_ignore(path):
                if path.suffix in supported_extensions:
                    info = self.process_file(path)
                    if info:
                        if info.type not in files_by_type:
                            files_by_type[info.type] = []
                        files_by_type[info.type].append(info)
                        total_files += 1
                        total_lines += info.lines
        
        # Sort files by path within each type
        for ftype in files_by_type:
            files_by_type[ftype].sort(key=lambda x: x.path)
        
        return {
            'stats': {
                'total_files': total_files,
                'total_lines': total_lines,
                'by_type': {k: len(v) for k, v in files_by_type.items()}
            },
            'files': {k: [asdict(v) for v in v_list] for k, v_list in files_by_type.items()}
        }

    def generate_markdown(self, data: Dict) -> str:
        """Generate markdown report from mapped data."""
        lines = []
        stats = data['stats']
        
        lines.append("# Codebase Map")
        lines.append(f"Generated for LLM-assisted development")
        lines.append("")
        lines.append("## Statistics")
        lines.append(f"- **Total Files**: {stats['total_files']}")
        lines.append(f"- **Total Lines**: {stats['total_lines']:,}")
        lines.append("")
        lines.append("### By Type")
        for ftype, count in sorted(stats['by_type'].items()):
            lines.append(f"- **{ftype}**: {count} files")
        lines.append("")
        
        # Type order for consistent output
        type_order = [
            # Config first
            'config', 'py_config', 'fastapi_config', 'laravel_config', 'spring_config', 'csharp_config',
            # Models
            'model', 'laravel_model', 'fastapi_model', 'django_model', 'flask_model', 'spring_entity', 'csharp_model',
            # Controllers
            'controller', 'laravel_controller', 'fastapi_main', 'django_view', 'flask_view', 'flask_blueprint', 'spring_controller', 'csharp_controller',
            # Routes
            'route', 'fastapi_router', 'django_url', 'csharp_route',
            # Services
            'service', 'laravel_service', 'fastapi_service', 'spring_service', 'csharp_service',
            # Middleware
            'middleware', 'laravel_middleware', 'fastapi_middleware', 'spring_filter', 'csharp_middleware',
            # Database
            'migration', 'laravel_migration', 'django_migration',
            'laravel_seeder', 'laravel_factory',
            # Validation/Requests
            'validator', 'laravel_request', 'django_form', 'flask_form', 'spring_dto', 'csharp_dto',
            # Resources/Serializers
            'laravel_resource', 'django_serializer', 'csharp_dto',
            # Auth/Security
            'laravel_policy', 'fastapi_security', 'laravel_guard', 'spring_security', 'csharp_security',
            # Jobs/Events
            'laravel_job', 'laravel_event', 'laravel_listener', 'laravel_command',
            # Notifications/Mail
            'laravel_notification', 'laravel_mail',
            # Dependencies
            'fastapi_dependency',
            # Exceptions
            'fastapi_exception', 'spring_exception', 'csharp_exception',
            # Providers/Configs
            'laravel_provider',
            # Repositories
            'spring_repository', 'csharp_repository',
            # Utilities
            'utility', 'helper', 'py_util', 'spring_util', 'csharp_util',
            # Components
            'laravel_component',
            # Rules
            'laravel_rule',
            # CRUD
            'fastapi_crud',
            # Observers
            'laravel_observer',
            # Main
            'spring_main', 'csharp_main',
            # Other
            'other',
        ]
        
        for ftype in type_order:
            if ftype not in data['files']:
                continue
            files = data['files'][ftype]
            lines.append(f"## {ftype.title()} ({len(files)} files)")
            lines.append("")
            
            for file_info in files:
                lines.append(f"### `{file_info['path']}` ({file_info['lines']} lines)")
                
                if file_info['exports']:
                    lines.append(f"**Exports**: {', '.join(file_info['exports'])}")
                
                if file_info['imports']:
                    lines.append(f"**Key Imports**: {', '.join(file_info['imports'][:8])}")
                
                lines.append(f"**Summary**: {file_info['summary']}")
                lines.append("")
        
        return '\n'.join(lines)

    def extract_functions(self, content: str, path: Path = None) -> List[FunctionSig]:
        """Extract all function/method/class signatures with line numbers."""
        sigs = []
        lines = content.split('\n')
        
        # Determine language from path
        ext = path.suffix if path else ''
        
        if ext in ['.js', '.ts', '.jsx', '.tsx']:
            patterns = [
                (r'(?:export\s+)?(?:async\s+)?function\s+(\w+)', 'function'),
                (r'(?:export\s+)?class\s+(\w+)', 'class'),
                (r'(\w+)\s*:\s*(?:async\s+)?function\b', 'method'),
                (r'(?:get|set)\s+(\w+)\s*\(', 'accessor'),
                (r'(?:export\s+)?(?:default\s+)?(?:async\s+)?\(?\s*(?:\([^)]*\))\s*(?:=>|\)\s*=>)', 'arrow_default'),
            ]
            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                for pat, kind in patterns:
                    for m in re.finditer(pat, stripped):
                        name = m.group(1) if m.lastindex and m.lastindex >= 1 else ''
                        if kind == 'arrow_default' and not name:
                            name = '<anonymous>'
                        sigs.append(FunctionSig(name=name, kind=kind, params=[], line=line_no, is_async='async' in line))
            # Arrow const patterns
            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                m = re.match(r'(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|\w+)\s*=>', stripped)
                if m:
                    sigs.append(FunctionSig(name=m.group(1), kind='arrow', params=[], line=line_no, is_async='async' in line))
                    
        elif ext == '.php':
            # PHP: classes, interfaces, traits, methods
            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                # Classes, interfaces, traits
                m = re.match(r'(?:abstract\s+|final\s+)?(class|interface|trait)\s+(\w+)', stripped)
                if m:
                    sigs.append(FunctionSig(name=m.group(2), kind=m.group(1), params=[], line=line_no, is_async=False))
                # Methods (public/protected/private functions)
                m = re.match(r'(?:public|protected|private)\s+(?:static\s+)?function\s+(\w+)\s*\(([^)]*)\)', stripped)
                if m:
                    params = [p.strip().split(':')[0].split('=')[0].strip() 
                             for p in m.group(2).split(',') if p.strip()]
                    sigs.append(FunctionSig(name=m.group(1), kind='method', params=params, line=line_no, is_async=False))
                    
        elif ext == '.py':
            # Python: classes, functions, async functions
            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                # Classes
                m = re.match(r'class\s+(\w+)', stripped)
                if m:
                    sigs.append(FunctionSig(name=m.group(1), kind='class', params=[], line=line_no, is_async=False))
                # Functions (async and regular)
                m = re.match(r'(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)', stripped)
                if m:
                    params = [p.strip().split(':')[0].split('=')[0].strip() 
                             for p in m.group(2).split(',') if p.strip()]
                    kind = 'async_function' if 'async' in stripped else 'function'
                    sigs.append(FunctionSig(name=m.group(1), kind=kind, params=params, line=line_no, is_async='async' in stripped))
                    
        elif ext == '.java':
            # Java: classes, interfaces, enums, records, methods
            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                # Classes, interfaces, enums, records
                m = re.match(r'(?:public\s+)?(?:abstract\s+)?(?:final\s+)?(class|interface|enum|record)\s+(\w+)', stripped)
                if m:
                    sigs.append(FunctionSig(name=m.group(2), kind=m.group(1), params=[], line=line_no, is_async=False))
                # Methods (public/protected/private, static, constructors)
                m = re.match(r'(?:public|protected|private)\s+(?:static\s+)?(?:final\s+)?(?:<[^>]+>\s+)?(\w+)\s*\(([^)]*)\)', stripped)
                if m:
                    # Skip constructors (same name as class - would need class context)
                    params = [p.strip().split(' ')[-1].split('=')[0].strip() 
                             for p in m.group(2).split(',') if p.strip()]
                    sigs.append(FunctionSig(name=m.group(1), kind='method', params=params, line=line_no, is_async=False))
                    
        elif ext == '.cs':
            # C#: classes, interfaces, records, structs, methods
            for line_no, line in enumerate(lines, 1):
                stripped = line.strip()
                # Classes, interfaces, records, structs
                m = re.match(r'(?:public\s+)?(?:abstract\s+)?(?:sealed\s+)?(?:partial\s+)?(class|interface|record|struct)\s+(\w+)', stripped)
                if m:
                    sigs.append(FunctionSig(name=m.group(2), kind=m.group(1), params=[], line=line_no, is_async=False))
                # Methods (public/protected/internal, static, async)
                m = re.match(r'(?:public|protected|internal)\s+(?:static\s+)?(?:async\s+)?(?:\w+\s+)*(\w+)\s*\(([^)]*)\)', stripped)
                if m:
                    params = [p.strip().split(' ')[-1].split('=')[0].strip() 
                             for p in m.group(2).split(',') if p.strip()]
                    kind = 'async_method' if 'async' in stripped else 'method'
                    sigs.append(FunctionSig(name=m.group(1), kind=kind, params=params, line=line_no, is_async='async' in stripped))
        
        sigs.sort(key=lambda s: s.line)
        return sigs

    def find_dependents(self, module_path: str) -> List[Dict]:
        """Find all files that import a given module path."""
        results = []
        target = module_path.replace('\\', '/')
        for path in self.root.rglob('*'):
            if not path.is_file() or self.should_ignore(path) or path.suffix not in ('.js', '.ts', '.jsx', '.tsx'):
                continue
            try:
                content = path.read_text(encoding='utf-8', errors='ignore')
                rel = str(path.relative_to(self.root)).replace('\\', '/')
                for m in re.finditer(r'(?:require\([\'"]|from\s+[\'"])([^\'"]+)[\'"]', content):
                    imported = m.group(1)
                    if imported.endswith(target.rstrip('.js').rstrip('.ts')) or target.endswith(imported.rstrip('.js').rstrip('.ts')):
                        results.append({'file': rel, 'import_statement': f"require('{imported}')" if 'require' in m.group() else f"from '{imported}'"})
            except Exception:
                pass
        return results

    def search_pattern(self, pattern: str, exts: List[str] = None, context: int = 0) -> List[Dict]:
        """Fast regex search with structured output (avoids raw grep tokens)."""
        if exts is None:
            exts = ['.js', '.ts', '.jsx', '.tsx']
        results = []
        try:
            rx = re.compile(pattern)
        except re.error as e:
            return [{'error': f'Invalid regex: {e}'}]
        for path in self.root.rglob('*'):
            if not path.is_file() or self.should_ignore(path) or path.suffix not in exts:
                continue
            try:
                content = path.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')
                rel = str(path.relative_to(self.root)).replace('\\', '/')
                for line_no, line in enumerate(lines, 1):
                    if rx.search(line):
                        ctx_lines = lines[max(0, line_no-1-context):line_no+context]
                        results.append({
                            'file': rel, 'line': line_no,
                            'match': line.strip()[:200],
                            'context': [l.rstrip()[:200] for l in ctx_lines]
                        })
            except Exception:
                pass
        return results

    def compact_tree(self, max_depth: int = 3) -> str:
        """Token-efficient directory tree: path | type | lines."""
        lines = []
        prefix_map = {}
        for path in self.root.rglob('*'):
            if not path.is_file() or self.should_ignore(path):
                continue
            rel = str(path.relative_to(self.root)).replace('\\', '/')
            parts = rel.split('/')
            if len(parts) > max_depth:
                key = '/'.join(parts[:max_depth])
                if key not in prefix_map:
                    prefix_map[key] = {'dirs': set(), 'files': 0, 'lines': 0}
                prefix_map[key]['files'] += 1
                try:
                    prefix_map[key]['lines'] += len(path.read_text(encoding='utf-8', errors='ignore').split('\n'))
                except Exception:
                    pass
            else:
                key = rel
        lines.append(f"# Compact Tree (depth <={max_depth})")
        lines.append(f"")
        # Show top-level dirs first
        for path in sorted(self.root.iterdir()):
            if path.is_dir() and path.name not in self.ignore_dirs:
                total_files = 0
                total_lines = 0
                for f in path.rglob('*'):
                    if f.is_file() and not self.should_ignore(f):
                        total_files += 1
                        try:
                            total_lines += len(f.read_text(encoding='utf-8', errors='ignore').split('\n'))
                        except Exception:
                            pass
                lines.append(f"{path.name}/\t{total_files} files\t{total_lines} lines")
        lines.append(f"")
        # Show individual files at root
        for path in sorted(self.root.iterdir()):
            if path.is_file() and not self.should_ignore(path):
                try:
                    lc = len(path.read_text(encoding='utf-8', errors='ignore').split('\n'))
                    ftype = self.get_file_type(path)
                    lines.append(f"{path.name}\t{ftype}\t{lc} lines")
                except Exception:
                    pass
        if prefix_map:
            lines.append(f"\n# Aggregated (beyond depth {max_depth})")
            for key in sorted(prefix_map):
                info = prefix_map[key]
                lines.append(f"{key}/\t{info['files']} files\t{info['lines']} lines")
        return '\n'.join(lines)

    def file_fingerprint(self, rel_path: str) -> Dict:
        """One-line fingerprint of a single file: type, exports, imports, functions."""
        full = self.root / rel_path
        if not full.is_file():
            return {'error': f'File not found: {rel_path}'}
        try:
            content = full.read_text(encoding='utf-8', errors='ignore')
            ftype = self.get_file_type(full)
            
            # Dispatch to appropriate extractor based on extension
            if full.suffix in ['.js', '.ts', '.jsx', '.tsx']:
                exports, imports, summary = self.extract_js_info(content)
            elif full.suffix == '.php':
                exports, imports, summary = self.extract_php_info(content)
            elif full.suffix == '.py':
                exports, imports, summary = self.extract_python_info(content)
            elif full.suffix == '.java':
                exports, imports, summary = self.extract_java_info(content)
            elif full.suffix == '.cs':
                exports, imports, summary = self.extract_csharp_info(content)
            else:
                exports, imports, summary = [], [], self.generate_summary(content)
            
            funcs = self.extract_functions(content, full)
            line_count = len(content.split('\n'))
            return {
                'path': rel_path, 'type': ftype, 'lines': line_count,
                'exports': exports[:8], 'imports': imports[:8],
                'summary': summary,
                'functions': [{'name': f.name, 'line': f.line} for f in funcs[:20]]
            }
        except Exception as e:
            return {'error': str(e)}


def main():
    parser = argparse.ArgumentParser(description='Codebase Mapper - Token-efficient codebase exploration')
    parser.add_argument('path', nargs='?', default='.', help='Project root path')
    parser.add_argument('--mode', choices=['map', 'compact', 'fingerprint', 'functions', 'dependents', 'search'], default='map',
                        help='Output mode: map (markdown), compact (tree), fingerprint (single file), functions (extract sigs), dependents (reverse deps), search (pattern)')
    parser.add_argument('--file', help='File path for fingerprint/functions mode (relative to project root)')
    parser.add_argument('--pattern', help='Regex pattern for search mode')
    parser.add_argument('--ext', default='.js', help='File extension filter for search (default: .js)')
    parser.add_argument('--context', type=int, default=2, help='Context lines for search (default: 2)')
    parser.add_argument('--depth', type=int, default=2, help='Tree depth for compact mode (default: 2)')
    parser.add_argument('--output', help='Output file path (default: stdout or CODEBASE_MAP.md for map mode)')
    args = parser.parse_args()

    project_root = Path(args.path).resolve()
    mapper = CodebaseMapper(str(project_root))

    if args.mode == 'map':
        print("Mapping codebase...")
        data = mapper.map_codebase()
        print(f"Found {data['stats']['total_files']} files, {data['stats']['total_lines']:,} lines")
        markdown = mapper.generate_markdown(data)
        output = Path(args.output) if args.output else project_root / 'CODEBASE_MAP.md'
        output.write_text(markdown, encoding='utf-8')
        print(f"Written to {output}")

    elif args.mode == 'compact':
        print(mapper.compact_tree(max_depth=args.depth))

    elif args.mode == 'fingerprint':
        if not args.file:
            parser.error("--file required for fingerprint mode")
        fp = mapper.file_fingerprint(args.file)
        print(json.dumps(fp, indent=2))

    elif args.mode == 'functions':
        if not args.file:
            parser.error("--file required for functions mode")
        full = project_root / args.file
        if not full.is_file():
            parser.error(f"File not found: {args.file}")
        content = full.read_text(encoding='utf-8', errors='ignore')
        funcs = mapper.extract_functions(content, full)
        for f in funcs:
            print(f"{f.line:4d}  {f.kind} {f.name}")

    elif args.mode == 'dependents':
        if not args.file:
            parser.error("--file required for dependents mode")
        dependents = mapper.find_dependents(args.file)
        print(json.dumps({'file': args.file, 'dependents': dependents}, indent=2))

    elif args.mode == 'search':
        if not args.pattern:
            parser.error("--pattern required for search mode")
        results = mapper.search_pattern(args.pattern, exts=[args.ext], context=args.context)
        print(json.dumps({'pattern': args.pattern, 'matches': results}, indent=2))


if __name__ == '__main__':
    main()