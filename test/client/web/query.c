#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <cerver/files.h>

#include <cerver/http/status.h>

#include <cerver/utils/log.h>

#include "curl.h"

#define ADDRESS_SIZE				1024

#define REQUEST_FORM_VALUE_SIZE		32

static const char *address = { "127.0.0.1:8080" };

static size_t query_request_all_data_handler (
	void *contents, size_t size, size_t nmemb, void *storage
) {

	(void) strncpy ((char *) storage, (char *) contents, size * nmemb);

	return size * nmemb;

}

static unsigned int query_request_all_actual (void) {

	unsigned int errors = 0;

	char data_buffer[4096] = { 0 };
	char actual_address[ADDRESS_SIZE] = { 0 };

	/*** query value ***/
	// GET /query/value - good
	(void) printf ("GET /query/value - good\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/value?value=test", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		query_request_all_data_handler, data_buffer
	);

	// GET /query/value - bad
	(void) printf ("GET /query/value - bad\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/value?hola=test", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		query_request_all_data_handler, data_buffer
	);

	// GET /query/value - missing
	(void) printf ("GET /query/value - missing\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/value", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		query_request_all_data_handler, data_buffer
	);

	/*** query int ***/
	// GET /query/int - good
	(void) printf ("GET /query/int - good\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/int?value=78", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		query_request_all_data_handler, data_buffer
	);

	// GET /query/int - missing
	(void) printf ("GET /query/int - missing\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/int?test=78", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		query_request_all_data_handler, data_buffer
	);

	// GET /query/int - bad
	(void) printf ("GET /query/int - bad\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/int?value=test", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		query_request_all_data_handler, data_buffer
	);

	/*** query float ***/
	// GET /query/float - good
	(void) printf ("GET /query/float - good\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/float?value=8.78", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		query_request_all_data_handler, data_buffer
	);

	// GET /query/float - missing
	(void) printf ("GET /query/float - missing\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/float?hola=8.78", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		query_request_all_data_handler, data_buffer
	);

	// GET /query/float - bad
	(void) printf ("GET /query/float - bad\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/float?hola=test", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		query_request_all_data_handler, data_buffer
	);

	/*** query bool ***/
	// GET /query/bool - good
	(void) printf ("GET /query/bool - good\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/bool?value=True", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_OK,
		query_request_all_data_handler, data_buffer
	);

	// GET /query/bool - missing
	(void) printf ("GET /query/bool - missing\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/bool", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		query_request_all_data_handler, data_buffer
	);

	// GET /query/bool - bad
	(void) printf ("GET /query/bool - bad\n");
	(void) snprintf (
		actual_address, ADDRESS_SIZE,
		"%s/query/bool?value=hola", address
	);

	errors |= curl_full_handle_data (
		actual_address, HTTP_STATUS_BAD_REQUEST,
		query_request_all_data_handler, data_buffer
	);

	return errors;

}

// perform requests to every route
static unsigned int query_request_all (void) {

	unsigned int retval = 1;

	if (!query_request_all_actual ()) {
		cerver_log_line_break ();
		cerver_log_line_break ();

		cerver_log_success (
			"query_request_all () - All requests succeeded!"
		);

		cerver_log_line_break ();
		cerver_log_line_break ();

		retval = 0;
	}

	return retval;

}

int main (int argc, char **argv) {

	int code = 0;

	cerver_log_init ();

	code = (int) query_request_all ();

	cerver_log_end ();

	return code;

}
