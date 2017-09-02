def main(argv):
    from urllib2 import urlopen
    bootstrap_url = "https://stash.atl.zillow.net/projects/CONFIG/repos/shared-buildouts/browse/bootstrap-buildout-pinned.py?raw"
    content = urlopen(bootstrap_url).read()
    exec(content)

if __name__ == "__main__":
    import sys
    main(sys.argv)
