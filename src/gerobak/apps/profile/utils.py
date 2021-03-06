import re

_pkg_url_re = re.compile(u"^'([^']+)' ([^ ]+) (\d+) (([^:]+:)?.+)")
def _parse_pkg_url(line):
    return _pkg_url_re.match(line).groups()

def parse_apt_install(out):
    res = []

    extra = []
    suggested = []
    recommended = []
    install = []
    packages = []
    newest = []
    upgrade = []
    keptback = []
    errors = []

    out2 = out.replace("\n  ", "  ")
    for line in out2.splitlines():
        if line.endswith('is already the newest version.'):
            newest.append(line.split(' ', 1)[0])
        elif line.startswith('The following extra packages will be installed:'):
            extra = line.split(':', 1)[1].strip().split()
        elif line.startswith('Suggested packages:'):
            suggested = line.split(':', 1)[1].strip().split()
        elif line.startswith('Recommended packages:'):
            recommended = line.split(':', 1)[1].strip().split()
        elif line.startswith('The following NEW packages will be installed:'):
            install = line.split(':', 1)[1].strip().split()
        elif line.startswith('The following packages have been kept back:'):
            keptback = line.split(':', 1)[1].strip().split()
        elif line.startswith('The following packages will be upgraded:'):
            upgrade = line.split(':', 1)[1].strip().split()
        elif line.startswith("'"):
            packages.append(_parse_pkg_url(line))
        elif line.startswith('E:'):
            errors.append(line.split(' ', 1)[1])

    return extra, suggested, recommended, install, packages, newest, \
           upgrade, keptback, errors

def parse_apt_search(out):
    res = []
    
    for line in out.splitlines():
        p = line.split(' ', 2)
        res.append((p[0], p[2]))

    return res

def _parse_apt_show_single(out):
    res = {}
    keys = []
    field = None
    
    for line in out.splitlines():
        if line.strip() == '':
            continue

        if line.startswith(' '):
            content = line.strip()
            if content == '.':
                content = ''
        else:
            field, content = line.split(':', 1)
            content = content.strip()
            keys.append(field)

        c = res.get(field, [])
        c.append(content)
        res[field] = c

    values = {}
    for key in keys:
        values[key] = "\n".join(res[key])

    return values, keys
    
def parse_apt_show(out):
    p = filter(lambda x: x != '', out.split("\n\n"))
    info = map(_parse_apt_show_single, p)
    info.append((None, []))
    return info[0]

if __name__ == '__main__':
    #print parse_apt_install(open('/tmp/apt-install.txt').read())
    #print parse_apt_search(open('/tmp/apt-search.txt').read())
    print parse_apt_show(open('/tmp/apt-show.txt').read())

