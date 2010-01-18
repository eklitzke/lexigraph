#include <stdlib.h>
#include <string.h>
#include <curl/curl.h>

#define LEXIGRAPH_DATAPOINT_URL "http://localhost:8080/api/new/datapoint"

#ifdef WITH_SSL
#define LEXIGRAPH_CURL_OPTS CURL_GLOBAL_SSL
#else
#define LEXIGRAPH_CURL_OPTS 0
#endif

void print_usage()
{
    fprintf(stderr, "usage: add_point <api_key> <dataset> <value>\n");
}

/* THIS WON'T WORK WITH SPACES */
char * add_field(CURL *handle, char *postdata, char *field, char *unencoded) {
    int ampersand;
    char *encoded;
    ampersand = strlen(postdata) == 0 ? 0 : 1;
    if (ampersand) {
        postdata = realloc(postdata, strlen(postdata) + strlen(field) + 2);
    } else {
        postdata = realloc(postdata, strlen(postdata) + strlen(field) + 1);
    }
    if (postdata == NULL) {
        perror("realloc()");
        exit(EXIT_FAILURE);
    }
    if (ampersand) {
        strcat(postdata, "&");
    }
    strcat(postdata, field);
    encoded = curl_easy_escape(handle, unencoded, 0);
    if (encoded == NULL) {
        perror("curl_easy_escape()");
        exit(EXIT_FAILURE);
    }
    postdata = realloc(postdata, strlen(postdata) + strlen(encoded) + 1);
    if (postdata == NULL) {
        perror("realloc()");
        exit(EXIT_FAILURE);
    }
    strcat(postdata, encoded);
    curl_free(encoded);
    return postdata;
}

void main(int argc, char **argv)
{
    CURL *handle;
    char *encoded;
    char *postdata;
    char *endptr;
    double val;

    if (argc != 4) {
        print_usage();
        goto error_case;
    }

    /* sanity check the api key */
    if (strlen(argv[1]) != 32) {
        print_usage();
        fprintf(stderr, "\nerror: invalid api key \"%s\"\n", argv[1]);
        goto error_case;
    }

    /* sanity check the value we've been given */
    val = strtod(argv[3], &endptr);
    if (!val && (argv[3] == endptr)) {
        print_usage();
        fprintf(stderr, "\nerror: invalid value \"%s\"\n", argv[3]);
        goto error_case;
    }

    /* set up curl */
    curl_global_init(LEXIGRAPH_CURL_OPTS);
    handle = curl_easy_init();

    /* construct the POST payload */
    postdata = malloc(1);
    postdata[0] = '\0';
    postdata = add_field(handle, postdata, "key=", argv[1]);
    postdata = add_field(handle, postdata, "dataset=", argv[2]);
    postdata = add_field(handle, postdata, "value=", argv[3]);

    curl_easy_setopt(handle, CURLOPT_POSTFIELDS, postdata);
    curl_easy_setopt(handle, CURLOPT_URL, LEXIGRAPH_DATAPOINT_URL);
    if (curl_easy_perform(handle)) {
        perror("curl_easy_perform()");
        goto error_case;
    }
    
    curl_easy_cleanup(handle);
    curl_global_cleanup();
    exit(EXIT_SUCCESS);

error_case:
    curl_easy_cleanup(handle);
    curl_global_cleanup();
    exit(EXIT_FAILURE);
}
