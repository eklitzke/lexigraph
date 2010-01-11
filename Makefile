src/add_point: src/add_point.c
	gcc -o $@ $^

clean:
	find . -name '*.py[co]' -delete
	find . -name '*.o' -delete
	rm -f src/add_point

.PHONY: clean
