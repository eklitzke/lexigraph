all: src/add_point src/dev_add_point

src/add_point: src/add_point.c
	gcc $$(curl-config --cflags --libs) -o $@ $^

src/dev_add_point: src/add_point.c
	gcc $$(curl-config --cflags --libs) -DLEXIGRAPH_DATAPOINT_URL=\"http://localhost:8080/api/new/datapoint\" -o $@ $^

clean:
	find . -name '*.py[co]' -delete
	find . -name '*.o' -delete
	rm -f src/add_point
	rm -f src/dev_add_point

.PHONY: clean
