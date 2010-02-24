import os
import re

env = Environment()

#################
# BUILD SERIALS
#################

serial_build = Builder(action='bin/gen_serials $SOURCES > $TARGET')
env.Append(BUILDERS = {'Serial': serial_build})

css_regex = re.compile(r'\.css$')
hash_sources = ['js/lexigraph.min.js', 'js/dygraph-combined.js', 'js/jquery-1.4.2.min.js']
for f in (x for x in os.listdir('static/css') if css_regex.search(x)):
	hash_sources.append(os.path.join('static/css', f))
serials = env.Serial('lexigraph/config/serials.py', hash_sources)
