#!/usr/bin/env python3
"""
Cleanup Manager for NotebookLM Skill
Manages cleanup of skill data and browser state
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path
from typing import TypedDict, cast


class PathInfo(TypedDict):
    """Type for path information dictionary."""

    path: str
    size: int
    type: str


class CleanupCategories(TypedDict):
    """Type for cleanup path categories."""

    browser_state: list[PathInfo]
    sessions: list[PathInfo]
    library: list[PathInfo]
    auth: list[PathInfo]
    other: list[PathInfo]


class CleanupPathsResult(TypedDict):
    """Type for get_cleanup_paths return value."""

    categories: CleanupCategories
    total_size: int
    total_items: int


class DryRunResult(TypedDict):
    """Type for dry run cleanup result."""

    dry_run: bool
    would_delete: int
    would_free: int


class FailedItem(TypedDict):
    """Type for failed deletion item."""

    path: str
    error: str


class CleanupResult(TypedDict):
    """Type for perform_cleanup return value."""

    deleted_items: list[str]
    failed_items: list[FailedItem]
    deleted_size: int
    deleted_count: int
    failed_count: int


class CleanupManager:
    """
    Manages cleanup of NotebookLM skill data

    Features:
    - Preview what will be deleted
    - Selective cleanup options
    - Library preservation
    - Safe deletion with confirmation
    """

    skill_dir: Path
    data_dir: Path

    def __init__(self) -> None:
        """Initialize the cleanup manager"""
        # Skill directory paths
        self.skill_dir = Path(__file__).parent.parent
        self.data_dir = self.skill_dir / "data"

    def get_cleanup_paths(self, preserve_library: bool = False) -> CleanupPathsResult:
        """
        Get paths that would be cleaned up

        Args:
            preserve_library: Keep library.json if True

        Returns:
            Dict with paths and sizes

        Note: .venv is NEVER deleted - it's part of the skill infrastructure
        """
        paths: CleanupCategories = {
            'browser_state': [],
            'sessions': [],
            'library': [],
            'auth': [],
            'other': []
        }

        total_size: int = 0

        if self.data_dir.exists():
            # Browser state
            browser_state_dir: Path = self.data_dir / "browser_state"
            if browser_state_dir.exists():
                for item in browser_state_dir.iterdir():
                    size: int = self._get_size(item)
                    paths['browser_state'].append({
                        'path': str(item),
                        'size': size,
                        'type': 'dir' if item.is_dir() else 'file'
                    })
                    total_size += size

            # Sessions
            sessions_file: Path = self.data_dir / "sessions.json"
            if sessions_file.exists():
                size = sessions_file.stat().st_size
                paths['sessions'].append({
                    'path': str(sessions_file),
                    'size': size,
                    'type': 'file'
                })
                total_size += size

            # Library (unless preserved)
            if not preserve_library:
                library_file: Path = self.data_dir / "library.json"
                if library_file.exists():
                    size = library_file.stat().st_size
                    paths['library'].append({
                        'path': str(library_file),
                        'size': size,
                        'type': 'file'
                    })
                    total_size += size

            # Auth info
            auth_info: Path = self.data_dir / "auth_info.json"
            if auth_info.exists():
                size = auth_info.stat().st_size
                paths['auth'].append({
                    'path': str(auth_info),
                    'size': size,
                    'type': 'file'
                })
                total_size += size

            # Other files in data dir (but NEVER .venv!)
            for item in self.data_dir.iterdir():
                if item.name not in ['browser_state', 'sessions.json', 'library.json', 'auth_info.json']:
                    size = self._get_size(item)
                    paths['other'].append({
                        'path': str(item),
                        'size': size,
                        'type': 'dir' if item.is_dir() else 'file'
                    })
                    total_size += size

        return {
            'categories': paths,
            'total_size': total_size,
            'total_items': sum(
                len(items) for items in [
                    paths['browser_state'],
                    paths['sessions'],
                    paths['library'],
                    paths['auth'],
                    paths['other'],
                ]
            )
        }

    def _get_size(self, path: Path) -> int:
        """Get size of file or directory in bytes."""
        if path.is_file():
            return path.stat().st_size
        elif path.is_dir():
            total: int = 0
            try:
                for item in path.rglob('*'):
                    if item.is_file():
                        total += item.stat().st_size
            except Exception:
                pass
            return total
        return 0

    def _format_size(self, size: int | float) -> str:
        """Format size in human-readable form."""
        size_float: float = float(size)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_float < 1024:
                return f"{size_float:.1f} {unit}"
            size_float /= 1024
        return f"{size_float:.1f} TB"

    def perform_cleanup(
        self,
        preserve_library: bool = False,
        dry_run: bool = False
    ) -> CleanupResult | DryRunResult:
        """
        Perform the actual cleanup

        Args:
            preserve_library: Keep library.json if True
            dry_run: Preview only, don't delete

        Returns:
            Dict with cleanup results
        """
        cleanup_data: CleanupPathsResult = self.get_cleanup_paths(preserve_library)
        deleted_items: list[str] = []
        failed_items: list[FailedItem] = []
        deleted_size: int = 0

        if dry_run:
            return {
                'dry_run': True,
                'would_delete': cleanup_data['total_items'],
                'would_free': cleanup_data['total_size']
            }

        # Perform deletion
        categories: CleanupCategories = cleanup_data['categories']
        all_items: list[tuple[str, list[PathInfo]]] = [
            ('browser_state', categories['browser_state']),
            ('sessions', categories['sessions']),
            ('library', categories['library']),
            ('auth', categories['auth']),
            ('other', categories['other']),
        ]
        for category, items in all_items:
            for item_info in items:
                path: Path = Path(item_info['path'])
                try:
                    if path.exists():
                        if path.is_dir():
                            shutil.rmtree(path)
                        else:
                            path.unlink()
                        deleted_items.append(str(path))
                        deleted_size += item_info['size']
                        print(f"  Deleted: {path.name}")
                except Exception as e:
                    failed_items.append({
                        'path': str(path),
                        'error': str(e)
                    })
                    print(f"  Failed: {path.name} ({e})")

        # Recreate browser_state dir if everything was deleted
        if not preserve_library and not failed_items:
            browser_state_dir: Path = self.data_dir / "browser_state"
            browser_state_dir.mkdir(parents=True, exist_ok=True)

        return {
            'deleted_items': deleted_items,
            'failed_items': failed_items,
            'deleted_size': deleted_size,
            'deleted_count': len(deleted_items),
            'failed_count': len(failed_items)
        }

    def print_cleanup_preview(self, preserve_library: bool = False) -> None:
        """Print a preview of what will be cleaned."""
        data: CleanupPathsResult = self.get_cleanup_paths(preserve_library)

        print("\n🔍 Cleanup Preview")
        print("=" * 60)

        categories: CleanupCategories = data['categories']
        all_items: list[tuple[str, list[PathInfo]]] = [
            ('browser_state', categories['browser_state']),
            ('sessions', categories['sessions']),
            ('library', categories['library']),
            ('auth', categories['auth']),
            ('other', categories['other']),
        ]
        category: str
        items: list[PathInfo]
        for category, items in all_items:
            if items:
                print(f"\n📁 {category.replace('_', ' ').title()}:")
                item: PathInfo
                for item in items:
                    path: Path = Path(item['path'])
                    size_str: str = self._format_size(item['size'])
                    type_icon: str = "📂" if item['type'] == 'dir' else "📄"
                    print(f"  {type_icon} {path.name:<30} {size_str:>10}")

        print("\n" + "=" * 60)
        print(f"Total items: {data['total_items']}")
        print(f"Total size: {self._format_size(data['total_size'])}")

        if preserve_library:
            print("\n📚 Library will be preserved")

        print("\nThis preview shows what would be deleted.")
        print("Use --confirm to actually perform the cleanup.")


def main() -> None:
    """Command-line interface for cleanup management."""
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description='Clean up NotebookLM skill data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what will be deleted
  python cleanup_manager.py

  # Perform cleanup (delete everything)
  python cleanup_manager.py --confirm

  # Cleanup but keep library
  python cleanup_manager.py --confirm --preserve-library

  # Force cleanup without preview
  python cleanup_manager.py --confirm --force
        """
    )

    parser.add_argument(
        '--confirm',
        action='store_true',
        help='Actually perform the cleanup (without this, only preview)'
    )

    parser.add_argument(
        '--preserve-library',
        action='store_true',
        help='Keep the notebook library (library.json)'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip confirmation prompt'
    )

    args: argparse.Namespace = parser.parse_args()

    # Initialize manager
    manager: CleanupManager = CleanupManager()

    if args.confirm:
        # Show preview first unless forced
        if not args.force:
            manager.print_cleanup_preview(args.preserve_library)

            print("\n⚠️  WARNING: This will delete the files shown above!")
            print("   Note: .venv is preserved (part of skill infrastructure)")
            response: str = input("Are you sure? (yes/no): ")

            if response.lower() != 'yes':
                print("Cleanup cancelled.")
                return

        # Perform cleanup
        print("\n🗑️ Performing cleanup...")
        result: CleanupResult = cast(
            CleanupResult,
            manager.perform_cleanup(args.preserve_library, dry_run=False)
        )

        print("\n✅ Cleanup complete!")
        print(f"  Deleted: {result['deleted_count']} items")
        print(f"  Freed: {manager._format_size(result['deleted_size'])}")

        if result['failed_count'] > 0:
            print(f"  ⚠️ Failed: {result['failed_count']} items")

    else:
        # Just show preview
        manager.print_cleanup_preview(args.preserve_library)
        print("\n💡 Note: Virtual environment (.venv) is never deleted")
        print("   It's part of the skill infrastructure, not user data")


if __name__ == "__main__":
    main()