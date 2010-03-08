# -*-Python-*-
import os
import re

env = Environment()

#################
# JAVASCRIPT
#################

def generate_minify(source, target, env, for_signature):
    cmd = 'java -jar vendor/compiler.jar '
    cmd += ' '.join('--js %s' % s for s in source)
    cmd += ' --js_output_file %s' % (target[0],)
    return cmd

minify_build = Builder(generator=generate_minify)
concatenate_build = Builder(action='bin/minjs --concatenate-only $SOURCES > $TARGET')
env.Append(BUILDERS = {'MinifyJs': minify_build, 'ConcatenateJs': concatenate_build})

inhouse_js = ['lexigraph', 'dashboard', 'dataset', 'canvas']
env.ConcatenateJs('js/lexigraph.dev.js', ['js/%s.js' % j for j in inhouse_js])
env.MinifyJs('js/lexigraph.min.js', ['js/%s.js' % j for j in inhouse_js])

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
