"""Firmware origins shared by Tessera and tools/generate_entries.py.

Keep GitHub owner/repository and ref here, not separate package, component and font URLs.
Boards without an override follow the official app's release channel as before.
"""
DEFAULT_REPOSITORY = 'MaxGramser/homeassistant_espscreen'
DEFAULT_REF = 'main'
BOARD_SOURCES = {
    'ha-panel-s3': ('sky32/homeassistant_espscreen', 'feature/ha-panel-s3-chinese-locale'),
}


def source_for(board, default_ref=DEFAULT_REF):
    """(GitHub owner/repository, ref); an explicit board source ignores the official channel."""
    return BOARD_SOURCES.get(board, (DEFAULT_REPOSITORY, default_ref))


def repository_url(repository=DEFAULT_REPOSITORY):
    return f'https://github.com/{repository}'


def known_repository_url(url):
    """Recognise configured firmware origins without mistaking an arbitrary fork for our profiles."""
    if not isinstance(url, str):
        return False
    normalised = url.rstrip('/').removesuffix('.git')
    repositories = {DEFAULT_REPOSITORY, *(repository for repository, _ in BOARD_SOURCES.values())}
    return normalised in {repository_url(repository) for repository in repositories}
