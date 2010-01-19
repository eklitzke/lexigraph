all: src/add_point src/dev_add_point

src/add_point: src/add_point.c
	gcc $$(curl-config --cflags) $$(curl-config --libs) -DLEXIGRAPH_DATAPOINT_URL=\"http://lexigraph.appspot.com/api/new/datapoint\" -o $@ $^

src/dev_add_point: src/add_point.c
	gcc $$(curl-config --cflags) $$(curl-config --libs) -o $@ $^

clean:
	find . -name '*.py[co]' -delete
	find . -name '*.o' -delete
	rm -f src/add_point

.PHONY: clean
