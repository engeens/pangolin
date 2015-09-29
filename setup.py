import versioneer

version=versioneer.get_version(),
cmdclass=versioneer.get_cmdclass(),
if version["error"]:
    raise RuntimeError(version["error"])
