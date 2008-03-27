import md5, os, tempfile, time, urllib2

class DiskCacheFetcher:
    def __init__(self, cache_dir=None):
        # If no cache directory specified, use system temp directory
        if cache_dir is None:
            cache_dir = tempfile.gettempdir()
        self.cache_dir = cache_dir
    def fetch(self, url, max_age=0):
        # Use MD5 hash of the URL as the filename
        filename = md5.new(url).hexdigest()
        filepath = os.path.join(self.cache_dir, filename)
        if os.path.exists(filepath):
            if int(time.time()) - os.path.getmtime(filepath) < max_age:
                return open(filepath).read()
        # Retrieve over HTTP and cache, using rename to avoid collisions
        data = urllib2.urlopen(url).read()
        fd, temppath = tempfile.mkstemp()
        fp = os.fdopen(fd, 'w')
        fp.write(data)
        fp.close()
        os.rename(temppath, filepath)
        return data