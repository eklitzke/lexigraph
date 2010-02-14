import os
import re
import hashlib
import commands

env = Environment()

closure_min = Builder(action='python vendor/closure/bin/calcdeps.py -i js/require.js -p js -p js/closure-templates -p js/closure -c vendor/closure.jar -f --compilation_level -f ADVANCED_OPTIMIZATIONS -o compiled > $TARGET')
closure_deps = Builder(action='python vendor/closure/bin/calcdeps.py -p js -p js/closure-templates -p js/closure -c vendor/closure.jar -o deps > $TARGET')
env.Append(BUILDERS = {'ClosureMin': closure_min})
env.Append(BUILDERS = {'ClosureDeps': closure_deps})

closure_sources = commands.getoutput("find -H js -name '*.js' | grep -v '\.min\.js$' | grep -v 'deps\.js$'").split('\n')
min_js = env.ClosureMin('js/lexigraph.min.js', closure_sources)
dep_js = env.ClosureDeps('js/deps.js', closure_sources)

#################
# BUILD JS TEMPLATES
#################

soy_build = Builder(action='java -jar vendor/closure-templates/SoyToJsSrcCompiler.jar --shouldProvideRequireSoyNamespaces --outputPathFormat $TARGET $SOURCE')
env.Append(BUILDERS = {'Soy': soy_build})

soy_regex = re.compile(r'\.soy$')
for f in (x for x in os.listdir('js/templates') if soy_regex.search(x)):
	source = 'js/templates/' + f
	target = 'js/templates/' + soy_regex.sub('.js', f)
	closure_sources.append(target)
	Requires(min_js, env.Soy(target, source))

#################
# BUILD SERIALS
#################

serial_build = Builder(action='bin/gen_serials $SOURCES > $TARGET')
env.Append(BUILDERS = {'Serial': serial_build})

css_regex = re.compile(r'\.css$')
hash_sources = ['js/lexigraph.min.js', 'js/dygraph-combined.js']
for f in (x for x in os.listdir('static/css') if css_regex.search(x)):
	hash_sources.append(os.path.join('static/css', f))
serials = env.Serial('lexigraph/config/serials.py', hash_sources)
