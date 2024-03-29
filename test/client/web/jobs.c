#include <stdlib.h>
#include <stdio.h>
#include <string.h>

#include <cerver/http/http.h>
#include <cerver/http/status.h>

#include <cerver/http/json/json.h>

#include <cerver/utils/log.h>
#include <cerver/utils/utils.h>

#include "curl.h"

static const char *address = { "127.0.0.1:8080" };

static size_t jobs_request_all_data_handler (
	void *contents, size_t size, size_t nmemb, void *storage
) {

	(void) strncpy ((char *) storage, (char *) contents, size * nmemb);

	return size * nmemb;

}

// GET /
static unsigned int jobs_request_main (
	char *data_buffer
) {

	unsigned int retval = 1;

	CURL *curl = curl_easy_init ();
	if (curl) {
		retval = curl_simple_handle_data (
			curl, address,
			HTTP_STATUS_OK,
			jobs_request_all_data_handler, data_buffer
		);
	}

	curl_easy_cleanup (curl);

	return retval;

}

// POST /jobs
static unsigned int jobs_request_job (
	const char *actual_address, char *data_buffer
) {

	unsigned int retval = 1;

	CURL *curl = curl_easy_init ();
	if (curl) {
		retval = curl_post_form_value (
			curl, actual_address,
			HTTP_STATUS_OK,
			jobs_request_all_data_handler, data_buffer,
			"value", "hola"
		);
	}

	curl_easy_cleanup (curl);

	return retval;

}

static unsigned int jobs_request_all_actual (void) {

	unsigned int errors = 0;

	char data_buffer[4096] = { 0 };
	char actual_address[128] = { 0 };

	// GET /
	(void) printf ("GET /\n");
	errors |= jobs_request_main (data_buffer);

	// POST /jobs
	(void) printf ("POST /jobs\n");
	(void) snprintf (actual_address, 128, "%s/jobs", address);
	errors |= jobs_request_job (actual_address, data_buffer);

	return errors;

}

// perform requests to every route
static unsigned int jobs_request_all (void) {

	unsigned int retval = 1;

	if (!jobs_request_all_actual ()) {
		cerver_log_line_break ();
		cerver_log_line_break ();

		cerver_log_success (
			"jobs_request_all () - All requests succeeded!"
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

	code = (int) jobs_request_all ();

	cerver_log_end ();

	return code;

}
