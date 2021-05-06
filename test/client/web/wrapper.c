#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <cerver/utils/log.h>

#include "curl.h"

#define ADDRESS_SIZE			128

#define BUFFER_SIZE				4096

static const char *address = { "127.0.0.1:8080" };

static size_t wrapper_request_all_data_handler (
	void *contents, size_t size, size_t nmemb, void *storage
) {

	(void) strncpy ((char *) storage, (char *) contents, size * nmemb);

	return size * nmemb;

}

static unsigned int wrapper_request_main (
	CURL *curl, char *actual_address, char *data_buffer
) {
	unsigned int retval = 1;

	//GET /
	(void) snprintf(actual_address, ADDRESS_SIZE, "%s/", address);
	retval = curl_simple_handle_data (
		curl, actual_address,
		wrapper_request_all_data_handler, data_buffer
	);

	if (!strcmp ("{\"msg\": \"Wrapper works!\"}", data_buffer)) {
		retval = 0;
	}

	return retval;
}

static unsigned int wrapper_request_echo (
	CURL *curl, char *actual_address, char *data_buffer
) {

	unsigned int retval = 1;

	// GET /echo
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/echo?value=test", address);
	retval = curl_simple_handle_data (
		curl, actual_address,
		wrapper_request_all_data_handler, data_buffer
	);

	if (!strcmp ("{\"echo_says\": \"Wrapper received\": \"test\"}", data_buffer)) {
		retval = 0;
	}

	return retval;

}

static unsigned int wrapper_request_params (
	CURL *curl, char *actual_address, char *data_buffer
){

	unsigned int retval = 1;
	
	//GET /params/:id
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/params/id_test", address);
	retval = curl_simple_handle_data (
		curl, actual_address,
		wrapper_request_all_data_handler, data_buffer
	);

	if (!strcmp ("{\"msg\": \"Request received 1 in request\", \"params\": [\"id_test\"]}", data_buffer)) {
		retval = 0;
	}

	return retval;
}

static unsigned int wrapper_request_data (
	CURL *curl, char *actual_address, char *data_buffer
) {

	unsigned int retval = 1;
	
	//POST /data
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/data", address);
	char *json = "{\"test\": \"test\" }";

	retval = curl_simple_post_json (
		curl, actual_address,
		json , strlen(json)
	);

	return retval;
}

static unsigned int wrapper_request_token (
	CURL *curl, char *actual_address, char *data_buffer
) {

	unsigned int retval = 1;
	
	//POST /token
	(void) snprintf (actual_address, ADDRESS_SIZE, "%s/token", address);
	char *json = "{\"test\": \"test\" }";

	retval = curl_simple_post_json (
		curl, actual_address,
		json , strlen(json)
	);

	return retval;
}

static unsigned int wrapper_request_all_actual (
	CURL *curl
) {

	unsigned int errors = 0;

	char data_buffer[BUFFER_SIZE] = { 0 };
	char actual_address[ADDRESS_SIZE] = { 0 };

	// GET /
	errors |= curl_simple_handle_data (
		curl, address,
		wrapper_request_all_data_handler, data_buffer
	);

	errors |= wrapper_request_main (curl, actual_address, data_buffer);

	errors |= wrapper_request_echo (curl, actual_address, data_buffer);

	errors |= wrapper_request_params (curl, actual_address, data_buffer);

	errors |= wrapper_request_data (curl, actual_address, data_buffer);

	errors |= wrapper_request_token (curl, actual_address, data_buffer);

	(void) memset (data_buffer, 0, BUFFER_SIZE);

	// GET /text
	// (void) snprintf (actual_address, ADDRESS_SIZE, "%s/text", address);
	// errors |= curl_simple_handle_data (
	// 	curl, actual_address,
	// 	wrapper_request_all_data_handler, data_buffer
	// );

	return errors;

}

// perform requests to every route
static unsigned int wrapper_request_all (void) {

	unsigned int retval = 1;

	CURL *curl = curl_easy_init ();
	if (curl) {
		if (!wrapper_request_all_actual (curl)) {
			cerver_log_line_break ();
			cerver_log_line_break ();

			cerver_log_success (
				"wrapper_request_all () - All requests succeeded!"
			);

			cerver_log_line_break ();
			cerver_log_line_break ();

			retval = 0;
		}
	}

	curl_easy_cleanup (curl);

	return retval;

}

int main (int argc, char **argv) {

	int code = 0;

	cerver_log_init ();

	code = (int) wrapper_request_all ();

	cerver_log_end ();

	return code;

}